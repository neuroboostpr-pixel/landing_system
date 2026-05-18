---
type: rule
name: wiki-graph-markup-design
sources: ["docs/superpowers/specs/2026-05-15-wiki-graph-markup-design.md"]
updated: 2026-05-15
triggers: []
stage: ""
uses: ["landing-orchestrator", "landing-go", "landing-start", "stage-gates", "memory", "wiki"]
tags: ["pr-f", "wiki", "memory", "graph", "karpaty"]
---

# Wiki/Граф-разметка системы (PR-F)

## Что делает

Компилирует «память» системы и проектов в markdown-файлы, которые агент читает при старте сессии — вместо того чтобы каждый раз сканировать сотни исходников. По методу Карпати: папка с markdown = скомпилированная долговременная память.

## Когда вызывать / в каком этапе

Не команда, а архитектурное правило. Активируется в трёх сценариях:

1. **При старте сессии** — хук `SessionStart` автоматически инжектит `wiki/index.md` в контекст.
2. **После закрытия этапа** — `landing-orchestrator` вызывает `compile.py --source-mode=project-graph` после успешного `gate-check.sh`.
3. **В конце рабочей сессии** — хук `SessionEnd` вызывает `flush.py`, сохраняя уроки в `memory/daily/`.

## Что на вход / на выход

**Три слоя (независимы, но общие скрипты):**

| Слой | Вход | Выход |
|---|---|---|
| **A. Системный** | `agents/`, `skills/`, `commands/`, `template/`, `docs/standards/` | `landing-system/wiki/` |
| **B1. Память проекта** | Транскрипты сессий | `<project>/memory/compiled/` |
| **B2. Граф проекта** | `.landing-state.yaml`, `prototype.md`, `selections.yaml`, `tokens.json`, `composed.html` | `<project>/wiki/` |

**Скрипты в `scripts/wiki/`:**
- `compile.py --source-mode=system|project-graph|conversations` — основной компилятор
- `query.py "вопрос"` — запрос ко всем трём слоям, синтез ответа
- `lint.py` — проверка здоровья wiki (7 проверок)
- `flush.py` — извлекает уроки из транскрипта в `memory/daily/`

**Артефакты на выход:** `wiki/index.md` (машинная память) + `wiki/preview.html` (HTML-просмотрщик для человека с поиском и граф-визуализацией через d3.js).

**Wiki-статья на каждый концепт** содержит frontmatter: `type`, `name`, `sources`, `updated`, `triggers`, `stage`, `uses`.

## Связанные концепты

- [[landing-orchestrator]] — вызывает `compile.py project-graph` после закрытия каждого этапа
- [[landing-go]] — единая точка входа; оркестратор обновляет граф при каждом шаге
- [[landing-start]] — создаёт пустые `wiki/` и `memory/` в новом проекте
- [[stage-gates]] — wiki решает проблему «агент не помнит где остановился»; PR-G «Stage Lock» усилит гейты на основе `current_stage` из wiki
- [[memory]] — слой B1 (разговоры) живёт в `memory/compiled/`
- [[wiki]] — слой A (системный) живёт в `landing-system/wiki/`

## Источник

- `docs/superpowers/specs/2026-05-15-wiki-graph-markup-design.md`