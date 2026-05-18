---
type: rule
name: landing-system-master-plan
sources: ["docs/superpowers/plans/2026-05-03-landing-system-master-plan.md"]
updated: 2026-05-18
triggers: []
stage: ""
uses:
  - landing-orchestrator
  - client-assets-collector
  - photo-stylist
  - references-curator
  - moodboard-composer
  - style-extractor
  - brand-architect
  - design-system-generator
  - scene-director
  - stack-planner
  - content-writer
  - wp-builder
  - integrations-engineer
  - analytics-engineer
  - seo-optimizer
  - wp-deployer
  - qa-auditor
  - lifecycle-keeper
  - landing-project-init
  - wp-gutenberg-block-builder
  - wp-theme-assembler
  - landing-versioning-and-cloning
  - wp-cli-deployer
tags: ["architecture", "phases", "mvp", "implementation"]
---

# Landing System — Мастер-план реализации

## Что делает

Описывает шестифазовый план построения агентской системы для производства WordPress-лендингов. Каждая фаза — самостоятельный рабочий продукт с измеримыми критериями приёмки. Фазы строго последовательны: каждая зависит от предыдущей.

## Когда вызывать / в каком этапе

Это архитектурный документ-ориентир, а не команда. Используется при планировании новых PR'ов, ревью системы и понимании общей структуры проекта. Актуален для любого, кто хочет понять, откуда берётся каждый агент, скилл или команда системы.

## Что на вход / на выход

**На вход:**
- Спецификация [`docs/superpowers/specs/2026-05-03-landing-system-design.md`](../specs/2026-05-03-landing-system-design.md)

**На выход (по фазам):**

| # | Фаза | Статус |
|---|---|---|
| 1 | Skeleton & Infrastructure | ✅ Готово |
| 2 | Brainstorming Pipeline (00–04) | ✅ Готово |
| 3 | Design Pipeline (05–07) | ✅ Готово |
| 4 | WP Build Pipeline (08) | ✅ Готово |
| 5 | Deploy & Operations (09–12) | ✅ Готово |
| 6 | Packaging & Pilot | ⚪ Не начато |

**Итого:** ~128 задач × 6 фаз ≈ 30–40 часов реализации MVP.

## Глобальные правила реализации

- **TDD строго** — каждая задача начинается с failing test (bats / vitest / pytest).
- **YAGNI** — ничего «на будущее», только то, что есть в spec.
- **Frequent commits** — один commit = одна логическая единица, Conventional Commits.
- **DRY** — общая логика — в модули, конфигурация — через `.env`.
- **File-per-responsibility** — один файл = одна ответственность; файлы >300 строк дробить.
- **Code review** — после каждой задачи двухступенчатое ревью: spec compliance + code quality.

## Связанные концепты

- [[landing-orchestrator]] — главный агент, запускает конвейер фаз
- [[client-assets-collector]] — Phase 2: сбор материалов клиента
- [[brand-architect]] — Phase 2: синтез brand-kit.md
- [[design-system-generator]] — Phase 3: DESIGN.md + tokens.json
- [[wp-builder]] — Phase 4: WordPress-тема и Gutenberg-блоки
- [[wp-deployer]] — Phase 5: деплой на Бегет
- [[qa-auditor]] — Phase 5: QA 7 пунктов
- [[lifecycle-keeper]] — Phase 5: версии, откат, A/B-клоны
- [[landing-project-init]] — Phase 1: создание папки проекта

## Источник

- `docs/superpowers/plans/2026-05-03-landing-system-master-plan.md`