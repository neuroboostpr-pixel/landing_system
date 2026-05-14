#!/usr/bin/env python3
"""Validate <project>/07_ПРОТОТИП/prototype.yaml schema."""
import sys
import yaml
from pathlib import Path

VALID_NICHES = {"services", "b2c", "local"}
VALID_BLOCK_TYPES = {
    "hero", "features", "social-proof", "process",
    "pricing", "trust", "cta", "faq", "quiz",
}
VALID_QUIZ_ROLES = {
    "welcome", "question", "intermediate", "progress",
    "loader", "discount", "lead-form", "thankyou",
}


def fail(m: str) -> None:
    print(f"ERROR: {m}", file=sys.stderr)
    sys.exit(1)


def main(path: str) -> None:
    data = yaml.safe_load(Path(path).read_text())
    if not isinstance(data, dict):
        fail("top-level must be a mapping")
    if "project" not in data:
        fail("missing 'project' section")
    proj = data["project"]
    for k in ("slug", "niche", "source_file"):
        if k not in proj:
            fail(f"project.{k} required")
    if proj["niche"] not in VALID_NICHES:
        fail(f"invalid niche: {proj['niche']!r}")
    if "blocks" not in data:
        fail("missing 'blocks' section")
    if not isinstance(data["blocks"], list):
        fail("blocks must be a list")
    seen_positions = set()
    for i, block in enumerate(data["blocks"]):
        if not isinstance(block, dict):
            fail(f"block #{i} must be a mapping")
        if "position" not in block:
            fail(f"block #{i} missing position")
        if block["position"] in seen_positions:
            fail(f"duplicate position {block['position']}")
        seen_positions.add(block["position"])
        if "type" not in block:
            fail(f"block #{i} missing type")
        if block["type"] not in VALID_BLOCK_TYPES:
            fail(f"block #{i} invalid type: {block['type']!r}")
        # quiz_role is optional; if present it must be a valid value and block must be type quiz
        if "quiz_role" in block:
            if block["type"] != "quiz":
                fail(f"block #{i} has quiz_role but type is {block['type']!r} (quiz_role only valid on quiz blocks)")
            if block["quiz_role"] not in VALID_QUIZ_ROLES:
                fail(f"block #{i} invalid quiz_role: {block['quiz_role']!r}. Valid: {sorted(VALID_QUIZ_ROLES)}")
    print("OK")


if __name__ == "__main__":
    if len(sys.argv) != 2:
        print("Usage: validate-prototype.py <path>", file=sys.stderr)
        sys.exit(2)
    main(sys.argv[1])
