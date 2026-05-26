---
type: block
name: stage-agent-preamble
sources: ["docs/standards/stage-agent-preamble.md"]
updated: 2026-05-26
triggers: []
stage: ""
uses:
  - stage-execution-protocol
  - landing-orchestrator
tags:
  - stage-gate
  - protocol
  - preamble
  - agents
---

# Stage Agent Preamble — канонический блок предусловий

## Что делает

Стандартный блок Markdown, который обязан быть вставлен в начало каждого агента-владельца этапа (stage-owner). Гарантирует, что агент не начнёт изменять файлы, пока не убедится: состояние проекта корректно, gate пройден, пользователь видит карту pipeline и список задач.

## Когда вызывать / в каком этапе

Не вызывается как команда — это шаблонный текст, который вставляется при создании нового агента. Применяется ко всем агентам-владельцам этапов (например, `brand-architect`, `design-builder`, `content-builder` и т.д.), кроме `landing-orchestrator` — у него собственная расширенная версия, которую не нужно перезаписывать.

## Что на вход / на выход

**Вход:**
- `<project>/.landing-state.yaml` — файл состояния проекта с текущим этапом
- `<STAGE>` — идентификатор этапа агента (например, `04_brand`, `07c_composed`)

**Выход (действия агента в runtime):**
1. Проверка `current_stage` из `.landing-state.yaml` — если не совпадает, агент останавливается
2. Mermaid-карта pipeline, сгенерированная `render-pipeline-map.sh`, показывается пользователю
3. TodoWrite-список оставшихся этапов от текущего до финала
4. Запуск `gate-check.sh` — если exit != 0, агент останавливается до решения проблем
5. Загрузка чеклиста `stage-<STAGE>-checklist.md` (если существует) и создание sub-todos
6. После завершения этапа — запуск `verify-<STAGE>.sh` и простановка `approved` через `gate-state.sh`

**Защитный механизм:**
Хук `scripts/hooks/enforce_stage_gate.py` на уровне harness физически блокирует любые Write/Edit к файлам этапа, у которого не закрыты предшественники. Обходить нельзя — нужно закрыть предшественника.

## Связанные концепты

- [[stage-execution-protocol]] — полная версия протокола, на которую ссылается блок
- [[landing-orchestrator]] — единственный агент, у которого собственная расширенная версия преамбулы (не перезаписывать)

## Источник

- `docs/standards/stage-agent-preamble.md`