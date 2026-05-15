# cursor-aura — Source & Attribution

## What it is
A radial-gradient light spot that follows the cursor position using CSS custom properties (`--aura-x`, `--aura-y`) updated by a minimal JS listener. The technique is widely used on premium SaaS sites (Vercel, Raycast, Linear) to add depth and interactivity to dark sections.

## Inspiration
- Vercel.com hero section
- Raycast.com product page
- Linear.app dark sections

## Applicability
- Dark hero sections
- Feature cards on dark background
- Any mood — most effective on dark surfaces

## WP integration
1. Enqueue `snippet.css` and `snippet.js` (deferred).
2. Add class `cursor-aura` to any block wrapper.
3. Child blocks get `z-index: 1` automatically via CSS.

## Accessibility
- Touch devices (`hover: none`): aura hidden, zero JS overhead.
- `prefers-reduced-motion`: aura hidden entirely.

## Performance
- Single `mousemove` listener on `document` (not per-element).
- Uses CSS `background` property not `background-image` — no layout cost.
- `will-change: background` — composited by GPU.
