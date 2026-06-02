#!/usr/bin/env python3
"""Generate block-library gallery.html from catalog.yaml with combobox filters.

This script reads catalog.yaml and generates an interactive HTML gallery
with two-level filtering: Категория (combobox 1) → Подкатегория (combobox 2).

B34: labels come from block-library/taxonomy.yaml (Russian, ordered by `order`).
The second combobox holds semantic `variant`s and is HIDDEN (display:none) for
categories that have no level-3 variants.

Usage:
  python scripts/generate-gallery.py --library block-library --output block-library/gallery.html
"""
import argparse
import html as _html
import importlib.util
import json as _json
import sys
from collections import defaultdict
from pathlib import Path

import yaml

LOADER_PATH = Path(__file__).resolve().parent / "lib" / "taxonomy.py"


def _load_taxonomy_lib():
    spec = importlib.util.spec_from_file_location("taxonomy_lib_gallery", LOADER_PATH)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


def extract_srcdoc(block_id: str, block_dir: Path) -> str:
    """Extract srcdoc from block's index.html preview."""
    index_path = block_dir / "index.html"
    if not index_path.exists():
        return ""

    try:
        content = index_path.read_text(encoding="utf-8")
        # Escape quotes and newlines for HTML attribute
        content = content.replace('"', '&quot;').replace('\n', ' ')
        return content
    except Exception:
        return ""


def main() -> None:
    p = argparse.ArgumentParser(description="Generate block library gallery.html")
    p.add_argument("--library", required=True, help="Path to block-library directory")
    p.add_argument("--output", required=True, help="Output path for gallery.html")
    args = p.parse_args()

    library_dir = Path(args.library)
    output_path = Path(args.output)

    tax = _load_taxonomy_lib()

    # Load catalog
    cat_path = library_dir / "catalog.yaml"
    if not cat_path.exists():
        print(f"ERROR: {cat_path} not found", file=sys.stderr)
        sys.exit(1)

    catalog = yaml.safe_load(cat_path.read_text(encoding="utf-8"))
    blocks = catalog.get("blocks", [])

    # Group blocks by category; count variants within each category.
    blocks_by_cat = defaultdict(list)
    variants_by_cat = defaultdict(lambda: defaultdict(int))
    for block in blocks:
        cat = block.get("category", "unknown")
        variant = block.get("variant")
        blocks_by_cat[cat].append(block)
        if variant:
            variants_by_cat[cat][variant] += 1

    # Categories in taxonomy order, but only those actually present.
    present = set(blocks_by_cat.keys())
    categories = [c for c in tax.categories_ordered() if c in present]
    # any stray categories not in taxonomy go last (defensive)
    categories += sorted(present - set(categories))

    # JS map: category -> {variantSlug: {label, count}} (only categories w/ variants)
    cat_variants = {}
    for cat in categories:
        if not tax.has_variants(cat):
            continue
        # order variants by taxonomy declaration, keep only present ones
        ordered = [v for v in tax.variants_ordered(cat) if v in variants_by_cat[cat]]
        ordered += [v for v in variants_by_cat[cat] if v not in ordered]
        cat_variants[cat] = {
            v: {"label": tax.variant_label(cat, v) if tax.valid_variant(cat, v) else v,
                "count": variants_by_cat[cat][v]}
            for v in ordered
        }
    cat_variants_json = _json.dumps(cat_variants, ensure_ascii=False)

    # CAT_LABELS / VARIANT_LABELS not strictly needed by JS (labels baked into
    # CAT_VARIANTS), but expose category labels for completeness.
    cat_labels = {c: tax.category_label(c) for c in categories}
    cat_labels_json = _json.dumps(cat_labels, ensure_ascii=False)

    total = len(blocks)
    stats = ", ".join(
        f"{tax.category_label(cat)}: {len(blocks_by_cat[cat])}" for cat in categories
    )

    # Start HTML
    html = f"""<!DOCTYPE html>
<html lang="ru">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>Галерея блоков — {total} блоков</title>
<style>
  * {{ box-sizing: border-box; margin: 0; padding: 0; }}
  body {{ font-family: system-ui, sans-serif; background: #f0f0f0; color: #111; }}

  .gallery-header {{ background: #111; color: #fff; padding: 20px 28px; }}
  .gallery-header h1 {{ font-size: 1.4rem; font-weight: 700; margin-bottom: 4px; }}
  .gallery-stats {{ font-size: 13px; color: #aaa; }}

  .filter-bar {{ display: flex; gap: 16px; flex-wrap: wrap; padding: 16px 24px; background: #fff; border-bottom: 1px solid #e0e0e0; position: sticky; top: 0; z-index: 10; align-items: center; }}
  .filter-label {{ font-size: 13px; font-weight: 600; color: #555; }}
  .filter-group {{ display: flex; gap: 8px; align-items: center; }}
  .filter-group.hidden {{ display: none; }}
  select.filter-combo {{ padding: 8px 12px; border: 1.5px solid #ccc; border-radius: 6px; font-size: 13px; cursor: pointer; background: #fff; color: #111; }}
  select.filter-combo:hover {{ border-color: #888; }}
  select.filter-combo:focus {{ outline: none; border-color: #111; }}

  .gallery-grid {{ display: grid; grid-template-columns: repeat(auto-fill, minmax(300px, 1fr)); gap: 20px; padding: 24px; }}

  .gallery-card {{ display: flex; flex-direction: column; background: #fff; border-radius: 10px; overflow: hidden; box-shadow: 0 2px 8px rgba(0,0,0,.08); transition: transform .2s, box-shadow .2s; }}
  .gallery-card:hover {{ transform: translateY(-3px); box-shadow: 0 8px 24px rgba(0,0,0,.12); }}
  .gallery-card.hidden {{ display: none; }}

  .card-thumb {{ width: 100%; height: 200px; overflow: hidden; background: #e8e8e8; position: relative; }}
  .thumb-scaler {{ position: absolute; top: 0; left: 0; width: 100%; height: 100%; overflow: hidden; }}
  .thumb-scaler iframe {{
    width: 1280px;
    height: 800px;
    border: none;
    transform: scale(0.234375);
    transform-origin: top left;
    pointer-events: none;
  }}

  .card-info {{ padding: 12px 14px; flex: 1; display: flex; flex-direction: column; gap: 6px; }}
  .card-name {{ font-size: 14px; font-weight: 600; line-height: 1.3; }}
  .card-meta {{ display: flex; gap: 6px; align-items: center; flex-wrap: wrap; }}
  .card-cat {{ font-size: 11px; font-weight: 600; padding: 2px 8px; border-radius: 10px; background: #111; color: #fff; }}
  .card-variant {{ font-size: 11px; font-weight: 600; padding: 2px 8px; border-radius: 10px; background: #eef2ff; color: #4338ca; }}
  .card-layout-pattern {{ font-size: 10px; color: #777; font-family: monospace; background: #f0f0f0; padding: 1px 7px; border-radius: 6px; }}
  .card-id {{ font-size: 10px; color: #999; font-family: monospace; margin-top: 2px; }}
  .card-open-btn {{ display: block; text-align: center; padding: 10px; background: #f5f5f5; color: #333; text-decoration: none; font-size: 13px; font-weight: 500; border-top: 1px solid #eee; transition: background .15s; }}
  .card-open-btn:hover {{ background: #111; color: #fff; }}

  .filter-stats {{ font-size: 12px; color: #888; margin-left: auto; }}
</style>
</head>
<body>

<header class="gallery-header">
  <h1>📚 Галерея блоков — {total} блоков</h1>
  <div class="gallery-stats">{_html.escape(stats)}</div>
</header>

<div class="filter-bar">
  <div class="filter-group">
    <label class="filter-label">Категория:</label>
    <select class="filter-combo" id="category-filter">
      <option value="">Все категории ({total})</option>
"""

    # Category options (level 1) — Russian labels, taxonomy order.
    for cat in categories:
        count = len(blocks_by_cat[cat])
        label = _html.escape(tax.category_label(cat))
        html += f'      <option value="{cat}">{label} ({count})</option>\n'

    html += """    </select>
  </div>
  <div class="filter-group hidden" id="variant-group">
    <label class="filter-label">Подкатегория:</label>
    <select class="filter-combo" id="variant-filter">
      <option value="">Все подкатегории</option>
    </select>
  </div>
  <span class="filter-stats">Показано: <span id="block-count">0</span> блоков</span>
</div>

<div class="gallery-grid" id="gallery">
"""

    # Block cards
    for block in blocks:
        block_id = block.get("id", "")
        category = block.get("category", "")
        variant = block.get("variant") or ""
        layout_pattern = block.get("layout_pattern", "default")
        display_name = block.get("display_name_ru", block_id)
        path = block.get("path", "")

        block_dir = library_dir / path
        srcdoc = extract_srcdoc(block_id, block_dir)
        if not srcdoc:
            srcdoc = f"<p>{_html.escape(str(display_name))}</p>"

        cat_label = _html.escape(tax.category_label(category)) if tax.valid_category(category) else _html.escape(category)
        variant_badge = ""
        if variant and tax.valid_variant(category, variant):
            variant_badge = f'<span class="card-variant">{_html.escape(tax.variant_label(category, variant))}</span>'

        html += f"""  <article class="gallery-card" data-category="{category}" data-variant="{variant}" data-layout="{layout_pattern}" data-id="{block_id}">
    <div class="card-thumb">
      <div class="thumb-scaler">
        <iframe sandbox srcdoc="{srcdoc}"></iframe>
      </div>
    </div>
    <div class="card-info">
      <div class="card-name">{_html.escape(str(display_name))}</div>
      <div class="card-meta">
        <span class="card-cat">{cat_label}</span>
        {variant_badge}
        <span class="card-layout-pattern">{layout_pattern}</span>
      </div>
      <div class="card-id">{block_id}</div>
    </div>
    <a href="#" class="card-open-btn" onclick="return false;">Просмотр</a>
  </article>
"""

    html += """  </div>

<script>
  const CAT_VARIANTS = """ + cat_variants_json + """;
  const CAT_LABELS = """ + cat_labels_json + """;
  const galleryGrid = document.getElementById('gallery');
  const categoryFilter = document.getElementById('category-filter');
  const variantGroup = document.getElementById('variant-group');
  const variantFilter = document.getElementById('variant-filter');
  const blockCount = document.getElementById('block-count');

  // When category changes, repopulate the variant (подкатегория) combobox.
  // Hide it entirely for categories without level-3 variants.
  function populateVariantFilter() {
    const selectedCat = categoryFilter.value;
    variantFilter.innerHTML = '<option value="">Все подкатегории</option>';

    const variants = (selectedCat && CAT_VARIANTS[selectedCat]) || null;
    if (!variants) {
      variantGroup.classList.add('hidden');
      variantFilter.value = '';
      return;
    }

    variantGroup.classList.remove('hidden');
    Object.keys(variants).forEach(vslug => {
      const opt = document.createElement('option');
      opt.value = vslug;
      opt.textContent = variants[vslug].label + ' (' + variants[vslug].count + ')';
      variantFilter.appendChild(opt);
    });
  }

  function updateGallery() {
    const selectedCat = categoryFilter.value;
    const selectedVariant = variantFilter.value;
    let visibleCount = 0;

    const cards = galleryGrid.querySelectorAll('.gallery-card');
    cards.forEach(card => {
      const catMatch = !selectedCat || card.dataset.category === selectedCat;
      const variantMatch = !selectedVariant || card.dataset.variant === selectedVariant;
      const isVisible = catMatch && variantMatch;

      if (isVisible) {
        card.classList.remove('hidden');
        visibleCount++;
      } else {
        card.classList.add('hidden');
      }
    });

    blockCount.textContent = visibleCount;
  }

  categoryFilter.addEventListener('change', () => {
    populateVariantFilter();
    updateGallery();
  });
  variantFilter.addEventListener('change', updateGallery);

  // Initial state
  blockCount.textContent = '""" + str(total) + """';
</script>
</body>
</html>
"""

    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text(html, encoding="utf-8")
    print(f"✅ Generated gallery with {total} blocks → {output_path}")


if __name__ == "__main__":
    main()
