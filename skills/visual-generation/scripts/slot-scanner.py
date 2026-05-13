#!/usr/bin/env python3
"""Parse composed.html for visual slots (type=icon and type=infographic).

Outputs structured YAML for visual-curator agent.
"""
from pathlib import Path

import yaml
from bs4 import BeautifulSoup


def _find_block_id(element) -> str:
    """Walk up DOM to find nearest ancestor with data-block-id attribute."""
    cur = element.parent
    while cur is not None:
        if hasattr(cur, "get") and cur.get("data-block-id"):
            return cur.get("data-block-id", "")
        cur = cur.parent
    return ""


def scan_html(html_path: Path) -> dict:
    """Scan composed.html for icon and infographic slots."""
    soup = BeautifulSoup(Path(html_path).read_text(encoding="utf-8"), "html.parser")
    icons: list[dict] = []
    infographics: list[dict] = []

    for el in soup.select('[data-slot-type="icon"]'):
        icons.append({
            "slot_name": el.get("data-slot", ""),
            "block_id": _find_block_id(el),
            "hint": el.get("data-hint", ""),
            "icon_color": el.get("data-icon-color", ""),
        })

    for el in soup.select('[data-slot-type="infographic"]'):
        infographics.append({
            "slot_name": el.get("data-slot", ""),
            "block_id": _find_block_id(el),
            "hint": el.get("data-hint", ""),
            "chart_type": el.get("data-chart-type", ""),
            "data": el.get("data-chart-data", ""),
        })

    return {"icons": icons, "infographics": infographics}


def scan_and_write(html_path: Path, out_path: Path) -> dict:
    """Scan and write result to YAML file."""
    result = scan_html(html_path)
    Path(out_path).parent.mkdir(parents=True, exist_ok=True)
    Path(out_path).write_text(yaml.safe_dump(result, allow_unicode=True, sort_keys=False), encoding="utf-8")
    return result


def main():
    import argparse
    ap = argparse.ArgumentParser()
    ap.add_argument("--html", required=True, help="Path to composed.html")
    ap.add_argument("--out", required=True, help="Path to output _slots.yaml")
    args = ap.parse_args()
    result = scan_and_write(Path(args.html), Path(args.out))
    print(f"Found {len(result['icons'])} icon slots, {len(result['infographics'])} infographic slots")


if __name__ == "__main__":
    main()
