#!/usr/bin/env python3
"""Extract text from a PDF prototype file.

Strategy:
1. Try text extraction via pypdf.
2. If empty (likely scanned PDF), suggest OCR via anthropic-skills:pdf.

Outputs raw text to stdout. Exit 0 on success, non-zero on failure.

Usage: extract-pdf-text.py <input.pdf>
"""
import sys
from pathlib import Path


def fail(m: str) -> None:
    print(f"ERROR: {m}", file=sys.stderr)
    sys.exit(1)


def main(path_str: str) -> None:
    path = Path(path_str)
    if not path.exists():
        fail(f"file not found: {path}")
    if path.stat().st_size == 0:
        fail("file is empty")

    try:
        from pypdf import PdfReader
    except ImportError:
        fail("pypdf is required. Install: pip install pypdf")

    try:
        reader = PdfReader(str(path))
    except Exception as e:
        fail(f"cannot open PDF: {e}")

    text_parts: list[str] = []
    for page in reader.pages:
        try:
            text_parts.append(page.extract_text() or "")
        except Exception:
            text_parts.append("")

    full = "\n".join(text_parts).strip()
    if not full:
        print(
            "ERROR: No text extracted (likely scanned PDF). "
            "Use anthropic-skills:pdf for OCR fallback.",
            file=sys.stderr,
        )
        sys.exit(2)

    print(full)


if __name__ == "__main__":
    if len(sys.argv) != 2:
        print("Usage: extract-pdf-text.py <path>", file=sys.stderr)
        sys.exit(3)
    main(sys.argv[1])
