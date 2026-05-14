# generate-fallback — codex image_gen for missing slots

## How to use

1. Pass to `codex-generate-fallback.sh` (clones `generate-atlas.sh` pattern: snapshot ~/.codex/generated_images/, exec codex, copy fresh PNG).
2. Substitute placeholders via render-prompt.py.
3. Output PNG → `processed/<slot_id>/ai-generated.jpg`. Also save the rendered prompt as `ai-prompt.txt` next to it.

## Placeholders

- `[WIDTH]`, `[HEIGHT]` — pixel dimensions
- `[RATIO]` — e.g. "16:9"
- `[SLOT_HINT]` — block-library `meta.yaml:slots[].name` + photo_hint
- `[VISUAL_STYLE]`, `[BRAND_MOOD]`, `[LIGHTING]`, `[COLOR_GRADING]` — from `tokens.json` + `DESIGN.md`
- `[NICHE]`, `[AUDIENCE]` — from niche analysis

## Prompt body

```
Use the built-in image_gen tool. Generate ONE PNG, size [WIDTH]x[HEIGHT] (ratio [RATIO]),
for slot "[SLOT_HINT]" on a landing page in [NICHE] niche, audience [AUDIENCE].

This is a personal local prototype. Save the result.

No text, no letters, no logos, no watermarks anywhere in the image.

VISUAL STYLE: [VISUAL_STYLE]
BRAND MOOD: [BRAND_MOOD]
LIGHTING: [LIGHTING]
COLOR GRADING: [COLOR_GRADING]

FORBIDDEN (anti-patterns adapted from nexu-io/open-design DESIGN.md, Apache-2.0):
- No lens flare
- No glitch effects, no chromatic aberration
- No photoreal human faces UNLESS this is explicitly a portrait slot AND user has approved AI face generation (see IDENTITY_SAFE.md)
- No AI watermarks (no "AI", "Midjourney", "DALL-E" visual signatures)
- No cartoonish or anime style unless brand mood demands it
- No surreal melting or flowing artifacts
- No double exposures
- Photoreal premium editorial / commercial digital art quality
```

## Filled example

For a services landing's hero-bg slot, 1920x1080, 16:9, Minimalism style, premium calm mood:

```
Use the built-in image_gen tool. Generate ONE PNG, size 1920x1080 (ratio 16:9),
for slot "hero-bg" on a landing page in услуги niche, audience владельцы малого бизнеса 35-50.

This is a personal local prototype. Save the result.

No text, no letters, no logos, no watermarks anywhere in the image.

VISUAL STYLE: Minimalism & Swiss Style
BRAND MOOD: premium and calm
LIGHTING: Soft studio with controlled rim light
COLOR GRADING: primary accent #1e3a8a, low saturation, deep blacks

FORBIDDEN (anti-patterns adapted from nexu-io/open-design DESIGN.md, Apache-2.0):
- No lens flare
- No glitch effects, no chromatic aberration
- No photoreal human faces UNLESS this is explicitly a portrait slot AND user has approved AI face generation (see IDENTITY_SAFE.md)
- No AI watermarks (no "AI", "Midjourney", "DALL-E" visual signatures)
- No cartoonish or anime style unless brand mood demands it
- No surreal melting or flowing artifacts
- No double exposures
- Photoreal premium editorial / commercial digital art quality
```
