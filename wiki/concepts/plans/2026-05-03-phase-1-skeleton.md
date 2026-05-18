---
type: stage
name: phase-1-skeleton
sources: ["docs/superpowers/plans/2026-05-03-phase-1-skeleton.md"]
updated: 2026-05-18
triggers: []
stage: "phase-1"
uses:
  - landing-project-init
  - landing-from-context
  - landing-orchestrator
  - landing-new
  - landing-status
  - landing-help
tags: ["infrastructure", "skeleton", "phase-1", "tdd", "bash"]
---

# Phase 1 — Skeleton & Infrastructure

## Что делает

Строит каркас мастер-системы `landing-system/` с нуля: создаёт шаблон проекта-лендинга (13 папок 00–12), два bash-скилла (`init.sh` и `from-context.sh`), агент-заглушку `landing-orchestrator` и четыре slash-команды (`/landing-new`, `/landing-from-context`, `/landing-help`, `/landing-status`). Покрывает весь каркас bats-тестами — 7 тест-файлов, все зелёные.

## Когда вызывать / в каком этапе

Это план первой фазы реализации мастер-системы, выполняется однократно на чистом репозитории. Запускается вручную разработчиком/субагентом через `superpowers:executing-plans` или `superpowers:subagent-driven-development`. Активируется до создания первого проекта-лендинга — без Phase 1 команды `/landing-new` и `/landing-from-context` не работают.

## Что на вход / на выход

**Вход:**
- Репозиторий `landing-system/` с существующим `.gitignore`
- Установлен bats-core, git, node ≥20, bash ≥5
- Спецификация `docs/superpowers/specs/2026-05-03-landing-system-design.md` (разделы 4, 6, 10, 17, 18)

**Выход (22 задачи, 5 блоков A–E):**

| Блок | Артефакт |
|---|---|
| A. Foundation | `scripts/check-deps.sh`, `tests/helpers/test_helpers.bash`, `CLAUDE.md`, `.env.local.example`, `package.json` |
| B. Template | `template/` — 13 папок + `CLAUDE.md`, `README.md`, `.env.example`, `.gitignore` |
| C. Skills & Agents | `skills/landing-project-init/`, `skills/landing-from-context/`, `agents/landing-orchestrator.md` |
| D. Commands | `.claude/commands/landing-new.md`, `landing-from-context.md`, `landing-help.md`, `landing-status.md` |
| E. Integration | `.claude/settings.json`, `tests/phase-1/test-integration.bats` |

Финальный тег `phase-1-complete` в git.

## Связанные концепты

- [[landing-project-init]] — скилл с `init.sh`, копирует `template/` в новую папку проекта, инициализирует git
- [[landing-from-context]] — скилл с `from-context.sh`, наследует контекст родительского проекта агентства
- [[landing-orchestrator]] — агент-заглушка этапов 00–01 (полная функциональность в Phase 2)
- [[landing-new]] — slash-команда, вызывает `landing-project-init` + передаёт управление оркестратору
- [[landing-status]] — slash-команда, определяет текущий этап проекта по наличию файлов в папках
- [[landing-help]] — slash-команда, выводит справку по всем командам системы

## Источник

- `docs/superpowers/plans/2026-05-03-phase-1-skeleton.md`