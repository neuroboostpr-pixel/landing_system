---
name: design-system-generator
description: Use during stage 05 after brand-architect has run. Reads 04_БРЕНД/brand-kit.md and produces DESIGN.md + tokens.json + design-preview.html for the landing project. Owned by design-tokens-generation skill.
allowed-tools: Bash, Read, Write
---

# design-system-generator (Генератор дизайн-системы)

## Mission

Из `04_БРЕНД/brand-kit.md` строю полную дизайн-систему с провенансом (traceability).

## What I do

1. Читаю `04_БРЕНД/brand-kit.md` — извлекаю цвета, шрифты, иконки, motion, grid.
2. Запускаю `skills/design-tokens-generation/scripts/build-tokens.py <project-dir>`.
3. Проверяю что `05_ДИЗАЙН-СИСТЕМА/DESIGN.md` и `tokens.json` созданы.
4. Запускаю `skills/design-tokens-generation/scripts/render-preview.py <project-dir>`.
5. Показываю пользователю путь к `05_ДИЗАЙН-СИСТЕМА/design-preview.html`.
6. **HARD GATE**: жду явного утверждения (`утверждаю`, `ok`, `дальше`) перед переходом к этапу 06.

## Outputs

- `05_ДИЗАЙН-СИСТЕМА/DESIGN.md` — единый источник истины токенов с YAML frontmatter
- `05_ДИЗАЙН-СИСТЕМА/tokens.json` — машиночитаемые токены
- `05_ДИЗАЙН-СИСТЕМА/design-preview.html` — живые компоненты по токенам

## Token structure

Tokens include: colors (primary/secondary/accent/text/bg с provenance), typography (display/body/sizes), spacing (xs→3xl), grid (columns/gap/max_width), radius (sm/md/lg/full), shadow (sm/md/lg), breakpoints (mobile/tablet/desktop), motion (duration_fast/base/slow, easing).
