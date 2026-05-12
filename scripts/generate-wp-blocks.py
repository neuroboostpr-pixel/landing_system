#!/usr/bin/env python3
"""Orchestrate stage-08 generators: ACF → block.json → registration → block-*.php.

Usage:
    python scripts/generate-wp-blocks.py --project <path>
    python scripts/generate-wp-blocks.py --project <path> --dry-run
"""
import argparse
import subprocess
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(REPO_ROOT / "scripts" / "lib"))

from content_parser import ContentParser, ContentParseError  # noqa: E402

STEPS = [
    ("ACF fields", "skills/wp-gutenberg-block-builder/scripts/generate-acf.py", []),
    ("block.json", "skills/wp-gutenberg-block-builder/scripts/generate-block-json.py", []),
    ("block registration", "skills/wp-gutenberg-block-builder/scripts/generate-block-registration.py", []),
    ("block template parts", "skills/wp-gutenberg-block-builder/scripts/generate-theme.py", ["--blocks-only"]),
]


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--project", required=True)
    ap.add_argument("--dry-run", action="store_true")
    args = ap.parse_args()

    # Validate content first — fail fast before running any generator
    md = Path(args.project) / "07_КОНТЕНТ" / "final-copy.md"
    try:
        blocks = ContentParser.parse(str(md))
        ContentParser.validate(blocks)
    except ContentParseError as e:
        print(f"ERROR: {e}", file=sys.stderr)
        sys.exit(1)

    print(f"✓ ContentParser: {len(blocks)} block(s) detected")

    if args.dry_run:
        print("(dry-run) would run the following generators:")
        for name, path, extra in STEPS:
            print(f"  - {name}: python {path} --project {args.project} {' '.join(extra)}")
        return

    for name, path, extra in STEPS:
        cmd = [sys.executable, str(REPO_ROOT / path), "--project", args.project, *extra]
        print(f"▶ {name}")
        result = subprocess.run(cmd, capture_output=False)
        if result.returncode != 0:
            print(f"ERROR: {name} failed (exit {result.returncode})", file=sys.stderr)
            sys.exit(result.returncode)

    print(f"✓ stage-08 artifacts generated for {args.project}")


if __name__ == "__main__":
    main()
