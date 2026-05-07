#!/usr/bin/env python3
"""Validate 01a_АНАЛИЗ_НИШИ/market-profile.md against schema.

Checks:
- All 8 sections present (## 1. ... ## 8.)
- Section 1 contains valid accessibility_tier value
- Section 7 contains valid Predicted mode value

Exits 0 on valid, 1 on errors with messages on stdout.
"""
import re
import sys
from pathlib import Path


REQUIRED_SECTIONS = [
    (r"##\s*1\.\s*Accessibility\s+tier", 1),
    (r"##\s*2\.\s*Consideration\s+cycle", 2),
    (r"##\s*3\.\s*Decision\s+unit", 3),
    (r"##\s*4\.\s*Regulated\s+category", 4),
    (r"##\s*5\.\s*Emotional\s+load", 5),
    (r"##\s*6\.\s*Cultural\s+context", 6),
    (r"##\s*7\.\s*Сводная\s+рекомендация\s+режима", 7),
    (r"##\s*8\.\s*Источники\s+и\s+допущения", 8),
]

VALID_TIERS = {
    "utility_essential", "mass_consumer", "mid_premium",
    "premium", "luxury_status", "ultra_luxury",
}

VALID_MODES_PATTERN = re.compile(
    r"^(rational|emotional_aspiration|trust_authority|hybrid:[a-z_]+\+[a-z_]+|legacy_v1)$"
)


def validate(path):
    errors = []
    text = path.read_text(encoding="utf-8")

    for pattern, num in REQUIRED_SECTIONS:
        if not re.search(pattern, text, re.IGNORECASE):
            errors.append(f"Section {num} missing or malformed")

    tier_match = re.search(r"\*\*Tier:\*\*\s*([a-z_]+)", text, re.IGNORECASE)
    if tier_match:
        tier = tier_match.group(1).strip().lower()
        if tier not in VALID_TIERS:
            errors.append(f"Invalid accessibility tier: '{tier}'. Valid: {sorted(VALID_TIERS)}")

    mode_match = re.search(r"\*\*Predicted mode:\*\*\s*([a-z0-9_+:]+)", text, re.IGNORECASE)
    if mode_match:
        mode = mode_match.group(1).strip().lower()
        if not VALID_MODES_PATTERN.match(mode):
            errors.append(
                f"Invalid Predicted mode: '{mode}'. Valid forms: rational | emotional_aspiration | trust_authority | hybrid:X+Y"
            )

    return errors


def main():
    if len(sys.argv) != 2:
        print("usage: validate-market-profile.py <market-profile.md>", file=sys.stderr)
        return 2
    path = Path(sys.argv[1])
    if not path.exists():
        print(f"ERROR: {path} not found", file=sys.stderr)
        return 1
    errors = validate(path)
    if errors:
        print("market-profile.md validation FAILED:")
        for e in errors:
            print(f"  - {e}")
        return 1
    print(f"OK: {path} is valid")
    return 0


if __name__ == "__main__":
    sys.exit(main())
