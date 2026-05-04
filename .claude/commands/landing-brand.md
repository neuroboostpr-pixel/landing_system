---
description: Build the brand kit for a landing project (stage 04). Run within a landing project folder after style extraction is complete.
allowed-tools: Bash, Read, Write, Edit, Glob
---

# /landing-brand

Run within a landing project after `style-extractor` has produced `04_БРЕНД/extracted/*.yaml`.

## What I do

1. Invoke `brand-architect` agent.
2. Synthesize `04_БРЕНД/brand-kit.md` from all extracted style data with full provenance.
3. Render `04_БРЕНД/brand-kit.html` visual preview.
4. **HARD GATE**: show the preview path, wait for user approval before proceeding to stage 05.

## Usage

Run: `/landing-brand`

Requires `04_БРЕНД/extracted/*.yaml` files produced by `style-extractor` (run after `/landing-moodboard` is approved).

## Output

- `04_БРЕНД/brand-kit.md` — canonical brand kit with provenance
- `04_БРЕНД/brand-kit.html` — visual preview (palette swatches, font specimens, icon thumbnails)
