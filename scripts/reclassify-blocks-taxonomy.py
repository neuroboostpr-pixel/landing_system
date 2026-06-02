#!/usr/bin/env python3
"""
DEPRECATED (2026-06-02, B34 rewrite). НЕ ЗАПУСКАТЬ.

Этот скрипт реализует СТАРУЮ модель таксономии (27 types в 10 категориях,
schema `tax['types']`). B34 переписан на двухуровневую модель
category → variant (11 категорий), у taxonomy.yaml больше НЕТ ключа `types`,
поэтому этот скрипт упадёт. Заменён на scripts/migrate-block-taxonomy.py
(Фаза 1 плана 2026-06-02-b34-taxonomy-implementation-plan.md).
Оставлен для git-истории.

Reclassify all blocks in block-library to the correct taxonomy from taxonomy.yaml.
Maps current types to 27 canonical types and their categories.
Updates meta.yaml files and rebuilds catalog.yaml.
"""

import yaml
import sys
from pathlib import Path
from collections import defaultdict

sys.exit(
    "DEPRECATED: scripts/reclassify-blocks-taxonomy.py использует старую 27-type "
    "модель. Используй scripts/migrate-block-taxonomy.py (B34 Фаза 1)."
)

# Block library directory
BLOCK_LIB = Path(__file__).parent.parent / "block-library"
TAXONOMY_FILE = BLOCK_LIB / "taxonomy.yaml"

def load_taxonomy():
    """Load taxonomy from taxonomy.yaml."""
    with open(TAXONOMY_FILE, encoding='utf-8') as f:
        tax = yaml.safe_load(f)

    # Build type -> category mapping
    type_to_category = {}
    for t in tax['types']:
        type_to_category[t['id']] = t['category']

    return tax, type_to_category

def infer_block_type(block_id, current_type):
    """
    Infer correct type from block_id and current type.

    Mapping rules (in order of specificity):
    1. If current_type is in taxonomy types, keep it
    2. Extract block category from directory/id and map to canonical type
    3. Fuzzy matching
    """
    taxonomy, type_to_category = load_taxonomy()
    canonical_types = [t['id'] for t in taxonomy['types']]

    # Normalize empty/None types
    if not current_type or current_type.strip() == '':
        current_type = None

    # Rule 1: Already canonical
    if current_type and current_type in canonical_types:
        return current_type

    # Rule 2: Extract from directory/id prefix
    # Examples: cta-001 -> cta, hero-001 -> hero, features-001 -> features
    # Also handle "ru-cta-01" style IDs
    id_parts = block_id.split('-')
    id_prefix = id_parts[1] if id_parts[0] == 'ru' and len(id_parts) > 1 else id_parts[0]

    # Special mappings for non-canonical prefixes
    prefix_map = {
        'cta': 'cta',
        'hero': 'hero',
        'features': 'features',
        'feature': 'features',
        'process': 'process',
        'pricing': 'pricing',
        'price': 'pricing',
        'gallery': 'gallery',
        'team': 'team',
        'footer': 'footer',
        'contact': 'contacts',
        'contacts': 'contacts',
        'header': 'header',
        'nav': 'header',
        'menu': 'menu',
        'about': 'about',
        'testimonial': 'testimonials',
        'testimonials': 'testimonials',
        'social': 'logos',
        'logos': 'logos',
        'stats': 'stats',
        'case': 'case-study',
        'case-study': 'case-study',
        'casetudy': 'case-study',
        'demo': 'demo',
        'showcase': 'demo',
        'integration': 'integrations',
        'integrations': 'integrations',
        'guarantee': 'guarantees',
        'guarantees': 'guarantees',
        'comparison': 'comparison',
        'vs': 'comparison',
        'alternative': 'comparison',
        'media': 'media-mentions',
        'mention': 'media-mentions',
        'form': 'lead-form',
        'lead': 'lead-form',
        'quiz': 'lead-form',
        'quizz': 'lead-form',
        'urgency': 'urgency',
        'banner': 'banner',
        'problem': 'problem-solution',
        'solution': 'problem-solution',
        'characteristic': 'characteristics',
        'characteristics': 'characteristics',
        'trust': 'guarantees',
        'faq': 'faq',
        'animation': None,  # Skip patterns
        'pattern': None,
        'glass': None,
        'hover': None,
        'ru': None,  # Skip ru-prefixed patterns
    }

    if id_prefix in prefix_map:
        mapped = prefix_map[id_prefix]
        if mapped and mapped in canonical_types:
            return mapped

    # Rule 3: Generic fallback based on current type
    type_fallback = {
        'unknown': 'demo',
        'pattern': None,
        'animation': None,
    }

    if current_type in type_fallback:
        mapped = type_fallback[current_type]
        if mapped and mapped in canonical_types:
            return mapped

    # Can't infer - return None to skip or default to demo
    return None

def reclassify_blocks():
    """Reclassify all blocks and return mapping."""
    taxonomy, type_to_category = load_taxonomy()

    blocks_updated = 0
    blocks_skipped = 0
    blocks_failed = []

    # Find all meta.yaml files
    meta_files = sorted(BLOCK_LIB.glob("**/meta.yaml"))
    print(f"Found {len(meta_files)} blocks to classify")

    for meta_file in meta_files:
        block_dir = meta_file.parent.name
        block_category_dir = meta_file.parent.parent.name

        # Load current meta.yaml
        with open(meta_file, encoding='utf-8') as f:
            meta = yaml.safe_load(f)

        current_type = meta.get('type', '').strip()
        current_category = meta.get('category', '').strip()
        block_id = meta.get('id', block_dir)

        # Infer correct type
        correct_type = infer_block_type(block_id, current_type)

        # Skip pattern/animation blocks
        if correct_type is None:
            blocks_skipped += 1
            continue

        # Get category from taxonomy
        correct_category = type_to_category.get(correct_type)

        if not correct_category:
            blocks_failed.append({
                'id': block_id,
                'dir': block_dir,
                'current_type': current_type,
                'inferred_type': correct_type,
                'reason': 'Type not found in taxonomy'
            })
            continue

        # Update meta.yaml if changed
        if current_type != correct_type or current_category != correct_category:
            meta['type'] = correct_type
            meta['category'] = correct_category

            with open(meta_file, 'w', encoding='utf-8') as f:
                yaml.dump(meta, f, default_flow_style=False, allow_unicode=True)

            blocks_updated += 1
            if blocks_updated <= 10 or blocks_updated % 50 == 0:
                print(f"  [{blocks_updated}] {block_id}: {current_type} → {correct_type} ({correct_category})")

    return blocks_updated, blocks_skipped, blocks_failed

def rebuild_catalog():
    """Rebuild catalog.yaml from all meta.yaml files."""
    taxonomy, type_to_category = load_taxonomy()

    blocks = []
    meta_files = sorted(BLOCK_LIB.glob("**/meta.yaml"))

    for meta_file in meta_files:
        with open(meta_file, encoding='utf-8') as f:
            meta = yaml.safe_load(f)

        block_type = meta.get('type')
        block_category = meta.get('category')

        # Skip patterns, animations, and blocks without proper classification
        if block_type in ['pattern', 'animation'] or block_category in ['_patterns', None]:
            continue

        block_entry = {
            'id': meta.get('id'),
            'type': block_type,
            'category': block_category,
            'layout_pattern': meta.get('layout_pattern'),
            'display_name_ru': meta.get('display_name_ru'),
        }
        blocks.append(block_entry)

    # Build catalog structure
    catalog = {
        'version': 3,
        'generated': '2026-06-01',
        'total_blocks': len(blocks),
        'blocks': blocks,
    }

    catalog_file = BLOCK_LIB / "catalog.yaml"
    with open(catalog_file, 'w', encoding='utf-8') as f:
        yaml.dump(catalog, f, default_flow_style=False, allow_unicode=True)

    print(f"\nRebuilt {catalog_file}: {len(blocks)} blocks")
    return len(blocks)

def main():
    print("=" * 70)
    print("BLOCK LIBRARY TAXONOMY RECLASSIFICATION")
    print("=" * 70)

    # Step 1: Reclassify
    print("\n[1/3] Reclassifying blocks...")
    updated, skipped, failed = reclassify_blocks()
    print(f"\n  ✓ Updated: {updated}")
    print(f"  ⊘ Skipped (patterns): {skipped}")
    print(f"  ✗ Failed: {len(failed)}")

    if failed:
        print("\nFailed blocks:")
        for item in failed[:10]:
            print(f"  - {item['id']} ({item['current_type']} → {item['inferred_type']}): {item['reason']}")
        if len(failed) > 10:
            print(f"  ... and {len(failed) - 10} more")

    # Step 2: Rebuild catalog
    print("\n[2/3] Rebuilding catalog.yaml...")
    catalog_count = rebuild_catalog()

    # Step 3: Regenerate gallery
    print("\n[3/3] Regenerating gallery.html...")
    import subprocess
    render_script = Path(__file__).parent / "block-library-management" / "scripts" / "render-gallery.py"
    if render_script.exists():
        result = subprocess.run(
            [sys.executable, str(render_script),
             "--library", str(BLOCK_LIB),
             "--output", str(BLOCK_LIB / "gallery.html")],
            capture_output=True, text=True
        )
        if result.returncode == 0:
            print(f"  ✓ Gallery generated: {BLOCK_LIB / 'gallery.html'}")
        else:
            print(f"  ⚠ Gallery generation had issues:")
            print(f"    {result.stderr}")
    else:
        print(f"  ⚠ render-gallery.py not found at {render_script}")

    # Summary
    print("\n" + "=" * 70)
    print(f"SUMMARY: Reclassified {updated} blocks to 27-type taxonomy")
    print(f"Catalog: {catalog_count} blocks | Gallery: regenerated")
    print("=" * 70)

if __name__ == '__main__':
    main()
