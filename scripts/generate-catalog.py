#!/usr/bin/env python3
"""Generate or update catalog.yaml from block-library directory structure.

This script scans block-library/<category>/<block-id>/ directories and generates
entries for catalog.yaml, ensuring all blocks are discoverable by match-candidates.

Usage:
  python scripts/generate-catalog.py --library block-library --output block-library/catalog.yaml
"""
import argparse
import sys
from pathlib import Path
from typing import Any

import yaml


def extract_block_info(block_dir: Path, category: str) -> dict[str, Any] | None:
    """Extract block metadata from meta.yaml or infer from directory structure."""
    meta_path = block_dir / "meta.yaml"

    if not meta_path.exists():
        # No metadata, infer basic info
        block_id = block_dir.name
        return {
            "id": block_id,
            "path": f"{category}/{block_id}/",
            "category": category,
            "type": category,  # Assume type matches category
            "layout_pattern": "default",
            "signature": f"{category}|default|[content]|bg:false",
            "display_name_ru": f"{category}: {block_id}",
            "created": "2026-06-02",
            "has_bg_image": False,
            "slots": [{"name": "content", "type": "text"}],
            "source": "auto-generated",
        }

    # Load from meta.yaml
    try:
        meta = yaml.safe_load(meta_path.read_text(encoding="utf-8")) or {}
    except Exception as e:
        print(f"WARNING: Failed to parse {meta_path}: {e}", file=sys.stderr)
        return None

    block_id = meta.get("id", block_dir.name)

    return {
        "id": block_id,
        "path": f"{category}/{block_id}/",
        "category": category,
        "type": meta.get("type", category),
        "layout_pattern": meta.get("layout_pattern", "default"),
        "signature": meta.get("signature", f"{category}|default|[content]|bg:false"),
        "display_name_ru": meta.get("display_name_ru", f"{category}: {block_id}"),
        "created": meta.get("created", "2026-06-02"),
        "has_bg_image": meta.get("has_bg_image", False),
        "slots": meta.get("slots", [{"name": "content", "type": "text"}]),
        "source": meta.get("source", "auto-generated"),
    }


def main() -> None:
    p = argparse.ArgumentParser(
        description="Generate catalog.yaml from block-library directory structure"
    )
    p.add_argument("--library", required=True, help="Path to block-library directory")
    p.add_argument("--output", required=True, help="Output path for catalog.yaml")
    args = p.parse_args()

    library_dir = Path(args.library)
    output_path = Path(args.output)

    if not library_dir.exists():
        print(f"ERROR: library directory not found: {library_dir}", file=sys.stderr)
        sys.exit(1)

    # Collect all blocks from category subdirectories
    blocks: list[dict[str, Any]] = []
    seen_ids: set[str] = set()

    # Iterate through category directories (skip hidden and special dirs)
    for category_dir in sorted(library_dir.iterdir()):
        if not category_dir.is_dir() or category_dir.name.startswith((".", "_")):
            continue

        category = category_dir.name

        # Iterate through block directories within each category
        for block_dir in sorted(category_dir.iterdir()):
            if not block_dir.is_dir() or block_dir.name.startswith("."):
                continue

            block_id = block_dir.name

            # Skip duplicates (keep first occurrence)
            if block_id in seen_ids:
                print(
                    f"SKIP: Duplicate block ID '{block_id}' (already processed)",
                    file=sys.stderr,
                )
                continue

            seen_ids.add(block_id)

            # Extract metadata
            block_info = extract_block_info(block_dir, category)
            if block_info:
                blocks.append(block_info)
                print(f"✓ {category}/{block_id}")

    # Write catalog
    catalog = {
        "version": 3,
        "updated": "2026-06-02",
        "blocks": blocks,
    }

    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text(
        yaml.dump(catalog, default_flow_style=False, sort_keys=False, allow_unicode=True),
        encoding="utf-8",
    )

    print(f"\n✅ Generated {len(blocks)} blocks → {output_path}")


if __name__ == "__main__":
    main()
