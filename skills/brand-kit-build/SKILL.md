---
name: brand-kit-build
description: Use during stage 04 to synthesize brand-kit.md from extracted style data and render brand-kit.html preview. Owned by brand-architect agent.
---

# brand-kit-build

## What I do

- Read all `04_БРЕНД/extracted/*.yaml` files.
- Synthesize `brand-kit.md` with full provenance (every token traces to its source image/URL).
- Render `brand-kit.html` preview showing palette swatches, font specimens, icon thumbnails.

## Scripts

- [scripts/build.py](scripts/build.py) — synthesize brand-kit.md
- [scripts/render-html.py](scripts/render-html.py) — render brand-kit.html
