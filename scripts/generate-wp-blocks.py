#!/usr/bin/env python3
"""Orchestrate stage-08 generators: theme → lzb-registration → block-spec.

Usage:
    python scripts/generate-wp-blocks.py --project <path>
    python scripts/generate-wp-blocks.py --project <path> --dry-run
"""
import argparse
import subprocess
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent

STEPS = [
    ("theme scaffold", "skills/wp-gutenberg-block-builder/scripts/generate-theme.py", []),
    ("lzb registration", "skills/wp-gutenberg-block-builder/scripts/generate-lzb-registration.py", []),
    ("block spec", "skills/wp-gutenberg-block-builder/scripts/generate-block-spec.py", []),
]


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--project", required=True)
    ap.add_argument("--dry-run", action="store_true")
    args = ap.parse_args()

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
