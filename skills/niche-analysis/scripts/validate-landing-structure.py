#!/usr/bin/env python3
"""Validate 01a_АНАЛИЗ_НИШИ/landing-structure.md.

Required:
- Frontmatter-style headers: Тип бренда, Режим
- Section "Блоки лендинга" with markdown table containing Hero, CTA, Footer
- Section "Обоснование выбора структуры"
- Section "Контракт с wp-builder"

Exits 0 on valid, 1 on errors.
"""
import re
import sys
from pathlib import Path


REQUIRED_BLOCKS = {"hero", "cta", "footer"}


def validate(path):
    errors = []
    text = path.read_text(encoding="utf-8")

    for header in (
        r"##\s+Блоки\s+лендинга",
        r"##\s+Обоснование\s+выбора\s+структуры",
        r"##\s+Контракт\s+с\s+wp-builder",
    ):
        if not re.search(header, text, re.IGNORECASE):
            errors.append(f"Section missing: {header}")

    if not re.search(r">\s*Тип\s+бренда:\s*[123]", text, re.IGNORECASE):
        errors.append("Header missing: > Тип бренда: 1|2|3")
    if not re.search(r">\s*Режим:\s*[a-z_+:]+", text, re.IGNORECASE):
        errors.append("Header missing: > Режим: <mode>")

    text_lower = text.lower()
    for block in REQUIRED_BLOCKS:
        if not re.search(rf"\|\s*{re.escape(block)}\b", text_lower):
            errors.append(f"Required block missing in table: {block}")

    return errors


def main():
    if len(sys.argv) != 2:
        print("usage: validate-landing-structure.py <landing-structure.md>", file=sys.stderr)
        return 2
    path = Path(sys.argv[1])
    if not path.exists():
        print(f"ERROR: {path} not found", file=sys.stderr)
        return 1
    errors = validate(path)
    if errors:
        print("landing-structure.md validation FAILED:")
        for e in errors:
            print(f"  - {e}")
        return 1
    print(f"OK: {path} is valid")
    return 0


if __name__ == "__main__":
    sys.exit(main())
