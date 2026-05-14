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


# Mapping from quiz_role to the preferred block ID (top match).
# These IDs must exist in the catalog.
QUIZ_ROLE_TOP: dict[str, str] = {
    "welcome":      "ru-quiz-06-welcome-screen",
    "question":     "ru-quiz-01-step-card",       # primary question variant
    "intermediate": "ru-quiz-03-intermediate",
    "progress":     "ru-quiz-02-progress-top",
    "loader":       "ru-quiz-10-loader-analyzing",
    "discount":     "ru-quiz-11-discount-bonus",
    "lead-form":    "ru-quiz-04-lead-form",
    "thankyou":     "ru-quiz-05-thankyou",
}

# For question role, offer additional question variants after the primary
QUIZ_QUESTION_EXTRAS = [
    "ru-quiz-07-image-choice",
    "ru-quiz-13-comparison-question",
    "ru-quiz-09-multi-select",
]


def _ids_in_catalog(catalog: dict) -> set[str]:
    return {b["id"] for b in catalog.get("blocks", [])}


def main() -> None:
    p = argparse.ArgumentParser()
    p.add_argument("--library", required=True)
    p.add_argument("--type", required=True)
    p.add_argument("--niche", required=True)
    p.add_argument("--top", type=int, default=3)
    p.add_argument("--quiz-role", default="", dest="quiz_role",
                   help="Optional quiz_role field from prototype block (welcome|question|...)")
    args = p.parse_args()

    cat_path = Path(args.library) / "catalog.yaml"
    if not cat_path.exists():
        print(f"ERROR: no catalog.yaml in {args.library}", file=sys.stderr)
        sys.exit(1)
    catalog = yaml.safe_load(cat_path.read_text())
    known_ids = _ids_in_catalog(catalog)

    # If this is a quiz block with a quiz_role, return role-specific candidates
    if args.type == "quiz" and args.quiz_role in QUIZ_ROLE_TOP:
        top_id = QUIZ_ROLE_TOP[args.quiz_role]
        result: list[str] = []
        if top_id in known_ids:
            result.append(top_id)

        # For question role, add extra question variants
        if args.quiz_role == "question":
            for extra in QUIZ_QUESTION_EXTRAS:
                if extra in known_ids and extra not in result:
                    result.append(extra)

        # Fill remaining slots with any other quiz blocks (generic fallback)
        for block in catalog.get("blocks", []):
            if len(result) >= args.top:
                break
            if block["category"] == "quiz" and block["id"] not in result:
                result.append(block["id"])

        print(json.dumps(result[: args.top]))
        return

    # Generic path (no quiz_role, or non-quiz block)
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
