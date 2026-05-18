---
type: stage
name: pr-f5-lint-query-preview
sources: ["docs/superpowers/plans/2026-05-15-wiki-graph-pr-f5-plan.md"]
updated: 2026-05-18
triggers: []
stage: "PR-F.5"
uses: ["sdk-client", "utils", "config", "pr-f4-hooks-memory", "landing-orchestrator"]
tags: ["wiki", "lint", "query", "preview", "cli", "python"]
---

# PR-F.5 — Lint + Query + Preview для wiki

## Что делает
Финальная часть wiki-подсистемы: три самостоятельных CLI-инструмента для проверки здоровья wiki (`lint.py`), поиска по wiki из терминала (`query.py`) и визуального просмотра всех концептов в браузере (`preview.py`). Также добавляет документацию об Obsidian как опциональном фронтенде.

## Когда вызывать / в каком этапе
Реализуется после PR-F.4 (хуки + memory). Инструменты запускаются вручную разработчиком или в CI:
- `lint.py` — при каждом коммите или ревью wiki
- `query.py` — когда нужно быстро найти информацию в wiki из терминала
- `preview.py` — для визуальной проверки состояния wiki в браузере

## Что на вход / на выход

**Вход:**
- `wiki/` — папка с концептами (`.md` файлы в `concepts/`)
- `wiki/index.md` — главный индекс wiki
- Опционально: `memory/daily/*.md` — дневные логи сессий
- Вопрос пользователя (для `query.py`)

**Выход:**
- `scripts/wiki/lint.py` — 7 структурных проверок (битые ссылки, сироты, устаревшие концепты, пустые концепты, непроверенные обратные ссылки; плюс LLM-проверка противоречий по флагу `--llm-check`)
- `scripts/wiki/query.py` — index-guided retrieval без RAG; флаг `--file-back` сохраняет ответ в `memory/qa/`
- `scripts/wiki/preview.py` + `templates/preview.html.j2` + `templates/styles.css` — генерирует `wiki/preview.html` со списком концептов, CSS-поиском и группировкой по типу
- `scripts/wiki/prompts/query.md` — системный промпт для query
- Тесты: `tests/wiki/test_lint.py`, `test_query.py`, `test_preview.py`
- Обновлённые `scripts/wiki/README.md` и `docs/SETUP.md` (секция Obsidian)

## Связанные концепты
- [[pr-f4-hooks-memory]] — предыдущий PR, на базе которого строится PR-F.5
- [[sdk-client]] — используется `lint.py` (LLM-проверка) и `query.py` (retrieval)
- [[utils]] — `parse_frontmatter`, `atomic_write`, `slugify` нужны во всех трёх инструментах
- [[config]] — `WIKI_DIR` используется в `query.py` для пути к системной wiki
- [[landing-orchestrator]] — фигурирует в тестах как образцовый концепт для проверок

## Источник
- `docs/superpowers/plans/2026-05-15-wiki-graph-pr-f5-plan.md`