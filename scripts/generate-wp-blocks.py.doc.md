---
type: script
name: generate-wp-blocks
language: python
sources: ["scripts/generate-wp-blocks.py"]
updated: 2026-05-18
---

# generate-wp-blocks.py

Orchestrate stage-08 generators in dependency order.

Pipeline (полный 11-шаговый flow, описан в .claude/commands/landing-build.md):

  CORE LAZY BLOCKS PIPELINE (Steps 1-5):
  1. generate-theme.py            — wp-theme scaffold (style.css, functions.php, blocks/ dir, main.css)
  2. generate-lzb-templates.py    — theme/blocks/lazyblock-<slug>/block.php per block
  3. generate-lzb-registration.py — lzb/init add_block() block in functions.php
  4. generate-css-patches.py      — display:contents rules in assets/css/main.css
  5. generate-page-content.py     — Gutenberg block markup → 08_КОД/page-content.html

  ASSETS, JS, AND PREVIEW (Steps 6-8):
  6. bundle-assets.py             — копирует обработанные фото из 07c_PHOTOS/, скачивает иконки
  7. generate-js-init.py          — main.js / sliders.js / animations.js / counters.js (zero-config JS)
  8. generate-popup.py            — модальное окно (JS + CSS + PHP overlay)

  INTEGRATIONS, ANALYTICS, PREVIEW (Steps 9-11):
  9. generate-analytics.py        — Yandex Metrika + GTM в functions.php (читает 00_БРИФ/brief.md)
  10. generate-integrations.py    — Fluent Forms webhook (AmoCRM / Bitrix24 / Telegram)
  11. render-build-preview.py     — статичный 08_КОД/build-preview.html для approve (HARD GATE)

Steps 1-5 читают 08_КОД/block-spec.yaml, который должен существовать до запуска.
Steps 6-11 читают артефакты предыдущих этапов проекта (фото, бриф, brand-kit).

Usage:
    python scripts/generate-wp-blocks.py --project <path>
    python scripts/generate-wp-blocks.py --project <path> --dry-run
    python scripts/generate-wp-blocks.py --project <path> --skip <step1,step2>
    python scripts/generate-wp-blocks.py --project <path> --only <step>

## Источник

- `scripts/generate-wp-blocks.py`
