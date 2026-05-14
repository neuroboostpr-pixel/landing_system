# magnetic-button — Source & Attribution

## What it is
Кнопка "притягивается" к курсору при наведении — курсор тянет кнопку в свою сторону пока не уходит. Техника используется на Awwwards-уровне сайтах (Stripe, Notion, Superhuman).

## Inspiration
- Stripe.com CTA buttons
- Awwwards-winning agency sites
- Creative Code community (magnetic button is a classic interaction pattern)

## Technical approach
- `mousemove` listener reads cursor position relative to button center
- Displacement (dx, dy) is scaled by `strength` factor (0.1–0.8)
- Updates CSS vars `--mag-tx` and `--mag-ty` → applied via `transform: translate()`
- CSS `transition` handles the spring-back on `mouseleave`
- Single listener per button, minimal memory overhead

## WP integration
1. Enqueue `snippet.css` and `snippet.js` (deferred).
2. Add class `mag-btn` to any `<button>` or `<a>` element.
3. Tune `data-mag-strength` and `data-mag-radius` per design.

## Accessibility
- Touch devices: disabled entirely (no mousemove events).
- `prefers-reduced-motion`: CSS overrides `transform: none !important`.
- Standard hover state preserved for all users.

## Performance
- Vanilla JS, no RAF loop — only fires on actual mousemove events.
- `will-change: transform` — GPU composited.
- Each button has its own listener (no global state).
