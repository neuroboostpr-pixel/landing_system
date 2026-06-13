#!/usr/bin/env python3
"""Waterfall prompt picker: OpenDesign 90 JSON → icons.csv → generic template.

For icons:    icons.csv keyword match → generic (skip OpenDesign — they're not icon-suited per spec R1).
For infographics: OpenDesign tag/category match → generic.

Returns PickedPrompt(prompt_text, source, attribution).
"""
import csv
import json
import re
from dataclasses import dataclass
from enum import Enum
from pathlib import Path
from typing import Optional


class PromptSource(Enum):
    LUCIDE = "lucide"
    OPENDESIGN = "opendesign"
    ICONS_CSV = "icons_csv"
    GENERIC = "generic"


@dataclass
class PickedPrompt:
    prompt: str
    source: PromptSource
    attribution: Optional[dict] = None
    lucide_icon_name: Optional[str] = None  # set when source == PromptSource.LUCIDE


GENERIC_ICON_TEMPLATE = """Use the built-in image_gen tool. Generate ONE PNG, 1024x1024,
on flat solid {chroma} background, for: {hint}.

VISUAL STYLE: {visual_style}, {icon_style} icon
COLOR: {brand_accent} primary, monochrome on {chroma} background
NICHE CONTEXT: {niche}

FORBIDDEN: lens flare, glitch, AI watermarks, text, numbers, photoreal faces, surreal artifacts.

Single clean shape, centered, occupying ~70% of canvas, flat {chroma} background for chroma-key removal."""


GENERIC_INFOGRAPHIC_TEMPLATE = """Use the built-in image_gen tool. Generate ONE PNG, 1024x1024,
on flat solid {chroma} background, for a {chart_type} infographic.

DATA: {data}
VISUAL STYLE: {visual_style}
COLOR: {brand_accent} primary
NICHE CONTEXT: {niche}

For "{chart_type}":
- "number" — large number with unit/label, ornamental frame
- "bar" — simple bar chart, 3-5 bars max
- "line" — single line chart, growth trend
- "donut" — donut chart, 2-4 segments

FORBIDDEN: lens flare, glitch, photoreal faces, surreal artifacts, text labels longer than 30 chars.

Single clean composition centered, ~80% canvas, flat {chroma} background."""


def _icons_csv_match(hint: str, icons_csv: Path) -> Optional[dict]:
    """Search icons.csv for keyword match. Returns row dict or None."""
    if not icons_csv or not icons_csv.exists():
        return None
    hint_lower = hint.lower().strip()
    if not hint_lower:
        return None
    with icons_csv.open(encoding="utf-8") as f:
        reader = csv.DictReader(f)
        for row in reader:
            keywords = (row.get("Keywords", "") + " " + row.get("Icon Name", "")).lower()
            if hint_lower in keywords:
                return row
    return None


def _opendesign_match(hint: str, opendesign_index: Path, category: Optional[str] = None) -> Optional[dict]:
    """Search opendesign prompt JSONs for tag/category match. Returns prompt dict or None."""
    if not opendesign_index or not opendesign_index.exists():
        return None
    hint_lower = hint.lower().strip()
    if not hint_lower:
        return None

    for json_path in sorted(opendesign_index.glob("*.json")):
        if json_path.name.endswith(".attribution.txt"):
            continue
        try:
            data = json.loads(json_path.read_text(encoding="utf-8"))
        except json.JSONDecodeError:
            continue

        if category and data.get("category", "").lower() != category.lower():
            continue

        if hint_lower in data.get("title", "").lower():
            return data
        if any(hint_lower in tag.lower() for tag in data.get("tags", [])):
            return data

    return None


def pick_icon_prompt(
    hint: str,
    brand_context: dict,
    icons_csv: Optional[Path] = None,
    opendesign_index: Optional[Path] = None,
) -> PickedPrompt:
    """Pick prompt for icon slot. Waterfall: icons.csv → generic."""
    chroma = brand_context.get("CHROMA_KEY", "#00ff00")
    brand_accent = brand_context.get("BRAND_ACCENT", "#888888")
    visual_style = brand_context.get("VISUAL_STYLE", "Minimalism")
    icon_style = brand_context.get("ICON_STYLE", "outlined")
    niche = brand_context.get("NICHE", "")

    row = _icons_csv_match(hint, icons_csv) if icons_csv else None

    # STEP 1: Library=Lucide → bypass codex entirely, return svg component reference
    if row and row.get("Library", "").strip().lower() == "lucide":
        return PickedPrompt(
            prompt="",
            source=PromptSource.LUCIDE,
            attribution={"source": "Lucide", "license": "ISC", "url": "https://lucide.dev"},
            lucide_icon_name=row["Icon Name"].strip(),
        )

    # STEP 2: icons.csv match (non-Lucide) → codex generic with hint enrichment
    if row:
        first_kw = row.get("Keywords", "").split()[0] if row.get("Keywords") else ""
        prompt = GENERIC_ICON_TEMPLATE.format(
            chroma=chroma,
            hint=f"{row['Icon Name']} icon ({first_kw})",
            visual_style=visual_style,
            icon_style=icon_style,
            brand_accent=brand_accent,
            niche=niche,
        )
        return PickedPrompt(prompt=prompt, source=PromptSource.ICONS_CSV)

    # STEP 3: generic fallback
    prompt = GENERIC_ICON_TEMPLATE.format(
        chroma=chroma,
        hint=hint if hint else "abstract minimalist icon",
        visual_style=visual_style,
        icon_style=icon_style,
        brand_accent=brand_accent,
        niche=niche,
    )
    return PickedPrompt(prompt=prompt, source=PromptSource.GENERIC)


def pick_infographic_prompt(
    hint: str,
    chart_type: str,
    brand_context: dict,
    opendesign_index: Optional[Path] = None,
) -> PickedPrompt:
    """Pick prompt for infographic. Waterfall: OpenDesign → generic."""
    chroma = brand_context.get("CHROMA_KEY", "#00ff00")
    brand_accent = brand_context.get("BRAND_ACCENT", "#888888")
    visual_style = brand_context.get("VISUAL_STYLE", "Minimalism")
    niche = brand_context.get("NICHE", "")

    od = _opendesign_match(hint, opendesign_index, category="Infographic") if opendesign_index else None
    if od:
        adapted = od.get("prompt", "")
        adapted = adapted.replace("[BRAND_ACCENT]", brand_accent)
        adapted = adapted.replace("[BRAND_PRIMARY]", brand_accent)
        adapted = adapted.replace("[CHROMA_KEY]", chroma)
        attribution = {
            "id": od.get("id"),
            "license": od.get("source", {}).get("license"),
            "author": od.get("source", {}).get("author"),
            "url": od.get("source", {}).get("url"),
        }
        return PickedPrompt(prompt=adapted, source=PromptSource.OPENDESIGN, attribution=attribution)

    prompt = GENERIC_INFOGRAPHIC_TEMPLATE.format(
        chroma=chroma,
        chart_type=chart_type or "number",
        data=str(hint) if hint else "placeholder data",
        visual_style=visual_style,
        brand_accent=brand_accent,
        niche=niche,
    )
    return PickedPrompt(prompt=prompt, source=PromptSource.GENERIC)


def main():
    import argparse
    ap = argparse.ArgumentParser()
    ap.add_argument("--type", choices=["icon", "infographic"], required=True)
    ap.add_argument("--hint", required=True)
    ap.add_argument("--chart-type", default="")
    ap.add_argument("--brand-accent", default="#1e3a8a")
    ap.add_argument("--visual-style", default="Minimalism")
    ap.add_argument("--niche", default="")
    ap.add_argument("--icons-csv", default="")
    ap.add_argument("--opendesign-index", default="")
    args = ap.parse_args()

    brand_ctx = {
        "BRAND_ACCENT": args.brand_accent,
        "VISUAL_STYLE": args.visual_style,
        "NICHE": args.niche,
        "ICON_STYLE": "outlined",
    }

    if args.type == "icon":
        result = pick_icon_prompt(args.hint, brand_ctx, Path(args.icons_csv) if args.icons_csv else None, None)
    else:
        result = pick_infographic_prompt(args.hint, args.chart_type, brand_ctx,
                                          Path(args.opendesign_index) if args.opendesign_index else None)

    print(f"Source: {result.source.value}")
    if result.attribution:
        print(f"Attribution: {result.attribution}")
    print("---PROMPT---")
    print(result.prompt)


if __name__ == "__main__":
    main()
