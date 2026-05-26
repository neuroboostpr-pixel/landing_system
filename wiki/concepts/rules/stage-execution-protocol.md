---
type: rule
name: stage-execution-protocol
sources: ["docs/standards/stage-execution-protocol.md"]
updated: 2026-05-26
triggers: []
stage: ""
uses: ["landing-orchestrator", "landing-go", "landing-prototype", "landing-wireframe", "landing-compose", "landing-photos", "landing-visuals", "landing-build", "landing-deploy", "gate-check", "render-pipeline-map", "premium-07b-checklist"]
tags: ["protocol", "orchestrator", "pipeline", "stages", "todo", "gate"]
---

# Stage Execution Protocol — обязательный протокол выполнения этапов

## Что делает

Задаёт четыре обязательных шага, которые любой агент или скилл должен выполнить перед тем, как приступить к работе над этапом лендинг-пайплайна. Гарантирует, что агент не пропускает шаги, не «прыгает» вперёд без gate-check и не объявляет этап завершённым без проверки артефактов.

## Когда вызывать / в каком этапе

Применяется **на каждом** запуске, который инициирует или продолжает любой этап pipeline:
- при вызове `/landing-go` (главная точка входа)
- при прямом вызове команд `/landing-prototype`, `/landing-wireframe`, `/landing-compose`, `/landing-photos`, `/landing-visuals`, `/landing-build`, `/landing-deploy`
- при запуске агента через `landing-orchestrator` для конкретного этапа

Действует с 2026-05-19. Не заменяет HARD GATE'ы и `gate-check.sh`, а добавляет дисциплину *до* их запуска.

## Что на вход / на выход

**Вход:**
- `<project>/.landing-state.yaml` — текущий статус всех этапов и `current_stage`
- `docs/standards/stage-<id>-checklist.md` — чек-лист конкретного этапа (если существует)
- `config/stage-gates.yaml` — описание gate-check правил

**Выход:**
- Mermaid-карта прогресса в чате и в `<project>/wiki/pipeline-map.md`
- TodoWrite со всеми оставшимися этапами (+ под-todo из чек-листа)
- Подтверждённый gate-check (approve) перед переходом к следующему этапу

## Четыре обязательных шага

1. **Прочитать состояние и нарисовать карту** — открыть `.landing-state.yaml`, запустить `render-pipeline-map.sh --write-wiki`, вывести Mermaid-блок пользователю.
2. **Выписать оставшиеся этапы в TodoWrite** — все этапы от `current_stage` до конца, формат: `"Этап <id> — <name>"`.
3. **Подгрузить чек-лист этапа** — если существует `docs/standards/stage-<id>-checklist.md`, создать под-todo для каждого пункта. Закрывать только по факту в артефакте.
4. **Verify → approve → переход** — запустить verify-скрипт (если есть), затем `gate-check.sh --approve`. Только после exit 0 — переходить к следующему этапу.

**Запрещено:** начинать действовать до Шага 1; объявлять этап завершённым без verify; игнорировать чек-лист; закрывать todo без реального артефакта.

## Связанные концепты

- [[landing-orchestrator]] — главный потребитель протокола, диспатчит этапы
- [[landing-go]] — главная команда, с которой начинается протокол
- [[gate-check]] — запускается на Шаге 4 для подтверждения этапа
- [[render-pipeline-map]] — скрипт рендера Mermaid-карты (Шаг 1)
- [[premium-07b-checklist]] — пример этапного чек-листа (эталон паттерна)
- [[landing-wireframe]] — один из этапов, на котором протокол обязателен
- [[landing-compose]] — аналогично, с HARD GATE по `verify-composed-premium.sh`

## Источник

- `docs/standards/stage-execution-protocol.md`