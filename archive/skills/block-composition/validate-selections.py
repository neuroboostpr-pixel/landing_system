#!/usr/bin/env python3
"""Validate <project>/07a_WIREFRAME/selections.yaml."""
import re
import sys
import yaml
from pathlib import Path

ISO_RE = re.compile(r"^\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}")


def fail(m: str) -> None:
    print(f"ERROR: {m}", file=sys.stderr)
    sys.exit(1)


def main(path: str) -> None:
    data = yaml.safe_load(Path(path).read_text(encoding="utf-8"))
    if not isinstance(data, dict):
        fail("top-level must be a mapping")
    for k in ("project_slug", "selections", "confirmed_at"):
        if k not in data:
            fail(f"missing {k}")
    if not ISO_RE.match(str(data["confirmed_at"])):
        fail(f"confirmed_at must be ISO-8601: {data['confirmed_at']!r}")
    if not isinstance(data["selections"], list) or not data["selections"]:
        fail("selections must be a non-empty list")
    seen = set()
    for i, sel in enumerate(data["selections"]):
        if "block_position" not in sel or "chosen_variant" not in sel:
            fail(f"selection #{i}: needs block_position and chosen_variant")
        if sel["block_position"] in seen:
            fail(f"duplicate block_position: {sel['block_position']}")
        seen.add(sel["block_position"])
    print("OK")


if __name__ == "__main__":
    if len(sys.argv) != 2:
        print("Usage: validate-selections.py <path>", file=sys.stderr)
        sys.exit(2)
    main(sys.argv[1])
