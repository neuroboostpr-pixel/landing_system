#!/usr/bin/env python3
"""Identify fonts from a web reference (URL) via DOM CSS inspection.

For image references, the style-extractor agent uses Claude Vision
directly — no script needed.

CLI: python3 identify-fonts.py <URL> <output-yaml>
"""
import argparse
import sys
from pathlib import Path
from typing import List
import yaml

sys.path.insert(0, str(Path(__file__).resolve().parents[3]))

from tools.adapters.web_scraper import get_page_fonts
from tools.logger import success, error


_GENERIC_FAMILIES = {
    "serif", "sans-serif", "monospace", "cursive", "fantasy",
    "system-ui", "ui-serif", "ui-sans-serif", "ui-monospace",
    "ui-rounded", "math", "emoji", "fangsong",
}


def parse_font_stack(stack: str) -> str:
    """Extract the primary font family from a CSS font-family stack.

    '"Cabinet Grotesk", serif' -> 'Cabinet Grotesk'
    'Inter, system-ui' -> 'Inter'
    'monospace' -> 'monospace'
    """
    first = stack.split(",")[0].strip().strip('"').strip("'")
    return first


def identify_url(url: str, out_path: str) -> None:
    """Read computed font-families from URL's DOM, write fonts.yaml."""
    stacks = get_page_fonts(url)
    candidates = []
    seen = set()
    for stack in stacks:
        primary = parse_font_stack(stack)
        if primary in _GENERIC_FAMILIES or primary in seen or not primary:
            continue
        seen.add(primary)
        candidates.append({
            "family": primary,
            "full_stack": stack,
            "source": "DOM computed style",
            "confidence": 1.0,  # DOM tells us exactly what's loaded
        })

    out = Path(out_path)
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(yaml.safe_dump({
        "source_url": url,
        "method": "DOM CSS inspection (Playwright)",
        "candidates": candidates,
        "manual_review_required": len(candidates) == 0,
    }, allow_unicode=True, sort_keys=False), encoding="utf-8")


def main(argv: list) -> int:
    p = argparse.ArgumentParser()
    p.add_argument("url")
    p.add_argument("output_yaml")
    args = p.parse_args(argv[1:])
    try:
        identify_url(args.url, args.output_yaml)
        success(f"Wrote {args.output_yaml}")
        return 0
    except Exception as exc:
        error(f"font identification failed: {exc}")
        return 1


if __name__ == "__main__":
    sys.exit(main(sys.argv))
