#!/usr/bin/env python3
"""Generate theme/blocks/lazyblock-<slug>/block.php files from block-spec.yaml.

CLI: python generate-lzb-templates.py --project <path>

Never overwrites an existing block.php — render templates are user-editable
after first generation (Lazy Blocks reads $attributes the same way regardless).

Rendering is **spec-driven** (no name-based heuristics):
  * Per-block wrapper: ``b.element`` + ``b.css_class``, or ``b.wrapper_open_html``
    / ``b.wrapper_close_html`` for arbitrary layouts (e.g. hero 2-col grid).
    Default: ``<section class="lp-block lp-block--<slug>">``.
  * Per-control element + class come from spec (``element``, ``css_class``);
    default class is ``lp-field--<name>``, default element by type.
  * CTA pair: a control with ``href_from: <url_control_name>`` becomes
    ``<a class="..." href="...">text</a>``; the referenced url control emits
    nothing.
"""
import argparse
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent / "lib"))

from block_spec import Block, BlockSpecError, Card, Control, load, validate  # noqa: E402


# Default element per control.type when spec doesn't override.
_DEFAULT_ELEMENT = {
    "text":      "span",
    "textarea":  "p",
    "rich-text": "div",
    "classic-editor": "div",
    "url":       "a",
    "image":     "img",
    "email":     "span",
    "number":    "span",
    "select":    "span",
}


def _echo_text(key: str) -> str:
    return f"<?php echo esc_html($attributes['{key}'] ?? ''); ?>"


def _control_class(c: Control) -> str:
    return c.css_class if c.css_class else f"lp-field--{c.name}"


def _control_element(c: Control) -> str:
    return c.element if c.element else _DEFAULT_ELEMENT.get(c.type, "div")


def _render_text_like(c: Control, key: str, tag: str, cls: str) -> str:
    if c.type == "textarea":
        echo = f"<?php echo nl2br(esc_html($attributes['{key}'] ?? '')); ?>"
    elif c.type in ("rich-text", "classic-editor"):
        echo = f"<?php echo wp_kses_post($attributes['{key}'] ?? ''); ?>"
    else:  # text, email, etc.
        echo = _echo_text(key)
    return f'    <{tag} class="{cls}">{echo}</{tag}>'


def _render_cta_anchor(c: Control, url_name: str, cls: str) -> str:
    return (
        f'    <a class="{cls}" '
        f'href="<?php echo esc_url($attributes[\'{url_name}\'] ?? \'#\'); ?>">'
        f'{_echo_text(c.name)}</a>'
    )


def _render_control_output(c: Control) -> str:
    """Return one PHP fragment that emits this control's markup.

    Caller is responsible for skipping controls listed in the consumed-set
    (those targeted by another control's ``href_from``).
    """
    key = c.name
    cls = _control_class(c)
    tag = _control_element(c)

    # CTA pair declaration: text control points at a sibling url control.
    if c.href_from:
        return _render_cta_anchor(c, c.href_from, cls)

    if c.type in ("text", "textarea", "rich-text", "classic-editor", "email", "number", "select"):
        return _render_text_like(c, key, tag, cls)

    if c.type == "url":
        # Standalone url control — generic anchor, empty body.
        return f'    <a class="{cls}" href="<?php echo esc_url($attributes[\'{key}\'] ?? \'#\'); ?>"></a>'

    if c.type == "image":
        return (
            f'    <?php $img_{key} = $attributes[\'{key}\'] ?? null; ?>\n'
            f'    <?php if (!empty($img_{key}[\'id\'])): ?>\n'
            f'        <?php echo wp_get_attachment_image($img_{key}[\'id\'], \'large\', false, [\'class\' => \'{cls}\']); ?>\n'
            f'    <?php elseif (!empty($img_{key}[\'url\'])): ?>\n'
            f'        <img class="{cls}" src="<?php echo esc_url($img_{key}[\'url\']); ?>" alt="">\n'
            f'    <?php endif; ?>'
        )

    if c.type == "toggle":
        return (
            f'    <?php if (!empty($attributes[\'{key}\'])): ?>\n'
            f'        <div class="{cls} {cls}--on"></div>\n'
            f'    <?php endif; ?>'
        )

    if c.type == "repeater":
        return ""  # rendered by _render_repeater

    return f'    <div class="{cls}"><?php echo esc_html((string)($attributes[\'{key}\'] ?? \'\')); ?></div>'


def _repeater_child_output(ch: Control) -> str:
    cls = ch.css_class if ch.css_class else f"lp-rep-item lp-rep-item--{ch.name}"
    tag = ch.element if ch.element else "li"
    key = ch.name
    if ch.type in ("rich-text", "classic-editor"):
        return f'        <{tag} class="{cls}"><?php echo wp_kses_post($row[\'{key}\'] ?? \'\'); ?></{tag}>'
    if ch.type == "url":
        return f'        <{tag} class="{cls}"><a href="<?php echo esc_url($row[\'{key}\'] ?? \'#\'); ?>"></a></{tag}>'
    if ch.type == "textarea":
        return f'        <{tag} class="{cls}"><?php echo nl2br(esc_html($row[\'{key}\'] ?? \'\')); ?></{tag}>'
    return f'        <{tag} class="{cls}"><?php echo esc_html((string)($row[\'{key}\'] ?? \'\')); ?></{tag}>'


def _render_repeater(c: Control, all_controls: list) -> str:
    children = [x for x in all_controls if x.child_of == c.id]
    item_lines = []
    for ch in children:
        if ch.type == "repeater":
            continue
        item_lines.append(_repeater_child_output(ch))
    items = "\n".join(item_lines)
    cls = c.css_class if c.css_class else f"lp-rep lp-rep--{c.name}"
    return (
        f'    <ul class="{cls}">\n'
        f'    <?php foreach ((array)($attributes[\'{c.name}\'] ?? []) as $row): ?>\n'
        f'{items}\n'
        f'    <?php endforeach; ?>\n'
        f'    </ul>'
    )


def _consumed_names(controls: list) -> set:
    """Names of url controls absorbed by sibling text controls via ``href_from``."""
    return {c.href_from for c in controls if c.href_from}


def _wrapper_open_default(slug: str, css_class: str | None, element: str | None) -> str:
    tag = element or "section"
    cls = css_class or f"lp-block lp-block--{slug}"
    return f'<{tag} class="{cls}">'


def _wrapper_close_default(element: str | None) -> str:
    return f"</{element or 'section'}>"


def _render_block_php(b: Block) -> str:
    consumed = _consumed_names(b.controls)
    if b.wrapper_open_html:
        open_html = b.wrapper_open_html.rstrip("\n")
        close_html = (b.wrapper_close_html or _wrapper_close_default(b.element)).rstrip("\n")
    else:
        open_html = _wrapper_open_default(b.slug, b.css_class, b.element)
        close_html = _wrapper_close_default(b.element)

    lines = [
        "<?php",
        f"/**",
        f" * Block — {b.title}.",
        f" * Auto-scaffolded by generate-lzb-templates.py. Hand-edit freely; not overwritten on regen.",
        f" */",
        "if (!defined('ABSPATH')) { exit; }",
        "?>",
        open_html,
    ]
    for c in b.controls:
        if c.child_of is not None:
            continue
        if c.name in consumed:
            continue
        if c.type == "repeater":
            lines.append(_render_repeater(c, b.controls))
            continue
        out = _render_control_output(c)
        if out:
            lines.append(out)
    if b.type == "section-card" and b.card is not None:
        tmpl_php = "[" + ",".join(f"['lazyblock/{b.card.slug}']" for _ in (b.card.template or [{}])) + "]"
        lines.append(f'    <div class="<?php echo esc_attr(\'{b.section_grid_class}\'); ?>">')
        lines.append(
            f'        <InnerBlocks allowedBlocks="[\'lazyblock/{b.card.slug}\']" template="{tmpl_php}" />'
        )
        lines.append("    </div>")
    lines.append(close_html)
    return "\n".join(lines) + "\n"


def _render_card_php(b: Block, card: Card) -> str:
    consumed = _consumed_names(card.controls)
    if card.wrapper_open_html:
        open_html = card.wrapper_open_html.rstrip("\n")
        close_html = (card.wrapper_close_html or _wrapper_close_default(card.element or "article")).rstrip("\n")
    else:
        tag = card.element or "article"
        cls = card.css_class or f"lp-card lp-card--{card.slug}"
        open_html = f'<{tag} class="{cls}">'
        close_html = f"</{tag}>"

    lines = [
        "<?php",
        f"/**",
        f" * Card block — {card.title} (child of {b.slug}).",
        f" */",
        "if (!defined('ABSPATH')) { exit; }",
        "?>",
        open_html,
    ]
    for c in card.controls:
        if c.child_of is not None:
            continue
        if c.name in consumed:
            continue
        if c.type == "repeater":
            lines.append(_render_repeater(c, card.controls))
            continue
        out = _render_control_output(c)
        if out:
            lines.append(out)
    lines.append(close_html)
    return "\n".join(lines) + "\n"


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--project", required=True)
    args = ap.parse_args()

    project = Path(args.project)
    spec_path = project / "08_КОД" / "block-spec.yaml"
    try:
        spec = load(spec_path)
        validate(spec)
    except BlockSpecError as e:
        print(f"ERROR: {e}", file=sys.stderr)
        return 1

    blocks_root = project / "08_КОД" / "wp-theme" / "blocks"
    blocks_root.mkdir(parents=True, exist_ok=True)
    written = 0
    skipped = 0
    for b in spec.blocks:
        dest_dir = blocks_root / f"lazyblock-{b.slug}"
        dest_dir.mkdir(parents=True, exist_ok=True)
        dest = dest_dir / "block.php"
        if dest.exists():
            skipped += 1
        else:
            dest.write_text(_render_block_php(b), encoding="utf-8", newline="\n")
            written += 1
        if b.card is not None:
            card_dir = blocks_root / f"lazyblock-{b.card.slug}"
            card_dir.mkdir(parents=True, exist_ok=True)
            card_dest = card_dir / "block.php"
            if card_dest.exists():
                skipped += 1
            else:
                card_dest.write_text(_render_card_php(b, b.card), encoding="utf-8", newline="\n")
                written += 1
    print(f"wrote {written} block.php file(s), skipped {skipped} existing")
    return 0


if __name__ == "__main__":
    sys.exit(main())
