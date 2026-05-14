# infographic-prompt — codex image_gen for infographic slots

## How to use

1. Render placeholders via prompt-picker.py.
2. If OpenDesign template matched — use it (with substituted brand vars).
3. Pass to `codex-generate-infographic.sh`.
4. Chroma-key remove afterwards.
5. Output → `07d_VISUALS/infographics/<slot_name>.png`.

## Placeholders

- `[VISUAL_STYLE]`, `[BRAND_ACCENT]`, `[NICHE]`, `[CHROMA_KEY]` — same as icon-prompt.md
- `[CHART_TYPE]` — `meta.yaml:slots[].chart_type` (number, bar, line, donut)
- `[CHART_DATA]` — JSON-stringified slots[].data (numbers + labels)

## Prompt body

```
Use the built-in image_gen tool. Generate ONE PNG, 1024x1024, on flat solid [CHROMA_KEY]
background, for a [CHART_TYPE] infographic.

DATA: [CHART_DATA]
VISUAL STYLE: [VISUAL_STYLE]
COLOR: [BRAND_ACCENT] primary, monochrome accents allowed
NICHE CONTEXT: [NICHE]

For "[CHART_TYPE]":
- "number" — large number with unit/label, ornamental frame
- "bar" — simple bar chart, 3-5 bars max
- "line" — single line chart, growth trend
- "donut" — donut chart, 2-4 segments

FORBIDDEN: lens flare, glitch, photoreal faces, surreal artifacts, text labels longer than 30 chars.

Single clean composition centered, ~80% canvas, flat [CHROMA_KEY] background.
```

## Filled example

When [CHART_TYPE]=number, [CHART_DATA]={"value": 1000, "label": "+", "caption": "клиентов"},
[VISUAL_STYLE]=Minimalism, [BRAND_ACCENT]=#c47a3a, [NICHE]=услуги, [CHROMA_KEY]=#00ff00:

```
Use the built-in image_gen tool. Generate ONE PNG, 1024x1024, on flat solid #00ff00
background, for a number infographic.

DATA: {"value": 1000, "label": "+", "caption": "клиентов"}
VISUAL STYLE: Minimalism
COLOR: #c47a3a primary, monochrome accents allowed
NICHE CONTEXT: услуги

For "number":
- "number" — large number with unit/label, ornamental frame

FORBIDDEN: lens flare, glitch, photoreal faces, surreal artifacts, text labels longer than 30 chars.

Single clean composition centered, ~80% canvas, flat #00ff00 background.
```
