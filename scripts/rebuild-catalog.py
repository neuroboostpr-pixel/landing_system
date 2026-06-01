#!/usr/bin/env python3
"""
Rebuild block-library/catalog.yaml from scratch by scanning all meta.yaml files.
"""

import os
import sys
import yaml
from pathlib import Path
from datetime import datetime
from typing import Dict, Any, List

def normalize_category(category: str) -> str:
    """Normalize category to lowercase."""
    if not category:
        return ''
    return category.lower().strip()

def extract_block_metadata(meta_path: str) -> Dict[str, Any]:
    """Extract metadata from a single meta.yaml file."""
    try:
        with open(meta_path, 'r', encoding='utf-8') as f:
            data = yaml.safe_load(f) or {}
        return data
    except Exception as e:
        print(f"Error reading {meta_path}: {e}", file=sys.stderr)
        return {}

def scan_blocks(library_path: str) -> List[Dict[str, Any]]:
    """Scan all meta.yaml files in the block library."""
    blocks = []
    library_dir = Path(library_path)

    # Find all meta.yaml files
    for meta_file in sorted(library_dir.glob('**/meta.yaml')):
        # Get relative path from library root
        rel_path = meta_file.relative_to(library_dir)

        # Extract parent directory (block id directory)
        block_dir = rel_path.parent
        category_dir = block_dir.parent

        # Read metadata
        meta = extract_block_metadata(str(meta_file))

        # Build block entry
        block_id = meta.get('id') or block_dir.name
        category = normalize_category(meta.get('category', str(category_dir)))

        block = {
            'id': block_id,
            'path': str(block_dir).replace('\\', '/') + '/',
            'category': category,
            'type': meta.get('type', ''),
            'layout_pattern': meta.get('layout_pattern', ''),
            'signature': meta.get('signature', ''),
            'display_name_ru': meta.get('display_name_ru', ''),
        }

        # Add any other fields from meta.yaml (but skip standard ones)
        standard_keys = {'id', 'category', 'type', 'layout_pattern', 'signature', 'display_name_ru'}
        for key, value in meta.items():
            if key not in standard_keys:
                block[key] = value

        blocks.append(block)

    return blocks

def rebuild_catalog(library_path: str, output_path: str):
    """Rebuild the catalog.yaml file."""
    print(f"Scanning blocks in {library_path}...")
    blocks = scan_blocks(library_path)

    # Sort by id for consistent output
    blocks.sort(key=lambda b: b['id'])

    print(f"Found {len(blocks)} blocks")

    # Build catalog structure
    catalog = {
        'version': 3,
        'updated': datetime.now().strftime('%Y-%m-%d'),
        'blocks': blocks,
    }

    # Write YAML
    print(f"Writing {output_path}...")
    with open(output_path, 'w', encoding='utf-8', newline='\n') as f:
        yaml.dump(
            catalog,
            f,
            default_flow_style=False,
            allow_unicode=True,
            sort_keys=False,
            width=120,
        )

    print(f"✓ Rebuilt catalog with {len(blocks)} blocks")

    # Summary
    categories = {}
    for block in blocks:
        cat = block['category'] or '(empty)'
        categories[cat] = categories.get(cat, 0) + 1

    print("\nBlock distribution by category:")
    for cat in sorted(categories.keys()):
        print(f"  {cat}: {categories[cat]}")

if __name__ == '__main__':
    library_path = 'D:\\AI_TEAMS\\landing_system\\block-library'
    output_path = 'D:\\AI_TEAMS\\landing_system\\block-library\\catalog.yaml'

    if not os.path.isdir(library_path):
        print(f"Error: Library path not found: {library_path}", file=sys.stderr)
        sys.exit(1)

    rebuild_catalog(library_path, output_path)
