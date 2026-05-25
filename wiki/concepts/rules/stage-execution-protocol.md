---
type: rule
name: stage-execution-protocol
sources: ["docs/standards/stage-execution-protocol.md"]
updated: 2026-05-25
triggers: []
stage: ""
uses: ["landing-orchestrator", "landing-go", "landing-prototype", "landing-wireframe", "landing-compose", "landing-photos", "landing-visuals", "landing-build", "landing-deploy", "premium-07b-checklist", "gate-check"]
tags: ["protocol", "orchestrator", "pipeline", "discipline", "stage-gates"]
---

# Stage Execution Protocol — Обязательный протокол выполнения этапов

## Что делает
Задаёт жёсткий порядок из 4 шагов, которому обязан следовать любой агент перед тем как что-то делать на этапе pipeline. Гарантирует, что агент всегда видит карту прогресса, выписывает все задачи в TodoWrite и не пропускает проверки.

## Когда вызывать / в каком этапе
Применяется **ко всем этапам** без исключения. Активируется при любом запуске, который инициирует или продолжает этап pipeline:
- `/landing-go` — главная точка входа
- Прямые вызовы `/landing-prototype`, `/landing-wireframe`, `/landing-compose`, `/landing-photos`, `/landing-visuals`, `/landing-build`, `/landing-deploy`
- Любой агент, запущенный оркестратором для конкретного этапа

## Что на вход / на выход

**Вход:**
- `<project>/.landing-state.yaml` — текущий статус всех этапов
- `docs/standards/stage-<id>-checklist.md` — чек-лист этапа (если есть)
- Verify-скрипты (например `scripts/verify-composed-premium.sh`)

**Выход:**
- Mermaid-карта прогресса в чате + `<project>/wiki/pipeline-map.md`
- TodoWrite со всеми оставшимися этапами и под-задачами из чек-листа
- Результат `gate-check.sh --approve` после verify

## Протокол (4 шага в строгом порядке)

1. **Читать состояние и нарисовать карту** — открыть `.landing-state.yaml`, запустить `render-pipeline-map.sh --write-wiki`, вывести Mermaid-блок пользователю.
2. **Выписать все оставшиеся этапы в TodoWrite** — от `current_stage` до конца pipeline, формат `"Этап <id> — <name>"`.
3. **Подгрузить чек-лист текущего этапа** — если существует `docs/standards/stage-<id>-checklist.md`, прочитать и создать под-todo на каждый пункт.
4. **Verify → approve → переход** — запустить verify-скрипт (exit ≠ 0 → доработать), затем `gate-check.sh --approve`, только после этого переходить к следующему этапу.

**Что запрещено:** начинать действия до шага 1; объявлять этап завершённым без verify; игнорировать чек-лист; закрывать todo без реального артефакта.

## Связанные концепты
- [[landing-orchestrator]] — главный агент, обязанный соблюдать этот протокол на каждом шаге
- [[landing-go]] — точка входа, с которой стартует протокол
- [[premium-07b-checklist]] — пример чек-листа для этапа 07b, встраивается в Шаг 3
- [[gate-check]] — скрипт проверки hard/soft gates, используется в Шаге 4

## Источник
- `docs/standards/stage-execution-protocol.md`