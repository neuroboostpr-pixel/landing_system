---
type: script
name: extract-patterns
language: python
sources: ["scripts/extract-effects/extract-patterns.py"]
updated: 2026-05-18
---

# extract-patterns.py

Анализирует CSS и извлекает премиум-эффекты.

Что ищем:
- @keyframes (анимации)
- transition: ... (плавные переходы)
- :hover state styles (hover-эффекты)
- @media (prefers-reduced-motion: ...) (правильный motion)
- backdrop-filter / filter (стекло/блюр)
- transform: translate3d / scale / rotate
- clip-path, mask-image
- ::before/::after декоративные элементы
- grid с auto-fit/auto-fill
- container queries
- @scroll-timeline / scroll-driven animations

Usage:
    extract-patterns.py <scraped-dir> [<scraped-dir> ...]

Печатает JSON в stdout: {pattern_name: [match_strings...]}

## Источник

- `scripts/extract-effects/extract-patterns.py`
