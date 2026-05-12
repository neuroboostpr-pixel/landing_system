#!/usr/bin/env python3
"""Export palettes from a project's 05_ДИЗАЙН-СИСТЕМА/palettes.yaml
into the global library, deduping by id."""
import argparse
import os
import sys
import yaml

REPO_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(REPO_ROOT, "scripts"))
# Reuse the validator
import importlib.util
spec = importlib.util.spec_from_file_location(
    "validate_palettes",
    os.path.join(REPO_ROOT, "scripts", "validate-palettes.py"),
)
validate_palettes = importlib.util.module_from_spec(spec)
spec.loader.exec_module(validate_palettes)


def load_yaml(path):
    try:
        with open(path, "r", encoding="utf-8") as f:
            return yaml.safe_load(f) or {}
    except FileNotFoundError:
        return {"palettes": []}
    except yaml.YAMLError as e:
        print(f"ERROR: invalid YAML in {path}: {e}", file=sys.stderr)
        sys.exit(1)


class _QuotedStr(str):
    pass


def _quoted_str_representer(dumper, data):
    return dumper.represent_scalar("tag:yaml.org,2002:str", data, style='"')


_UNQUOTED_KEYS = {"id"}


def _quote_strings(obj, parent_key=None):
    """Recursively wrap str values in _QuotedStr so they render with double quotes.
    Keys in _UNQUOTED_KEYS are left unquoted (plain style)."""
    if isinstance(obj, dict):
        return {k: _quote_strings(v, parent_key=k) for k, v in obj.items()}
    if isinstance(obj, list):
        return [_quote_strings(item, parent_key=parent_key) for item in obj]
    if isinstance(obj, str):
        if parent_key in _UNQUOTED_KEYS:
            return obj  # leave plain
        return _QuotedStr(obj)
    return obj


def save_yaml(path, data):
    os.makedirs(os.path.dirname(os.path.abspath(path)), exist_ok=True)
    dumper = yaml.Dumper
    dumper.add_representer(_QuotedStr, _quoted_str_representer)
    quoted_data = _quote_strings(data)
    is_new = not os.path.exists(path)
    with open(path, "w", encoding="utf-8") as f:
        if is_new:
            f.write("# Global palette library for landing-system.\n")
            f.write("# Populated by /landing-design after design-system approval.\n")
            f.write("# Manual edits OK. Dedup by id.\n")
        yaml.dump(quoted_data, f, Dumper=dumper, sort_keys=False, allow_unicode=True)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--project", required=True, help="path to project root")
    ap.add_argument("--library", required=True, help="path to landing_system/presets/palettes.yaml")
    args = ap.parse_args()

    src = os.path.join(args.project, "05_ДИЗАЙН-СИСТЕМА", "palettes.yaml")
    project_data = load_yaml(src)
    src_palettes = project_data.get("palettes", []) or []

    # Validate the project file via the existing validator (will sys.exit on failure)
    try:
        validate_palettes.main(src)
    except SystemExit as e:
        if e.code:
            sys.exit(e.code)

    library_data = load_yaml(args.library)
    library = library_data.get("palettes", []) or []
    existing_ids = {p["id"] for p in library}

    added = []
    skipped = []
    for p in src_palettes:
        if p["id"] in existing_ids:
            skipped.append(p["id"])
        else:
            library.append(p)
            existing_ids.add(p["id"])
            added.append(p["id"])

    library_data["palettes"] = library
    save_yaml(args.library, library_data)

    for pid in added:
        print(f"added: {pid}")
    for pid in skipped:
        print(f"skipped (id already in library): {pid}")
    print(f"library now has {len(library)} palette(s)")


if __name__ == "__main__":
    main()
