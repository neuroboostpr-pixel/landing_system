---
type: script
name: generate-wp-blocks
language: python
sources: ["scripts/generate-wp-blocks.py"]
updated: 2026-05-18
---

# generate-wp-blocks.py

Orchestrate stage-08 generators in dependency order.

Pipeline:
  1. generate-theme.py            — wp-theme scaffold (style.css, functions.php, blocks/ dir, main.css)
  2. generate-lzb-templates.py    — theme/blocks/lazyblock-<slug>/block.php per block
  3. generate-lzb-registration.py — lzb/init add_block() block in functions.php
  4. generate-css-patches.py      — display:contents rules in assets/css/main.css
  5. generate-page-content.py     — Gutenberg block markup → 08_КОД/page-content.html

Step 1 takes the project path as a positional argument; steps 2–5 use --project.
Steps 2–5 each read 08_КОД/block-spec.yaml, which must exist before running this.

Usage:
    python scripts/generate-wp-blocks.py --project <path>
    python scripts/generate-wp-blocks.py --project <path> --dry-run

## Источник

- `scripts/generate-wp-blocks.py`
