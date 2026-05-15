---
type: command
name: landing-go
sources: ["commands/landing-go.md"]
updated: 2026-05-15
triggers:
  - "запустить лендинг с нуля"
  - "поехали по этапам"
  - "продолжить конвейер"
  - "следующий этап проекта"
  - "провести через все этапы"
stage: ""
uses:
  - landing-orchestrator
  - prototype-importer
  - references-curator
  - brand-architect
  - design-system-generator
  - stack-planner
  - content-writer
  - ux-composer
  - block-composer
  - photo-curator
  - visual-curator
  - wp-builder
  - wp-deployer
  - qa-auditor
  - analytics-engineer
  - seo-optimizer
tags: ["orchestrator", "entry-point", "pipeline", "auto-fix"]
---

# /landing-go — Главная команда конвейера

## Что делает

Единая точка входа для всего производства лендинга. Запускаешь один раз — команда сама читает статус проекта, находит следующий этап и ведёт тебя от прототипа до живого сайта на Бегете, не давая пропустить ни один шаг.

## Когда вызывать / в каком этапе

Вызывать после того, как прототип (`prototype.pdf` или `prototype.md`) положен в `<project>/07_ПРОТОТИП/source/`. Подходит и для старта с нуля, и для возобновления застрявшего проекта — команда читает `.landing-state.yaml` и подхватывает с нужного места. Этапы 00–02 (бриф, контекст, ниша, материалы клиента) считаются сделанными до системы и помечаются `n/a` автоматически.

**Синтаксис:**
```
/landing-go [--project <slug>] [--auto-fix yes|no] [--skip-gate <id>]
```

## Что на вход / на выход

**Вход:**
- `<project>/.landing-state.yaml` — текущий статус этапов проекта
- `<project>/07_ПРОТОТИП/source/prototype.pdf` (или `.md`) — исходный прототип
- Опциональные флаги: `--project`, `--auto-fix yes`, `--skip-gate <id>`

**Выход:**
- Последовательный проход через все 13+ этапов конвейера с HTML-превью на каждом gate
- Финальный результат: задеплоенный WordPress-сайт на Бегете + QA + аналитика + SEO
- При падении гейта — `fix_hint` из `config/stage-gates.yaml` и авто-фикс на `yes`

**Особый режим:** на этапах 07d (фото) и 07e (визуалы) оркестратор диспатчит оба субагента **параллельно**, сокращая время сборки.

## Ключевые этапы

| Этап | Режим | Агент |
|---|---|---|
| 07a prototype | авто | `prototype-importer` |
| 03–05 бренд | руками + AI | `brand-architect`, `design-system-generator` |
| 06–07 стек + контент | авто | `stack-planner`, `content-writer` |
| 07b–07c wireframe + compose | маркетолог утверждает | `ux-composer`, `block-composer` |
| **07d ⇆ 07e** фото + визуалы | **параллельно** | `photo-curator` ‖ `visual-curator` |
| 08–12 build → QA → SEO | авто | `wp-builder`, `wp-deployer`, QA, SEO |

Ручные команды `/landing-photos`, `/landing-visuals`, `/landing-prototype`, `/landing-wireframe`, `/landing-compose` продолжают работать независимо.

## Связанные концепты

- [[landing-orchestrator]] — агент, которого вызывает команда для диспетчеризации этапов
- [[prototype-importer]] — первый автоматический шаг: парсит `prototype.pdf` → `prototype.yaml`
- [[photo-curator]] — параллельный этап 07d: классификация и matching клиентских фото
- [[visual-curator]] — параллельный этап 07e: AI-генерация иконок и инфографики
- [[wp-builder]] — этап 08: генерация WordPress-темы из собранных артефактов
- [[landing-start]] — точка входа для новых проектов (wizard перед `/landing-go`)

## Источник

- `commands/landing-go.md`