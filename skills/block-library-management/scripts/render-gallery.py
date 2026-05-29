#!/usr/bin/env python3
"""Render a visual block gallery HTML from the block-library catalog.

Usage:
  render-gallery.py --library <path> --output <path>

Generates a single HTML page showing all blocks as thumbnail cards with
CSS-only category filtering (no JS frameworks required).
"""

import argparse
import html
from pathlib import Path

import yaml


def main() -> None:
    p = argparse.ArgumentParser()
    p.add_argument("--library", required=True, help="Path to block-library/ directory")
    p.add_argument("--output", required=True, help="Output HTML path (e.g. block-library/gallery.html)")
    args = p.parse_args()

    lib = Path(args.library).resolve()
    output_dir = Path(args.output).resolve().parent
    catalog_path = lib / "catalog.yaml"
    if not catalog_path.exists():
        print(f"ERROR: catalog.yaml not found at {catalog_path}")
        return

    catalog = yaml.safe_load(catalog_path.read_text(encoding="utf-8"))
    blocks = catalog.get("blocks", [])

    # Gather unique categories
    categories: list[str] = []
    seen: set[str] = set()
    for b in blocks:
        cat = b.get("category", "unknown")
        if cat not in seen:
            seen.add(cat)
            categories.append(cat)

    # Category RU labels
    cat_labels_ru = {
        "hero": "Hero",
        "features": "Фичи",
        "social-proof": "Отзывы",
        "process": "Процесс",
        "pricing": "Цены",
        "trust": "Доверие",
        "cta": "CTA",
        "faq": "FAQ",
        "quiz": "Квиз",
        "references": "Референсы",
    }

    # Category stats
    cat_counts: dict[str, int] = {}
    for b in blocks:
        cat = b.get("category", "unknown")
        cat_counts[cat] = cat_counts.get(cat, 0) + 1

    # Build CSS for :checked filter rules
    filter_rules: list[str] = []
    # Default state: show all (when no radio is checked, show all via :not(:checked) on "all")
    # Actually use "all" radio as default checked
    filter_rules.append(
        '#filter-all:checked ~ .gallery-grid .gallery-card { display: flex !important; }'
    )
    for cat in categories:
        safe_cat = cat.replace("-", "_")
        # When category filter checked: hide all, show matching
        filter_rules.append(
            f'#filter-{safe_cat}:checked ~ .gallery-grid .gallery-card {{ display: none; }}'
        )
        filter_rules.append(
            f'#filter-{safe_cat}:checked ~ .gallery-grid .gallery-card[data-cat="{cat}"] {{ display: flex; }}'
        )
        # Active label styling
        filter_rules.append(
            f'#filter-{safe_cat}:checked ~ .filter-bar label[for="filter-{safe_cat}"] {{ background: #111; color: #fff; border-color: #111; }}'
        )

    filter_rules.append(
        '#filter-all:checked ~ .filter-bar label[for="filter-all"] { background: #111; color: #fff; border-color: #111; }'
    )

    # Build cards HTML
    cards_parts: list[str] = []
    for b in blocks:
        block_id = b["id"]
        cat = b.get("category", "unknown")
        block_path = lib / b.get("path", f"{cat}/{block_id}/")
        meta_path = block_path / "meta.yaml"
        template_path = block_path / "assets" / "template.html"

        meta: dict = {}
        if meta_path.exists():
            meta = yaml.safe_load(meta_path.read_text(encoding="utf-8")) or {}

        display_name = html.escape(meta.get("display_name_ru", block_id))
        layout_summary = html.escape(meta.get("layout_summary_ru", ""))
        layout_pattern = html.escape(meta.get("layout_pattern", b.get("layout_pattern", "")))
        use_cases = meta.get("use_cases", b.get("use_cases", []))
        source = meta.get("source", b.get("source", "manual"))
        recommended_styles = meta.get("recommended_styles_ru", [])

        # Lo-fi wireframe CSS reset — injected AFTER block styles
        LOFI_CSS = """
<style>
/* === LO-FI WIREFRAME RESET === */
*, *::before, *::after {
  color: #333 !important;
  font-family: system-ui, sans-serif !important;
  text-shadow: none !important;
  -webkit-text-fill-color: unset !important;
}
/* Backgrounds: all sections/wrappers → light grey */
html, body, section, header, footer, main, article, aside, nav,
div, figure, blockquote, form, fieldset {
  background-color: #f5f5f5 !important;
  background-image: none !important;
  box-shadow: none !important;
}
/* Cards, badges, feature boxes, step circles → slightly darker grey */
.card, .badge, .tier, .col, .feature, .step,
[class*="card"], [class*="badge"], [class*="tier"],
[class*="feature"], [class*="step"], [class*="item"],
[class*="block__col"], [class*="__card"], [class*="__item"] {
  background-color: #e8e8e8 !important;
  background-image: none !important;
}
/* Images and photo slots → grey placeholder */
img {
  background: #d0d0d0 !important;
  opacity: 0.6 !important;
  filter: grayscale(100%) !important;
}
/* SVG icons → grey */
svg, svg * {
  fill: #aaa !important;
  stroke: #aaa !important;
  color: #aaa !important;
}
/* Buttons and CTAs */
a, button, .btn, .cta,
[class*="btn"], [class*="cta"], [class*="button"], [class*="__link"] {
  background-color: #999 !important;
  background-image: none !important;
  color: #fff !important;
  border-color: #999 !important;
}
/* Borders → subtle grey */
* {
  border-color: #d0d0d0 !important;
  outline-color: #d0d0d0 !important;
}
/* Gradients and pseudo-elements */
*::before, *::after {
  background-image: none !important;
  background-color: transparent !important;
}
</style>
"""

        # Read template content for srcdoc
        tmpl_content = ""
        if template_path.exists():
            raw = template_path.read_text(encoding="utf-8")
            # Inject lo-fi reset after the last </style> or at end of <head>
            # Strategy: append before </body> or at end if no </body>
            if "</body>" in raw:
                tmpl_content = raw.replace("</body>", LOFI_CSS + "</body>", 1)
            elif "</html>" in raw:
                tmpl_content = raw.replace("</html>", LOFI_CSS + "</html>", 1)
            else:
                tmpl_content = raw + LOFI_CSS
        else:
            tmpl_content = f"<html><body style='display:flex;align-items:center;justify-content:center;height:100%;color:#999;font-size:12px;font-family:sans-serif;'>template.html not found</body></html>"

        # Build use_case badges
        uc_badges = " ".join(
            f'<span class="uc-badge">{html.escape(uc)}</span>'
            for uc in use_cases
        )

        # Source badge
        source_badge = ""
        if source == "opendesign":
            source_badge = '<span class="source-badge od-badge">OpenDesign</span>'

        # Style tags
        style_tags = ""
        if recommended_styles:
            style_tags = " ".join(
                f'<span class="style-tag">{html.escape(s[:20])}</span>'
                for s in recommended_styles[:2]
            )

        # Iframe with scale transform
        srcdoc_escaped = html.escape(tmpl_content, quote=True)
        iframe_html = (
            f'<div class="card-thumb">'
            f'<div class="thumb-scaler">'
            f'<iframe sandbox srcdoc="{srcdoc_escaped}" '
            f'title="{html.escape(block_id)}" '
            f'loading="lazy"></iframe>'
            f'</div>'
            f'</div>'
        )

        styles_div = (
            f'<div class="card-styles">{style_tags}</div>' if style_tags else ''
        )
        # Ссылка относительно папки, где лежит сам gallery.html, с forward-slash
        # (Windows backslash в href не работает).
        try:
            rel = template_path.resolve().relative_to(output_dir)
        except ValueError:
            import os as _os
            rel = Path(_os.path.relpath(template_path.resolve(), output_dir))
        open_href = html.escape(rel.as_posix(), quote=True)
        layout_pattern_html = (
            f'<span class="card-layout-pattern">layout: {layout_pattern}</span>'
            if layout_pattern else ''
        )
        card = (
            f'<article class="gallery-card" data-cat="{html.escape(cat)}" data-id="{html.escape(block_id)}">'
            f'{iframe_html}'
            f'<div class="card-info">'
            f'<div class="card-name">{display_name}</div>'
            f'<div class="card-meta">'
            f'<span class="card-cat">{html.escape(cat_labels_ru.get(cat, cat))}</span>'
            f'{source_badge}'
            f'{layout_pattern_html}'
            f'</div>'
            f'<div class="card-uc">{uc_badges}</div>'
            f'{styles_div}'
            f'<div class="card-id">{html.escape(block_id)}</div>'
            f'</div>'
            f'<a class="card-open-btn" href="{open_href}" target="_blank">Открыть</a>'
            f'</article>'
        )
        cards_parts.append(card)

    # Build filter buttons
    filter_radios = ['<input type="radio" id="filter-all" name="gallery-filter" checked hidden>']
    filter_labels = ['<label for="filter-all" class="filter-btn active">Все блоки <span class="filter-count">{}</span></label>'.format(len(blocks))]

    for cat in categories:
        safe_cat = cat.replace("-", "_")
        filter_radios.append(
            f'<input type="radio" id="filter-{safe_cat}" name="gallery-filter" hidden>'
        )
        filter_labels.append(
            f'<label for="filter-{safe_cat}" class="filter-btn">'
            f'{html.escape(cat_labels_ru.get(cat, cat))} '
            f'<span class="filter-count">{cat_counts.get(cat, 0)}</span>'
            f'</label>'
        )

    stats_by_cat = ", ".join(
        f'{cat_labels_ru.get(cat, cat)}: {cnt}'
        for cat, cnt in sorted(cat_counts.items())
    )

    html_out = f"""<!DOCTYPE html>
<html lang="ru">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>Block Library Gallery — {len(blocks)} блоков</title>
<style>
  * {{ box-sizing: border-box; margin: 0; padding: 0; }}
  body {{ font-family: system-ui, sans-serif; background: #f0f0f0; color: #111; }}

  .gallery-header {{ background: #111; color: #fff; padding: 20px 28px; }}
  .gallery-header h1 {{ font-size: 1.4rem; font-weight: 700; margin-bottom: 4px; }}
  .gallery-stats {{ font-size: 13px; color: #aaa; }}

  /* CSS-only filter: radios control display */
  {chr(10).join(filter_rules)}

  .filter-bar {{ display: flex; gap: 8px; flex-wrap: wrap; padding: 16px 24px; background: #fff; border-bottom: 1px solid #e0e0e0; position: sticky; top: 0; z-index: 10; }}
  .filter-btn {{ padding: 7px 14px; border: 1.5px solid #ccc; border-radius: 20px; cursor: pointer; font-size: 13px; font-weight: 500; color: #444; transition: all .15s; user-select: none; }}
  .filter-btn:hover {{ border-color: #888; color: #111; }}
  .filter-count {{ font-size: 11px; color: #888; margin-left: 2px; }}

  .gallery-grid {{ display: grid; grid-template-columns: repeat(auto-fill, minmax(300px, 1fr)); gap: 20px; padding: 24px; }}

  .gallery-card {{ display: flex; flex-direction: column; background: #fff; border-radius: 10px; overflow: hidden; box-shadow: 0 2px 8px rgba(0,0,0,.08); transition: transform .2s, box-shadow .2s; }}
  .gallery-card:hover {{ transform: translateY(-3px); box-shadow: 0 8px 24px rgba(0,0,0,.12); }}

  .card-thumb {{ width: 100%; height: 200px; overflow: hidden; background: #e8e8e8; position: relative; }}
  .thumb-scaler {{ position: absolute; top: 0; left: 0; width: 100%; height: 100%; overflow: hidden; }}
  .thumb-scaler iframe {{
    width: 1280px;
    height: 800px;
    border: none;
    transform: scale(0.234375);  /* 300/1280 */
    transform-origin: top left;
    pointer-events: none;
  }}

  .card-info {{ padding: 12px 14px; flex: 1; display: flex; flex-direction: column; gap: 6px; }}
  .card-name {{ font-size: 14px; font-weight: 600; line-height: 1.3; }}
  .card-meta {{ display: flex; gap: 6px; align-items: center; flex-wrap: wrap; }}
  .card-cat {{ font-size: 11px; font-weight: 600; padding: 2px 8px; border-radius: 10px; background: #f0f0f0; color: #555; text-transform: uppercase; letter-spacing: .04em; }}
  .source-badge {{ font-size: 10px; font-weight: 600; padding: 2px 7px; border-radius: 10px; }}
  .od-badge {{ background: #e8f4fd; color: #0066cc; }}
  .card-uc {{ display: flex; gap: 4px; flex-wrap: wrap; }}
  .uc-badge {{ font-size: 10px; padding: 2px 6px; border-radius: 6px; background: #f8f0ff; color: #7c3aed; }}
  .card-styles {{ display: flex; gap: 4px; flex-wrap: wrap; }}
  .style-tag {{ font-size: 10px; padding: 2px 6px; border-radius: 6px; background: #fff7ed; color: #c2410c; }}
  .card-id {{ font-size: 10px; color: #999; font-family: monospace; margin-top: 2px; }}
  .card-layout-pattern {{ font-size: 10px; color: #777; font-family: monospace; background: #f0f0f0; padding: 1px 6px; border-radius: 6px; }}
  .card-open-btn {{ display: block; text-align: center; padding: 10px; background: #f5f5f5; color: #333; text-decoration: none; font-size: 13px; font-weight: 500; border-top: 1px solid #eee; transition: background .15s; }}
  .card-open-btn:hover {{ background: #111; color: #fff; }}
</style>
</head>
<body>

<header class="gallery-header">
  <h1>📚 Block Library Gallery — {len(blocks)} блоков</h1>
  <div class="gallery-stats">{stats_by_cat}</div>
</header>

{"".join(filter_radios)}
<div class="filter-bar">
  {"".join(filter_labels)}
</div>

<div class="gallery-grid">
  {"".join(cards_parts)}
</div>

</body>
</html>
"""

    out_path = Path(args.output)
    out_path.parent.mkdir(parents=True, exist_ok=True)
    out_path.write_text(html_out, encoding="utf-8")
    print(f"OK: gallery rendered at {out_path} ({len(blocks)} blocks)")


if __name__ == "__main__":
    main()
