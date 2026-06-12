#!/usr/bin/env python3
"""Validate block-library/catalog.yaml.

Usage: validate-catalog.py <path-to-catalog.yaml>
Exit 0 on valid, non-zero with explanation on invalid.
"""
import sys
import yaml
from pathlib import Path


REQUIRED_TOP_KEYS = {"version", "updated", "blocks"}
REQUIRED_BLOCK_KEYS = {"id", "path", "category", "use_cases"}
VALID_CATEGORIES = {
    "hero", "features", "social-proof", "process",
    "pricing", "trust", "cta", "faq", "quiz",
}
VALID_USE_CASES = {"services", "b2c", "local"}


def fail(msg: str) -> None:
    print(f"ERROR: {msg}", file=sys.stderr)
    sys.exit(1)


def main(path: str) -> None:
    data = yaml.safe_load(Path(path).read_text())
    if not isinstance(data, dict):
        fail("top-level must be a mapping")
    missing = REQUIRED_TOP_KEYS - set(data.keys())
    if missing:
        fail(f"missing required top-level keys: {sorted(missing)}")
    if not isinstance(data["blocks"], list):
        fail("blocks must be a list")
    seen_ids: set[str] = set()
    for i, block in enumerate(data["blocks"]):
        if not isinstance(block, dict):
            fail(f"block #{i} must be a mapping")
        missing_b = REQUIRED_BLOCK_KEYS - set(block.keys())
        if missing_b:
            fail(f"block #{i} missing keys: {sorted(missing_b)}")
        if block["id"] in seen_ids:
            fail(f"duplicate id: {block['id']}")
        seen_ids.add(block["id"])
        if block["category"] not in VALID_CATEGORIES:
            fail(f"block {block['id']}: invalid category {block['category']!r}")
        for uc in block["use_cases"]:
            if uc not in VALID_USE_CASES:
                fail(f"block {block['id']}: invalid use_case {uc!r}")
    print("OK")


if __name__ == "__main__":
    if len(sys.argv) != 2:
        print("Usage: validate-catalog.py <path>", file=sys.stderr)
        sys.exit(2)
    main(sys.argv[1])
