#!/usr/bin/env python3
"""
Restore template.html files for new blocks from git history.

Uses migration-map.yaml to find old_id -> new_id mappings,
then retrieves HTML from the old blocks at commit 8ca8901 (before cleanup).
"""

import os
import sys
import yaml
import subprocess
import json
from pathlib import Path

def run_git_show(ref, path):
    """Get file content from git history."""
    try:
        result = subprocess.run(
            ["git", "show", f"{ref}:{path}"],
            capture_output=True,
            text=True,
            cwd=os.getcwd()
        )
        if result.returncode == 0:
            return result.stdout
        return None
    except Exception as e:
        print(f"Error running git show: {e}")
        return None

def extract_category_from_id(block_id):
    """Extract category prefix from block ID."""
    parts = block_id.split("-")
    # Return everything except the last part (the number)
    if len(parts) > 1:
        # For blocks like "cta-brutalist-split-sskrusgun-ru-3",
        # category is "cta", and the rest is the variant
        return parts[0]
    return None

def extract_category_from_new_id(new_id):
    """Extract category from new style ID like 'cta-001'."""
    parts = new_id.split("-")
    return parts[0]

def main():
    # Read migration map
    migration_map_path = Path("block-library/migration-map.yaml")
    if not migration_map_path.exists():
        print(f"Error: {migration_map_path} not found")
        sys.exit(1)

    with open(migration_map_path) as f:
        migration_map = yaml.safe_load(f)

    print(f"Loaded {len(migration_map)} mappings from migration-map.yaml")

    # Source commit (before cleanup)
    source_commit = "8ca8901"

    restored = 0
    skipped = 0
    errors = []

    for old_id, new_id in migration_map.items():
        # Determine category
        new_category = extract_category_from_new_id(new_id)

        # Path to new block
        new_block_dir = Path(f"block-library/{new_category}/{new_id}")
        new_template_path = new_block_dir / "assets" / "template.html"

        if not new_block_dir.exists():
            skipped += 1
            errors.append(f"New block directory not found: {new_block_dir}")
            continue

        # Check if template already has real content (not just a comment)
        if new_template_path.exists():
            with open(new_template_path) as f:
                content = f.read().strip()
                # If it's not just a comment, skip
                if content and not content.startswith("<!--"):
                    print(f"✓ {new_id} already has real HTML, skipping")
                    skipped += 1
                    continue

        # Get old template from git
        old_template_path = f"block-library/{new_category}/{old_id}/assets/template.html"
        old_content = run_git_show(source_commit, old_template_path)

        if old_content is None:
            errors.append(f"Could not get template from git: {old_template_path}")
            skipped += 1
            continue

        # Write to new block
        new_template_path.parent.mkdir(parents=True, exist_ok=True)
        with open(new_template_path, "w") as f:
            f.write(old_content)

        # Also try to copy template-mobile.html if it exists
        old_mobile_path = f"block-library/{new_category}/{old_id}/assets/template-mobile.html"
        old_mobile_content = run_git_show(source_commit, old_mobile_path)

        if old_mobile_content:
            new_mobile_path = new_block_dir / "assets" / "template-mobile.html"
            with open(new_mobile_path, "w") as f:
                f.write(old_mobile_content)

        print(f"✓ Restored {new_id} from {old_id}")
        restored += 1

    print(f"\n{'='*60}")
    print(f"Summary:")
    print(f"  Restored: {restored}")
    print(f"  Skipped:  {skipped}")
    if errors:
        print(f"  Errors:   {len(errors)}")
        for err in errors[:5]:  # Show first 5 errors
            print(f"    - {err}")
        if len(errors) > 5:
            print(f"    ... and {len(errors) - 5} more")
    print(f"{'='*60}")

    return 0 if len(errors) == 0 else 1

if __name__ == "__main__":
    sys.exit(main())
