#!/usr/bin/env python3
"""gen-design-system — извлечь палитру РЕФЕРЕНСА по ПИКСЕЛЯМ (не на глаз).

Снимает с скриншота(ов) референса:
  - доминантные цвета (фоны/поверхности) — самые частые;
  - vivid-акценты (высокая насыщенность) — кнопки/акцентные слова.
Помогает заполнить palette.css токенами по факту, а не угадывая hex.

⚠️ Это ПОДСКАЗКА, не замена глаза: финальные --lp-* проверять зумом на самом
референсе (страница палитры референса, если есть, — точнее всего).

Требует Pillow (`pip install Pillow`).

Использование:
  python extract-palette.py <ref1.png> [ref2.png ...] [--n 8]
Выводит блоки «dominant» и «vivid accents» с hex/rgb/частотой в stdout.
"""
from __future__ import annotations

import argparse
import colorsys
import sys
from collections import Counter
from pathlib import Path


def _load(path: str):
    from PIL import Image
    im = Image.open(path).convert("RGB")
    w, h = im.size
    # лёгкий ресайз для скорости, пропорции сохраняем
    scale = min(1.0, 300 / w)
    return im.resize((int(w * scale), int(h * scale)))


def dominant(im, n: int):
    return Counter(im.getdata()).most_common(n)


def vivid(im, n: int):
    c = Counter()
    for px in im.getdata():
        r, g, b = (v / 255 for v in px)
        _, s, v = colorsys.rgb_to_hsv(r, g, b)
        if s > 0.45 and v > 0.35:        # только насыщенные/яркие = акценты
            c[px] += 1
    return c.most_common(n)


def _fmt(rows):
    for col, freq in rows:
        print("  #%02x%02x%02x" % col, col, freq)


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("refs", nargs="+")
    ap.add_argument("--n", type=int, default=8)
    args = ap.parse_args()

    try:
        import PIL  # noqa: F401
    except ImportError:
        print("ERROR: Pillow required. Install: pip install Pillow", file=sys.stderr)
        return 2

    for ref in args.refs:
        if not Path(ref).exists():
            print(f"ERROR: file not found: {ref}", file=sys.stderr)
            return 1
        im = _load(ref)
        print(f"=== {ref} — доминантные (фоны/поверхности) ===")
        _fmt(dominant(im, args.n))
        print(f"=== {ref} — vivid-акценты (кнопки/акцент-слова) ===")
        _fmt(vivid(im, args.n))
        print()
    return 0


if __name__ == "__main__":
    sys.exit(main())
