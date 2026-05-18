---
type: command
name: migrate-state-add-01a
sources: ["scripts/migrate-state-add-01a.sh"]
updated: 2026-05-18
triggers: ["добавить этап 01a в существующий проект", "мигрировать state для анализа ниши"]
stage: "01a"
uses: ["landing-orchestrator", "niche-analyst", "stage-gates"]
tags: ["migration", "state", "01a", "niche-analysis", "bash"]
---

# migrate-state-add-01a — Миграция .landing-state.yaml: добавить этап 01a

## Что делает

Скрипт добавляет поле `01a_niche_analysis` в файл `.landing-state.yaml` существующего проекта. Если проект уже прошёл этап `02_assets` (помечен как `approved`), этап 01a помечается как `skipped` — для legacy-проектов, созданных до введения анализа ниши. Иначе — как `locked`.

## Когда вызывать / в каком этапе

Запускается **вручную**, разово, при миграции старых проектов на новую версию пайплайна, где появился этап `01a_АНАЛИЗ_НИШИ`. Нужен, если `.landing-state.yaml` не содержит ключа `01a_niche_analysis` и `landing-orchestrator` падает с ошибкой отсутствующего этапа.

Типичный сценарий: проект создан до PR-A/PR-D, теперь нужно его прогнать через `landing-go`, но оркестратор требует 01a.

## Что на вход / на выход

**Вход:**
- Путь к `.landing-state.yaml` существующего проекта (аргумент скрипта).
- Значение поля `02_assets.status` внутри того же файла.

**Выход:**
- Обновлённый `.landing-state.yaml` с новым полем `01a_niche_analysis`:
  - `status: skipped` — если `02_assets` уже `approved` (legacy-проект).
  - `status: locked` — если проект ещё не дошёл до 02_assets.

## Связанные концепты

- [[landing-orchestrator]] — потребляет `.landing-state.yaml`; падает, если 01a отсутствует.
- [[niche-analyst]] — агент, который выполняет этап 01a при нормальном прохождении пайплайна.
- [[stage-gates]] — правила переходов между этапами; 01a — hard gate перед 02.
- [[landing-go]] — единая точка входа, которая и обнаруживает отсутствие 01a у старых проектов.

## Источник

- `scripts/migrate-state-add-01a.sh`