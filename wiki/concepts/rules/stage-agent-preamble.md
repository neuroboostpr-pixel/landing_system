---
type: block
name: stage-agent-preamble
sources: ["docs/standards/stage-agent-preamble.md"]
updated: 2026-05-25
triggers: []
stage: ""
uses: ["landing-orchestrator", "stage-execution-protocol", "landing-state"]
tags: ["protocol", "pipeline", "stage-gate", "agents", "mandatory"]
---

# Stage Agent Preamble — обязательный блок для агентов этапов

## Что делает

Канонический copy-paste блок из 7 шагов, который должен стоять в самом начале каждого агента-владельца этапа. Он гарантирует, что агент не начнёт менять файлы, пока не проверит состояние pipeline, не показал карту прогресса и не убедился, что все предшественники закрыты.

## Когда вызывать / в каком этапе

Вставляется **однократно** при создании нового агента-владельца этапа (например `brand-architect`, `design-system-builder` и т.п.). Подставь `<STAGE>` на реальный ID этапа (например `04_brand`, `07c_composed`). Не применяется к `landing-orchestrator` — у него своя расширенная версия.

## Что на вход / на выход

**Вход:**
- `<project>/.landing-state.yaml` — состояние pipeline
- `docs/standards/stage-<STAGE>-checklist.md` — чеклист этапа (если есть)

**Выход — 7 обязательных действий перед любым Write/Edit:**
1. Проверить `current_stage == <STAGE>` в `.landing-state.yaml`, иначе STOP.
2. Запустить `render-pipeline-map.sh` и показать пользователю Mermaid-карту.
3. Создать TodoWrite со всеми оставшимися этапами до конца pipeline.
4. Запустить `gate-check.sh` для текущего этапа; при exit != 0 — STOP.
5. Если есть чеклист этапа — прочитать и создать sub-todos.
6. Только после exit 0 начинать выполнение.
7. По завершении запустить `verify-<STAGE>.sh` и выставить `approved` через `gate-state.sh`.

**Дополнительная защита:** хук `scripts/hooks/enforce_stage_gate.py` физически блокирует Write/Edit к файлам этапа, если его предшественники не закрыты. Обходить запрещено — нужно сначала закрыть предшественника.

## Зачем это нужно

До введения этого блока только `landing-orchestrator` проверял gate-check. Остальные 28+ агентов-владельцев этапов не делали этого совсем: при прямом вызове через Task tool или пользователем pipeline lock полностью обходился. Этот блок закрывает брешь.

## Связанные концепты

- [[landing-orchestrator]] — имеет собственную расширенную версию преамбулы; не перезаписывать этим блоком
- [[stage-execution-protocol]] — полная спецификация протокола, на которую блок ссылается
- [[landing-state]] — файл `.landing-state.yaml`, который агент читает в шаге 1

## Источник

- `docs/standards/stage-agent-preamble.md`