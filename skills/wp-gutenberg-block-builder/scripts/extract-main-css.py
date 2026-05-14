#!/usr/bin/env python3
"""Regenerate <project>/08_КОД/wp-theme/assets/css/main.css from DESIGN.md.

Uses the existing design_extractor.extract() — which scans DESIGN.md §3-§9
fenced ```css blocks — and writes ONLY main.css. style.css is left alone.

Used by /landing-style after frontend-builder edits DESIGN.md §5.

WARNING: any manual edits to main.css are overwritten on every run.
Edit DESIGN.md §3-§9 (single source of truth) instead.

Exit 0: main.css written.
Exit 1: theme css dir missing (run /landing-build first), or DESIGN.md missing.
Exit 2: missing argv.

Usage: extract-main-css.py <project-dir>
"""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent / "lib"))
from design_extractor import DesignExtractError, extract  # noqa: E402


def main(argv: list[str]) -> int:
    if len(argv) < 2:
        print("usage: extract-main-css.py <project-dir>", file=sys.stderr)
        return 2
    project = Path(argv[1])
    md = project / "05_ДИЗАЙН-СИСТЕМА" / "DESIGN.md"
    out_dir = project / "08_КОД" / "wp-theme" / "assets" / "css"
    out_path = out_dir / "main.css"
    if not out_dir.exists():
        print(f"theme css dir not found: {out_dir} — run /landing-build first", file=sys.stderr)
        return 1
    try:
        _style_css, main_css = extract(md)
    except DesignExtractError as e:
        print(f"error: {e}", file=sys.stderr)
        return 1
    body = main_css.strip() if main_css.strip() else "/* main.css — DESIGN.md had no §3-§9 styles */"
    out_path.write_text(body + "\n", encoding="utf-8")
    print(str(out_path))
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv))
