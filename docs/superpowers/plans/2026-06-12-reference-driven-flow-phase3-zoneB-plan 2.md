# Reference-Driven Flow — Phase 3 (Zone B: декор и премиум)

> **For agentic workers:** REQUIRED SUB-SKILL: superpowers:executing-plans.

**Goal:** Зона B спеки: правила генерации декора, премиум чек-лист с verify-гейтом, стандарт логотипов/favicon.

### Task B1+B4: docs/standards/design-elements-rules.md
Перенос раздела 3.4 спеки в обязательный стандарт: принцип «элемент под потребность места», плотность ≤1 акцента на зону, каталог элементов (справочно), алгоритм добавления, дерево решений «откуда брать», правила разделителей (единообразие А/Б), таблица запретов. `_shapes/` — только подсказка-палитра. Ссылки из block-composer.

### Task B2: Премиум чек-лист v2 + verify
- `scripts/verify_composed_premium.py` (новая реализация) + `verify-composed-premium.sh` становится тонкой обёрткой (имя сохраняется — его зовут гейты 07c/07f).
- ОБЯЗАТЕЛЬНО (fail): :root-токены; clamp(); движение (IntersectionObserver/@keyframes/transition); :hover; prefers-reduced-motion; production-голова (og:title+og:image, favicon, theme-color, шрифты); ЗАПРЕТ эмодзи в `<h1>–<h3>`.
- РЕКОМЕНДАЦИИ (warn, не fail): glassmorphism, parallax, slider, lightbox, gradient text, count-up, clip-path — старые «13 фич» перестают быть обязательными (спека §3.2: декор под потребность места, премиум ≠ набор эффектов).
- Tests: `tests/phase-stage-07/test_verify_composed_premium.py` (TDD).
- `docs/standards/premium-07b-checklist.md` — заголовок v2: обязательный список из спеки, старые 13 фич помечены «рекомендации».

### Task B3: docs/standards/logo-icon-favicon.md
Зафиксировать отработанный флоу: логотип = векторизация исходника (vtracer), не генерация; inline SVG + currentColor (не mask-image); оптический размер по площади чернил; favicon из монограммы через headless Chrome.
