#!/usr/bin/env python3
"""Generate theme/blocks/lazyblock-<slug>/block.php files from block-spec.yaml.

CLI: python generate-lzb-templates.py --project <path>

Never overwrites an existing block.php — render templates are user-editable
after first generation (Lazy Blocks reads $attributes the same way regardless).
"""
import argparse
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent / "lib"))

from block_spec import Block, BlockSpecError, Card, Control, load, validate  # noqa: E402


def _render_control_output(c: Control) -> str:
    """Return one PHP line that echoes/prints the field within the block markup."""
    key = c.name
    cls = f"lp-field--{c.name}"
    if c.type in ("text",):
        return f'    <div class="{cls}"><?php echo esc_html($attributes[\'{key}\'] ?? \'\'); ?></div>'
    if c.type == "textarea":
        return f'    <div class="{cls}"><?php echo nl2br(esc_html($attributes[\'{key}\'] ?? \'\')); ?></div>'
    if c.type in ("rich-text", "classic-editor"):
        return f'    <div class="{cls}"><?php echo wp_kses_post($attributes[\'{key}\'] ?? \'\'); ?></div>'
    if c.type == "url":
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
        return ""  # handled by caller (nested loop)
    return f'    <div class="{cls}"><?php echo esc_html((string)($attributes[\'{key}\'] ?? \'\')); ?></div>'


def _repeater_child_output(ch: Control) -> str:
    cls = f"lp-rep-item lp-rep-item--{ch.name}"
    key = ch.name
    if ch.type in ("rich-text", "classic-editor"):
        return f'        <li class="{cls}"><?php echo wp_kses_post($row[\'{key}\'] ?? \'\'); ?></li>'
    if ch.type == "url":
        return f'        <li class="{cls}"><a href="<?php echo esc_url($row[\'{key}\'] ?? \'#\'); ?>"></a></li>'
    if ch.type == "textarea":
        return f'        <li class="{cls}"><?php echo nl2br(esc_html($row[\'{key}\'] ?? \'\')); ?></li>'
    return f'        <li class="{cls}"><?php echo esc_html((string)($row[\'{key}\'] ?? \'\')); ?></li>'


def _render_repeater(c: Control, all_controls: list) -> str:
    children = [x for x in all_controls if x.child_of == c.id]
    item_lines = []
    for ch in children:
        if ch.type == "repeater":
            continue
        item_lines.append(_repeater_child_output(ch))
    items = "\n".join(item_lines)
    return (
        f'    <ul class="lp-rep lp-rep--{c.name}">\n'
        f'    <?php foreach ((array)($attributes[\'{c.name}\'] ?? []) as $row): ?>\n'
        f'{items}\n'
        f'    <?php endforeach; ?>\n'
        f'    </ul>'
    )


def _render_block_php(b: Block) -> str:
    lines = [
        "<?php",
        f"/**",
        f" * Block — {b.title}.",
        f" * Auto-scaffolded by generate-lzb-templates.py. Hand-edit freely; not overwritten on regen.",
        f" */",
        "if (!defined('ABSPATH')) { exit; }",
        "?>",
        f'<section class="lp-block lp-block--{b.slug}">',
    ]
    for c in b.controls:
        if c.child_of is not None:
            continue
        if c.type == "repeater":
            lines.append(_render_repeater(c, b.controls))
        else:
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
    lines.append("</section>")
    return "\n".join(lines) + "\n"


def _render_card_php(b: Block, card: Card) -> str:
    lines = [
        "<?php",
        f"/**",
        f" * Card block — {card.title} (child of {b.slug}).",
        f" */",
        "if (!defined('ABSPATH')) { exit; }",
        "?>",
        f'<article class="lp-card lp-card--{card.slug}">',
    ]
    for c in card.controls:
        if c.child_of is not None:
            continue
        if c.type == "repeater":
            lines.append(_render_repeater(c, card.controls))
        else:
            out = _render_control_output(c)
            if out:
                lines.append(out)
    lines.append("</article>")
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
