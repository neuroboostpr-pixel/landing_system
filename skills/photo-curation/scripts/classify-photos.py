#!/usr/bin/env python3
"""classify-photos.py — PR-K AI-классификация фоток в inbox/ через codex.

Для каждого фото в `<project>/07c_PHOTOS/inbox/`:
  1. Считает hash файла (sha256, 16 hex).
  2. Если в `.classifications.json` уже есть запись с тем же hash → skip (cache).
  3. Иначе зовёт codex c промптом-одним-словом (templates/classify-prompt-type.md).
  4. Парсит ОДНО слово из 9-типов:
        hero | portrait | team | car | vehicle | product | interior | lifestyle | background
     Если codex отвечает что-то другое → fallback "lifestyle".
  5. Записывает в `<project>/07c_PHOTOS/inbox/.classifications.json`:
        {
          "<filename>": {"type": "team", "ratio": "16:9", "size": "1920x1080", "hash": "..."},
          ...
        }

Паттерн вызова codex идентичен `codex-process-photo.sh`:
    printf '%s' "$PROMPT" | codex exec --skip-git-repo-check -i <photo> -

Mock-режим для тестов:
    CODEX_CLASSIFY_MOCK=team — все фото классифицируются как team
    CODEX_CLASSIFY_MOCK_MAP=foo.jpg:hero,bar.jpg:product — per-file mapping

Usage:
    python3 classify-photos.py <project_dir>
"""
import hashlib
import json
import os
import subprocess
import sys
from pathlib import Path

try:
    from PIL import Image
except ImportError:
    Image = None


VALID_TYPES = {
    "hero", "portrait", "team", "car", "vehicle",
    "product", "interior", "lifestyle", "background",
}

IMAGE_EXTS = {".jpg", ".jpeg", ".png", ".webp"}


def file_hash(path: Path) -> str:
    """sha256 первых 1 МБ + общий размер — быстрый стабильный hash."""
    h = hashlib.sha256()
    with path.open("rb") as f:
        h.update(f.read(1024 * 1024))
    h.update(str(path.stat().st_size).encode())
    return h.hexdigest()[:16]


def image_dims(path: Path):
    """Возвращает (ratio_str, size_str) или ('?', '?') если Pillow недоступен."""
    if Image is None:
        return "?", "?"
    try:
        with Image.open(path) as im:
            w, h = im.size
        return _ratio(w, h), f"{w}x{h}"
    except Exception:
        return "?", "?"


def _ratio(w: int, h: int) -> str:
    """Округлённое соотношение сторон, например '16:9', '1:1', '9:16'."""
    from math import gcd
    if w == 0 or h == 0:
        return "?"
    # Подгон под канонические ratios
    val = w / h
    candidates = {
        "16:9": 16 / 9,
        "9:16": 9 / 16,
        "4:3": 4 / 3,
        "3:4": 3 / 4,
        "1:1": 1.0,
        "3:2": 3 / 2,
        "2:3": 2 / 3,
    }
    best, best_err = "?", 1e9
    for label, v in candidates.items():
        err = abs(val - v) / v
        if err < best_err:
            best, best_err = label, err
    # tolerance — 5%
    if best_err <= 0.05:
        return best
    # иначе вернём сырое w:h после gcd
    g = gcd(w, h)
    return f"{w // g}:{h // g}"


def parse_codex_type(raw: str) -> str:
    """Берём первое валидное слово из ответа codex. Fallback — lifestyle."""
    if not raw:
        return "lifestyle"
    for token in raw.replace(",", " ").replace(".", " ").split():
        t = token.strip().lower()
        if t in VALID_TYPES:
            return t
    return "lifestyle"


def call_codex(prompt: str, photo: Path) -> str:
    """Вызывает codex exec с промптом через stdin и фото через -i.

    Mock через env: CODEX_CLASSIFY_MOCK / CODEX_CLASSIFY_MOCK_MAP.
    """
    mock_map = os.environ.get("CODEX_CLASSIFY_MOCK_MAP", "")
    if mock_map:
        for pair in mock_map.split(","):
            if ":" in pair:
                fname, ftype = pair.split(":", 1)
                if photo.name == fname.strip():
                    return ftype.strip()
    mock = os.environ.get("CODEX_CLASSIFY_MOCK")
    if mock:
        return mock

    # реальный codex
    env = os.environ.copy()
    env["PATH"] = (
        f"{os.path.expanduser('~/.local/node-current/bin')}:"
        f"{os.path.expanduser('~/.local/bin')}:" + env.get("PATH", "")
    )
    try:
        proc = subprocess.run(
            ["codex", "exec", "--skip-git-repo-check", "-i", str(photo), "-"],
            input=prompt,
            text=True,
            capture_output=True,
            env=env,
            timeout=120,
        )
    except FileNotFoundError:
        print("ERROR: codex CLI not found in PATH", file=sys.stderr)
        return "lifestyle"
    except subprocess.TimeoutExpired:
        print(f"WARN: codex timeout for {photo.name}", file=sys.stderr)
        return "lifestyle"

    if proc.returncode != 0:
        print(f"WARN: codex rc={proc.returncode} for {photo.name}: {proc.stderr[:200]}",
              file=sys.stderr)
        return "lifestyle"
    return proc.stdout or ""


def load_prompt(template_path: Path) -> str:
    """Извлекает Prompt body из templates/classify-prompt-type.md."""
    import re
    text = template_path.read_text(encoding="utf-8")
    m = re.search(r"## Prompt body\s*\n+```\s*\n(.+?)\n```", text, re.DOTALL)
    if not m:
        raise SystemExit(f"ERROR: {template_path} missing '## Prompt body' code fence")
    return m.group(1)


def main(project_dir: Path) -> int:
    inbox = project_dir / "07c_PHOTOS" / "inbox"
    if not inbox.is_dir():
        print(f"ERROR: {inbox} не существует", file=sys.stderr)
        return 2

    cache_file = inbox / ".classifications.json"
    cache = {}
    if cache_file.exists():
        try:
            cache = json.loads(cache_file.read_text(encoding="utf-8"))
        except json.JSONDecodeError:
            print(f"WARN: {cache_file} битый — пересоздаём", file=sys.stderr)
            cache = {}

    template = Path(__file__).resolve().parent.parent / "templates" / "classify-prompt-type.md"
    prompt = load_prompt(template)

    photos = sorted(p for p in inbox.iterdir()
                    if p.is_file() and p.suffix.lower() in IMAGE_EXTS)
    if not photos:
        print(f"WARN: в {inbox} нет фото", file=sys.stderr)
        cache_file.write_text(json.dumps(cache, indent=2, ensure_ascii=False))
        return 0

    new_count = 0
    cached_count = 0
    for photo in photos:
        h = file_hash(photo)
        existing = cache.get(photo.name)
        if existing and existing.get("hash") == h:
            cached_count += 1
            continue

        raw = call_codex(prompt, photo)
        ptype = parse_codex_type(raw)
        ratio, size = image_dims(photo)
        cache[photo.name] = {
            "type": ptype,
            "ratio": ratio,
            "size": size,
            "hash": h,
        }
        new_count += 1
        print(f"  classified: {photo.name} → {ptype} ({ratio}, {size})", file=sys.stderr)

    cache_file.write_text(json.dumps(cache, indent=2, ensure_ascii=False))
    print(f"OK: classified {new_count} new, {cached_count} cached → {cache_file}",
          file=sys.stderr)
    return 0


if __name__ == "__main__":
    if len(sys.argv) != 2:
        print("Usage: classify-photos.py <project_dir>", file=sys.stderr)
        sys.exit(2)
    sys.exit(main(Path(sys.argv[1])))
