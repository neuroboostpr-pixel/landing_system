---
type: script
name: project-graph-compiler
sources: ["scripts/wiki/project_graph_compiler.py", "scripts/wiki/project_graph_compiler.py.doc.md"]
updated: 2026-05-18
triggers: []
stage: ""
uses: ["wiki", "stage-gates", "landing-orchestrator"]
tags: ["wiki", "compiler", "python", "project-graph"]
---

# project_graph_compiler.py — компилятор wiki проекта

## Что делает

Читает артефакты конкретного проекта-лендинга (yaml, json, html) и генерирует набор wiki-страниц в папку `<project>/wiki/`. Работает полностью детерминированно — без обращения к AI SDK.

## Когда вызывать / в каком этапе

Запускается командой `python -m scripts.wiki.compile --source-mode=project-graph` (или через post-commit хук при изменении файлов проекта). Входит в тройку режимов wiki-компилятора наряду с `system` и `conversations`. Автоматически вызывается `.githooks/post-commit`, если коммит затрагивает артефакты проекта.

## Что на вход / на выход

**Вход:**
- Артефакты проекта в `~/Lendings/<slug>/` — `.landing-state.yaml`, `tokens.json`, `prototype.yaml`, `brand-kit.md`, `DESIGN.md`, `composed.html` и другие файлы этапов 00–12.

**Выход:**
- Markdown-страницы в `<project>/wiki/` — по одной на каждый значимый артефакт.
- `<project>/wiki/index.md` — сводный индекс проекта, генерируется как детерминированный stub (без SDK).

**Важная деталь:** прежде SDK вызывался для генерации `index.md`, но выдавал мусор и путал имя проекта. Заменён на детерминированный парсинг: компилятор сам извлекает название проекта из `.landing-state.yaml` или имени папки.

## Связанные концепты

- [[wiki]] — правило: wiki проекта должна быть синхронна с исходниками в каждом коммите
- [[stage-gates]] — файл `.landing-state.yaml` (один из главных источников для компилятора)
- [[landing-orchestrator]] — ведёт проект через 12 этапов; его артефакты и становятся входом компилятора

## Источник

- `scripts/wiki/project_graph_compiler.py`