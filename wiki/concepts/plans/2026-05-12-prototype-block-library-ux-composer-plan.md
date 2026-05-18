---
type: rule
name: pr-a-prototype-block-library-plan
sources: ["docs/superpowers/plans/2026-05-12-prototype-block-library-ux-composer-plan.md"]
updated: 2026-05-12
triggers: []
stage: "07–07b"
uses:
  - prototype-importer
  - ux-composer
  - block-composer
  - prototype-import
  - block-library-management
  - wireframe-rendering
  - block-composition
  - landing-prototype
  - landing-wireframe
  - landing-compose
  - design-tokens-generation
tags: [pr-a, prototype, wireframe, compose, block-library, plan]
---

# PR-A: Прототип + Block Library + UX-Composer — план реализации

## Что делает

Описывает полный план реализации PR-A: даёт системе явный артефакт «Прототип», создаёт общую библиотеку из 17 RU-блоков и выстраивает трёхэтапный конвейер `/landing-prototype` → `/landing-wireframe` → `/landing-compose` для сборки макета между Design.md и финальным кодом.

## Когда вызывать / в каком этапе

Документ используется как дорожная карта при реализации этапов **07 Прототип**, **07a Wireframe** и **07b Composed**. Не вызывается как команда — это архитектурный план для разработчика или субагента-исполнителя.

## Что на вход / на выход

**Входы системы (после реализации плана):**
- `<project>/07_ПРОТОТИП/source/prototype.pdf` или `prototype.md` — исходник от пользователя
- `block-library/catalog.yaml` — общая библиотека блоков
- `<project>/07a_WIREFRAME/selections.yaml` — выбор пользователя по каждому блоку
- `<project>/05_ДИЗАЙН-СИСТЕМА/tokens.json` — дизайн-токены

**Выходы системы (после реализации плана):**
- `07_ПРОТОТИП/prototype.md` + `prototype.yaml` + `import-log.md`
- `07a_WIREFRAME/wireframe.html` (интерактивный, CSS-only radio) + `candidates.yaml`
- `07b_COMPOSED/composed.html` + `composed-mobile.html` + `block-injection-log.md`

**Создаваемые артефакты кодовой базы:**

| Фаза | Ключевые файлы |
|---|---|
| 0 — Foundation | `template/07_ПРОТОТИП/`, `template/07a_WIREFRAME/`, `template/07b_COMPOSED/`, `block-library/`, `vendor/opendesign-extracts/`, `THIRD_PARTY_NOTICES.md` |
| 1 — Validators | `validate-catalog.py`, `validate-meta.py`, `validate-prototype.py`, `validate-selections.py` |
| 2 — Scaffolder | `scaffold-block.py` |
| 3 — Seed blocks | 17 блоков в `block-library/` (12 базовых + 5 quiz) |
| 4 — Prototype import | `extract-pdf-text.py`, `md-to-yaml.py`, агент `prototype-importer`, команда `/landing-prototype` |
| 5 — Wireframe | `match-candidates.py`, `render-wireframe.py`, `wireframe-shell.html`, агент `ux-composer`, команда `/landing-wireframe` |
| 6 — Compose | `inject-tokens.py`, `inject-content.py`, `compose-blocks.py`, агент `block-composer`, команда `/landing-compose` |
| 7 — DESIGN.md | 9-секционная структура (color / typography / spacing / layout / components / motion / voice / brand / anti-patterns) |

**17 seed-блоков:** `ru-hero-01-services-calc`, `ru-hero-02-b2c-expert`, `ru-hero-03-local-interior`, `ru-features-01-3col-icons`, `ru-features-02-bento-grid`, `ru-testimonials-01-video-circles`, `ru-testimonials-02-text-photo`, `ru-process-01-4steps-icons`, `ru-pricing-01-rub-from`, `ru-trust-01-guarantees-docs`, `ru-cta-01-callback-tg-max`, `ru-faq-01-accordion`, `ru-quiz-01-step-card` — `ru-quiz-05-thankyou`.

**Ограничения:** `/landing-prototype`, `/landing-wireframe`, `/landing-compose` вызываются вручную — интеграция в `landing-orchestrator` и `stage-gates.yaml` относится к PR-D. Quiz-блоки не содержат WhatsApp (запрещён в РФ) — только Telegram + Max + звонок.

## Связанные концепты

- [[prototype-importer]] — агент этапа 07, реализуется в задачах 10–13
- [[ux-composer]] — агент этапа 07a, реализуется в задаче 16
- [[block-composer]] — агент этапа 07b, реализуется в задаче 20
- [[prototype-import]] — скилл с валидаторами и парсерами PDF/MD
- [[block-library-management]] — скилл для scaffold и валидации catalog/meta
- [[wireframe-rendering]] — скилл рендера интерактивного wireframe.html
- [[block-composition]] — скилл финальной сборки composed.html
- [[landing-prototype]] — команда `/landing-prototype`
- [[landing-wireframe]] — команда `/landing-wireframe`
- [[landing-compose]] — команда `/landing-compose`
- [[design-tokens-generation]] — обновляется до 9-секционного DESIGN.md (задача 21)

## Источник

- `docs/superpowers/plans/2026-05-12-prototype-block-library-ux-composer-plan.md`