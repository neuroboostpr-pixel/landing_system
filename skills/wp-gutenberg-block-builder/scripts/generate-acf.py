#!/usr/bin/env python3
"""Generate ACF Local JSON from 07_КОНТЕНТ/final-copy.md using ContentParser.

CLI: python generate-acf.py --project <path>
Output: <project>/08_КОД/acf-fields.json
"""
import argparse
import json
import shutil
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(REPO_ROOT / "scripts" / "lib"))

from content_parser import ContentParser, ContentParseError, Field, Block  # noqa: E402


def _field_key(slug: str, fname: str, parent: str = "") -> str:
    if parent:
        return f"field_lp_{slug}_{parent}_{fname}"
    return f"field_lp_{slug}_{fname}"


def _field_to_acf(f: Field, slug: str, parent: str = "") -> dict:
    out = {
        "key": _field_key(slug, f.name, parent),
        "label": f.label,
        "name": f.name,
        "type": f.type,
    }
    if f.default is not None and f.type != "repeater":
        out["default_value"] = f.default
    if f.type == "repeater":
        out["sub_fields"] = [_field_to_acf(sf, slug, parent=f.name) for sf in (f.subfields or [])]
        if f.defaults:
            out["min"] = 0
    return out


def _block_to_group(b: Block) -> dict:
    return {
        "key": f"group_lp_{b.slug}",
        "title": b.title,
        "fields": [_field_to_acf(f, b.slug) for f in b.fields],
        "location": [[{"param": "block", "operator": "==", "value": f"acf/lp-{b.slug}"}]],
        "menu_order": 0,
        "position": "normal",
        "style": "default",
        "label_placement": "top",
        "instruction_placement": "label",
    }


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--project", required=True)
    args = ap.parse_args()

    src = Path(args.project) / "07_КОНТЕНТ" / "final-copy.md"
    if not src.exists():
        print(f"ERROR: {src} not found", file=sys.stderr)
        sys.exit(1)

    try:
        blocks = ContentParser.parse(str(src))
        ContentParser.validate(blocks)
    except ContentParseError as e:
        print(f"ERROR: {e}", file=sys.stderr)
        sys.exit(1)

    groups = [_block_to_group(b) for b in blocks]

    dest = Path(args.project) / "08_КОД" / "acf-fields.json"
    dest.parent.mkdir(parents=True, exist_ok=True)

    if dest.exists():
        shutil.copy2(dest, dest.with_suffix(".json.bak"))

    with dest.open("w", encoding="utf-8", newline="\n") as f:
        json.dump(groups, f, ensure_ascii=False, indent=2, sort_keys=False)
        f.write("\n")

    print(f"wrote {dest} ({len(groups)} group(s))")


if __name__ == "__main__":
    main()
