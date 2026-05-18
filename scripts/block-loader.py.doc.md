---
type: script
name: block-loader
language: python
sources: ["scripts/block-loader.py"]
updated: 2026-05-18
---

# block-loader.py

Универсальный loader для блоков из block-library.

Поддерживает оба формата:
- Старый: assets/template.html + assets/template-mobile.html
- Новый: index.html + styles.css

Использование:
  from scripts.block_loader import load_block
  block = load_block("hero/ru-hero-01-services-calc")
  # → {"html": "...", "css": "...", "mobile_html": "...", "meta": {...}}

## Источник

- `scripts/block-loader.py`
