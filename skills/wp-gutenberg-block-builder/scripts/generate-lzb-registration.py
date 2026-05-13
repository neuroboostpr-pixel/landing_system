#!/usr/bin/env python3
"""Inject AUTO-GENERATED Lazy Blocks registration section into functions.php.

CLI: python generate-lzb-registration.py --project <path>
"""
import argparse
import re
import shutil
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent / "lib"))

from block_spec import BlockSpec, BlockSpecError, Block, Card, Control, load, validate  # noqa: E402

MARKER_START = "// AUTO-GENERATED START: lzb-block-registration — DO NOT EDIT MANUALLY"
MARKER_END = "// AUTO-GENERATED END: lzb-block-registration"
SECTION_RE = re.compile(
    r"\n?// AUTO-GENERATED START: lzb-block-registration.*?// AUTO-GENERATED END: lzb-block-registration\n?",
    re.DOTALL,
)


def _php_str(s) -> str:
    if s is None:
        return "''"
    s = str(s)
    return "'" + s.replace("\\", "\\\\").replace("'", "\\'") + "'"


def _render_controls(controls: list) -> str:
    if not controls:
        return "array()"
    lines = ["array("]
    for c in controls:
        parts = [
            f"'name' => {_php_str(c.name)}",
            f"'type' => {_php_str(c.type)}",
            f"'label' => {_php_str(c.label)}",
        ]
        if c.default is not None:
            parts.append(f"'default' => {_php_str(c.default)}")
        if c.child_of is not None:
            parts.append(f"'child_of' => {_php_str(c.child_of)}")
        lines.append(f"            {_php_str(c.id)} => array({', '.join(parts)}),")
    lines.append("        )")
    return "\n".join(lines)


def _render_block(slug: str, title: str, icon: str, category: str, controls: list) -> str:
    return (
        "    lazyblocks()->add_block(array(\n"
        f"        'slug' => {_php_str('lazyblock/' + slug)},\n"
        f"        'title' => {_php_str(title)},\n"
        f"        'icon' => {_php_str(icon)},\n"
        f"        'category' => {_php_str(category)},\n"
        f"        'controls' => {_render_controls(controls)},\n"
        "        'code' => array('output_method' => 'template'),\n"
        "    ));\n"
    )


def _render_section(spec: BlockSpec) -> str:
    body_parts: list = []
    for b in spec.blocks:
        body_parts.append(_render_block(b.slug, b.title, b.icon, b.category, b.controls))
        if b.card is not None:
            # Card inherits icon/category from parent section block
            body_parts.append(_render_block(b.card.slug, b.card.title, b.icon, b.category, b.card.controls))
    body = "\n".join(body_parts)
    return f"""
{MARKER_START}
add_action('lzb/init', function() {{
    if (!function_exists('lazyblocks')) {{ return; }}
{body}}});
{MARKER_END}
"""


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--project", required=True)
    args = ap.parse_args()

    spec_path = Path(args.project) / "08_КОД" / "block-spec.yaml"
    try:
        spec = load(spec_path)
        validate(spec)
    except BlockSpecError as e:
        print(f"ERROR: {e}", file=sys.stderr)
        return 1

    fn_php = Path(args.project) / "08_КОД" / "wp-theme" / "functions.php"
    if not fn_php.exists():
        print(f"ERROR: {fn_php} not found", file=sys.stderr)
        return 1

    shutil.copy2(fn_php, fn_php.with_suffix(".php.bak"))
    src = fn_php.read_text(encoding="utf-8")
    section = _render_section(spec)
    if SECTION_RE.search(src):
        new = SECTION_RE.sub(section, src)
    else:
        new = src.rstrip() + "\n" + section
    fn_php.write_text(new, encoding="utf-8", newline="\n")
    print(f"wrote {fn_php} ({len(spec.blocks)} block(s), {sum(1 for b in spec.blocks if b.card)} card(s))")
    return 0


if __name__ == "__main__":
    sys.exit(main())
