#!/usr/bin/env python3
# skills/wp-cli-deployer/scripts/import-redirects.py
# Parse redirects.csv and generate wp-cli commands for Redirection plugin.
# Usage: python import-redirects.py <redirects.csv> [--wp-cmd "wp --path=..."]
#        Prints shell commands; caller pipes to bash or executes via ssh_run.
import argparse
import csv
import sys
from pathlib import Path
from urllib.parse import urlparse

ALLOWED_CODES = {"301", "302", "307", "308"}


def parse_csv(path: str) -> list:
    """Return list of dicts with source/target/code from CSV file."""
    rows = []
    with open(path, encoding="utf-8", newline="") as fh:
        reader = csv.DictReader(fh)
        for row in reader:
            source = (row.get("source") or "").strip()
            target = (row.get("target") or "").strip()
            code = (row.get("code") or "301").strip()
            if source and target:
                rows.append({"source": source, "target": target, "code": code})
    return rows


def validate_rows(rows: list) -> list:
    """Return list of error strings; empty list if all rows are valid."""
    errors = []
    for i, row in enumerate(rows, start=1):
        source = row["source"]
        code = row["code"]
        parsed = urlparse(source)
        if parsed.scheme in ("http", "https"):
            errors.append(f"Row {i}: source must be a path, not an external URL: {source!r}")
        if code not in ALLOWED_CODES:
            errors.append(
                f"Row {i}: invalid redirect code {code!r}. Allowed: {', '.join(sorted(ALLOWED_CODES))}"
            )
    return errors


def generate_wp_commands(rows: list, wp_cmd: str = "wp") -> list:
    """Return list of wp-cli shell command strings."""
    cmds = []
    for row in rows:
        source = row["source"].replace("'", "\\'")
        target = row["target"].replace("'", "\\'")
        code = row["code"]
        cmds.append(
            f"{wp_cmd} redirection add --status={code} "
            f"--url='{source}' --action-url='{target}'"
        )
    return cmds


def main() -> int:
    parser = argparse.ArgumentParser(description="Import redirects.csv into Redirection plugin via wp-cli")
    parser.add_argument("csv_path", help="Path to redirects.csv")
    parser.add_argument(
        "--wp-cmd",
        default="wp",
        help="wp-cli command prefix (default: wp)",
    )
    parser.add_argument(
        "--validate-only",
        action="store_true",
        help="Only validate the CSV; do not print commands",
    )
    args = parser.parse_args()

    if not Path(args.csv_path).is_file():
        print(f"ERROR: file not found: {args.csv_path}", file=sys.stderr)
        return 1

    rows = parse_csv(args.csv_path)
    if not rows:
        print("WARNING: no redirect rows found in CSV", file=sys.stderr)
        return 0

    errors = validate_rows(rows)
    if errors:
        for e in errors:
            print(f"ERROR: {e}", file=sys.stderr)
        return 1

    if args.validate_only:
        print(f"OK: {len(rows)} redirects validated")
        return 0

    for cmd in generate_wp_commands(rows, wp_cmd=args.wp_cmd):
        print(cmd)
    return 0


if __name__ == "__main__":
    sys.exit(main())
