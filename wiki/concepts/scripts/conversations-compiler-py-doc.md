---
type: rule
name: conversations-compiler
sources: ["scripts/wiki/conversations_compiler.py.doc.md", "scripts/wiki/conversations_compiler.py"]
updated: 2026-05-18
triggers: ["SessionEnd хук", "python -m scripts.wiki.compile --source-mode=conversations"]
stage: ""
uses: ["wiki", "landing-orchestrator"]
tags: ["wiki", "memory", "compiler", "python", "sessions"]
---

# Conversations Compiler — компилятор диалогов в wiki

## Что делает

Собирает файлы ежедневных сессий из папки `daily/` и компилирует их в концепты памяти проекта по пути `memory/compiled/concepts/`. Позволяет системе «помнить» контекст прошлых разговоров и накапливать знания о проекте между сессиями.

## Когда вызывать / в каком этапе

Запускается автоматически хуком `SessionEnd` — по завершении каждой рабочей сессии Claude Code. Также можно вызвать вручную для конкретного проекта:

```bash
python -m scripts.wiki.compile --source-mode=conversations --project=<slug>
```

Флаг `--source-mode=conversations` отличает этот режим от `--source-mode=system` (пересборки системной wiki) и `--source-mode=project-graph` (графа зависимостей проекта).

## Что на вход / на выход

**Вход:**
- Папка `daily/` внутри проекта — markdown-файлы сессий, сохранённые в хронологическом порядке.

**Выход:**
- Файлы концептов в `memory/compiled/concepts/` — структурированные выжимки из диалогов для дальнейшего использования оркестратором и агентами.

Хэш-кэш пропускает файлы, которые не изменились с последней компиляции — повторный запуск без новых сессий работает практически мгновенно.

## Связанные концепты

- [[wiki]] — папка системной wiki, куда попадают результаты компиляции
- [[landing-orchestrator]] — читает скомпилированную память при диспатче следующего этапа
- [[memory]] — общее правило хранения проектной памяти

## Источник

- `scripts/wiki/conversations_compiler.py.doc.md`
- `scripts/wiki/conversations_compiler.py`