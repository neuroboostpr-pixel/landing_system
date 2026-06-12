---
name: style-decomposition
description: Extract palette, fonts, and icons from reference images and URLs. Owned by style-extractor agent. Produces palette.yaml, fonts.yaml, icons.yaml, grid.md, motion.md.
---

# style-decomposition

## Pre-flight

```bash
python -m scripts.wiki.log --type skill_call --skill style-decomposition --stage 04
```

## What I do

- Extract dominant color palette from reference images (colorthief + Pillow).
- Identify fonts from reference URLs via DOM CSS inspection (Playwright).
- Match semantic icon names to Iconify icon library.
- Download recommended fonts as WOFF2 for offline use.
- Orchestrate all the above into 5 structured outputs in `04_БРЕНД/extracted/`.

## Scripts

- [scripts/extract-palette.py](scripts/extract-palette.py) — color extraction from images
- [scripts/identify-fonts.py](scripts/identify-fonts.py) — font detection from URLs
- [scripts/match-icons.py](scripts/match-icons.py) — icon matching via Iconify
- [scripts/download-fonts.py](scripts/download-fonts.py) — WOFF2 font caching
- [scripts/orchestrate.py](scripts/orchestrate.py) — main entry point tying all above
