#!/usr/bin/env python3
"""Validate 01a_АНАЛИЗ_НИШИ/competitors.yaml against schema.

Exits 0 on valid, 1 on errors with messages on stdout.
"""
import sys
from pathlib import Path

try:
    import yaml
except ImportError:
    print("ERROR: PyYAML not installed. Run: pip install pyyaml", file=sys.stderr)
    sys.exit(2)

VALID_ROLES = {
    "direct", "local_dealer", "manufacturer", "analog",
    "category_leader", "local_competitor", "indirect",
}
VALID_CONFIDENCE = {"high", "medium", "low"}
REQUIRED_FIELDS = {
    "name", "role", "url", "region", "positioning", "target_audience",
    "price_range", "key_messages", "visual_notes", "notes_for_us",
    "source", "confidence",
}
MIN_COUNT = 15
MAX_COUNT = 25


def validate(path):
    errors = []
    try:
        data = yaml.safe_load(path.read_text(encoding="utf-8"))
    except Exception as e:
        return [f"YAML parse error: {e}"]

    if not isinstance(data, dict) or "competitors" not in data:
        return ["Top-level must be a mapping with key 'competitors'"]

    items = data["competitors"]
    if not isinstance(items, list):
        return ["'competitors' must be a list"]

    n = len(items)
    if n < MIN_COUNT:
        errors.append(f"Need minimum 15 entries, got {n}")
    if n > MAX_COUNT:
        errors.append(f"Maximum 25 entries allowed, got {n}")

    seen_roles = set()
    for i, entry in enumerate(items):
        if not isinstance(entry, dict):
            errors.append(f"Entry {i}: must be a mapping")
            continue
        missing = REQUIRED_FIELDS - set(entry.keys())
        if missing:
            errors.append(f"Entry {i} ({entry.get('name', '?')}): missing fields {sorted(missing)}")
        role = entry.get("role")
        if role not in VALID_ROLES:
            errors.append(f"Entry {i} ({entry.get('name', '?')}): invalid role '{role}', must be one of {sorted(VALID_ROLES)}")
        else:
            seen_roles.add(role)
        conf = entry.get("confidence")
        if conf not in VALID_CONFIDENCE:
            errors.append(f"Entry {i} ({entry.get('name', '?')}): invalid confidence '{conf}'")

    if len(seen_roles) < 3:
        errors.append(f"Need at least 3 different roles, got {len(seen_roles)}: {sorted(seen_roles)}")

    return errors


def main():
    if len(sys.argv) != 2:
        print("usage: validate-competitors.py <competitors.yaml>", file=sys.stderr)
        return 2
    path = Path(sys.argv[1])
    if not path.exists():
        print(f"ERROR: {path} not found", file=sys.stderr)
        return 1
    errors = validate(path)
    if errors:
        print("competitors.yaml validation FAILED:")
        for e in errors:
            print(f"  - {e}")
        return 1
    print(f"OK: {path} is valid")
    return 0


if __name__ == "__main__":
    sys.exit(main())
