---
type: stage
name: wiki-graph-pr-f3-plan
sources: ["docs/superpowers/plans/2026-05-15-wiki-graph-pr-f3-plan.md"]
updated: 2026-05-18
triggers: []
stage: "PR-F.3"
uses: ["landing-orchestrator", "block-composer", "photo-curator", "visual-curator"]
tags: ["wiki", "project-graph", "parsers", "template", "migration"]
---

# PR-F.3 — Граф проекта и интеграция в шаблон

## Что делает
Реализует режим `compile.py --source-mode=project-graph --project=<slug>` — компилирует артефакты конкретного лендинга в `~/Lendings/<slug>/wiki/`. Большинство концептов генерируется без SDK (чистая обработка YAML/JSON/HTML), SDK вызывается только для финального индекса `index.md`.

## Когда вызывать / в каком этапе
Запускается как часть разработки системы landing-system (PR-F.3). После выполнения — новые проекты получают `wiki/` и `memory/` автоматически через шаблон; существующие проекты мигрируют через `scripts/migrate-add-wiki.sh`.

## Что на вход / на выход

**Вход:**
- `.landing-state.yaml` — статус этапов проекта
- `07a_WIREFRAME/selections.yaml` — выбранные блоки
- `04_БРЕНД/tokens.json` — дизайн-токены (цвета, шрифты)
- `07b_COMPOSED/composed.html` — скомпонованный HTML

**Выход:**
- `<project>/wiki/index.md` — главный индекс проекта (через SDK)
- `<project>/wiki/concepts/stage-current.md` — текущий этап (без SDK)
- `<project>/wiki/concepts/blocks.md` — выбранные блоки (без SDK)
- `<project>/wiki/concepts/brand.md` — цвета и шрифты (без SDK)
- `<project>/wiki/concepts/photos.md` — карта фото-ссылок (без SDK)
- `<project>/wiki/log.md` — хронология обновлений
- `template/wiki/README.md`, `template/memory/README.md` — заготовки для новых проектов
- `scripts/migrate-add-wiki.sh` — скрипт миграции существующих проектов

## Связанные концепты
- [[landing-orchestrator]] — оркестратор, после gate-check которого wiki будет обновляться автоматически (интеграция запланирована в PR-G)
- [[block-composer]] — генерирует `composed.html`, который парсит `parsers/composed_html.py`
- [[photo-curator]] — работает с `selections.yaml` для фото-слотов, результат отражается в `photos.md`
- [[visual-curator]] — наполняет `composed.html` иконками/инфографикой, также попадают в граф
- [[stage-gates]] — gate-check.sh планируется как триггер авто-пересборки wiki после PR-G

## Источник
- `docs/superpowers/plans/2026-05-15-wiki-graph-pr-f3-plan.md`