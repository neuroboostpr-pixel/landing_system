#!/usr/bin/env python3
"""Generate theme/blocks/lazyblock-<slug>/block.php files from block-spec.yaml.

CLI: python generate-lzb-templates.py --project <path>

Never overwrites an existing block.php — render templates are user-editable
after first generation (Lazy Blocks reads $attributes the same way regardless).

Semantic HTML heuristics (per-control, by name convention):
  - title / heading / h1 → <h1 class="lp-h1">  (in `single` blocks)
  - heading              → <h2 class="lp-h2">  (in `section-card` blocks)
  - subtitle             → <h2 class="lp-h2">
  - lede                 → <p  class="lp-lede">
  - eyebrow / tag / *pill_tag* → <span class="lp-eyebrow">
  - note / anchor_note / caption → <small class="lp-caption">
  - <base>_text / <base>_label paired with a sibling <base>_url url-control
    → <a class="lp-btn" href="<url>">text</a>  (and url emits nothing standalone)
  - card-level `name` → <h3 class="lp-h3">
  - card-level `popular` toggle → folded into the card wrapper class
    (lp-card--popular), skipping its own div
"""
import argparse
import re
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent / "lib"))

from block_spec import Block, BlockSpecError, Card, Control, load, validate  # noqa: E402


# ---------- name-based classification helpers ----------

_RE_TITLE_LIKE = re.compile(r"^(title|heading|h1)$", re.I)
_RE_H2_TEXT    = re.compile(r"^(subtitle|h2)$", re.I)
_RE_LEDE       = re.compile(r"^lede$", re.I)
_RE_EYEBROW    = re.compile(r"^(eyebrow|tag|.*pill_tag.*)$", re.I)
_RE_CAPTION    = re.compile(r"^(anchor_note|note|caption)$", re.I)
_RE_CTA_TEXT   = re.compile(r"^(.*)(?:_text|_label)$|^button$", re.I)


def _is_text_like(c: Control) -> bool:
    return c.type in ("text", "textarea", "rich-text", "classic-editor")


def _find_cta_pairs(controls: list) -> dict:
    """Return mapping {text_control_name: url_control_name} for CTA pairs.

    Pair = a text-type control named <base>_text or <base>_label, when there's a
    sibling url-type control named <base>_url.
    """
    by_name = {c.name: c for c in controls if c.child_of is None}
    pairs = {}
    for c in controls:
        if c.child_of is not None or not _is_text_like(c):
            continue
        m = _RE_CTA_TEXT.match(c.name)
        if not m:
            continue
        if c.name == "button":
            # accept a bare `button_url` sibling
            url_name = "button_url"
        else:
            base = m.group(1)
            if not base:
                continue
            url_name = f"{base}_url"
        sibling = by_name.get(url_name)
        if sibling is not None and sibling.type == "url":
            pairs[c.name] = url_name
    return pairs


# ---------- per-element renderers ----------

def _echo_text(key: str) -> str:
    return f"<?php echo esc_html($attributes['{key}'] ?? ''); ?>"


def _render_cta_anchor(text_c: Control, url_name: str) -> str:
    return (
        f'    <a class="lp-btn lp-btn--{text_c.name}" '
        f'href="<?php echo esc_url($attributes[\'{url_name}\'] ?? \'#\'); ?>">'
        f'{_echo_text(text_c.name)}</a>'
    )


def _render_text_semantic(c: Control, block_type: str) -> str:
    """Return semantic HTML for a text-like control, or empty string for default."""
    name = c.name
    key = c.name

    if _RE_TITLE_LIKE.match(name):
        if name == "title" or block_type == "single":
            return f'    <h1 class="lp-h1">{_echo_text(key)}</h1>'
        # section-card etc. → h2
        return f'    <h2 class="lp-h2">{_echo_text(key)}</h2>'

    if _RE_H2_TEXT.match(name):
        return f'    <h2 class="lp-h2">{_echo_text(key)}</h2>'

    if _RE_LEDE.match(name):
        return f'    <p class="lp-lede">{_echo_text(key)}</p>'

    if _RE_EYEBROW.match(name):
        return f'    <span class="lp-eyebrow">{_echo_text(key)}</span>'

    if _RE_CAPTION.match(name):
        return f'    <small class="lp-caption">{_echo_text(key)}</small>'

    return ""


def _render_control_output(
    c: Control,
    all_controls: list,
    block_type: str,
    consumed_names: set,
    is_card: bool = False,
) -> str:
    """Return one PHP block that echoes/prints the field within the block markup."""
    if c.name in consumed_names:
        return ""

    key = c.name
    cls = f"lp-field--{c.name}"

    # Card-level semantic: `name` → <h3>
    if is_card and c.name == "name" and _is_text_like(c):
        return f'    <h3 class="lp-h3">{_echo_text(key)}</h3>'

    # Card-level `popular` toggle is folded into wrapper — emit nothing.
    if is_card and c.name == "popular" and c.type == "toggle":
        return ""

    if _is_text_like(c):
        # Try semantic first
        sem = _render_text_semantic(c, block_type)
        if sem:
            return sem
        if c.type == "text":
            return f'    <div class="{cls}">{_echo_text(key)}</div>'
        if c.type == "textarea":
            return f'    <div class="{cls}"><?php echo nl2br(esc_html($attributes[\'{key}\'] ?? \'\')); ?></div>'
        # rich-text / classic-editor
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


def _cta_emit_for_text(text_c: Control, pairs: dict, all_controls: list) -> str:
    url_name = pairs[text_c.name]
    return _render_cta_anchor(text_c, url_name)


def _render_block_php(b: Block) -> str:
    pairs = _find_cta_pairs(b.controls)
    consumed = set(pairs.values())  # url controls absorbed into anchors
    lines = [
        "<?php",
        f"/**",
        f" * Block — {b.title}.",
        f" * Auto-scaffolded by generate-lzb-templates.py. Hand-edit freely; not overwritten on regen.",
        f" */",
        "if (!defined('ABSPATH')) { exit; }",
        "?>",
        f'<section class="lp-block lp-block--{b.slug} nu-section nu-section--{b.slug}">',
    ]
    for c in b.controls:
        if c.child_of is not None:
            continue
        if c.type == "repeater":
            lines.append(_render_repeater(c, b.controls))
            continue
        if c.name in pairs:
            lines.append(_cta_emit_for_text(c, pairs, b.controls))
            continue
        out = _render_control_output(c, b.controls, b.type, consumed, is_card=False)
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


def _has_popular_toggle(card: Card) -> bool:
    return any(c.name == "popular" and c.type == "toggle" for c in card.controls)


def _render_card_php(b: Block, card: Card) -> str:
    pairs = _find_cta_pairs(card.controls)
    consumed = set(pairs.values())

    if _has_popular_toggle(card):
        wrapper = (
            f'<article class="lp-card lp-card--{card.slug} nu-card'
            f'<?php echo !empty($attributes[\'popular\']) ? \' lp-card--popular\' : \'\'; ?>"'
            f'<?php echo !empty($attributes[\'popular\']) ? \' data-popular="1"\' : \'\'; ?>>'
        )
    else:
        wrapper = f'<article class="lp-card lp-card--{card.slug} nu-card">'

    lines = [
        "<?php",
        f"/**",
        f" * Card block — {card.title} (child of {b.slug}).",
        f" */",
        "if (!defined('ABSPATH')) { exit; }",
        "?>",
        wrapper,
    ]
    # cards live inside a section-card → headings inside a card are h3-ish; we
    # already special-case `name` to h3. For `heading`/`title` inside a card we
    # treat block_type as "section-card" so they emit <h2>; cards usually don't
    # have those, but if they do, h2 is still semantically valid inside section.
    for c in card.controls:
        if c.child_of is not None:
            continue
        if c.type == "repeater":
            lines.append(_render_repeater(c, card.controls))
            continue
        if c.name in pairs:
            lines.append(_cta_emit_for_text(c, pairs, card.controls))
            continue
        out = _render_control_output(c, card.controls, "section-card", consumed, is_card=True)
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
