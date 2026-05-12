#!/usr/bin/env python3
"""Generate <project>/08_КОД/gutenberg-blocks/<slug>/block.json per block.

CLI: python generate-block-json.py --project <path>
"""
import argparse
import json
import sys
from pathlib import Path

import yaml

REPO_ROOT = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(REPO_ROOT / "scripts" / "lib"))

from content_parser import ContentParser, ContentParseError  # noqa: E402


def _load_icons() -> dict:
    p = REPO_ROOT / "scripts" / "lib" / "block-icons.yaml"
    if not p.exists():
        return {}
    return (yaml.safe_load(p.read_text(encoding="utf-8")) or {}).get("icons") or {}


def _block_json(slug: str, title: str, icons: dict) -> dict:
    return {
        "apiVersion": 3,
        "name": f"acf/lp-{slug}",
        "title": title,
        "description": f"{title} block (auto-generated from 07_КОНТЕНТ/final-copy.md)",
        "category": "lp-blocks",
        "icon": icons.get(slug, "block-default"),
        "keywords": [slug, "lp"],
        "acf": {
            "mode": "preview",
            "renderTemplate": f"template-parts/block-{slug}.php",
        },
        "supports": {
            "align": False,
            "anchor": True,
            "html": False,
        },
    }


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--project", required=True)
    args = ap.parse_args()

    src = Path(args.project) / "07_КОНТЕНТ" / "final-copy.md"
    try:
        blocks = ContentParser.parse(str(src))
        ContentParser.validate(blocks)
    except ContentParseError as e:
        print(f"ERROR: {e}", file=sys.stderr)
        sys.exit(1)

    icons = _load_icons()
    base = Path(args.project) / "08_КОД" / "gutenberg-blocks"

    for b in blocks:
        block_dir = base / b.slug
        block_dir.mkdir(parents=True, exist_ok=True)
        dest = block_dir / "block.json"
        with dest.open("w", encoding="utf-8", newline="\n") as f:
            json.dump(_block_json(b.slug, b.title, icons), f, ensure_ascii=False, indent=2)
            f.write("\n")

    print(f"wrote {len(blocks)} block.json file(s) under {base}")


if __name__ == "__main__":
    main()
