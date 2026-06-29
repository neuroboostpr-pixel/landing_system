#!/usr/bin/env python3
"""gen-prototype флоу A — нарезать графический PDF/страницу на горизонтальные
срезы при заданном зуме, чтобы агент читал текст ГЛАЗАМИ (а не доверял авто-OCR).

Каждая страница режется на N полос; каждая полоса рендерится в PNG при zoom.
Срезы пишутся во ВРЕМЕННУЮ папку (или --out), вне проекта — это промежуточные
файлы для чтения, не артефакт прототипа.

Требует PyMuPDF (`pip install pymupdf`).

Использование:
  python render-pdf-slices.py --source <proto.pdf> [--slices 12] [--zoom 3.0] \
         [--out <dir>]

Выводит список путей PNG (по одному на строку) в stdout — агент читает их Read-ом.
"""
from __future__ import annotations

import argparse
import sys
import tempfile
from pathlib import Path


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--source", required=True)
    ap.add_argument("--slices", type=int, default=12,
                    help="сколько горизонтальных полос на страницу")
    ap.add_argument("--zoom", type=float, default=3.0)
    ap.add_argument("--out", default="")
    args = ap.parse_args()

    src = Path(args.source)
    if not src.exists():
        print(f"ERROR: file not found: {src}", file=sys.stderr)
        sys.exit(1)

    try:
        import fitz  # PyMuPDF
    except ImportError:
        print("ERROR: PyMuPDF required. Install: pip install pymupdf", file=sys.stderr)
        sys.exit(2)

    out_dir = Path(args.out) if args.out else Path(tempfile.mkdtemp(prefix="proto-slices-"))
    out_dir.mkdir(parents=True, exist_ok=True)

    doc = fitz.open(str(src))
    written: list[str] = []
    for pi, page in enumerate(doc):
        r = page.rect
        n = max(1, args.slices)
        for i in range(n):
            clip = fitz.Rect(0, r.height * i / n, r.width, r.height * (i + 1) / n)
            pix = page.get_pixmap(matrix=fitz.Matrix(args.zoom, args.zoom), clip=clip)
            name = f"page{pi + 1:02d}-slice{i + 1:02d}.png"
            path = out_dir / name
            pix.save(str(path))
            written.append(str(path))

    print(f"# {len(written)} срезов в {out_dir} (zoom {args.zoom}, {args.slices} полос/стр)",
          file=sys.stderr)
    for w in written:
        print(w)


if __name__ == "__main__":
    main()
