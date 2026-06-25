#!/usr/bin/env python3
"""Проверяет что текст из prototype.yaml присутствует в composed.html.

Exit codes:
  0 — все строки прототипа найдены, порядок блоков сохранён
  1 — есть расхождения (детали в stderr)
  2 — файл prototype.yaml или composed.html не найден
"""
import re
import sys
from pathlib import Path

import yaml
from bs4 import BeautifulSoup


# name/hint — это метаданные слота (машинный id и описание фото-инструкция),
# а не видимый текст лендинга → не требуем их в composed (reference-driven §1.1).
SKIP_KEYS = {"id", "type", "block_id", "class", "tag", "data-block", "name", "hint",
             "slug", "source_file", "action",
             # ── структурные ключи типизированного формата gen-prototype ──
             # (роли/группы/ярлыки/служебная мета — НЕ видимый контент лендинга)
             "role", "group", "screen_label", "block_label", "label", "position",
             "meta", "source", "niche", "project", "title",
             "client_notes", "block_instructions", "seo_phrases"}
MIN_LEN = 3  # минимальная длина строки чтобы проверять (короткие — false positives)
PLACEHOLDER_MARKERS = ("____", "___", "TBD", "tbd")


def normalize(s: str) -> str:
    """Нормализует whitespace, сохраняет регистр."""
    return re.sub(r"\s+", " ", s).strip()


def is_placeholder(s: str) -> bool:
    return any(m in s for m in PLACEHOLDER_MARKERS)


def extract_yaml_strings(node) -> list[str]:
    """Рекурсивно собирает все строковые значения, кроме служебных."""
    if isinstance(node, str):
        s = node.strip()
        if len(s) >= MIN_LEN and not is_placeholder(s):
            return [s]
        return []
    if isinstance(node, list):
        out = []
        for item in node:
            out.extend(extract_yaml_strings(item))
        return out
    if isinstance(node, dict):
        out = []
        for k, v in node.items():
            if k in SKIP_KEYS:
                continue
            out.extend(extract_yaml_strings(v))
        return out
    return []


def _md_strings(md_path: Path) -> list[str]:
    """Значимые строки prototype.md (A1: канон этапа — md, yaml опционален).

    Содержательные строки без markdown-заголовков; «Ключ: Значение» → значение.
    """
    out: list[str] = []
    for raw in md_path.read_text(encoding="utf-8").splitlines():
        line = raw.strip()
        if not line or line.startswith("#"):
            continue
        line = line.lstrip("-*").strip()
        if ":" in line:
            _, _, value = line.partition(":")
            if value.strip():
                line = value.strip()
        # «Заголовок — Текст» в одной строке прототипа = два отдельных поля
        for part in re.split(r"\s+[—–]\s+", line):
            part = part.strip()
            if len(part) >= MIN_LEN and not is_placeholder(part):
                out.append(part)
    return out


def _active_proto_yaml(proto_dir: Path) -> Path | None:
    """Активный prototype-*.yaml по meta.active:true (формат gen-prototype).

    Раньше читался только legacy prototype.yaml → новый prototype-01.yaml не
    находился и весь контент считался «потерянным» (ложный FAIL). Теперь
    источник истины — флаг active; legacy-имя остаётся fallback'ом.
    """
    for p in sorted(proto_dir.glob("prototype-*.yaml")):
        try:
            d = yaml.safe_load(p.read_text(encoding="utf-8")) or {}
        except Exception:
            continue
        if (d.get("meta") or {}).get("active") is True:
            return p
    legacy = proto_dir / "prototype.yaml"
    return legacy if legacy.exists() else None


def main(project_dir: Path) -> int:
    proto_dir = project_dir / "07_ПРОТОТИП"
    proto_yaml = _active_proto_yaml(proto_dir) or (proto_dir / "prototype.yaml")
    proto_md = proto_dir / "prototype.md"
    composed_path = project_dir / "07b_COMPOSED" / "composed.html"

    if not proto_yaml.exists() and not proto_md.exists():
        print(f"ERROR: нет активного prototype-*.yaml / prototype.yaml / prototype.md в "
              f"{proto_dir}", file=sys.stderr)
        return 2
    if not composed_path.exists():
        print(f"ERROR: {composed_path} не найден", file=sys.stderr)
        return 2

    proto_data = (yaml.safe_load(proto_yaml.read_text(encoding="utf-8")) or {}) \
        if proto_yaml.exists() else {}
    html_raw = composed_path.read_text(encoding="utf-8")
    soup = BeautifulSoup(html_raw, "html.parser")
    html_text = normalize(soup.get_text(separator=" "))

    # 1. Substring match для всех значимых строк (yaml если есть, иначе канон-md)
    blocks = proto_data.get("blocks", [])
    all_strings = extract_yaml_strings(blocks) if blocks else (
        _md_strings(proto_md) if proto_md.exists() else [])
    missing = []
    for s in all_strings:
        norm = normalize(s)
        if norm and norm not in html_text:
            missing.append(norm[:100])

    # 2. Порядок блоков по data-block="<id>"
    proto_ids = [b.get("id") for b in blocks if isinstance(b, dict) and b.get("id")]
    html_ids_all = [el.get("data-block") for el in soup.find_all(attrs={"data-block": True})]
    html_ids = [b for b in html_ids_all if b in proto_ids]
    order_ok = True
    if proto_ids and html_ids:
        expected_order = [b for b in proto_ids if b in html_ids]
        if html_ids[: len(expected_order)] != expected_order:
            order_ok = False

    fail = bool(missing) or not order_ok

    if fail:
        if missing:
            print(
                f"❌ В composed.html не найдено {len(missing)} строк из prototype.yaml:",
                file=sys.stderr,
            )
            for m in missing[:10]:
                print(f"   - «{m}»", file=sys.stderr)
            if len(missing) > 10:
                print(f"   ... ещё {len(missing) - 10}", file=sys.stderr)
        if not order_ok:
            print("❌ Порядок блоков в composed.html отличается от prototype.yaml", file=sys.stderr)
            print(f"   Прототип: {proto_ids}", file=sys.stderr)
            print(f"   HTML:     {html_ids}", file=sys.stderr)
        return 1

    print(f"✅ Контент прототипа сохранён ({len(all_strings)} строк проверено)")
    return 0


if __name__ == "__main__":
    if len(sys.argv) != 2:
        print("Usage: verify_content_preserved.py <project-dir>", file=sys.stderr)
        sys.exit(2)
    sys.exit(main(Path(sys.argv[1])))
