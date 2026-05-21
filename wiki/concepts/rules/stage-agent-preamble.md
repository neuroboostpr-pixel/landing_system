---
type: rule
name: stage-agent-preamble
sources: ["docs/standards/stage-agent-preamble.md"]
updated: 2026-05-20
triggers: []
stage: ""
uses: ["landing-orchestrator", "stage-execution-protocol", "gate-check"]
tags: ["pipeline", "stage-gate", "preamble", "protocol", "agents"]
---

# Stage Agent Preamble — обязательный блок для этапных агентов

## Что делает
Канонический copy-paste блок из 7 шагов, который каждый агент-владелец этапа обязан выполнить перед любым Write/Edit действием. Обеспечивает соблюдение Stage Execution Protocol и предотвращает обход pipeline-замков.

## Когда вызывать / в каком этапе
Применяется ко **всем** stage-owner агентам (тем, кто отвечает за конкретный этап пайплайна): `04_brand`, `05_design`, `07c_composed`, `08_kod` и т.д. Блок вставляется сразу после YAML frontmatter и заголовка `# <name>` нового агента. Заменить `<STAGE>` на реальный ID этапа.

**Исключение:** `landing-orchestrator` имеет собственный расширенный вариант преамбулы — этот блок его НЕ заменяет.

## Что на вход / на выход

**Вход:**
- `<project>/.landing-state.yaml` — файл состояния проекта
- Опционально: `docs/standards/stage-<STAGE>-checklist.md`

**Алгоритм (7 шагов):**
1. Прочитать `.landing-state.yaml`, убедиться что `current_stage == <STAGE>`. Иначе — STOP.
2. Запустить `render-pipeline-map.sh` с флагом `--write-wiki`, показать Mermaid-карту.
3. Создать TodoWrite-список со всеми оставшимися этапами.
4. Запустить `gate-check.sh --stage <STAGE> --project <project>`. Если exit ≠ 0 — STOP, решить проблемы.
5. Если есть checklist для этапа — прочитать, добавить sub-todos.
6. Только после exit 0 — выполнять этап.
7. По завершении: запустить `verify-<STAGE>.sh` (если есть) → при PASS утвердить через `gate-state.sh approve`.

**Выход:**
- Гарантия того, что агент работает в правильном контексте и не пропускает predecessors.

## Почему это важно
До введения правила только `landing-orchestrator` содержал gate-check. Остальные 28+ этапных агентов можно было вызвать напрямую (через Task tool или пользователем), полностью обходя pipeline-замки. Теперь `PreToolUse` hook (`scripts/hooks/enforce_stage_gate.py`) физически блокирует Write/Edit к файлам этапа с незакрытыми предшественниками — это штатное поведение, обходить нельзя.

## Связанные концепты
- [[landing-orchestrator]] — имеет собственный расширенный вариант преамбулы, не перезаписывать
- [[stage-execution-protocol]] — полная версия протокола, на которую ссылается преамбула
- [[gate-check]] — скрипт проверки условий перед переходом на этап

## Источник
- `docs/standards/stage-agent-preamble.md`