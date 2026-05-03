#!/usr/bin/env python3
"""Identity-safe photo processing.

Allowed operations: cutout, cleanup, crop, resize.
NEVER alters faces, age, body. NEVER AI-repaint.

CLI: python3 style.py <input> <output> --mode <cutout|cleanup|crop|resize> [--aspect 1:1] [--max-dim 1600]
"""
import argparse
import sys
from pathlib import Path
from PIL import Image

sys.path.insert(0, str(Path(__file__).resolve().parents[3]))

from tools.logger import info, error, success


def resize(src: str, dst: str, max_dim: int = 1600) -> None:
    img = Image.open(src)
    w, h = img.size
    scale = max_dim / max(w, h)
    if scale < 1:
        new_size = (int(w * scale), int(h * scale))
        img = img.resize(new_size, Image.LANCZOS)
    img.save(dst)


def crop_aspect(src: str, dst: str, aspect: str) -> None:
    """Crop src to given aspect ratio (e.g. '1:1', '16:9'), centered."""
    a, b = map(int, aspect.split(":"))
    target = a / b
    img = Image.open(src)
    w, h = img.size
    current = w / h
    if current > target:
        # too wide -> crop width
        new_w = int(h * target)
        left = (w - new_w) // 2
        box = (left, 0, left + new_w, h)
    else:
        # too tall -> crop height
        new_h = int(w / target)
        top = (h - new_h) // 2
        box = (0, top, w, top + new_h)
    img.crop(box).save(dst)


def cutout(src: str, dst: str) -> None:
    """Remove background. Uses rembg if installed, else simple alpha heuristic."""
    try:
        from rembg import remove
        with open(src, "rb") as f:
            input_bytes = f.read()
        output_bytes = remove(input_bytes)
        with open(dst, "wb") as f:
            f.write(output_bytes)
        return
    except ImportError:
        info("rembg not installed, using Pillow fallback (less accurate)")

    # Fallback: convert to RGBA and use crude near-white-to-transparent
    img = Image.open(src).convert("RGBA")
    pixels = img.getdata()
    new_pixels = []
    for r, g, b, a in pixels:
        # Crude: pixels close to white become transparent
        if r > 240 and g > 240 and b > 240:
            new_pixels.append((r, g, b, 0))
        else:
            new_pixels.append((r, g, b, a))
    img.putdata(new_pixels)
    img.save(dst, "PNG")


def cleanup(src: str, dst: str) -> None:
    """Edge smoothing on existing alpha channel."""
    from PIL import ImageFilter
    img = Image.open(src).convert("RGBA")
    img.filter(ImageFilter.SMOOTH).save(dst, "PNG")


def main(argv: list) -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("input")
    parser.add_argument("output")
    parser.add_argument("--mode", choices=["cutout", "cleanup", "crop", "resize"], required=True)
    parser.add_argument("--aspect", default="1:1")
    parser.add_argument("--max-dim", type=int, default=1600)
    args = parser.parse_args(argv[1:])

    try:
        if args.mode == "cutout":
            cutout(args.input, args.output)
        elif args.mode == "cleanup":
            cleanup(args.input, args.output)
        elif args.mode == "crop":
            crop_aspect(args.input, args.output, args.aspect)
        elif args.mode == "resize":
            resize(args.input, args.output, args.max_dim)
        success(f"{args.mode}: {args.output}")
        return 0
    except Exception as exc:
        error(f"{args.mode} failed: {exc}")
        return 1


if __name__ == "__main__":
    sys.exit(main(sys.argv))
