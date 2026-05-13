#!/usr/bin/env python3
"""Inject prototype.yaml content into a template.html via data-slot attributes.

Rules:
  - Element with data-slot="headline" → replace inner content with block.headline
  - data-slot="subhead" → block.subhead
  - data-slot="primary-cta" or "submit-cta" or any cta-suffix → block.cta.text
  - data-slot="<photo-slot-name>" — if photo_selections provided and slot has processed
    paths, insert <img> (or <picture> with mobile <source> when mobile_ratio defined).
    Otherwise render a placeholder block listing the slot hint from prototype's slots list.
  - Unknown slots → keep visible placeholder "[SLOT: <name>]"

Uses BeautifulSoup for safe HTML manipulation.

Usage:
  inject-content.py --template <html> --prototype <yaml> --position <int> --output <html>
                    [--selections <yaml>]
"""
import argparse
import json
import sys
from pathlib import Path

import yaml
from bs4 import BeautifulSoup, NavigableString


def fail(m: str) -> None:
    print(f"ERROR: {m}", file=sys.stderr)
    sys.exit(1)


def inject_block(
    html_str: str,
    block_meta: dict,
    content: dict,
    photo_selections: dict | None = None,
) -> str:
    """Inject content and optional real photos into a block's HTML string.

    Args:
        html_str: Raw HTML of the block template.
        block_meta: A single block entry from prototype.yaml (with 'slots', 'headline', etc.).
        content: Extra content dict (currently unused; reserved for future use).
        photo_selections: Optional dict loaded from 07c_PHOTOS/selections.yaml.
                          When provided, photo slots with processed paths get real <img>/<picture>.
                          When absent (None), the original placeholder behavior is preserved.

    Returns:
        Modified HTML string with slots injected.
    """
    soup = BeautifulSoup(html_str, "html.parser")
    photo_slots = {s["name"]: s for s in block_meta.get("slots", []) if s["type"] == "photo"}

    # Build slot_id → selection lookup from PR-B selections.yaml (backward-compatible)
    sel_by_slot: dict[str, dict] = {}
    if photo_selections:
        for s in photo_selections.get("slots", []):
            sel_by_slot[s["slot_id"]] = s

    for el in soup.select("[data-slot]"):
        slot_name = el["data-slot"]
        if slot_name == "headline" and "headline" in block_meta:
            el.clear()
            el.append(NavigableString(block_meta["headline"]))
        elif slot_name == "subhead" and "subhead" in block_meta:
            el.clear()
            el.append(NavigableString(block_meta["subhead"]))
        elif slot_name.endswith("-cta") and "cta" in block_meta:
            el.clear()
            el.append(NavigableString(block_meta["cta"].get("text", "")))
        elif slot_name in photo_slots:
            el.clear()
            sel = sel_by_slot.get(slot_name)
            if sel and sel.get("processed", {}).get("desktop"):
                # PR-B: substitute real processed photo
                desktop = sel["processed"]["desktop"]
                mobile = sel["processed"].get("mobile")
                slot_meta = photo_slots[slot_name]
                alt_text = slot_meta.get("hint", "")
                if mobile and slot_meta.get("mobile_ratio"):
                    # Use <picture> with a mobile <source> for art-directed responsive images
                    picture = soup.new_tag("picture")
                    src_mobile = soup.new_tag(
                        "source",
                        attrs={"srcset": mobile, "media": "(max-width: 768px)"},
                    )
                    picture.append(src_mobile)
                    img = soup.new_tag("img", attrs={"src": desktop, "alt": alt_text})
                    picture.append(img)
                    el.append(picture)
                else:
                    # Plain <img> — no mobile variant or no mobile_ratio defined
                    img = soup.new_tag("img", attrs={"src": desktop, "alt": alt_text})
                    el.append(img)
            else:
                # PR-A fallback: placeholder div (existing behavior)
                label_div = soup.new_tag("div", **{"class": "slot-placeholder"})
                label_div.append(NavigableString(
                    f"[photo slot: {slot_name} — hint: {photo_slots[slot_name].get('hint', '')}]"
                ))
                el.append(label_div)
        else:
            el.clear()
            el.append(NavigableString(f"[SLOT: {slot_name}]"))

    return str(soup)


def main() -> None:
    p = argparse.ArgumentParser()
    p.add_argument("--template", required=True)
    p.add_argument("--prototype", required=True)
    p.add_argument("--position", type=int, required=True)
    p.add_argument("--output", required=True)
    p.add_argument(
        "--selections",
        default=None,
        help="Optional path to 07c_PHOTOS/selections.yaml for real photo substitution (PR-B).",
    )
    args = p.parse_args()

    proto = yaml.safe_load(Path(args.prototype).read_text())
    block = next(
        (b for b in proto["blocks"] if b["position"] == args.position),
        None,
    )
    if block is None:
        fail(f"no block with position {args.position} in prototype")

    photo_selections = None
    if args.selections:
        sel_path = Path(args.selections)
        if sel_path.exists():
            photo_selections = yaml.safe_load(sel_path.read_text())

    html_str = Path(args.template).read_text()
    result = inject_block(html_str, block, {}, photo_selections=photo_selections)

    Path(args.output).write_text(result)
    print(f"OK: wrote {args.output}")


if __name__ == "__main__":
    main()
