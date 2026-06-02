#!/usr/bin/env python3
"""Generate block-library gallery.html from catalog.yaml with combobox filters.

This script reads catalog.yaml and generates an interactive HTML gallery
with two-level filtering: Category (dropdown 1) → Subcategory/Type (dropdown 2).

Usage:
  python scripts/generate-gallery.py --library block-library --output block-library/gallery.html
"""
import argparse
import sys
from collections import defaultdict
from pathlib import Path

import yaml


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

    # Load catalog
    cat_path = library_dir / "catalog.yaml"
    if not cat_path.exists():
        print(f"ERROR: {cat_path} not found", file=sys.stderr)
        sys.exit(1)

    catalog = yaml.safe_load(cat_path.read_text(encoding="utf-8"))
    blocks = catalog.get("blocks", [])

    # Group blocks by category
    blocks_by_cat = defaultdict(list)
    for block in blocks:
        cat = block.get("category", "unknown")
        blocks_by_cat[cat].append(block)

    # Sort categories alphabetically
    categories = sorted(blocks_by_cat.keys())

    # Build stats for header
    total = len(blocks)
    stats = ", ".join(f"{cat.title()}: {len(blocks_by_cat[cat])}" for cat in categories)

    # Start HTML
    html = f"""<!DOCTYPE html>
<html lang="ru">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>Block Library Gallery — {total} блоков</title>
<style>
  * {{ box-sizing: border-box; margin: 0; padding: 0; }}
  body {{ font-family: system-ui, sans-serif; background: #f0f0f0; color: #111; }}

  .gallery-header {{ background: #111; color: #fff; padding: 20px 28px; }}
  .gallery-header h1 {{ font-size: 1.4rem; font-weight: 700; margin-bottom: 4px; }}
  .gallery-stats {{ font-size: 13px; color: #aaa; }}

  .filter-bar {{ display: flex; gap: 16px; flex-wrap: wrap; padding: 16px 24px; background: #fff; border-bottom: 1px solid #e0e0e0; position: sticky; top: 0; z-index: 10; align-items: center; }}
  .filter-label {{ font-size: 13px; font-weight: 600; color: #555; }}
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
  .card-cat {{ font-size: 11px; font-weight: 600; padding: 2px 8px; border-radius: 10px; background: #f0f0f0; color: #555; text-transform: uppercase; letter-spacing: .04em; }}
  .card-id {{ font-size: 10px; color: #999; font-family: monospace; margin-top: 2px; }}
  .card-open-btn {{ display: block; text-align: center; padding: 10px; background: #f5f5f5; color: #333; text-decoration: none; font-size: 13px; font-weight: 500; border-top: 1px solid #eee; transition: background .15s; }}
  .card-open-btn:hover {{ background: #111; color: #fff; }}

  .filter-stats {{ font-size: 12px; color: #888; margin-left: auto; }}
</style>
</head>
<body>

<header class="gallery-header">
  <h1>📚 Block Library Gallery — {total} блоков</h1>
  <div class="gallery-stats">{stats}</div>
</header>

<div class="filter-bar">
  <label class="filter-label">Категория:</label>
  <select class="filter-combo" id="category-filter">
    <option value="">Все ({total})</option>
"""

    # Add category options
    for cat in categories:
        count = len(blocks_by_cat[cat])
        html += f'    <option value="{cat}">{cat.title()} ({count})</option>\n'

    html += """  </select>
  <span class="filter-stats" id="filter-stats">Всего: <span id="block-count">0</span> блоков</span>
</div>

<div class="gallery-grid" id="gallery">
"""

    # Add block cards
    for block in blocks:
        block_id = block.get("id", "")
        category = block.get("category", "")
        display_name = block.get("display_name_ru", block_id)
        path = block.get("path", "")

        block_dir = library_dir / path
        srcdoc = extract_srcdoc(block_id, block_dir)

        if not srcdoc:
            srcdoc = f"<p>{display_name}</p>"

        html += f"""  <article class="gallery-card" data-category="{category}" data-id="{block_id}">
    <div class="card-thumb">
      <div class="thumb-scaler">
        <iframe sandbox srcdoc="{srcdoc}"></iframe>
      </div>
    </div>
    <div class="card-info">
      <div class="card-name">{display_name}</div>
      <div class="card-meta">
        <span class="card-cat">{category.upper()}</span>
      </div>
      <div class="card-id">{block_id}</div>
    </div>
    <a href="#" class="card-open-btn" onclick="return false;">Просмотр</a>
  </article>
"""

    html += """  </div>

<script>
  const galleryGrid = document.getElementById('gallery');
  const categoryFilter = document.getElementById('category-filter');
  const blockCount = document.getElementById('block-count');

  function updateGallery() {
    const selectedCat = categoryFilter.value;
    let visibleCount = 0;

    const cards = galleryGrid.querySelectorAll('.gallery-card');
    cards.forEach(card => {
      const cardCat = card.dataset.category;
      const isVisible = !selectedCat || cardCat === selectedCat;

      if (isVisible) {
        card.classList.remove('hidden');
        visibleCount++;
      } else {
        card.classList.add('hidden');
      }
    });

    blockCount.textContent = visibleCount;
  }

  categoryFilter.addEventListener('change', updateGallery);

  // Initial count
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
