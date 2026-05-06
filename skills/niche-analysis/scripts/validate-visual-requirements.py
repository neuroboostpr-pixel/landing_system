#!/usr/bin/env python3
"""Validate 01a_АНАЛИЗ_НИШИ/visual-requirements.md against schema.

Checks:
- All 7 sections present (## 1. ... ## 7.)
- Section 6 has at least 3 entries with ❌ and at least 3 with ✅
Exits 0 on valid, 1 on errors with messages on stdout.
"""
import re
import sys
from pathlib import Path


REQUIRED_SECTIONS = [
    r"##\s*1\.\s*Hero\s+focal\s+point",
    r"##\s*2\.\s*Photography\s+style",
    r"##\s*3\.\s*People\s+in\s+frame",
    r"##\s*4\.\s*Product\s+treatment",
    r"##\s*5\.\s*Background\s+palette",
    r"##\s*6\.\s*Red\s+flags",
    r"##\s*7\.\s*Источники\s+правил",
]


def validate(path):
    errors = []
    text = path.read_text(encoding="utf-8")

    for i, pattern in enumerate(REQUIRED_SECTIONS, start=1):
        if not re.search(pattern, text, re.IGNORECASE):
            errors.append(f"Section {i} missing or malformed (pattern: {pattern})")

    s6_match = re.search(
        r"##\s*6\.\s*Red\s+flags.*?(?=##\s*7\.|\Z)",
        text,
        re.IGNORECASE | re.DOTALL,
    )
    if s6_match:
        s6_text = s6_match.group(0)
        red = len(re.findall(r"❌", s6_text))
        green = len(re.findall(r"✅", s6_text))
        if red < 3:
            errors.append(f"Section 6: at least 3 red flags (❌) required, found {red}")
        if green < 3:
            errors.append(f"Section 6: at least 3 preferences (✅) required, found {green}")

    return errors


def main():
    if len(sys.argv) != 2:
        print("usage: validate-visual-requirements.py <visual-requirements.md>", file=sys.stderr)
        return 2
    path = Path(sys.argv[1])
    if not path.exists():
        print(f"ERROR: {path} not found", file=sys.stderr)
        return 1
    errors = validate(path)
    if errors:
        print("visual-requirements.md validation FAILED:")
        for e in errors:
            print(f"  - {e}")
        return 1
    print(f"OK: {path} is valid")
    return 0


if __name__ == "__main__":
    sys.exit(main())
