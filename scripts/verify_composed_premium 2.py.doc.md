---
type: script
name: verify_composed_premium 2
language: python
sources: ["scripts/verify_composed_premium 2.py"]
updated: 2026-05-18
---

# verify_composed_premium 2.py

Premium-проверка composed.html — v2 (B2, спека reference-driven flow §3.2).

ОБЯЗАТЕЛЬНО (fail):
  - CSS-токены в :root
  - clamp() для типографики
  - движение (IntersectionObserver / @keyframes / transition)
  - hover-эффекты
  - prefers-reduced-motion
  - production-голова: og:title + og:image, favicon, theme-color, шрифты
  - ЗАПРЕТ: эмодзи в заголовках <h1>–<h3>

РЕКОМЕНДАЦИИ (warn, не fail): glassmorphism, parallax, slider, lightbox,
gradient text, count-up, clip-path — добавляются под потребность места
(docs/standards/design-elements-rules.md), а не «обязательным набором».

Exit: 0 PASS · 1 FAIL · 2 файл не найден.
Usage: verify_composed_premium.py <composed.html>

## Источник

- `scripts/verify_composed_premium 2.py`
