"""Оркестратор импорта блоков в block-library.

Usage:
    python -m skills.landing_import_blocks.scripts.import_blocks --url <URL>
    python -m skills.landing_import_blocks.scripts.import_blocks --screenshot <path>
    python -m skills.landing_import_blocks.scripts.import_blocks --from-chat
"""
from __future__ import annotations
import argparse
import json
import subprocess
import sys
import tempfile
from pathlib import Path

import yaml

REPO_ROOT = Path(__file__).resolve().parents[3]
BLOCK_LIB = REPO_ROOT / "block-library"
CATALOG = BLOCK_LIB / "catalog.yaml"

# check_duplicates лежит рядом, но папка содержит дефис — грузим по пути,
# чтобы работало и как `python import_blocks.py`, и как `-m ...`.
import importlib.util as _ilu

_cd_path = Path(__file__).resolve().parent / "check_duplicates.py"
_spec = _ilu.spec_from_file_location("import_blocks_check_duplicates", _cd_path)
_cd = _ilu.module_from_spec(_spec)
_spec.loader.exec_module(_cd)
compute_signature = _cd.compute_signature
find_duplicate = _cd.find_duplicate


def _find_bash() -> str:
    """Locate a Git-Bash / MSYS bash, NOT the WSL one.

    On Windows the bare `bash` often resolves to WSL's bash, which only sees
    drives via /mnt/<d>/ — but our POSIX-style paths use /<d>/ (Git Bash style).
    Prefer the Git Bash bundled with Git for Windows.
    """
    import shutil
    candidates = [
        r"C:\Program Files\Git\bin\bash.exe",
        r"C:\Program Files\Git\usr\bin\bash.exe",
        r"C:\Program Files (x86)\Git\bin\bash.exe",
    ]
    for c in candidates:
        if Path(c).exists():
            return c
    return shutil.which("bash") or "bash"


def _bash_path(p) -> str:
    """Convert a Windows path to a Git-Bash POSIX path (D:\\x → /d/x).

    Git Bash eats backslashes, so we must pass forward-slash paths.
    On POSIX this is a no-op.
    """
    s = str(Path(p))
    if len(s) > 1 and s[1] == ":":  # drive-letter path like D:\...
        drive = s[0].lower()
        rest = s[2:].replace("\\", "/")
        return f"/{drive}{rest}"
    return s.replace("\\", "/")


def next_block_id(block_type: str, existing_blocks: list[dict]) -> str:
    """Вычислить следующий id вида hero-004."""
    prefix = f"{block_type}-"
    nums = []
    for b in existing_blocks:
        bid = b.get("id", "")
        if bid.startswith(prefix):
            try:
                nums.append(int(bid[len(prefix):]))
            except ValueError:
                pass
    n = max(nums) + 1 if nums else 1
    return f"{block_type}-{n:03d}"


def get_image_from_url(url: str, work_dir: Path) -> Path:
    """Скачать скриншот URL через take-page-screenshot.py."""
    out_dir = work_dir / "screenshots"
    out_dir.mkdir(parents=True, exist_ok=True)
    script = REPO_ROOT / "scripts" / "import-blocks" / "take-page-screenshot.py"
    subprocess.run(
        [sys.executable, str(script), url, "--out", str(out_dir)],
        check=True,
    )
    screenshots = list(out_dir.glob("*.png"))
    if not screenshots:
        raise FileNotFoundError(f"No screenshots found in {out_dir}")
    return screenshots[0]


def get_image_from_chat(work_dir: Path) -> Path | None:
    """Извлечь скриншот из JSONL сессии через wizard-save-images.py."""
    out_dir = work_dir / "screenshots"
    out_dir.mkdir(parents=True, exist_ok=True)
    script = REPO_ROOT / "scripts" / "wizard-save-images.py"
    if not script.exists():
        return None
    result = subprocess.run(
        [sys.executable, str(script), "--dst", str(out_dir), "--prefix", "import"],
        capture_output=True, text=True, encoding="utf-8",
    )
    try:
        data = json.loads(result.stdout)
        if data.get("count", 0) > 0:
            return out_dir / data["saved"][0]
    except (json.JSONDecodeError, KeyError):
        pass
    return None


def format_duplicate_warning(existing: dict, new_block: dict) -> str:
    """Форматировать предупреждение о дубле."""
    ex_slots = ", ".join(s["name"] for s in existing.get("slots", []))
    new_slots = ", ".join(s["name"] for s in new_block.get("slots", []))
    ex_bg = "есть" if existing.get("has_bg_image") else "нет"
    new_bg = "есть" if new_block.get("has_bg_image") else "нет"
    new_name = new_block.get("display_name_ru", "")
    diff_slots = (
        set(s["name"] for s in new_block.get("slots", []))
        - set(s["name"] for s in existing.get("slots", []))
    )
    if diff_slots:
        diff_str = f"Отличие: новый добавляет слоты [{', '.join(sorted(diff_slots))}]."
    elif ex_bg != new_bg:
        diff_str = "Отличие: фоновое изображение."
    else:
        diff_str = "Отличия минимальны."
    return (
        f"⚠️  Похожий блок уже есть в библиотеке: {existing['id']}\n"
        f"   Существующий: {existing.get('layout_pattern','')} | {ex_slots} | фон: {ex_bg}\n"
        f"   Новый:        {new_block.get('layout_pattern','')} | {new_slots} | фон: {new_bg}\n"
        f"   {diff_str}\n"
        f"   Добавить '{new_name}' как новый блок? (yes/no)"
    )


def format_result_summary(added: list[dict], skipped: list[dict]) -> str:
    lines = []
    if added:
        lines.append(f"✅ Добавлено {len(added)} блоков: {', '.join(b['id'] for b in added)}")
    if skipped:
        lines.append(f"⏭  Пропущено {len(skipped)} дублей: {', '.join(b['id'] for b in skipped)}")
    lines.append(f"Открой: {BLOCK_LIB / 'gallery.html'}")
    return "\n".join(lines)


def main(argv: list[str] | None = None) -> int:
    p = argparse.ArgumentParser(description="Import blocks into block-library")
    group = p.add_mutually_exclusive_group(required=True)
    group.add_argument("--url", help="URL страницы")
    group.add_argument("--screenshot", help="Путь к скриншоту")
    group.add_argument("--from-chat", action="store_true", help="Скриншот из чата")
    p.add_argument("--yes-to-all", action="store_true", help="Добавить все без подтверждения")
    args = p.parse_args(argv)

    work_dir = Path(tempfile.mkdtemp(prefix="import-blocks-"))

    # [1] Получить изображение
    if args.url:
        print(f"[1/6] Скачиваю скриншот {args.url}...")
        screenshot = get_image_from_url(args.url, work_dir)
    elif args.screenshot:
        screenshot = Path(args.screenshot)
    else:
        print("[1/6] Извлекаю скриншот из чата...")
        screenshot = get_image_from_chat(work_dir)
        if not screenshot:
            print("ERROR: Скриншот не найден в сессии.", file=sys.stderr)
            return 1

    # [2] Codex vision → structure.json
    print("[2/6] Анализирую структуру через Codex...")
    structure_path = work_dir / "structure.json"
    analyze_sh = REPO_ROOT / "scripts" / "import-blocks" / "codex-analyze-structure.sh"
    result = subprocess.run(
        [_find_bash(), _bash_path(analyze_sh), _bash_path(screenshot)],
        capture_output=True, text=True, encoding="utf-8",
    )
    if result.returncode != 0:
        print(f"ERROR: Codex failed:\n{result.stderr}", file=sys.stderr)
        return 1
    structure_path.write_text(result.stdout, encoding="utf-8")
    blocks = json.loads(result.stdout).get("blocks", [])
    print(f"   Найдено блоков: {len(blocks)}")

    # [3] Проверка дублей
    print("[3/6] Проверяю дубли...")
    catalog_data = (
        yaml.safe_load(CATALOG.read_text(encoding="utf-8"))
        if CATALOG.exists() else {"blocks": []}
    )
    existing_blocks = catalog_data.get("blocks", [])

    to_add, skipped = [], []
    for block in blocks:
        dup_id = find_duplicate(block, CATALOG)
        if dup_id:
            if args.yes_to_all:
                skipped.append({"id": dup_id})
                continue
            dup_block = next(
                (b for b in existing_blocks if b.get("id") == dup_id),
                {"id": dup_id, "slots": []},
            )
            print(format_duplicate_warning(dup_block, block))
            if input("> ").strip().lower() not in ("yes", "y", "да"):
                skipped.append({"id": dup_id})
                continue
        block["_id"] = next_block_id(block["type"], existing_blocks)
        to_add.append(block)

    if not to_add:
        print(format_result_summary([], skipped))
        return 0

    # [4] Генерация template.html
    print(f"[4/6] Генерирую HTML для {len(to_add)} блоков...")
    added_json = work_dir / "added-blocks.json"
    structure_path.write_text(json.dumps({"blocks": to_add}), encoding="utf-8")
    subprocess.run([
        sys.executable,
        str(REPO_ROOT / "scripts" / "import-blocks" / "generate-blocks.py"),
        "--structure", str(structure_path),
        "--screenshot", str(screenshot),
        "--niche", "generic",
        "--source-url", args.url or str(screenshot),
        "--out", str(BLOCK_LIB),
        "--work-dir", str(work_dir),
    ], check=True)

    # [5] update-catalog.py
    print("[5/6] Обновляю catalog.yaml...")
    subprocess.run([
        sys.executable,
        str(REPO_ROOT / "scripts" / "import-blocks" / "update-catalog.py"),
        "--library", str(BLOCK_LIB),
        "--added-from", str(added_json),
    ], check=True)

    # [6] canonical gallery generator (B35: single scripts/generate-gallery.py)
    print("[6/6] Обновляю gallery.html...")
    subprocess.run([
        sys.executable,
        str(REPO_ROOT / "scripts" / "generate-gallery.py"),
        "--library", str(BLOCK_LIB),
        "--output", str(BLOCK_LIB / "gallery.html"),
    ], check=True)

    print(format_result_summary([{"id": b["_id"]} for b in to_add], skipped))
    return 0


if __name__ == "__main__":
    sys.exit(main())
