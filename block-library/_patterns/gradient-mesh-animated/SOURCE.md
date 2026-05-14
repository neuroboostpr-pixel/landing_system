# gradient-mesh-animated — Source & Attribution

## What it is
Cinematic animated gradient mesh: 3-4 coloured blobs drift slowly with CSS `@keyframes`. Zero JS, pure CSS. More advanced than the existing `ambient-mesh-bg` pattern — uses an oversized `::before` pseudo-element so blobs can drift without revealing edges.

## Inspiration
- Apple hero backgrounds (macOS Sonoma, Vision Pro)
- Linear.app gradient section
- OpenDesign `kami-landing` warm palette approach

## Applicability
- Any section needing depth without a photo
- Hero sections on dark or light backgrounds
- `editorial-warm`, `coral-soft`, `monochrome-precision` moods

## WP integration
1. Enqueue `snippet.css` in `wp_enqueue_scripts`.
2. Add class `gma-bg` to any block wrapper in the Gutenberg editor.
3. Set section background colour to the base colour (the blobs are additive on top).

## Accessibility
- `prefers-reduced-motion: reduce` → animation disabled, static gradient.
- Content sits above via `isolation: isolate` + `z-index:1` on children.

## Performance
- Single `filter: blur()` on a pseudo-element (GPU composited).
- `will-change: transform` — only on the pseudo, not the parent.
- No JS, no external resources.
