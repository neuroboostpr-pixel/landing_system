# sticky-section-reveal — Source & Attribution

## What it is
Section "pinning" — the section sticks to the viewport while inner "states" change as the user scrolls. This is the core technique behind Apple AirPods Pro, Apple Watch, and many Linear/Stripe product pages. Multiple content panels occupy the same visual space and transition sequentially.

## Inspiration
- Apple.com AirPods Pro page (section pinning + state reveal)
- Linear.app product page scroll storytelling
- OpenDesign `gsap-scrolltrigger` skill (ScrollTrigger pin pattern)

## Technical approach
- GSAP `ScrollTrigger.pin` pins the `.ssr-sticky` container
- `onUpdate` callback maps scroll progress to state index
- States use CSS `is-active` / `is-exiting` classes for transitions
- Graceful fallback: IntersectionObserver if GSAP not loaded

## WP integration
1. Enqueue GSAP + ScrollTrigger CDN in theme (or via `wp_enqueue_script`).
2. Enqueue `snippet.css` and `snippet.js`.
3. Structure HTML per `snippet.html` example.

## Accessibility
- `prefers-reduced-motion`: CSS transitions disabled, states still switch.
- All states are accessible text (opacity:0 ≠ `visibility:hidden`).
- Progress dots are visual only (`pointer-events: none`).

## Performance
- GSAP ScrollTrigger is the industry standard for scroll effects.
- Fallback uses IntersectionObserver if GSAP not available.
- Pin is applied only to `.ssr-sticky`, not the whole section.
