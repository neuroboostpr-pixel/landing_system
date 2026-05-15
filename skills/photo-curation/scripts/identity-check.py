#!/usr/bin/env python3
"""Сравнивает оригинал и обработанное фото через perceptual hash.

Использование:
  identity-check.py <orig.jpg> <processed.jpg> [--threshold 10]

Exit 0 — identity сохранён (Hamming distance <= threshold)
Exit 1 — изменения слишком сильные
"""
import sys
import argparse
from pathlib import Path

from PIL import Image
import imagehash


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("orig")
    parser.add_argument("processed")
    parser.add_argument("--threshold", type=int, default=10)
    args = parser.parse_args()

    orig_path = Path(args.orig)
    proc_path = Path(args.processed)

    if not orig_path.exists() or not proc_path.exists():
        print(f"ERROR: file not found", file=sys.stderr)
        return 2

    h1 = imagehash.phash(Image.open(orig_path))
    h2 = imagehash.phash(Image.open(proc_path))
    distance = h1 - h2

    print(f"phash distance: {distance} (threshold: {args.threshold})")

    return 0 if distance <= args.threshold else 1


if __name__ == "__main__":
    sys.exit(main())
