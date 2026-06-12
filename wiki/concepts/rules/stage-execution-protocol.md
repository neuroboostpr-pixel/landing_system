---
slug: stage-execution-protocol
type: rule
name: "Протокол выполнения этапов (обязательный)"
stage: "all"
tags: [protocol, orchestrator, pipeline, gates, todo]
triggers: [landing-go, landing-build, landing-deploy, landing-compose, landing-wireframe, landing-prototype, landing-photos, landing-visuals]
inputs: [".landing-state.yaml", "config/stage-gates.yaml", "docs/standards/stage-<id>-checklist.md"]
outputs: ["wiki/pipeline-map.md", "TodoWrite tasks"]
gates: [hard_checks, gate-check-approve]
pre_reqs: []
related: [landing-go, landing-orchestrator, landing-build, landing-compose, landing-wireframe, landing-prototype, landing-photos, landing-visuals, landing-deploy]
sources: ["docs/standards/stage-execution-protocol.md"]
updated: 2026-05-26
confidence: {}
---

# Протокол выполнения этапов (обязательный)

## Что делает

Обязательный четырёхшаговый протокол, которому следует любой агент или скилл, приступающий к этапу pipeline. Протокол гарантирует, что агент сначала видит актуальную карту состояния проекта, фиксирует все оставшиеся задачи в TodoWrite, загружает чек-лист текущего этапа и закрывает этап только через verify-скрипт. Основан на принципах из Tencent Agent-Memory paper: Mermaid-карта как единый источник истины + структурированный workflow. Не заменяет HARD GATE'ы и `gate-check.sh`, а добавляет дисциплину *до* их вызова.

## Когда вызывается

Применяется при любом старте или продолжении этапа: через `/landing-go`, через прямые вызовы этапных команд (`/landing-build`, `/landing-compose`, `/landing-wireframe` и т.п.), а также при диспатче агента из `landing-orchestrator`. Действует с 2026-05-19.

## Вход → выход

**Вход:** `.landing-state.yaml` текущего проекта с `current_stage` и статусами всех этапов; опционально — `docs/standards/stage-<id>-checklist.md`.

**Выход:** Mermaid-карта в чате и в `wiki/pipeline-map.md`; список TodoWrite для всех оставшихся этапов; под-todo по чек-листу; артефакт этапа, прошедший verify-скрипт и approve в `gate-check.sh`.

## Чем закрывается этап (gates)

- `hard_checks` — gate-check.sh проходит hard-проверки, иначе этап не открывается
- `gate-check-approve` — агент вызывает `gate-check.sh --approve` только после выполнения всех под-todo и exit 0 verify-скрипта

## Failure modes

- Агент начинает действовать до шага 1 — карта не прочитана, порядок этапов берётся «из памяти», состояние расходится с реальностью.
- TodoWrite не создан — агент «прыгает» через промежуточные шаги, пользователь не видит прогресса.
- `stage-<id>-checklist.md` существует, но не загружен — часть обязательных действий внутри этапа пропускается молча.
- Verify-скрипт вернул ненулевой код, агент объявил этап завершённым — HARD GATE не пройден, но `gate-check.sh --approve` вызван до исправления.
- TodoWrite-пункт закрыт «на словах» без реального артефакта — несоответствие между статусом в трекере и фактическим файлом.

## Related

- [[landing-go]] — главная точка входа; именно он первым применяет протокол
- [[landing-orchestrator]] — диспатчит агентов по этапам; обязан соблюдать протокол
- [[landing-build]] — этап 08, для которого протокол особенно критичен (много под-шагов)
- [[landing-compose]] — этап 07b с HARD GATE и `premium-07b-checklist.md`
- [[landing-wireframe]] — этап 07a, интерактивный; протокол не даёт пропустить confirm