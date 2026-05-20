---
type: rule
name: stage-agent-preamble
sources: ["docs/standards/stage-agent-preamble.md"]
updated: 2026-05-20
triggers: []
stage: ""
uses: ["landing-orchestrator", "stage-execution-protocol", "gate-check"]
tags: ["protocol", "stage-gate", "pipeline", "preamble", "agents"]
---

# Stage Agent Preamble — обязательный преамбул этапных агентов

## Что делает

Canonical-блок (copy-paste), который **все** агенты-владельцы этапа обязаны вставить прямо в начало своего файла. Блок гарантирует, что агент не сделает ни одного Write/Edit до того, как проверит состояние проекта, убедится, что находится на нужном этапе, и получит подтверждение от gate-check.

## Когда вызывать / в каком этапе

Применяется ко **всем** stage-owner агентам (тем, кто владеет конкретным этапом pipeline: `04_brand`, `05_design`, `07c_composed` и т.д.). При копировании блока `<STAGE>` заменяется на реальный ID этапа агента.

Нарушение — агент вызван напрямую (через Task tool или пользователем), минуя `landing-orchestrator`, и тем самым обходит блокировку pipeline.

## Что на вход / на выход

**Вход:**
- `<project>/.landing-state.yaml` — файл состояния проекта
- Скрипты: `render-pipeline-map.sh`, `gate-check.sh`, `gate-state.sh`, опционально `verify-<STAGE>.sh`
- Опциональный `docs/standards/stage-<STAGE>-checklist.md`

**Выход (результат выполнения преамбула):**
- Mermaid-карта pipeline, показанная пользователю
- TodoWrite-список оставшихся этапов
- Подтверждение exit 0 от `gate-check.sh`
- При успешном завершении этапа — вызов `gate-state.sh approve` и закрытие этапа

**Что блокирует:**
- harness hook `scripts/hooks/enforce_stage_gate.py` физически блокирует Write/Edit к файлам этапа, если у него не закрыты предшественники. Обходить нельзя — нужно сначала закрыть предшественника.

## Связанные концепты

- [[landing-orchestrator]] — единственный агент, у которого этот преамбул был изначально; остальные 28+ агентов получили его в рамках аудита
- [[stage-execution-protocol]] — полная спецификация протокола, на которую ссылается преамбул
- [[gate-check]] — скрипт `gate-check.sh`, запускаемый на шаге 4 преамбула

## Источник

- `docs/standards/stage-agent-preamble.md`