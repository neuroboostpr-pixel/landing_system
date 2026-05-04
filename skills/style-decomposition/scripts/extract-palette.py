#!/usr/bin/env python3
"""Extract dominant color palette from a reference image.

CLI: python3 extract-palette.py <image> <output-yaml> [--count 5]
"""
import argparse
import sys
from pathlib import Path
from PIL import Image
import colorthief
import yaml

sys.path.insert(0, str(Path(__file__).resolve().parents[3]))
from tools.logger import success


def rgb_to_hex(rgb):
    r, g, b = (max(0, min(255, v)) for v in rgb)
    return "#{:02x}{:02x}{:02x}".format(r, g, b)


def extract(image_path: str, count: int = 5) -> list:
    """Extract `count` dominant colors. Return list of dicts with hex + source pixel."""
    ct = colorthief.ColorThief(image_path)
    # colorthief requires color_count >= 2
    palette_rgb = ct.get_palette(color_count=max(count, 2), quality=10)
    # Trim to requested count
    palette_rgb = palette_rgb[:count]

    # For each color, find a representative pixel coordinate (first match)
    img = Image.open(image_path).convert("RGB")
    w, h = img.size
    pixels = list(img.getdata())
    results = []
    for rgb in palette_rgb:
        # Find first pixel within Manhattan distance <= 20 of target
        coord = None
        for idx, p in enumerate(pixels):
            if all(abs(p[c] - rgb[c]) <= 20 for c in range(3)):
                coord = (idx % w, idx // w)
                break
        results.append({
            "hex": rgb_to_hex(rgb),
            "rgb": list(rgb),
            "source_pixel": list(coord) if coord else None,
        })

    # Deduplicate by hex value, keeping first occurrence
    seen_hex = set()
    deduped = []
    for entry in results:
        if entry["hex"] not in seen_hex:
            seen_hex.add(entry["hex"])
            deduped.append(entry)
    results = deduped

    return results


def main(argv: list) -> int:
    p = argparse.ArgumentParser()
    p.add_argument("image")
    p.add_argument("output_yaml")
    p.add_argument("--count", type=int, default=5)
    args = p.parse_args(argv[1:])

    palette = extract(args.image, args.count)
    out = Path(args.output_yaml)
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(yaml.safe_dump({
        "source_image": args.image,
        "palette": palette,
    }, allow_unicode=True, sort_keys=False), encoding="utf-8")
    success(f"Wrote {out} ({len(palette)} colors)")
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv))
