---
type: rule
name: config-wiki-compiler
sources: ["scripts/wiki/config.py"]
updated: 2026-05-18
triggers: []
stage: ""
uses: ["landing-orchestrator", "block-library-management"]
tags: ["wiki", "config", "compiler", "scripts"]
---

# config.py — конфигурация wiki-компайлера

## Что делает
Задаёт все пути и источники для автоматической сборки wiki системы. Три режима компиляции: по источникам самой landing-system, по артефактам конкретного проекта-лендинга, и по дневным логам сессий.

## Когда вызывать / в каком этапе
Файл не вызывается напрямую — он импортируется скриптом `scripts/wiki/compile.py` при любом запуске компайлера. Косвенно задействуется при каждом `git commit`, если хук `.githooks/post-commit` установлен и затронутые файлы входят в один из источников.

## Что на вход / на выход

**На вход:** ничего — файл содержит только константы.

**На выход** (константы, которые экспортирует):

| Константа | Содержимое |
|---|---|
| `REPO_ROOT` | Абсолютный путь к корню `landing-system/` |
| `WIKI_DIR` | `landing-system/wiki/` — куда пишется wiki |
| `SOURCE_MODES` | `("system", "project-graph", "conversations")` |
| `SYSTEM_SOURCES` | 17 glob-записей: агенты, скиллы, команды, этапы шаблона, стандарты, блоки, паттерны, стили, конфиги, доки, спеки, планы, тесты, пресеты, авто-доки скриптов |
| `PROJECT_SOURCES` | 7 записей для артефактов конкретного лендинга (`prototype.md`, `tokens.json`, `selections.yaml` и др.) |

Режим `conversations` объявлен в `SOURCE_MODES`, но источники для него в этом файле не перечислены — они, видимо, конфигурируются в другом месте.

## Структура SYSTEM_SOURCES

Каждая запись — словарь `{path, concept_dir}`:
- `path` — glob-паттерн относительно `REPO_ROOT`
- `concept_dir` — подпапка в `wiki/`, куда кладётся сгенерированная страница

Охватываемые папки: `agents/`, `skills/`, `commands/`, `template/`, `docs/standards/`, `block-library/`, `config/`, `docs/`, `tests/`, `presets/`, `scripts/`.

## Связанные концепты
- [[wiki]] — папка, куда компайлер пишет результат
- [[block-library-management]] — блоки (`block-library/*/*/meta.yaml`) включены в `SYSTEM_SOURCES`
- [[landing-orchestrator]] — его исходник `agents/landing-orchestrator.md` попадает в `SYSTEM_SOURCES` через `agents/*.md`

## Источник
- `scripts/wiki/config.py`