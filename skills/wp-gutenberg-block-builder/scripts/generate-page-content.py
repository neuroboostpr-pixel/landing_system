#!/usr/bin/env python3
"""Generate Gutenberg block markup (page-content.html) seeded with defaults
from block-spec.yaml. Deploy step substitutes image-attachment placeholders."""
import argparse
import json
import sys
from pathlib import Path
from urllib.parse import quote

sys.path.insert(0, str(Path(__file__).resolve().parent / "lib"))

from block_spec import Block, BlockSpec, BlockSpecError, Card, Control, load, validate  # noqa: E402


def _attr_value(c: Control, override: dict | None = None) -> object:
    """Return the attribute value for control c, honouring template override or default."""
    if override is not None and c.name in override:
        return override[c.name]
    d = c.default
    if c.type == "image" and d:
        # Placeholder; deploy substitutes real attachment ID after wp media import
        return {"id": f"__IMAGE_ATTACHMENT_ID__{d}__", "url": ""}
    if c.type == "toggle":
        if isinstance(d, bool):
            return d
        return d in ("true", "1", True)
    if c.type == "number" and d is not None:
        try:
            return int(d)
        except (ValueError, TypeError):
            return 0
    if c.type == "repeater":
        return []  # repeater rows seeded only via section+card template, not flat seeds
    return d if d is not None else ""


def _build_attrs(controls: list[Control], override: dict | None = None) -> dict:
    """Return dict {attr_name: value} suitable for Gutenberg block attrs JSON.

    Repeater values are serialised as urlencoded JSON arrays per Lazy Blocks
    convention (see research-doc).
    """
    attrs: dict[str, object] = {}
    top_level = [c for c in controls if c.child_of is None]
    for c in top_level:
        if c.type == "repeater":
            attrs[c.name] = quote(json.dumps([]))
        else:
            attrs[c.name] = _attr_value(c, override)
    return attrs


def _render_block(slug: str, attrs: dict, inner_html: str = "") -> str:
    attr_json = json.dumps(attrs, ensure_ascii=False)
    if inner_html:
        return f'<!-- wp:lazyblock/{slug} {attr_json} -->\n{inner_html}\n<!-- /wp:lazyblock/{slug} -->'
    return f'<!-- wp:lazyblock/{slug} {attr_json} /-->'


def _render_for_block(b: Block) -> str:
    if b.type == "single":
        return _render_block(b.slug, _build_attrs(b.controls))
    # section-card
    inner_parts: list[str] = []
    for tmpl in (b.card.template or [{}]):
        card_attrs = _build_attrs(b.card.controls, override=tmpl)
        inner_parts.append(_render_block(b.card.slug, card_attrs))
    inner_html = "\n".join(inner_parts)
    return _render_block(b.slug, _build_attrs(b.controls), inner_html=inner_html)


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
    out = "\n\n".join(_render_for_block(b) for b in spec.blocks) + "\n"
    dest = project / "08_КОД" / "page-content.html"
    dest.write_text(out, encoding="utf-8", newline="\n")
    print(f"wrote {dest} ({len(spec.blocks)} top-level block(s))")
    return 0


if __name__ == "__main__":
    sys.exit(main())
