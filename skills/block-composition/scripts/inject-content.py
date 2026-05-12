#!/usr/bin/env python3
"""Inject prototype.yaml content into a template.html via data-slot attributes.

Rules:
  - Element with data-slot="headline" → replace inner content with block.headline
  - data-slot="subhead" → block.subhead
  - data-slot="primary-cta" or "submit-cta" or any cta-suffix → block.cta.text
  - data-slot="<photo-slot-name>" — render a placeholder block listing the
    slot hint from prototype's slots list.
  - Unknown slots → keep visible placeholder "[SLOT: <name>]"

Uses BeautifulSoup for safe HTML manipulation.

Usage:
  inject-content.py --template <html> --prototype <yaml> --position <int> --output <html>
"""
import argparse
import sys
from pathlib import Path

import yaml
from bs4 import BeautifulSoup, NavigableString


def fail(m: str) -> None:
    print(f"ERROR: {m}", file=sys.stderr)
    sys.exit(1)


def main() -> None:
    p = argparse.ArgumentParser()
    p.add_argument("--template", required=True)
    p.add_argument("--prototype", required=True)
    p.add_argument("--position", type=int, required=True)
    p.add_argument("--output", required=True)
    args = p.parse_args()

    proto = yaml.safe_load(Path(args.prototype).read_text())
    block = next(
        (b for b in proto["blocks"] if b["position"] == args.position),
        None,
    )
    if block is None:
        fail(f"no block with position {args.position} in prototype")

    soup = BeautifulSoup(Path(args.template).read_text(), "html.parser")
    photo_slots = {s["name"]: s for s in block.get("slots", []) if s["type"] == "photo"}

    for el in soup.select("[data-slot]"):
        slot_name = el["data-slot"]
        if slot_name == "headline" and "headline" in block:
            el.clear()
            el.append(NavigableString(block["headline"]))
        elif slot_name == "subhead" and "subhead" in block:
            el.clear()
            el.append(NavigableString(block["subhead"]))
        elif slot_name.endswith("-cta") and "cta" in block:
            el.clear()
            el.append(NavigableString(block["cta"].get("text", "")))
        elif slot_name in photo_slots:
            label_div = soup.new_tag("div", **{"class": "slot-placeholder"})
            label_div.append(NavigableString(
                f"[photo slot: {slot_name} — hint: {photo_slots[slot_name].get('hint', '')}]"
            ))
            el.clear()
            el.append(label_div)
        else:
            el.clear()
            el.append(NavigableString(f"[SLOT: {slot_name}]"))

    Path(args.output).write_text(str(soup))
    print(f"OK: wrote {args.output}")


if __name__ == "__main__":
    main()
