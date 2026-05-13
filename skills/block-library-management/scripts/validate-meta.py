#!/usr/bin/env python3
"""Validate block-library/<category>/<id>/meta.yaml."""
import re
import sys
import yaml
from pathlib import Path

REQUIRED_KEYS = {
    "id", "category", "ru_market", "use_cases",
    "description", "slots", "source", "created",
    "display_name_ru", "layout_summary_ru",
}
DISPLAY_NAME_RU_MAX = 60
LAYOUT_SUMMARY_RU_MAX = 200
VALID_CATEGORIES = {
    "hero", "features", "social-proof", "process",
    "pricing", "trust", "cta", "faq", "quiz",
}
VALID_USE_CASES = {"services", "b2c", "local"}
VALID_SLOT_TYPES = {"photo", "text", "cta", "icon", "infographic"}
KEBAB = re.compile(r"^[a-z][a-z0-9-]*$")


def fail(m: str) -> None:
    print(f"ERROR: {m}", file=sys.stderr)
    sys.exit(1)


def main(path: str) -> None:
    data = yaml.safe_load(Path(path).read_text())
    if not isinstance(data, dict):
        fail("top-level must be a mapping")
    missing = REQUIRED_KEYS - set(data.keys())
    if missing:
        fail(f"missing required keys: {sorted(missing)}")
    if not KEBAB.match(data["id"]):
        fail(f"id must be kebab-case lowercase: {data['id']!r}")
    if data["category"] not in VALID_CATEGORIES:
        fail(f"invalid category: {data['category']!r}")
    if not isinstance(data["use_cases"], list) or not data["use_cases"]:
        fail("use_cases must be a non-empty list")
    for uc in data["use_cases"]:
        if uc not in VALID_USE_CASES:
            fail(f"invalid use_case: {uc!r}")
    dn = data.get("display_name_ru", "")
    if not isinstance(dn, str) or not dn.strip():
        fail("display_name_ru must be a non-empty string")
    if len(dn) > DISPLAY_NAME_RU_MAX:
        fail(f"display_name_ru exceeds {DISPLAY_NAME_RU_MAX} chars (got {len(dn)})")
    ls = data.get("layout_summary_ru", "")
    if not isinstance(ls, str) or not ls.strip():
        fail("layout_summary_ru must be a non-empty string")
    if len(ls) > LAYOUT_SUMMARY_RU_MAX:
        fail(f"layout_summary_ru exceeds {LAYOUT_SUMMARY_RU_MAX} chars (got {len(ls)})")
    if not isinstance(data["slots"], list):
        fail("slots must be a list (may be empty)")
    for i, slot in enumerate(data["slots"]):
        if not isinstance(slot, dict):
            fail(f"slot #{i} must be a mapping")
        if "type" not in slot or "name" not in slot:
            fail(f"slot #{i} missing type or name")
        if slot["type"] not in VALID_SLOT_TYPES:
            fail(f"slot #{i} invalid type: {slot['type']!r}")
    print("OK")


if __name__ == "__main__":
    if len(sys.argv) != 2:
        print("Usage: validate-meta.py <path>", file=sys.stderr)
        sys.exit(2)
    main(sys.argv[1])
