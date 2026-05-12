#!/usr/bin/env python3
"""Validate block-library/<category>/<id>/meta.yaml."""
import re
import sys
import yaml
from pathlib import Path

REQUIRED_KEYS = {
    "id", "category", "ru_market", "use_cases",
    "description", "slots", "source", "created",
}
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
