---
name: client-assets-collection
description: Use during stage 02 to scaffold client materials folder, parse external reviews, and build the assets gallery preview. Owned by client-assets-collector agent.
---

# client-assets-collection

## What I do

- Initialize `02_МАТЕРИАЛЫ_КЛИЕНТА/` subfolders if not present.
- Run `parse-reviews.py` to scrape Я.Карты / 2GIS / Otzovik using free local
  Playwright + trafilatura (no API keys).
- Run `collect.py` to build manifest + HTML gallery.

## Scripts

- [scripts/collect.py](scripts/collect.py)
- [scripts/parse-reviews.py](scripts/parse-reviews.py)
