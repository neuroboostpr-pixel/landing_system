#!/usr/bin/env python3
"""Read .landing-state.yaml and print the next actionable stage id.

Output: stage id on stdout. Prints "DONE" if everything approved.
"""
import argparse
import sys
from pathlib import Path

import yaml


# Canonical stage order — single source of truth (E1): config/stages.yaml
_ROOT = Path(__file__).resolve().parent.parent
STAGE_ORDER = [
    s["id"]
    for s in yaml.safe_load(
        (_ROOT / "config" / "stages.yaml").read_text(encoding="utf-8")
    )["stages"]
]


def next_stage(state_yaml: dict) -> str:
    """Return next actionable stage.

    Priority order (high to low):
    1. First `in_progress` stage in STAGE_ORDER
    2. First `failed` stage in STAGE_ORDER (treat as needs attention)
    3. First `locked` stage in STAGE_ORDER
    Skip `approved` and `n/a` stages.
    """
    stages = state_yaml.get("stages", {})

    in_progress_stages = []
    failed_stages = []
    locked_stages = []

    for stage_id in STAGE_ORDER:
        entry = stages.get(stage_id, {})
        status = entry.get("status") if isinstance(entry, dict) else None
        if status in ("approved", "n/a", None):
            continue
        if status == "in_progress":
            in_progress_stages.append(stage_id)
        elif status == "failed":
            failed_stages.append(stage_id)
        else:  # locked or other
            locked_stages.append(stage_id)

    if in_progress_stages:
        return in_progress_stages[0]
    if failed_stages:
        return failed_stages[0]
    if locked_stages:
        return locked_stages[0]
    return "DONE"


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--project", required=True, help="Project directory containing .landing-state.yaml")
    args = ap.parse_args()

    state_path = Path(args.project) / ".landing-state.yaml"
    if not state_path.exists():
        print(f"ERROR: {state_path} not found", file=sys.stderr)
        sys.exit(2)

    state = yaml.safe_load(state_path.read_text(encoding="utf-8"))
    print(next_stage(state))


if __name__ == "__main__":
    main()
