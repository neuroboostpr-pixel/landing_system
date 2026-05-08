#!/usr/bin/env python3
"""prepare-layers.py — slice a 2x2 parallax atlas into 4 named layers.

Usage:
    python prepare-layers.py <project_dir>

Reads:  <project_dir>/assets/atlas.png
Writes: <project_dir>/assets/{background,far,near,subject}.png
        <project_dir>/assets/layers-report.json

Atlas convention (exactly what codex was told to draw):
    +--------+--------+
    |   TL   |   TR   |   TL = background (no transparency needed)
    |   BG   |  FAR   |   TR = distant overlay details (alpha)
    +--------+--------+
    |   BL   |   BR   |   BL = near foreground frame (alpha)
    |  NEAR  |SUBJECT |   BR = main subject (alpha)
    +--------+--------+

Reports per-layer alpha presence so caller knows which layers still need
recraft_remove_background (or another tool) to be made transparent.
"""

from __future__ import annotations
import json
import sys
from pathlib import Path

try:
    from PIL import Image
except ImportError:
    print("ERROR: Pillow not installed. Run: pip install Pillow", file=sys.stderr)
    sys.exit(2)


LAYERS = [
    # name, (x_frac, y_frac) of top-left of quadrant
    ("background", (0.0, 0.0)),
    ("far",        (0.5, 0.0)),
    ("near",       (0.0, 0.5)),
    ("subject",    (0.5, 0.5)),
]


def has_real_alpha(img: Image.Image) -> bool:
    """Check whether at least 5% of pixels are non-opaque."""
    if img.mode != "RGBA":
        return False
    alpha = img.getchannel("A")
    histogram = alpha.histogram()  # 256 buckets
    total = sum(histogram)
    if total == 0:
        return False
    transparent = sum(histogram[:255])  # everything not fully opaque
    return (transparent / total) >= 0.05


def slice_atlas(project_dir: Path) -> dict:
    atlas_path = project_dir / "assets" / "atlas.png"
    if not atlas_path.exists():
        raise FileNotFoundError(f"atlas not found: {atlas_path}")

    img = Image.open(atlas_path).convert("RGBA")
    w, h = img.size
    qw, qh = w // 2, h // 2

    report = {
        "atlas": {"path": str(atlas_path), "size": [w, h]},
        "layers": {},
    }

    for name, (xf, yf) in LAYERS:
        x0 = int(round(w * xf))
        y0 = int(round(h * yf))
        x1 = x0 + qw
        y1 = y0 + qh
        crop = img.crop((x0, y0, x1, y1))
        out = project_dir / "assets" / f"{name}.png"
        crop.save(out, format="PNG", optimize=True)
        report["layers"][name] = {
            "path": str(out),
            "size": list(crop.size),
            "has_alpha": has_real_alpha(crop),
            "needs_bg_removal": (name != "background") and (not has_real_alpha(crop)),
        }

    report_path = project_dir / "assets" / "layers-report.json"
    report_path.write_text(json.dumps(report, indent=2, ensure_ascii=False), encoding="utf-8")
    return report


def main() -> int:
    if len(sys.argv) != 2:
        print(__doc__, file=sys.stderr)
        return 2
    project_dir = Path(sys.argv[1]).resolve()
    if not project_dir.is_dir():
        print(f"ERROR: not a directory: {project_dir}", file=sys.stderr)
        return 2

    try:
        report = slice_atlas(project_dir)
    except FileNotFoundError as e:
        print(f"ERROR: {e}", file=sys.stderr)
        return 3

    print("Sliced atlas into 4 layers:")
    for name, info in report["layers"].items():
        flag = "✓ alpha" if info["has_alpha"] else "✗ NO alpha — needs bg removal"
        if name == "background":
            flag = "(opaque OK)"
        print(f"  {name:11s} → {info['path']}  [{flag}]")

    needs = [n for n, info in report["layers"].items() if info["needs_bg_removal"]]
    if needs:
        print()
        print(f"  Layers without alpha (expected — chroma-key removal next): {', '.join(needs)}")
        print(f"    Run: bash skills/paralaximus-codex/scripts/remove-bg.sh <project_dir>")
    else:
        print()
        print("  All overlay layers already have alpha. No chroma-key step needed.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
