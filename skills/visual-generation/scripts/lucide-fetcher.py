#!/usr/bin/env python3
"""Fetch Lucide icon SVG, render as brand-colored PNG.

Lucide icons are ISC-licensed (https://lucide.dev). We download SVG from the
official GitHub raw URL, replace `currentColor` with the brand color, and
rasterize to a square PNG of the requested size.

Used as the first-step bypass in prompt-picker waterfall for icons matched in
icons.csv where Library=Lucide.
"""
import os
import re
import sys
from pathlib import Path
from typing import Optional


LUCIDE_BASE_URL = "https://raw.githubusercontent.com/lucide-icons/lucide/main/icons"
DEFAULT_CACHE = Path.home() / ".cache" / "landing-system" / "lucide"


def lucide_url(icon_name: str) -> str:
    return f"{LUCIDE_BASE_URL}/{icon_name}.svg"


def cache_path(icon_name: str) -> Path:
    cache_dir = Path(os.environ.get("LUCIDE_CACHE_DIR", str(DEFAULT_CACHE)))
    return cache_dir / f"{icon_name}.svg"


def _http_get(url: str):
    """Simple HTTP GET with stdlib (no requests dependency)."""
    import urllib.request
    import urllib.error
    try:
        req = urllib.request.Request(url, headers={"User-Agent": "landing-system/1.0"})
        with urllib.request.urlopen(req, timeout=5) as resp:
            class R:
                pass
            r = R()
            r.status_code = resp.status
            r.text = resp.read().decode("utf-8")
            return r
    except urllib.error.URLError as e:
        class R:
            pass
        r = R()
        r.status_code = 0
        r.text = f"ERROR: {e}"
        return r


def fetch_svg(icon_name: str) -> Optional[Path]:
    """Return path to cached SVG, downloading if needed. None on failure."""
    cp = cache_path(icon_name)
    if cp.exists() and cp.stat().st_size > 0:
        return cp

    cp.parent.mkdir(parents=True, exist_ok=True)
    resp = _http_get(lucide_url(icon_name))
    if resp.status_code != 200 or "<svg" not in resp.text:
        return None
    cp.write_text(resp.text, encoding="utf-8")
    return cp


def render_to_png(svg_path: Path, out_path: Path, brand_color: str = "#000000", size: int = 1024) -> None:
    """Rasterize SVG to a square PNG of `size` pixels with brand color.

    Strategy:
    1. Replace `currentColor` and hardcoded stroke colors in SVG with brand_color.
    2. Try cairosvg if installed -> best quality.
    3. Try svglib + reportlab if installed.
    4. Last resort: write a brand-color border placeholder PNG via Pillow.
    """
    svg_text = Path(svg_path).read_text(encoding="utf-8")
    svg_text = svg_text.replace("currentColor", brand_color)
    svg_text = re.sub(r"\bstroke=\"#[0-9a-fA-F]{3,6}\"", f'stroke="{brand_color}"', svg_text)

    Path(out_path).parent.mkdir(parents=True, exist_ok=True)

    # Try cairosvg first (highest quality)
    try:
        import cairosvg  # type: ignore
        cairosvg.svg2png(
            bytestring=svg_text.encode("utf-8"),
            write_to=str(out_path),
            output_width=size, output_height=size,
        )
        return
    except ImportError:
        pass

    # Try svglib + reportlab
    try:
        from svglib.svglib import svg2rlg  # type: ignore
        from reportlab.graphics import renderPM  # type: ignore
        tmp_svg = Path(out_path).with_suffix(".tmp.svg")
        tmp_svg.write_text(svg_text, encoding="utf-8")
        drawing = svg2rlg(str(tmp_svg))
        scale = size / max(drawing.width, drawing.height)
        drawing.width *= scale
        drawing.height *= scale
        drawing.scale(scale, scale)
        renderPM.drawToFile(drawing, str(out_path), fmt="PNG")
        tmp_svg.unlink()
        return
    except ImportError:
        pass

    # Pillow fallback (placeholder)
    from PIL import Image, ImageDraw
    img = Image.new("RGBA", (size, size), (0, 0, 0, 0))
    draw = ImageDraw.Draw(img)
    border = size // 8
    rgb = tuple(int(brand_color.lstrip("#")[i:i+2], 16) for i in (0, 2, 4))
    draw.rectangle(
        [border, border, size - border, size - border],
        outline=rgb + (255,),
        width=max(2, size // 32),
    )
    img.save(out_path, "PNG")


def fetch_and_render(icon_name: str, out_path: Path, brand_color: str = "#000000", size: int = 1024) -> Optional[Path]:
    """One-shot: fetch SVG (cached) + render PNG. Returns out_path on success."""
    svg = fetch_svg(icon_name)
    if svg is None:
        return None
    render_to_png(svg, Path(out_path), brand_color=brand_color, size=size)
    return Path(out_path)


def main():
    import argparse
    ap = argparse.ArgumentParser()
    ap.add_argument("--name", required=True, help="Lucide icon name (e.g. 'menu', 'shield')")
    ap.add_argument("--out", required=True, help="Output PNG path")
    ap.add_argument("--color", default="#000000", help="Brand color hex")
    ap.add_argument("--size", type=int, default=1024)
    args = ap.parse_args()

    result = fetch_and_render(args.name, args.out, args.color, args.size)
    if result is None:
        print(f"FAIL: could not fetch Lucide icon '{args.name}'", file=sys.stderr)
        sys.exit(1)
    print(f"OK: {result}")


if __name__ == "__main__":
    main()
