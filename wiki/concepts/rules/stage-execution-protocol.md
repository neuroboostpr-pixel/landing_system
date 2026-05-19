---
type: rule
name: stage-execution-protocol
sources: ["docs/standards/stage-execution-protocol.md"]
updated: 2026-05-19
triggers: []
stage: ""
uses:
  - landing-orchestrator
  - landing-go
  - gate-check
  - premium-07b-checklist
  - render-pipeline-map
  - landing-wireframe
  - landing-compose
  - landing-photos
  - landing-visuals
  - landing-build
  - landing-deploy
tags: ["protocol", "orchestration", "quality", "standards"]
---

# Stage Execution Protocol — обязательный протокол выполнения этапов

## Что делает

Протокол задаёт строгий порядок из 4 шагов, который **любой агент обязан выполнять перед началом и после завершения каждого этапа pipeline**. Цель — не пропускать действия внутри этапа, держать пользователя в курсе прогресса и не допускать «прыжков» между этапами без верификации.

## Когда вызывать / в каком этапе

Применяется ко **всем этапам** pipeline без исключения. Активируется при любом запуске:
- `/landing-go` (главная точка входа)
- Прямых вызовах `/landing-prototype`, `/landing-wireframe`, `/landing-compose`, `/landing-photos`, `/landing-visuals`, `/landing-build`, `/landing-deploy`
- Любым агентом, вызванным `landing-orchestrator` для конкретного этапа

## Что на вход / на выход

**Вход:**
- `<project>/.landing-state.yaml` — текущий статус всех этапов
- `docs/standards/stage-<id>-checklist.md` — чек-лист для конкретного этапа (если существует)
- `config/stage-gates.yaml` — конфигурация hard/soft проверок

**Выход:**
- Mermaid-карта прогресса (в чат + `<project>/wiki/pipeline-map.md`)
- TodoWrite со всеми оставшимися этапами и под-todo из чек-листа
- Approve в `.landing-state.yaml` после прохождения verify-скрипта

## Четыре обязательных шага

**Шаг 1 — Прочитать состояние и нарисовать карту.** Открыть `.landing-state.yaml`, запустить `render-pipeline-map.sh --write-wiki`, вывести Mermaid пользователю. Карта — единый источник истины о прогрессе.

**Шаг 2 — Выписать все оставшиеся этапы в TodoWrite.** Создать список от `current_stage` до конца pipeline (без `n/a`). Формат: `"Этап <id> — <name>"`.

**Шаг 3 — Подгрузить чек-лист текущего этапа.** Если существует `docs/standards/stage-<id>-checklist.md` — прочитать и создать под-todo на каждый пункт. Без чек-листа — выполнять по описанию агента.

**Шаг 4 — Verify → approve → переход.** Запустить verify-скрипт (если есть), затем `gate-check.sh --approve`. Только после approve — закрывать todo и идти дальше. Exit ≠ 0 → доработать, не объявлять успех.

## Что запрещено

Начинать действия до Шага 1; объявлять этап завершённым без verify-скрипта; игнорировать существующий `stage-<id>-checklist.md`; закрывать todo, если действие не отражено в артефакте.

## Связанные концепты

- [[landing-orchestrator]] — главный агент, обязанный соблюдать протокол
- [[landing-go]] — точка входа, с которой начинается Шаг 1
- [[premium-07b-checklist]] — эталонный чек-лист для этапа 07b
- [[gate-check]] — скрипт верификации, используемый в Шаге 4
- [[render-pipeline-map]] — скрипт рендера Mermaid-карты для Шага 1

## Источник

- `docs/standards/stage-execution-protocol.md`