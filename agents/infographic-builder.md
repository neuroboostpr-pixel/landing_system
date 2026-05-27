---
name: infographic-builder
description: Generates ONE infographic PNG via codex image_gen. Uses prompt-picker waterfall (OpenDesign 90 JSON → generic). Hash-cache via visual-cache.py.
---

# infographic-builder

> Helper agent — dispatched by `visual-curator`. Stage Execution Protocol is
> enforced by the parent agent; this helper does not own a stage and should
> not be invoked directly.


## Pre-flight

Перед любым действием — wiki-запрос для маршрутизации:

```bash
python -m scripts.wiki.query --slug=infographic-builder --agent=infographic-builder
python -m scripts.wiki.log --type agent_call --agent infographic-builder --stage 07e
```

## Mission

Generate ONE infographic PNG for one slot_name. Used by visual-curator in stage 07d.

## Input

- `<project_dir>`
- `<slot_name>` (e.g. `kpi-clients`)
- `<chart_type>` (number, bar, line, donut)
- `<data_json>` (JSON-stringified data spec)

## Output

`<project>/07d_VISUALS/infographics/<slot_name>.png`

## Process

1. Compute cache key from (hint, chart_type, brand_accent, niche).
2. If cache hit → copy to `infographics/<slot>.png`, exit.
3. Otherwise:
   ```bash
   bash skills/visual-generation/scripts/codex-generate-infographic.sh \
     <project_dir> <slot_name> <chart_type> '<data_json>'
   ```
4. After successful generation, copy to `.cache/<hash>.png`.
5. Record attribution (if OpenDesign source) in `07d_VISUALS/prompts.yaml`.

## Errors

- codex fail after retry → SVG-placeholder fallback.
- Invalid `data_json` → use generic placeholder data, warn in STATE.yaml.

## Tools

Bash, Read.
