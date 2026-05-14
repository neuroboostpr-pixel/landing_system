# text-reveal-mask — Source & Attribution

## What it is
Text "materialises" through a CSS `mask-image` gradient animation — identical to Apple keynote slide reveals and Apple.com product page text animations. Uses IntersectionObserver to trigger when element enters viewport.

## Inspiration
- Apple.com hero text animations (AirPods Pro, iPhone 15 page)
- OpenDesign `html-ppt-zhangzara-monochrome` data-anim system
- Linear.app feature section reveals

## Technical approach
- `mask-image: linear-gradient(...)` animated via `transition` on `.is-revealed` class
- 4 direction variants via `data-reveal-dir` attribute
- 5 stagger delay levels via `data-delay`
- IntersectionObserver triggers `.is-revealed` at 15% viewport intersection
- Unobserves after first reveal (plays once)

## WP integration
1. Enqueue `snippet.css` and `snippet.js` (deferred).
2. Add `data-animate="reveal"` attribute to any text element.
3. Optional: `data-reveal-dir="ltr|rtl|up|down"` and `data-delay="1-5"`.

## Accessibility
- `prefers-reduced-motion`: mask removed instantly, opacity set to 1, no transition.
- Content is always readable (no `visibility:hidden`).

## Browser support
`mask-image` requires `-webkit-mask-image` prefix for Safari. Both are included.
Fallback: `transition: none` and opacity:1 for reduced motion.
