---
type: unknown
name: compile-py
sources: ["scripts/wiki/compile.py"]
updated: 2026-05-18
triggers: []
stage: ""
uses: ["landing-orchestrator", "stage-gates", "wiki", "memory"]
tags: ["wiki", "cli", "python", "build-tool"]
---

# compile.py — Wiki-компилятор системы

## Что делает
Собирает wiki-страницы из исходников системы (агентов, скиллов, команд, шаблонов, правил) и записывает их в соответствующие папки `wiki/`. Запускается вручную или автоматически через git-хук после каждого коммита.

## Когда вызывать / в каком этапе
Не привязан к конкретному этапу проекта. Вызывается:
- Автоматически через `.githooks/post-commit` при изменении источников (агенты, скиллы, команды и т.д.).
- Вручную при рассинхроне wiki: `python3 -m scripts.wiki.compile --source-mode=system`.
- Через `scripts/check-wiki-sync.sh` — диагностика синхронности.

## Что на вход / на выход

**Вход:**
- Флаг `--source-mode` (обязателен): `system`, `project-graph` или `conversations`.
- Флаг `--project=<slug>` (обязателен для `project-graph` и `conversations`).
- Исходники: `agents/*.md`, `skills/*/SKILL.md`, `commands/*.md`, `template/*/README.md`, `docs/standards/*.md`, `block-library/**/meta.yaml` и другие.

**Выход:**
- `system` → `landing-system/wiki/` — глобальная wiki всей системы.
- `project-graph` → `<project>/wiki/` — wiki артефактов конкретного проекта.
- `conversations` → `<project>/wiki/` — wiki ежедневных логов сессий.

**Оптимизация:** хэш-кэш пропускает неизменённые файлы (~0 сек при повторном прогоне без изменений).

## Связанные концепты
- [[wiki]] — правило обязательной синхронности wiki с каждым коммитом
- [[memory]] — папка проекта, где хранятся артефакты и wiki
- [[landing-orchestrator]] — основной агент-оркестратор, чьи исходники попадают в wiki
- [[stage-gates]] — конфиг, включённый в источники wiki

## Источник
- `scripts/wiki/compile.py`