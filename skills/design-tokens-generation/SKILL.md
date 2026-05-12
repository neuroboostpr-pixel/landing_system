---
name: design-tokens-generation
description: Generates DESIGN.md and tokens.json from brand-kit.md. Used by design-system-generator agent at stage 05.
allowed-tools: Bash, Read, Write
---

# design-tokens-generation

Reads `04_БРЕНД/brand-kit.md` YAML frontmatter and builds a complete design token set.

## Scripts

- `scripts/build-tokens.py <project-dir>` — writes `05_ДИЗАЙН-СИСТЕМА/DESIGN.md` + `tokens.json`
- `scripts/render-preview.py <project-dir>` — writes `05_ДИЗАЙН-СИСТЕМА/design-preview.html`

## Palette library export (post-approve hook)

When stage `05_design_system` is approved (gate-check passes), run:

```bash
python scripts/export-palettes-to-library.py \
    --project "$PROJECT_ROOT" \
    --library "$LANDING_SYSTEM_ROOT/presets/palettes.yaml"
```

This adds new palette ids to the global library. Existing ids are preserved
(skipped with a notice — see `scripts/export-palettes-to-library.py`).

Invariant: do NOT call this script before approval. Black-box behaviour is
"approved palettes are reusable across projects." Drafts must not pollute
the library.

## DESIGN.md output structure (updated 2026-05-12)

DESIGN.md теперь содержит 9 обязательных секций (формат заимствован у OpenDesign Apache-2.0 — см. THIRD_PARTY_NOTICES.md):

1. **## Color** — палитра + roles (bg/fg/accent/error/success), контрастные пары
2. **## Typography** — стек шрифтов (display/body/mono), масштаб (h1-h6, body, small), line-height
3. **## Spacing** — модульная сетка (xs/sm/md/lg/xl), правила отступов
4. **## Layout** — сетка (12 колонок), breakpoints (mobile/tablet/desktop), max-widths
5. **## Components** — стиль кнопок, инпутов, карточек, navbar
6. **## Motion** — duration tokens, easing curves, какие элементы анимируются
7. **## Voice** — тон коммуникации, длина текста, лексика (RU specific)
8. **## Brand** — что выражает бренд через визуал (3-5 ключевых атмосфер)
9. **## Anti-patterns** — чего НЕ делать в этом проекте (явный список)

Цель: глубина и предсказуемость как у Linear/Stripe/Notion (см. `vendor/opendesign-extracts/design-systems-refs/` для референсов — папка будет наполнена позже).
