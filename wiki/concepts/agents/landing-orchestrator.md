---
type: agent
name: landing-orchestrator
sources: ["agents/landing-orchestrator.md"]
updated: 2026-05-26
triggers: []
stage: ""
uses:
  - landing-go
  - landing-build
  - landing-deploy
  - landing-prototype
  - landing-wireframe
  - landing-compose
  - landing-photos
  - landing-visuals
  - stage-execution-protocol
  - gate-check
  - render-pipeline-map
  - niche-analyst
  - brand-architect
  - design-system-generator
  - content-writer
  - wp-builder
  - wp-deployer
  - qa-auditor
tags: [orchestrator, pipeline, workflow, core]
---

# Landing Orchestrator (Главный дирижёр)

## Что делает

Ведёт проект-лендинг через все 12 этапов производства — от брифа до SEO — и не даёт перепрыгнуть ни один шаг без явного утверждения пользователя. Диспатчит специализированных агентов на каждый этап и проверяет качество перед переходом дальше.

## Когда вызывать / в каком этапе

Активируется через команду `/landing-go` (основной вход) или `/landing-build`, `/landing-deploy` и другие этапные команды. Работает поверх любого проекта с `.landing-state.yaml`. В **prototype-first режиме** (PR-D) вход — файл `prototype.pdf` в `07_ПРОТОТИП/source/`, этапы 00–02 помечаются `n/a`.

## Что на вход / на выход

**Вход:**
- `.landing-state.yaml` — текущее состояние проекта
- `config/stage-gates.yaml` — правила переходов между этапами
- Пользовательский контент (прототип, фото, бриф)

**Выход:**
- Последовательно: `brief.md`, `niche-analysis.md`, `moodboard.html`, `brand-kit.md`, `DESIGN.md`, `final-copy.md`, `composed.html`, WordPress-тема, задеплоенный сайт, `qa-report.md`
- Обновлённый `.landing-state.yaml` с `approved`-статусами этапов
- Mermaid-карта пайплайна (`wiki/pipeline-map.md`)

**Обязательный протокол перед каждым действием (4 шага):**
1. Прочитать state, показать Mermaid-карту через `render-pipeline-map.sh`
2. Создать TodoWrite со всеми оставшимися этапами
3. Запустить `gate-check.sh` + загрузить чек-лист этапа
4. Verify-скрипт → approve → переход к следующему

**HARD GATE:** этап N+1 не начинается без явного «утверждаю» / «ok» от пользователя. Не выполняется автоматически даже при просьбе «пропусти».

**Параллельная диспетчеризация:** после approve этапа 07c запускает `photo-curator` и `visual-curator` одновременно; ждёт оба результата перед переходом к 07f.

## Связанные концепты

- [[landing-go]] — единственная точка входа в оркестратор (PR-D)
- [[stage-execution-protocol]] — обязательный протокол 4 шагов для каждого этапа
- [[gate-check]] — скрипт проверки гейтов и approve этапов
- [[render-pipeline-map]] — визуализация состояния пайплайна
- [[landing-wireframe]] — интерактивный этап выбора вариантов блоков (07b)
- [[landing-compose]] — сборка composed.html (07c / 07f)
- [[wp-builder]] — агент генерации WordPress-темы (этап 08)
- [[landing-photos]] — пайплайн фото клиента (07d)
- [[landing-visuals]] — генерация иконок и инфографики (07e)

## Источник

- `agents/landing-orchestrator.md`