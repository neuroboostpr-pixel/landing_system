#!/usr/bin/env python3
"""Универсальный loader для блоков из block-library.

Поддерживает оба формата:
- Старый: assets/template.html + assets/template-mobile.html
- Новый: index.html + styles.css

Использование:
  from scripts.block_loader import load_block
  block = load_block("hero/ru-hero-01-services-calc")
  # → {"html": "...", "css": "...", "mobile_html": "...", "meta": {...}}
"""
from pathlib import Path

LIB = Path(__file__).resolve().parents[1] / "block-library"


def load_block(rel_path):
    """rel_path как 'hero/ru-hero-01-services-calc' или 'hero/hero-cinematic-...'"""
    block_dir = LIB / rel_path
    if not block_dir.is_dir():
        return None

    result = {"path": rel_path, "meta": {}}

    # Meta
    meta_file = block_dir / "meta.yaml"
    if meta_file.exists():
        import yaml
        result["meta"] = yaml.safe_load(meta_file.read_text(encoding="utf-8")) or {}

    # Try old format first
    old_template = block_dir / "assets" / "template.html"
    if old_template.exists():
        result["html"] = old_template.read_text(encoding="utf-8")
        mobile = block_dir / "assets" / "template-mobile.html"
        if mobile.exists():
            result["mobile_html"] = mobile.read_text(encoding="utf-8")
        return result

    # New format
    index = block_dir / "index.html"
    css_file = block_dir / "styles.css"
    if index.exists():
        result["html"] = index.read_text(encoding="utf-8")
        if css_file.exists():
            result["css"] = css_file.read_text(encoding="utf-8")
        return result

    return None


if __name__ == "__main__":
    import sys
    if len(sys.argv) < 2:
        print("Usage: block-loader.py <category>/<block-id>", file=sys.stderr)
        sys.exit(2)
    b = load_block(sys.argv[1])
    if not b:
        print(f"Block not found: {sys.argv[1]}", file=sys.stderr)
        sys.exit(1)
    print(f"Loaded: {b['path']}")
    print(f"  html: {len(b.get('html', ''))} chars")
    print(f"  css: {len(b.get('css', ''))} chars")
    print(f"  mobile_html: {len(b.get('mobile_html', ''))} chars")
    print(f"  meta keys: {list(b.get('meta', {}).keys())}")
