#!/usr/bin/env python3
"""Сравнивает оригинал и обработанное фото через perceptual hash.

Использование:
  identity-check.py <orig.jpg> <processed.jpg> [--threshold N | --slot-type TYPE]

Exit 0 — identity сохранён (Hamming distance <= threshold)
Exit 1 — изменения слишком сильные
"""
import sys
import argparse
from pathlib import Path

from PIL import Image
import imagehash


# Per-slot-type Hamming distance thresholds.
# Lower = stricter (small change = violation).
THRESHOLDS = {
    "portrait": 5,
    "team": 5,
    "testimonial": 5,
    "expert": 5,
    "vehicle": 10,
    "car": 10,
    "product": 8,
    "hero-bg": 12,
    "interior": 15,
    "lifestyle": 15,
    "background": 18,
    "default": 10,
}


def resolve_threshold(slot_type: str | None, override: int | None) -> int:
    """Override побеждает slot-type. Если оба None → default."""
    if override is not None:
        return override
    if slot_type:
        return THRESHOLDS.get(slot_type, THRESHOLDS["default"])
    return THRESHOLDS["default"]


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("orig")
    parser.add_argument("processed")
    parser.add_argument("--threshold", type=int, default=None,
                        help="Ручной override (целое число Hamming distance)")
    parser.add_argument("--slot-type", default=None,
                        help="Тип слота (portrait, vehicle, product, hero-bg, interior, …)")
    args = parser.parse_args()

    orig_path = Path(args.orig)
    proc_path = Path(args.processed)

    if not orig_path.exists() or not proc_path.exists():
        print(f"ERROR: file not found", file=sys.stderr)
        return 2

    threshold = resolve_threshold(args.slot_type, args.threshold)

    h1 = imagehash.phash(Image.open(orig_path))
    h2 = imagehash.phash(Image.open(proc_path))
    distance = h1 - h2

    print(f"phash distance: {distance} (threshold: {threshold}, slot_type: {args.slot_type or 'default'})")

    return 0 if distance <= threshold else 1


if __name__ == "__main__":
    sys.exit(main())
