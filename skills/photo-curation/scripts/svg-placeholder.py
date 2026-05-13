#!/usr/bin/env python3
"""SVG placeholder generator. Ports nexu-io/open-design placeholder.ts pattern
(Apache-2.0) — writes SVG content under a .png filename so `<img src="x.png">`
keeps working in HTML without an actual raster image.
"""
from pathlib import Path
from html import escape


SVG_TEMPLATE = """<svg xmlns="http://www.w3.org/2000/svg" width="{width}" height="{height}" viewBox="0 0 {width} {height}">
  <defs>
    <pattern id="paper" patternUnits="userSpaceOnUse" width="40" height="40">
      <rect width="40" height="40" fill="{bg}" />
      <circle cx="10" cy="10" r="1" fill="{fg}" opacity="0.15" />
      <circle cx="30" cy="30" r="1" fill="{fg}" opacity="0.15" />
    </pattern>
  </defs>
  <rect width="{width}" height="{height}" fill="url(#paper)" />
  <rect x="2" y="2" width="{wm2}" height="{hm2}" fill="none" stroke="{fg}" stroke-width="2" stroke-dasharray="8 8" opacity="0.4" />
  <text x="{cx}" y="{cy_id}" font-family="ui-sans-serif, system-ui, -apple-system, Segoe UI" font-size="{fs_id}" fill="{fg}" text-anchor="middle" font-weight="600">{slot_id}</text>
  <text x="{cx}" y="{cy_hint}" font-family="ui-sans-serif, system-ui" font-size="{fs_hint}" fill="{fg}" text-anchor="middle" opacity="0.7">{hint}</text>
  <text x="{cx}" y="{cy_size}" font-family="ui-monospace, monospace" font-size="{fs_size}" fill="{fg}" text-anchor="middle" opacity="0.4">{width}×{height}</text>
</svg>"""


def make_placeholder_svg(
    slot_id: str,
    width: int,
    height: int,
    hint: str,
    brand_primary: str = "#888888",
) -> str:
    cx = width // 2
    cy_id = int(height * 0.4)
    cy_hint = int(height * 0.5)
    cy_size = int(height * 0.62)
    fs_id = max(14, int(min(width, height) * 0.06))
    fs_hint = max(11, int(min(width, height) * 0.035))
    fs_size = max(10, int(min(width, height) * 0.025))

    bg = "#f5f5f4"
    return SVG_TEMPLATE.format(
        width=width, height=height,
        wm2=width - 4, hm2=height - 4,
        cx=cx, cy_id=cy_id, cy_hint=cy_hint, cy_size=cy_size,
        fs_id=fs_id, fs_hint=fs_hint, fs_size=fs_size,
        slot_id=escape(slot_id), hint=escape(hint),
        bg=bg, fg=brand_primary,
    )


def write_placeholder(out_path: Path, slot_id: str, width: int, height: int, hint: str, brand_primary: str = "#888888") -> None:
    svg = make_placeholder_svg(slot_id, width, height, hint, brand_primary)
    Path(out_path).parent.mkdir(parents=True, exist_ok=True)
    Path(out_path).write_text(svg, encoding="utf-8")


def main():
    import argparse
    ap = argparse.ArgumentParser()
    ap.add_argument("--slot-id", required=True)
    ap.add_argument("--width", type=int, required=True)
    ap.add_argument("--height", type=int, required=True)
    ap.add_argument("--hint", default="")
    ap.add_argument("--brand-primary", default="#888888")
    ap.add_argument("--out", required=True)
    args = ap.parse_args()
    write_placeholder(Path(args.out), args.slot_id, args.width, args.height, args.hint, args.brand_primary)


if __name__ == "__main__":
    main()
