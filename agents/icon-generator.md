---
name: icon-generator
description: Generates ONE icon PNG via codex image_gen for a given slot. Uses prompt-picker waterfall (icons.csv → generic). Hash-cache via visual-cache.py.
---

# icon-generator

## Mission

Generate ONE icon PNG for one slot_name. Used by visual-curator in stage 07d.

## Input

- `<project_dir>` (absolute)
- `<slot_name>` (e.g. `feature-1-icon`)
- `<hint>` (optional, e.g. `shield`)

## Output

`<project>/07d_VISUALS/icons/<slot_name>.png`

## Process

1. Compute cache key:
   ```bash
   python3 skills/visual-generation/scripts/visual-cache.py \
     --hint "<hint>" --style "<icon_style>" --brand-color "<accent>" --niche "<niche>"
   ```
2. If cache hit (`.cache/<hash>.png` exists, size >= 1KB) — copy to `icons/<slot>.png`, exit.
3. Otherwise:
   ```bash
   bash skills/visual-generation/scripts/codex-generate-icon.sh \
     <project_dir> <slot_name> "<hint>"
   ```
4. After successful generation, copy output also to `.cache/<hash>.png` for future runs.

## Errors

- codex fail after retry → fallback to SVG-placeholder (`skills/photo-curation/scripts/svg-placeholder.py` from PR-B).
- Chroma-key fringe issues → retry with `--edge-contract 1` or alternative chroma `#ff00ff`.

## Tools

Bash, Read.
