# marquee-3d-perspective — Source & Attribution

## What it is
Бегущая строка с 3D-перспективой — как на Awwwards-сайтах. CSS `perspective` + `rotateX` создаёт иллюзию глубины, CSS `@keyframes` + `translateX` прокручивает список. JS дублирует список один раз для seamless loop.

## Inspiration
- Awwwards sites (agency homepages)
- OpenDesign `open-design-landing.html` marquee pattern
- Existing `marquee-fade` pattern in this library (this is the 3D upgrade)

## Difference from existing `marquee-fade`
| Feature | `marquee-fade` | `marquee-3d-perspective` |
|---|---|---|
| Direction | horizontal | horizontal + 3D tilt |
| Perspective | none | CSS `perspective: 800px` |
| Fade edges | yes | yes |
| Hover pause | no | yes |
| Viewport pause | no | yes (IntersectionObserver) |

## WP integration
1. Enqueue `snippet.css` and `snippet.js` (deferred).
2. Use the HTML structure from `snippet.html`.
3. Control speed via `data-speed="25"` (seconds for one full loop).

## Accessibility
- `prefers-reduced-motion`: animation disabled, static wrapped list shown.
- `perspective` transform removed in reduced-motion mode.
- Content is readable text (not decorative-only).

## Performance
- CSS animation is GPU composited (`transform: translateX`).
- Animation paused when scrolled out of viewport (IntersectionObserver).
- Hover pause for readability.
