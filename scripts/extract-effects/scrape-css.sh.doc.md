---
type: script
name: scrape-css
language: bash
sources: ["scripts/extract-effects/scrape-css.sh"]
updated: 2026-05-18
---

# scrape-css.sh

scripts/extract-effects/scrape-css.sh — скачивает HTML+CSS живого сайта.

Usage: scrape-css.sh <url> <out-dir>
Создаёт в <out-dir>:
page.html        — исходный HTML
inline.css       — все inline <style>...</style>
link-N.css       — каждый внешний stylesheet

## Источник

- `scripts/extract-effects/scrape-css.sh`
