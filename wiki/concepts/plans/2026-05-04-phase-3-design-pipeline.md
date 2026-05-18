---
type: stage
name: phase-3-design-pipeline
sources: ["docs/superpowers/plans/2026-05-04-phase-3-design-pipeline.md"]
updated: 2026-05-18
triggers: []
stage: "05-07"
uses: ["design-system-generator", "scene-director", "stack-planner", "content-writer", "design-tokens-generation", "landing-design", "landing-stack", "landing-content", "landing-orchestrator", "brand-architect"]
tags: ["design", "tokens", "pipeline", "phase-3"]
---

# Phase 3 — Design Pipeline (Этапы 05–07)

## Что делает

Реализует Design Pipeline — цепочку из трёх этапов: генерация дизайн-системы (05), выбор стека плагинов (06), создание финального контента (07). Превращает утверждённый brand-kit в набор токенов, HTML-превью, YAML-стек и готовые тексты для всех блоков лендинга.

## Когда вызывать / в каком этапе

Активируется после утверждения этапа 04 (brand-architect создал `04_БРЕНД/brand-kit.md`). Три команды запускаются последовательно:
1. `/landing-design` → этап 05 (дизайн-система)
2. `/landing-stack` → этап 06 (стек)
3. `/landing-content` → этап 07 (контент)

Каждый следующий этап блокируется HARD GATE — требует явного утверждения пользователя.

## Что на вход / на выход

**Вход:**
- `04_БРЕНД/brand-kit.md` — YAML frontmatter с цветами, шрифтами, иконками (от [[brand-architect]])
- `07_КОНТЕНТ/prototype.md` — исходный прототип текста (для content-writer)
- `02_МАТЕРИАЛЫ_КЛИЕНТА/testimonials/` — реальные отзывы клиентов

**Выход:**

| Файл | Этап | Описание |
|---|---|---|
| `05_ДИЗАЙН-СИСТЕМА/DESIGN.md` | 05 | Единый источник токенов (YAML frontmatter + таблицы) |
| `05_ДИЗАЙН-СИСТЕМА/tokens.json` | 05 | Машиночитаемые токены: colors, typography, spacing, grid, radius, shadow, breakpoints, motion |
| `05_ДИЗАЙН-СИСТЕМА/design-preview.html` | 05 | HTML-превью живых компонентов по токенам |
| `05_ДИЗАЙН-СИСТЕМА/scenes.md` | 05 | Scene grammar (только при флаге `--cinematic`) |
| `06_СТЕК/design-stack.yaml` | 06 | WordPress-плагины, JS-библиотеки, CDN шрифтов, иконки |
| `06_СТЕК/*.md` | 06 | component-library-plan, effects-plan, font-and-color-plan |
| `07_КОНТЕНТ/final-copy.md` | 07 | Финальные тексты расставлены по Gutenberg-блокам |
| `07_КОНТЕНТ/seo-copy.md` | 07 | Title, Description, H1, alt-теги |

**Ключевые скрипты:**
- `skills/design-tokens-generation/scripts/build-tokens.py <project-dir>` — читает brand-kit.md, пишет DESIGN.md + tokens.json
- `skills/design-tokens-generation/scripts/render-preview.py <project-dir>` — рендерит design-preview.html через Jinja2 (`tools/html/templates/design-preview.html.j2`)

**Тесты:** `tests/phase-3/python/` (pytest, 14 тестов), `tests/phase-3/*.bats` + `integration/` (26+ bats-тестов).

## Связанные концепты

- [[design-system-generator]] — агент этапа 05, запускает build-tokens.py и render-preview.py
- [[scene-director]] — агент этапа 05 для cinematic-режима, генерирует scenes.md
- [[stack-planner]] — агент этапа 06, пишет design-stack.yaml
- [[content-writer]] — агент этапа 07, адаптирует прототип по блокам
- [[design-tokens-generation]] — скилл с build-tokens.py и render-preview.py
- [[brand-architect]] — предшествующий агент, поставляет brand-kit.md
- [[landing-design]] — slash-команда для запуска этапа 05
- [[landing-stack]] — slash-команда для запуска этапа 06
- [[landing-content]] — slash-команда для запуска этапа 07
- [[landing-orchestrator]] — расширен Phase 3 scope для диспатча агентов 05→06→07

## Источник

- `docs/superpowers/plans/2026-05-04-phase-3-design-pipeline.md`