#!/usr/bin/env python3
"""Match block-library candidates for a given prototype block.

Niche-aware scoring:
  - Тип совпадает: +10
  - use_cases содержит точную нишу: +8 (или substring match: +4)
  - style_mood входит в preferred moods для ниши: +5
  - ru_market=true: +2

Usage: match-candidates.py --library <path> --type <hero|...> --niche <premium-auto|services|...> [--top 5]

Output: JSON array of block ids to stdout (best first).
"""
import argparse
import json
import sys
from pathlib import Path

import yaml


# Mapping from quiz_role to the preferred block ID (top match).
QUIZ_ROLE_TOP: dict[str, str] = {
    "welcome":      "ru-quiz-06-welcome-screen",
    "question":     "ru-quiz-01-step-card",
    "intermediate": "ru-quiz-03-intermediate",
    "progress":     "ru-quiz-02-progress-top",
    "loader":       "ru-quiz-10-loader-analyzing",
    "discount":     "ru-quiz-11-discount-bonus",
    "lead-form":    "ru-quiz-04-lead-form",
    "thankyou":     "ru-quiz-05-thankyou",
}

QUIZ_QUESTION_EXTRAS = [
    "ru-quiz-07-image-choice",
    "ru-quiz-13-comparison-question",
    "ru-quiz-09-multi-select",
]


# Niche -> предпочтительные style_mood (от наиболее уместного к менее)
NICHE_MOODS: dict[str, list[str]] = {
    "premium-auto": ["cinematic", "luxury", "editorial"],
    "luxury":       ["cinematic", "luxury", "editorial"],
    "real-estate":  ["cinematic", "editorial", "minimal"],
    "b2b-saas":     ["technical", "minimal", "corporate"],
    "tech":         ["technical", "minimal", "corporate"],
    "medical":      ["minimal", "corporate", "editorial"],
    "services":     ["editorial", "minimal", "corporate"],
    "education":    ["editorial", "playful"],
    "ecommerce":    ["editorial", "corporate"],
    # b2c — широкая категория, для премиум-продуктов уместен cinematic/editorial
    "b2c":          ["cinematic", "editorial", "luxury"],
    "generic":      [],
}


def _ids_in_catalog(catalog: dict) -> set[str]:
    return {b["id"] for b in catalog.get("blocks", [])}


def score_block_for_niche(block_meta: dict, niche: str, btype: str) -> int:
    """Возвращает score (выше = лучше match) с учётом ниши проекта."""
    score = 0

    # 1. Тип совпадает — большой плюс
    if block_meta.get("category") == btype:
        score += 10

    # 2. Use cases overlap
    use_cases = block_meta.get("use_cases") or block_meta.get("niches_suitable") or []
    if isinstance(use_cases, list):
        if niche in use_cases:
            score += 8
        else:
            # substring match (например niche="b2c-auto" matches uc="b2c")
            if any(uc and uc in niche for uc in use_cases):
                score += 4
            elif any(uc and niche in uc for uc in use_cases):
                score += 4

    # 3. Style mood предпочтителен для ниши
    preferred_moods = NICHE_MOODS.get(niche, [])
    block_mood = block_meta.get("style_mood")
    if block_mood and block_mood in preferred_moods:
        # бонус выше у более предпочтительного mood
        try:
            rank = preferred_moods.index(block_mood)
            score += max(5 - rank, 1)
        except ValueError:
            score += 1

    # 4. ru_market — небольшой плюс (русскоязычный рынок)
    if block_meta.get("ru_market"):
        score += 2

    return score


def main() -> None:
    p = argparse.ArgumentParser()
    p.add_argument("--library", required=True)
    p.add_argument("--type", required=True)
    p.add_argument("--niche", required=True)
    p.add_argument("--top", type=int, default=3)
    p.add_argument("--quiz-role", default="", dest="quiz_role")
    args = p.parse_args()

    cat_path = Path(args.library) / "catalog.yaml"
    if not cat_path.exists():
        print(f"ERROR: no catalog.yaml in {args.library}", file=sys.stderr)
        sys.exit(1)
    catalog = yaml.safe_load(cat_path.read_text(encoding="utf-8"))
    known_ids = _ids_in_catalog(catalog)

    niche = args.niche or "generic"

    # quiz_role-specific path (unchanged)
    if args.type == "quiz" and args.quiz_role in QUIZ_ROLE_TOP:
        top_id = QUIZ_ROLE_TOP[args.quiz_role]
        result: list[str] = []
        if top_id in known_ids:
            result.append(top_id)
        if args.quiz_role == "question":
            for extra in QUIZ_QUESTION_EXTRAS:
                if extra in known_ids and extra not in result:
                    result.append(extra)
        for block in catalog.get("blocks", []):
            if len(result) >= args.top:
                break
            if block["category"] == "quiz" and block["id"] not in result:
                result.append(block["id"])
        print(json.dumps(result[: args.top]))
        return

    # Niche-aware generic path
    matching = [b for b in catalog.get("blocks", []) if b.get("category") == args.type]
    scored = [
        (score_block_for_niche(b, niche, args.type), b["id"])
        for b in matching
    ]
    # сортируем: высокий score первым; при равенстве — стабильный порядок по id
    scored.sort(key=lambda x: (-x[0], x[1]))
    top_ids = [bid for s, bid in scored[: args.top] if s > 0]
    print(json.dumps(top_ids))


if __name__ == "__main__":
    main()
