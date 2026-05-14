#!/usr/bin/env python3
"""Orchestrate stage-08 generators in dependency order.

Pipeline:
  1. generate-theme.py            — wp-theme scaffold (style.css, functions.php, blocks/ dir, main.css)
  2. generate-lzb-templates.py    — theme/blocks/lazyblock-<slug>/block.php per block
  3. generate-lzb-registration.py — lzb/init add_block() block in functions.php
  4. generate-css-patches.py      — display:contents rules in assets/css/main.css
  5. generate-page-content.py     — Gutenberg block markup → 08_КОД/page-content.html

Step 1 takes the project path as a positional argument; steps 2–5 use --project.
Steps 2–5 each read 08_КОД/block-spec.yaml, which must exist before running this.

Usage:
    python scripts/generate-wp-blocks.py --project <path>
    python scripts/generate-wp-blocks.py --project <path> --dry-run
"""
import argparse
import subprocess
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent

# Each entry: (label, script path, arg-style)
# arg-style: "positional" → `python <script> <project>`
#            "flag"       → `python <script> --project <project>`
STEPS = [
    ("theme scaffold",   "skills/wp-gutenberg-block-builder/scripts/generate-theme.py",            "positional"),
    ("lzb templates",    "skills/wp-gutenberg-block-builder/scripts/generate-lzb-templates.py",    "flag"),
    ("lzb registration", "skills/wp-gutenberg-block-builder/scripts/generate-lzb-registration.py", "flag"),
    ("css patches",      "skills/wp-gutenberg-block-builder/scripts/generate-css-patches.py",      "flag"),
    ("page content",     "skills/wp-gutenberg-block-builder/scripts/generate-page-content.py",     "flag"),
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
    args = ap.parse_args()

    if args.dry_run:
        print("(dry-run) would run the following generators:")
        for name, script, style in STEPS:
            cmd = _cmd_for(script, args.project, style)
            print(f"  - {name}: {' '.join(cmd)}")
        return 0

    for name, script, style in STEPS:
        cmd = _cmd_for(script, args.project, style)
        print(f"▶ {name}")
        result = subprocess.run(cmd)
        if result.returncode != 0:
            print(f"ERROR: {name} failed (exit {result.returncode})", file=sys.stderr)
            return result.returncode

    print(f"✓ stage-08 artifacts generated for {args.project}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
