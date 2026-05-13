#!/usr/bin/env python3
"""Identity-safe photo processing.

Allowed operations: cutout, cleanup, crop, resize, target-ratio.
NEVER alters faces, age, body. NEVER AI-repaint.

CLI: python3 style.py <input> <output> --mode <cutout|cleanup|crop|resize|target-ratio> [--aspect 1:1] [--ratio 16:9] [--max-dim 1600]
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


def target_ratio(src: str, dst: str, ratio: str, max_dim: int = 1920) -> None:
    """Crop to target ratio (center), then resize to fit max_dim.

    PR-B helper: combines crop_aspect + resize in one call so the photo-preview-board
    agent can produce slot-ready desktop+mobile variants without juggling intermediate files.
    """
    a, b = map(int, ratio.split(":"))
    target = a / b
    img = Image.open(src)
    w, h = img.size
    current = w / h
    if current > target:
        # too wide -> crop width
        new_w = int(h * target)
        left = (w - new_w) // 2
        img = img.crop((left, 0, left + new_w, h))
    elif current < target:
        # too tall -> crop height
        new_h = int(w / target)
        top = (h - new_h) // 2
        img = img.crop((0, top, w, top + new_h))
    # else: already correct ratio, no crop

    w, h = img.size
    if max(w, h) > max_dim:
        scale = max_dim / max(w, h)
        img = img.resize((int(w * scale), int(h * scale)), Image.LANCZOS)
    img.save(dst, "JPEG", quality=85)


def cutout(src: str, dst: str) -> None:
    """Remove background using rembg.

    Raises ImportError with install hint if rembg not installed —
    naive fallback was removed because it produced garbage on real photos.
    """
    try:
        from rembg import remove
    except ImportError:
        raise ImportError(
            "rembg required for cutout. Install with:\n"
            "  pip install rembg\n"
            "Or use --mode resize/crop/cleanup for non-cutout operations."
        )

    with open(src, "rb") as f:
        input_bytes = f.read()
    output_bytes = remove(input_bytes)
    with open(dst, "wb") as f:
        f.write(output_bytes)


def cleanup(src: str, dst: str) -> None:
    """Edge smoothing on existing alpha channel."""
    from PIL import ImageFilter
    img = Image.open(src).convert("RGBA")
    img.filter(ImageFilter.SMOOTH).save(dst, "PNG")


def main(argv: list) -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("input")
    parser.add_argument("output")
    parser.add_argument("--mode", choices=["cutout", "cleanup", "crop", "resize", "target-ratio"], required=True)
    parser.add_argument("--aspect", default="1:1")
    parser.add_argument("--ratio", default=None, help="Target aspect ratio for target-ratio mode, e.g. '16:9'")
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
        elif args.mode == "target-ratio":
            if not args.ratio:
                sys.exit("ERROR: --ratio required for target-ratio mode (e.g. --ratio 16:9)")
            target_ratio(args.input, args.output, args.ratio, args.max_dim if args.max_dim else 1920)
        success(f"{args.mode}: {args.output}")
        return 0
    except Exception as exc:
        error(f"{args.mode} failed: {exc}")
        return 1


if __name__ == "__main__":
    sys.exit(main(sys.argv))
