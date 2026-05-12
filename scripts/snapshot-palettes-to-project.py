#!/usr/bin/env python3
"""Copy a subset of palettes from the global library into a project."""
import argparse
import importlib.util
import os
import sys
import yaml

REPO_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
spec = importlib.util.spec_from_file_location(
    "validate_palettes",
    os.path.join(REPO_ROOT, "scripts", "validate-palettes.py"),
)
validate_palettes = importlib.util.module_from_spec(spec)
spec.loader.exec_module(validate_palettes)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--project", required=True)
    ap.add_argument("--library", required=True)
    ap.add_argument("--id", action="append", default=[], help="palette id to include (repeat)")
    ap.add_argument("--all", action="store_true", help="copy every palette")
    args = ap.parse_args()

    try:
        validate_palettes.main(args.library)
    except SystemExit as e:
        if e.code:
            sys.exit(e.code)

    with open(args.library, "r", encoding="utf-8") as f:
        lib = yaml.safe_load(f) or {}
    palettes = lib.get("palettes", []) or []
    by_id = {p["id"]: p for p in palettes}

    if args.all:
        selected = list(palettes)
    else:
        if not args.id:
            print("ERROR: pass --all or one or more --id", file=sys.stderr)
            sys.exit(2)
        missing = [i for i in args.id if i not in by_id]
        if missing:
            print(f"ERROR: unknown palette id(s): {missing}", file=sys.stderr)
            sys.exit(1)
        selected = [by_id[i] for i in args.id]

    dest_dir = os.path.join(args.project, "04_БРЕНД")
    os.makedirs(dest_dir, exist_ok=True)
    dest = os.path.join(dest_dir, "palettes.yaml")
    with open(dest, "w", encoding="utf-8") as f:
        f.write("# Project palette snapshot from landing_system/presets/palettes.yaml\n")
        yaml.safe_dump({"palettes": selected}, f, sort_keys=False, allow_unicode=True)

    print(f"snapshotted {len(selected)} palette(s) to {dest}")


if __name__ == "__main__":
    main()
