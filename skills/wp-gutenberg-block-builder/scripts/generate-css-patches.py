#!/usr/bin/env python3
"""Append AUTO-GENERATED display:contents patches for InnerBlocks wrappers."""
import argparse
import re
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent / "lib"))

from block_spec import BlockSpecError, load, validate  # noqa: E402

MARKER_START = "/* AUTO-GENERATED START: lzb-inner-blocks-patches — DO NOT EDIT */"
MARKER_END = "/* AUTO-GENERATED END: lzb-inner-blocks-patches */"
SECTION_RE = re.compile(
    r"\n?/\* AUTO-GENERATED START: lzb-inner-blocks-patches.*?/\* AUTO-GENERATED END: lzb-inner-blocks-patches \*/\n?",
    re.DOTALL,
)


def _render_section(spec) -> str:
    rules: list[str] = []
    for b in spec.blocks:
        if b.type != "section-card" or b.card is None:
            continue
        grid = b.section_grid_class
        card_slug = b.card.slug
        rules.append(
            f".{grid} .lazyblock-inner-blocks,\n"
            f".{grid} > .wp-block-lazyblock-{card_slug},\n"
            f".lazyblock-inner-blocks > .wp-block-lazyblock-{card_slug} {{ display: contents; }}"
        )
    body = "\n".join(rules)
    return f"\n{MARKER_START}\n{body}\n{MARKER_END}\n"


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--project", required=True)
    args = ap.parse_args()
    project = Path(args.project)
    try:
        spec = load(project / "08_КОД" / "block-spec.yaml")
        validate(spec)
    except BlockSpecError as e:
        print(f"ERROR: {e}", file=sys.stderr)
        return 1
    css_path = project / "08_КОД" / "wp-theme" / "assets" / "css" / "main.css"
    if not css_path.exists():
        print(f"ERROR: {css_path} not found — run generate-theme.py first", file=sys.stderr)
        return 1
    src = css_path.read_text(encoding="utf-8")
    section = _render_section(spec)
    if SECTION_RE.search(src):
        new = SECTION_RE.sub(section, src)
    else:
        new = src.rstrip() + "\n" + section
    css_path.write_text(new, encoding="utf-8", newline="\n")
    n = sum(1 for b in spec.blocks if b.type == "section-card")
    print(f"wrote {css_path} ({n} section+card patch(es))")
    return 0


if __name__ == "__main__":
    sys.exit(main())
