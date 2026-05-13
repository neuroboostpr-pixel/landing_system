#!/usr/bin/env python3
"""Read .landing-state.yaml and print the next actionable stage id.

Output: stage id on stdout. Prints "DONE" if everything approved.
"""
import argparse
import sys
from pathlib import Path

import yaml


# Canonical stage order (matches template/.landing-state.yaml)
STAGE_ORDER = [
    "00_brief", "01_context", "01a_niche_analysis", "02_assets",
    "03_references", "04_brand", "05_design", "06_stack", "07_content",
    "07a_prototype", "07b_wireframe", "07c_composed",
    "07d_photos", "07e_visuals", "07f_composed_final",
    "08_build", "09_deploy", "10_qa", "11_analytics", "12_seo",
]


def next_stage(state_yaml: dict) -> str:
    stages = state_yaml.get("stages", {})
    for stage_id in STAGE_ORDER:
        entry = stages.get(stage_id, {})
        status = entry.get("status") if isinstance(entry, dict) else None
        if status in ("approved", "n/a", None):
            continue
        return stage_id
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
