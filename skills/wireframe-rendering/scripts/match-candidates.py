#!/usr/bin/env python3
"""Match block-library candidates for a given prototype block.

Selects blocks from catalog where category matches and use_cases overlap
with project niche. Returns top-N sorted by use_cases overlap descending.

Usage: match-candidates.py --library <path> --type <hero|...> --niche <services|b2c|local> [--top 3]

Output: JSON array of block ids to stdout.
"""
import argparse
import json
import sys
from pathlib import Path

import yaml


def main() -> None:
    p = argparse.ArgumentParser()
    p.add_argument("--library", required=True)
    p.add_argument("--type", required=True)
    p.add_argument("--niche", required=True)
    p.add_argument("--top", type=int, default=3)
    args = p.parse_args()

    cat_path = Path(args.library) / "catalog.yaml"
    if not cat_path.exists():
        print(f"ERROR: no catalog.yaml in {args.library}", file=sys.stderr)
        sys.exit(1)
    catalog = yaml.safe_load(cat_path.read_text())

    scored: list[tuple[int, str]] = []
    for block in catalog.get("blocks", []):
        if block["category"] != args.type:
            continue
        if args.niche in block["use_cases"]:
            score = 10 if len(block["use_cases"]) == 1 else 5
            scored.append((score, block["id"]))

    scored.sort(key=lambda x: -x[0])
    top_ids = [b for _, b in scored[: args.top]]
    print(json.dumps(top_ids))


if __name__ == "__main__":
    main()
