#!/usr/bin/env python3
"""Validate selections.yaml schema (canonical, post-approve).

Enforces:
- Required fields per slot (slot_id, block_id, ratio, strategy)
- strategy enum (generate | placeholder | bring-your-own)
- strategy=bring-your-own requires chosen_photo_id
- strategy=generate on identity-safe slots (testimonial/expert/team-member/avatar)
  requires ai_approved_by_user=True
"""
import sys
from pathlib import Path

import yaml


VALID_STRATEGIES = {"generate", "placeholder", "bring-your-own"}
IDENTITY_SAFE_PATTERNS = ["testimonial", "expert", "team-member", "team_member", "avatar"]


class ValidationError(ValueError):
    """Raised when selections.yaml violates schema or identity-safe rules."""


def _is_identity_safe_slot(slot_id: str) -> bool:
    sid = slot_id.lower()
    return any(p in sid for p in IDENTITY_SAFE_PATTERNS)


def validate(data: dict) -> None:
    """Raise ValidationError if data is not a valid canonical selections.yaml."""
    if not isinstance(data, dict):
        raise ValidationError("Root must be a dict")
    if "slots" not in data or not isinstance(data["slots"], list):
        raise ValidationError("Missing 'slots' list")

    for i, s in enumerate(data["slots"]):
        prefix = f"slot[{i}] ({s.get('slot_id', '?')})"

        for req in ["slot_id", "block_id", "ratio", "strategy"]:
            if req not in s:
                raise ValidationError(f"{prefix}: missing field '{req}'")

        if s["strategy"] not in VALID_STRATEGIES:
            raise ValidationError(
                f"{prefix}: strategy='{s['strategy']}' not in {sorted(VALID_STRATEGIES)}"
            )

        if s["strategy"] == "bring-your-own" and not s.get("chosen_photo_id"):
            raise ValidationError(
                f"{prefix}: strategy=bring-your-own requires chosen_photo_id"
            )

        if s["strategy"] == "generate":
            if _is_identity_safe_slot(s["slot_id"]) and not s.get("ai_approved_by_user"):
                raise ValidationError(
                    f"{prefix}: identity-safe slot requires ai_approved_by_user=True "
                    f"for strategy=generate (see IDENTITY_SAFE.md)"
                )


def main():
    if len(sys.argv) < 2:
        print("Usage: selections-validator.py <selections.yaml>", file=sys.stderr)
        sys.exit(2)
    path = Path(sys.argv[1])
    if not path.exists():
        print(f"ERROR: file not found: {path}", file=sys.stderr)
        sys.exit(2)
    data = yaml.safe_load(path.read_text())
    try:
        validate(data)
    except ValidationError as e:
        print(f"INVALID: {e}", file=sys.stderr)
        sys.exit(1)
    print("OK: selections.yaml is valid")


if __name__ == "__main__":
    main()
