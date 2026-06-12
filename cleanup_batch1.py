#!/usr/bin/env python3
import json
import re
from pathlib import Path

# Blocks to process (first 10)
blocks_to_process = [
    ("cta-minimal-split-portfolio-kdm1-ru-8", "cta/cta-minimal-split-portfolio-kdm1-ru-8"),
    ("cta-minimal-split-project21993216-tild-8", "cta/cta-minimal-split-project21993216-tild-8"),
    ("cta-technical-centered-antidiler-karpov-ru-5", "cta/cta-technical-centered-antidiler-karpov-ru-5"),
    ("cta-technical-split-medregistrant-ru-7", "cta/cta-technical-split-medregistrant-ru-7"),
    ("ru-cta-01-callback-tg-max", "cta/ru-cta-01-callback-tg-max"),
    ("ru-cta-02-banner-stripe", "cta/ru-cta-02-banner-stripe"),
    ("ru-cta-03-urgency-scarcity", "cta/ru-cta-03-urgency-scarcity"),
    ("ru-cta-04-lead-magnet", "cta/ru-cta-04-lead-magnet"),
    ("ru-cta-05-login-cta", "cta/ru-cta-05-login-cta"),
    ("ru-cta-06-editorial-paper", "cta/ru-cta-06-editorial-paper"),
]

import os
import sys

# Change to the script directory
script_dir = Path(__file__).parent
os.chdir(script_dir)

staging_dir = Path(".cleanup-staging")
staging_dir.mkdir(exist_ok=True)

def extract_slots(html_content):
    """Extract slot names from {{slot:...}} placeholders."""
    slots_set = set()
    slot_matches = re.findall(r'\{\{slot:([^}]+)\}\}', html_content)

    for slot_name in slot_matches:
        slot_type = "text"
        if "image" in slot_name.lower() or "photo" in slot_name.lower():
            slot_type = "image"
        elif "url" in slot_name.lower() or "link" in slot_name.lower() or "action" in slot_name.lower():
            slot_type = "url"

        slots_set.add((slot_name, slot_type))

    return [{"name": name, "type": typ} for name, typ in sorted(slots_set)]

def detect_layout(html_content):
    """Detect layout pattern from HTML classes and structure."""
    lower = html_content.lower()

    # Check class names and structure
    if "grid-template-columns" in lower or "grid-cols-4" in lower:
        return "grid-4"
    if "1fr 1fr 1fr" in lower or "grid-cols-3" in lower or "33%" in lower:
        return "grid-3"
    if "1fr 1fr" in lower or "grid-cols-2" in lower or "50%" in lower:
        return "grid-2"
    if "grid" in lower:
        return "grid"

    if "split" in lower:
        return "split"
    if "stacked" in lower or "flex-col" in lower:
        return "stacked"
    if "centered" in lower or "center" in lower:
        return "centered"
    if "sidebar" in lower:
        return "sidebar"
    if "timeline" in lower:
        return "timeline"
    if "card" in lower:
        return "cards"
    if "bento" in lower:
        return "bento"

    return "default"

def has_bg_image(html_content):
    """Check if block uses background image."""
    return ("background-image" in html_content or
            ("background:" in html_content and "url(" in html_content))

processed = 0
skipped = 0

for old_id, path in blocks_to_process:
    staging_file = staging_dir / f"{old_id}.json"

    # Skip if already processed
    if staging_file.exists():
        print(f"SKIP: {old_id} (already exists)")
        skipped += 1
        continue

    # Find template file (try assets/template.html first)
    template_path = Path(f"block-library/{path}/assets/template.html")
    if not template_path.exists():
        template_path = Path(f"block-library/{path}/template.html")

    if not template_path.exists():
        print(f"ERROR: {old_id} - template not found")
        continue

    try:
        # Read template HTML
        with open(template_path, 'r', encoding='utf-8') as f:
            html_content = f.read()

        # Extract data
        slots = extract_slots(html_content)
        layout = detect_layout(html_content)
        has_bg = has_bg_image(html_content)

        # Build signature
        slot_names = [s['name'] for s in slots]
        signature = f"cta|{layout}|{','.join(slot_names) if slot_names else 'default'}|bg:{'true' if has_bg else 'false'}"

        # Build output JSON
        output = {
            "old_path": path,
            "old_id": old_id,
            "type": "cta",
            "category": "CallToAction",
            "layout_pattern": layout,
            "slots": slots if slots else [{"name": "content", "type": "text"}],
            "has_bg_image": has_bg,
            "display_name_ru": old_id.replace('-', ' ').title(),
            "clean_html": html_content,
            "signature": signature,
            "status": "ok",
            "source": "cleaned"
        }

        # Write JSON file
        with open(staging_file, 'w', encoding='utf-8') as f:
            json.dump(output, f, ensure_ascii=False, indent=2)

        processed += 1
        print(f"OK: {old_id}")

    except Exception as e:
        print(f"ERROR: {old_id} - {str(e)}")

print(f"\nBatch summary:")
print(f"  Processed: {processed}")
print(f"  Skipped: {skipped}")
print(f"  Total: {processed + skipped}")
