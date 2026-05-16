#!/usr/bin/env python3
"""Inject prototype.yaml content into a template.html via data-slot attributes
AND/OR ``{{slot:NAME}}`` text placeholders (new block format).

Rules (data-slot path — legacy ru-* blocks):
  - Element with data-slot="headline" → replace inner content with block.headline
  - data-slot="subhead" → block.subhead
  - data-slot="primary-cta" or "submit-cta" or any cta-suffix → block.cta.text
  - data-slot="<photo-slot-name>" — if photo_selections provided and slot has processed
    paths, insert <img> (or <picture> with mobile <source> when mobile_ratio defined).
    Otherwise render a placeholder block listing the slot hint from prototype's slots list.
  - data-slot="<icon-slot-name>" — if visuals_dir provided and icons/<name>.png exists,
    insert <img class="lp-icon">. Otherwise render a slot-placeholder.
  - data-slot="<infographic-slot-name>" — if visuals_dir provided and
    infographics/<name>.png exists, insert <img class="lp-infographic">. Otherwise placeholder.
  - Unknown slots → keep visible placeholder "[SLOT: <name>]"

Rules ({{slot:NAME}} text path — new imported blocks):
  - Universal mapping (see SLOT_MAPPING) — pulls block.title / block.headline /
    block.cta.text etc. depending on slot name.
  - item-N-FIELD slots → block.items[N-1].FIELD (1-indexed).
  - Unfilled slots → small gray italic placeholder `[name]` so the wireframe stays
    readable instead of dumping raw `{{slot:...}}` text.

Uses BeautifulSoup for safe HTML manipulation.

Usage:
  inject-content.py --template <html> --prototype <yaml> --position <int> --output <html>
                    [--selections <yaml>] [--visuals-dir <path>]
"""
import argparse
import json
import re
import sys
from pathlib import Path

import yaml
from bs4 import BeautifulSoup, NavigableString


def fail(m: str) -> None:
    print(f"ERROR: {m}", file=sys.stderr)
    sys.exit(1)


# -----------------------------------------------------------------------------
# Universal {{slot:NAME}} substitution (new block format)
# -----------------------------------------------------------------------------
#
# Maps a slot name (whatever the template author wrote inside {{slot:...}})
# to one or more candidate fields inside a prototype block. The first
# non-empty field wins. Nested fields use dot notation: "cta.text".
#
# Item-aware slots are handled by a separate regex (item-N-FIELD).
SLOT_MAPPING: dict[str, list[str]] = {
    # --- titles / headings ---
    "title": ["title", "headline", "heading"],
    "heading": ["title", "headline", "heading"],
    "headline": ["headline", "title", "heading"],
    "eyebrow": ["eyebrow", "subtype", "category"],
    "section-title": ["title", "headline"],
    # --- subtitles / intros ---
    "subhead": ["subhead", "subtitle", "intro"],
    "subtitle": ["subtitle", "subhead", "intro"],
    "lead": ["intro", "subhead", "subtitle"],
    "intro": ["intro", "subhead", "subtitle", "description"],
    "description": ["description", "intro", "body", "text"],
    "body": ["body", "intro", "description", "text"],
    "text": ["text", "body", "description"],
    "caption": ["caption", "subtitle", "intro"],
    # --- CTA labels ---
    "cta": ["cta.text", "cta_primary", "primary_cta", "cta_label"],
    "cta-label": ["cta.text", "cta_primary", "primary_cta"],
    "cta-text": ["cta.text", "cta_primary", "primary_cta"],
    "primary-cta-label": ["cta.text", "cta_primary", "primary_cta"],
    "primary-cta": ["cta.text", "cta_primary", "primary_cta"],
    "secondary-cta-label": ["cta_secondary", "secondary_cta"],
    "secondary-cta": ["cta_secondary", "secondary_cta"],
    "submit-cta": ["cta.text", "cta_primary"],
    # --- CTA hrefs ---
    "cta-url": ["cta.href"],
    "cta-href": ["cta.href"],
    "primary-cta-url": ["cta.href"],
    "primary-cta-href": ["cta.href"],
    # --- contacts ---
    "phone": ["phone"],
    "email": ["email"],
    "address": ["address"],
    "copyright": ["copyright"],
    # --- counts / proof ---
    "count": ["count", "value"],
    "value": ["value", "count"],
}


def _get_nested(obj, path: str):
    """Resolve a dotted path like 'cta.text' against a dict tree."""
    cur = obj
    for part in path.split("."):
        if isinstance(cur, dict):
            cur = cur.get(part)
        else:
            return None
        if cur is None:
            return None
    return cur


def _stringify(val) -> str:
    if val is None:
        return ""
    if isinstance(val, str):
        return val
    if isinstance(val, (int, float, bool)):
        return str(val)
    if isinstance(val, list):
        return ", ".join(_stringify(x) for x in val if x is not None and _stringify(x))
    if isinstance(val, dict):
        # Prefer common label-bearing fields when reducing a dict to string.
        for k in ("title", "name", "label", "text", "value", "headline"):
            if k in val:
                return _stringify(val[k])
        return ""
    return str(val)


def _resolve_item_slot(block: dict, idx: int, field: str) -> str:
    """Return value for items[idx].field (idx is 0-based)."""
    items = block.get("items") or []
    if idx < 0 or idx >= len(items):
        return ""
    item = items[idx]
    if not isinstance(item, dict):
        # Plain string list — only the bare item-N (no field) maps to the string.
        return _stringify(item) if not field or field in ("title", "name", "label", "text") else ""

    if not field:
        # Bare "item-1" → pick a sensible default field
        for k in ("title", "name", "label", "text", "headline"):
            if item.get(k):
                return _stringify(item[k])
        return ""

    # Try field as written, then dash↔underscore aliases.
    candidates = [field, field.replace("-", "_"), field.replace("_", "-")]
    # Friendly aliases inside an item
    field_aliases = {
        "title": ["title", "name", "label", "headline", "q", "question"],
        "name": ["name", "title", "label"],
        "label": ["label", "title", "name"],
        "text": ["text", "description", "body", "a", "answer"],
        "description": ["description", "text", "body", "a", "answer"],
        "body": ["body", "description", "text"],
        "icon": ["icon", "icon_slot", "icon_name"],
        "badge": ["badge", "marker", "label", "step", "number"],
        "marker": ["marker", "badge", "step", "number"],
        "step": ["step", "number", "marker", "badge"],
        "number": ["number", "step", "marker", "badge"],
        "price": ["price", "price_from_aed", "amount"],
        "question": ["question", "q", "title"],
        "answer": ["answer", "a", "description", "text"],
        "q": ["q", "question", "title"],
        "a": ["a", "answer", "description", "text"],
        "image": ["image", "photo", "photo_slot", "img"],
        "photo": ["photo", "photo_slot", "image"],
    }
    expanded: list[str] = []
    for c in candidates:
        expanded.append(c)
        for alias in field_aliases.get(c, []):
            if alias not in expanded:
                expanded.append(alias)

    for key in expanded:
        if key in item and item[key] not in (None, ""):
            return _stringify(item[key])
    return ""


_ITEM_SLOT_RE = re.compile(r"^item[-_]?(\d+)(?:[-_](.+))?$")


def resolve_slot(block: dict, slot_name: str) -> str:
    """Universal slot resolver — returns a string value or '' if not found."""
    slot_name = slot_name.strip()

    # 1. item-N or item-N-FIELD pattern (handles items[] from prototype)
    m = _ITEM_SLOT_RE.match(slot_name)
    if m:
        idx = int(m.group(1)) - 1
        field = (m.group(2) or "").strip()
        return _resolve_item_slot(block, idx, field)

    # 2. feature-N-FIELD / step-N-FIELD / faq-N-FIELD / etc. — map to items[N-1].FIELD
    prefix_match = re.match(
        r"^(feature|step|stage|faq|item|tier|plan|card|metric|stat|fact|"
        r"benefit|advantage|service|testimonial|review|logo|model|tab|"
        r"point|reason)[-_](\d+)(?:[-_](.+))?$",
        slot_name,
    )
    if prefix_match:
        idx = int(prefix_match.group(2)) - 1
        field = (prefix_match.group(3) or "").strip()
        # Hyphens inside compound fields like "cta-label" stay as-is
        return _resolve_item_slot(block, idx, field)

    # 3. Universal mapping table
    candidates = SLOT_MAPPING.get(slot_name)
    if not candidates:
        # Try dash↔underscore variants
        for alt in (slot_name.replace("-", "_"), slot_name.replace("_", "-")):
            if alt in SLOT_MAPPING:
                candidates = SLOT_MAPPING[alt]
                break
    if not candidates:
        # Fall back: literal field name on the block
        candidates = [slot_name, slot_name.replace("-", "_"), slot_name.replace("_", "-")]

    for src in candidates:
        if "." in src:
            val = _get_nested(block, src)
        else:
            val = block.get(src)
            if val is None:
                val = block.get(src.replace("-", "_"))
        s = _stringify(val)
        if s:
            return s
    return ""


_SLOT_PLACEHOLDER_RE = re.compile(r"\{\{slot:([^}]+)\}\}")


def substitute_text_placeholders(html_str: str, block: dict) -> str:
    """Replace all {{slot:NAME}} occurrences using universal resolver.

    Unfilled slots become a small inline gray italic placeholder so the
    wireframe renders cleanly instead of leaking template syntax.
    """
    def _repl(m: re.Match) -> str:
        name = m.group(1).strip()
        val = resolve_slot(block, name)
        if val:
            return val
        # Inline placeholder — keep it visible but unobtrusive.
        return (
            f'<span style="color:#bbb;font-style:italic;font-size:11px">'
            f'[{name}]</span>'
        )

    return _SLOT_PLACEHOLDER_RE.sub(_repl, html_str)


def inject_block(
    html_str: str,
    block_meta: dict,
    content: dict,
    photo_selections: dict | None = None,
    visuals_dir=None,
) -> str:
    """Inject content and optional real photos/visuals into a block's HTML string.

    Args:
        html_str: Raw HTML of the block template.
        block_meta: A single block entry from prototype.yaml (with 'slots', 'headline', etc.).
        content: Extra content dict (currently unused; reserved for future use).
        photo_selections: Optional dict loaded from 07c_PHOTOS/selections.yaml.
                          When provided, photo slots with processed paths get real <img>/<picture>.
                          When absent (None), the original placeholder behavior is preserved.
        visuals_dir: Optional path to 07d_VISUALS/ directory (PR-C).
                     When provided, icon and infographic slots with matching PNG files get
                     real <img> elements. When absent (None), placeholder behavior is preserved.

    Returns:
        Modified HTML string with slots injected.
    """
    soup = BeautifulSoup(html_str, "html.parser")
    photo_slots = {s["name"]: s for s in block_meta.get("slots", []) if s["type"] == "photo"}
    icon_slots = {s["name"]: s for s in block_meta.get("slots", []) if s.get("type") == "icon"}
    info_slots = {s["name"]: s for s in block_meta.get("slots", []) if s.get("type") == "infographic"}

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
        elif slot_name in icon_slots:
            el.clear()
            icon_png = None
            if visuals_dir:
                candidate = Path(visuals_dir) / "icons" / f"{slot_name}.png"
                if candidate.exists():
                    icon_png = candidate
            if icon_png:
                img = soup.new_tag("img", attrs={
                    "src": f"../07d_VISUALS/icons/{slot_name}.png",
                    "alt": icon_slots[slot_name].get("hint", slot_name),
                    "class": "lp-icon",
                })
                el.append(img)
            else:
                ph = soup.new_tag("div", **{"class": "slot-placeholder"})
                ph.string = f"[SLOT: {slot_name}]"
                el.append(ph)
        elif slot_name in info_slots:
            el.clear()
            info_png = None
            if visuals_dir:
                candidate = Path(visuals_dir) / "infographics" / f"{slot_name}.png"
                if candidate.exists():
                    info_png = candidate
            if info_png:
                img = soup.new_tag("img", attrs={
                    "src": f"../07d_VISUALS/infographics/{slot_name}.png",
                    "alt": info_slots[slot_name].get("chart_type", "infographic"),
                    "class": "lp-infographic",
                })
                el.append(img)
            else:
                ph = soup.new_tag("div", **{"class": "slot-placeholder"})
                ph.string = f"[INFOGRAPHIC: {slot_name}]"
                el.append(ph)
        else:
            el.clear()
            el.append(NavigableString(f"[SLOT: {slot_name}]"))

    # Second pass: handle {{slot:NAME}} text-placeholder format used by
    # the new imported blocks. BeautifulSoup keeps them inside text nodes,
    # so a plain regex on the serialized string is the simplest, safest way.
    out = str(soup)
    if "{{slot:" in out:
        out = substitute_text_placeholders(out, block_meta)
    return out


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
    p.add_argument(
        "--visuals-dir",
        default="",
        help="Optional path to 07d_VISUALS/ for icon + infographic substitution (PR-C).",
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

    visuals_dir = Path(args.visuals_dir) if args.visuals_dir else None

    html_str = Path(args.template).read_text()
    result = inject_block(html_str, block, {}, photo_selections=photo_selections, visuals_dir=visuals_dir)

    Path(args.output).write_text(result)
    print(f"OK: wrote {args.output}")


if __name__ == "__main__":
    main()
