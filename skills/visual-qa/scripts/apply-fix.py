#!/usr/bin/env python3
"""Применить fix_hint от codex к HTML/CSS.

Использование:
  apply-fix.py <html-file> --issue '<json>'

Поддерживаемые fix типы:
  css_tweak       — добавить inline style в selector
  photo_recrop    — TODO (вызывает photo-pipeline.py)
  photo_reprocess — TODO (codex reprocess)

Запрещены: text_*, block_* (блокированы content-preserve/structure-preserve).
"""
import argparse
import json
import sys
from pathlib import Path

from bs4 import BeautifulSoup


ALLOWED_TYPES = {"css_tweak"}
FORBIDDEN_PREFIXES = ("text_", "block_")


def apply_css_tweak(html_path: Path, selector: str, fix_hint: str) -> bool:
    """Парсит fix_hint типа 'css_tweak: object-position: center 20%' и добавляет inline style."""
    soup = BeautifulSoup(html_path.read_text(encoding="utf-8"), "html.parser")

    # Извлечь CSS правило из fix_hint
    # Формат ожидается: "css_tweak: <property>: <value>" или просто "<property>: <value>"
    css_part = fix_hint.split(":", 1)[-1].strip() if ":" in fix_hint else fix_hint
    if "css_tweak" in css_part:
        css_part = css_part.split(":", 1)[-1].strip()

    # Select element
    try:
        element = soup.select_one(selector)
    except Exception:
        return False
    if not element:
        return False

    existing_style = element.get("style", "")
    new_style = f"{existing_style}; {css_part}".strip("; ")
    element["style"] = new_style

    html_path.write_text(str(soup), encoding="utf-8")
    return True


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("html_file")
    parser.add_argument("--issue", required=True, help="JSON-string with issue")
    args = parser.parse_args()

    html_path = Path(args.html_file)
    if not html_path.exists():
        print(f"ERROR: {html_path} not found", file=sys.stderr)
        return 2

    try:
        issue = json.loads(args.issue)
    except json.JSONDecodeError as e:
        print(f"ERROR: invalid JSON: {e}", file=sys.stderr)
        return 2

    issue_type = issue.get("type", "")
    if any(issue_type.startswith(p) for p in FORBIDDEN_PREFIXES):
        print(f"BLOCKED: тип '{issue_type}' запрещён (content/structure preserve)", file=sys.stderr)
        return 3

    if issue_type not in ALLOWED_TYPES and not issue_type.startswith("css"):
        print(f"SKIP: тип '{issue_type}' не поддерживается auto-fix (попадает в warning)", file=sys.stderr)
        return 4

    selector = issue.get("selector", "")
    fix_hint = issue.get("fix_hint", "")
    if not selector or not fix_hint:
        print(f"ERROR: issue missing selector or fix_hint", file=sys.stderr)
        return 2

    applied = apply_css_tweak(html_path, selector, fix_hint)
    if applied:
        print(f"✅ Fix applied: {selector}")
        return 0
    else:
        print(f"❌ Failed to apply fix: selector not found или ошибка", file=sys.stderr)
        return 1


if __name__ == "__main__":
    sys.exit(main())
