# icon-prompt — codex image_gen for icon slots

## How to use

1. Render placeholders via prompt-picker.py (which uses tokens.json + niche).
2. Pass to `codex-generate-icon.sh` (clones `generate-atlas.sh` snapshot pattern).
3. Chroma-key remove afterwards.
4. Output → `07d_VISUALS/icons/<slot_name>.png`.

## Placeholders

- `[VISUAL_STYLE]` — `tokens.json:design.visual_style`
- `[BRAND_ACCENT]` — `tokens.json:colors.accent` (icon primary color)
- `[ICON_STYLE]` — `tokens.json:design.icon_style` (outlined / filled / duotone / 3d). Default: outlined.
- `[NICHE]` — `01a_АНАЛИЗ_НИШИ/market-profile.md:niche`
- `[SLOT_HINT]` — hint from meta.yaml or slot.name parsed
- `[CHROMA_KEY]` — `#00ff00` default; `#ff00ff` if accent is green

## Prompt body

```
Use the built-in image_gen tool. Generate ONE PNG, 1024x1024, on flat solid [CHROMA_KEY]
background, for: [SLOT_HINT].

VISUAL STYLE: [VISUAL_STYLE], [ICON_STYLE] icon
COLOR: [BRAND_ACCENT] primary, monochrome on [CHROMA_KEY] background
NICHE CONTEXT: [NICHE]

FORBIDDEN (from open-design DESIGN.md):
- No lens flare, no glitch, no chromatic aberration
- No AI watermarks (no "AI", "Midjourney", "DALL-E" signatures)
- No text, no numbers, no letters on the icon
- No photoreal human faces or recognizable people
- No surreal melting or flowing artifacts
- No cartoon/anime style unless brand_mood demands

Single clean shape, centered, occupying ~70% of the canvas, on a perfectly flat
[CHROMA_KEY] background for clean chroma-key removal.
```

## Filled example

When [SLOT_HINT]=shield, [VISUAL_STYLE]=Minimalism & Swiss Style, [BRAND_ACCENT]=#1e3a8a,
[ICON_STYLE]=outlined, [NICHE]=услуги, [CHROMA_KEY]=#00ff00:

```
Use the built-in image_gen tool. Generate ONE PNG, 1024x1024, on flat solid #00ff00
background, for: shield.

VISUAL STYLE: Minimalism & Swiss Style, outlined icon
COLOR: #1e3a8a primary, monochrome on #00ff00 background
NICHE CONTEXT: услуги

FORBIDDEN (from open-design DESIGN.md):
- No lens flare, no glitch, no chromatic aberration
- No AI watermarks (no "AI", "Midjourney", "DALL-E" signatures)
- No text, no numbers, no letters on the icon
- No photoreal human faces or recognizable people
- No surreal melting or flowing artifacts
- No cartoon/anime style unless brand_mood demands

Single clean shape, centered, occupying ~70% of the canvas, on a perfectly flat
#00ff00 background for clean chroma-key removal.
```
