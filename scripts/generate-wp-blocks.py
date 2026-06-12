#!/usr/bin/env python3
"""Orchestrate stage-08 generators in dependency order.

Pipeline (полный 11-шаговый flow, описан в .claude/commands/landing-build.md):

  CORE LAZY BLOCKS PIPELINE (Steps 1-5):
  1. generate-theme.py            — wp-theme scaffold (style.css, functions.php, blocks/ dir, main.css)
  2. generate-lzb-templates.py    — theme/blocks/lazyblock-<slug>/block.php per block
  3. generate-lzb-registration.py — lzb/init add_block() block in functions.php
  4. generate-css-patches.py      — display:contents rules in assets/css/main.css
  5. generate-page-content.py     — Gutenberg block markup → 08_КОД/page-content.html

  ASSETS, JS, AND PREVIEW (Steps 6-8):
  6. bundle-assets.py             — копирует обработанные фото из 07c_PHOTOS/, скачивает иконки
  7. generate-js-init.py          — main.js / sliders.js / animations.js / counters.js (zero-config JS)
  8. generate-popup.py            — модальное окно (JS + CSS + PHP overlay)

  INTEGRATIONS, ANALYTICS, PREVIEW (Steps 9-11):
  9. generate-analytics.py        — Yandex Metrika + GTM в functions.php (читает 00_БРИФ/brief.md)
  10. generate-integrations.py    — Fluent Forms webhook (AmoCRM / Bitrix24 / Telegram)
  11. render-build-preview.py     — статичный 08_КОД/build-preview.html для approve (HARD GATE)

Steps 1-5 читают 08_КОД/block-spec.yaml, который должен существовать до запуска.
Steps 6-11 читают артефакты предыдущих этапов проекта (фото, бриф, brand-kit).

Usage:
    python scripts/generate-wp-blocks.py --project <path>
    python scripts/generate-wp-blocks.py --project <path> --dry-run
    python scripts/generate-wp-blocks.py --project <path> --skip <step1,step2>
    python scripts/generate-wp-blocks.py --project <path> --only <step>
"""
import argparse
import subprocess
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent

# Each entry: (step_id, label, script path, arg-style, required)
# arg-style: "positional" → `python <script> <project>`
#            "flag"       → `python <script> --project <project>`
# required:  если False — exit code != 0 не падает весь pipeline, только warning
STEPS = [
    # CORE LAZY BLOCKS (must pass)
    ("theme",        "theme scaffold",   "skills/wp-gutenberg-block-builder/scripts/generate-theme.py",            "positional", True),
    ("templates",    "lzb templates",    "skills/wp-gutenberg-block-builder/scripts/generate-lzb-templates.py",    "flag",       True),
    ("registration", "lzb registration", "skills/wp-gutenberg-block-builder/scripts/generate-lzb-registration.py", "flag",       True),
    ("patches",      "css patches",      "skills/wp-gutenberg-block-builder/scripts/generate-css-patches.py",      "flag",       True),
    ("page",         "page content",     "skills/wp-gutenberg-block-builder/scripts/generate-page-content.py",     "flag",       True),

    # ASSETS + JS (must pass)
    ("assets",       "bundle assets",    "skills/wp-theme-assembler/scripts/bundle-assets.py",                     "positional", True),
    ("js",           "JS init",          "skills/wp-gutenberg-block-builder/scripts/generate-js-init.py",          "positional", True),
    ("popup",        "popup system",     "skills/wp-gutenberg-block-builder/scripts/generate-popup.py",            "positional", False),

    # INTEGRATIONS + ANALYTICS (могут падать если нет integrations/brief — это OK, warning)
    ("analytics",    "analytics inject", "skills/wp-gutenberg-block-builder/scripts/generate-analytics.py",        "positional", False),
    ("integrations", "CRM integrations", "skills/wp-gutenberg-block-builder/scripts/generate-integrations.py",     "positional", False),

    # PREVIEW (HARD GATE artefact)
    ("preview",      "build preview",    "skills/wp-theme-assembler/scripts/render-build-preview.py",              "positional", True),
]


def _cmd_for(script: str, project: str, style: str) -> list[str]:
    full = str(REPO_ROOT / script)
    if style == "positional":
        return [sys.executable, full, project]
    return [sys.executable, full, "--project", project]


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--project", required=True)
    ap.add_argument("--dry-run", action="store_true")
    ap.add_argument("--skip", default="",
                    help="comma-separated step ids to skip (e.g. analytics,integrations)")
    ap.add_argument("--only", default="",
                    help="comma-separated step ids to run exclusively (e.g. preview)")
    args = ap.parse_args()

    skip_ids = {s.strip() for s in args.skip.split(",") if s.strip()}
    only_ids = {s.strip() for s in args.only.split(",") if s.strip()}

    def selected(step_id):
        if only_ids:
            return step_id in only_ids
        return step_id not in skip_ids

    if args.dry_run:
        print("(dry-run) would run the following generators:")
        for step_id, name, script, style, required in STEPS:
            mark = "✓" if selected(step_id) else "✗ (skipped)"
            cmd = _cmd_for(script, args.project, style)
            tag = "" if required else " [optional]"
            print(f"  {mark} [{step_id}] {name}{tag}: {' '.join(cmd)}")
        return 0

    failed_optional = []
    for step_id, name, script, style, required in STEPS:
        if not selected(step_id):
            print(f"⊘ {name} (skipped via --skip/--only)")
            continue
        cmd = _cmd_for(script, args.project, style)
        tag = "" if required else " [optional]"
        print(f"▶ {name}{tag}")
        result = subprocess.run(cmd)
        if result.returncode != 0:
            if required:
                print(f"ERROR: {name} failed (exit {result.returncode})", file=sys.stderr)
                return result.returncode
            print(f"⚠ {name} failed (exit {result.returncode}) — optional step, продолжаем", file=sys.stderr)
            failed_optional.append(step_id)

    if failed_optional:
        print(f"\n⚠ stage-08 завершён с {len(failed_optional)} optional warnings: {', '.join(failed_optional)}")
    print(f"✓ stage-08 artifacts generated for {args.project}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
