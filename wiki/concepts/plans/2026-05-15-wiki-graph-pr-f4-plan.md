---
type: rule
name: wiki-pr-f4-hooks-conversation-memory
sources: ["docs/superpowers/plans/2026-05-15-wiki-graph-pr-f4-plan.md"]
updated: 2026-05-18
triggers: []
stage: ""
uses:
  - wiki
  - memory
  - landing-project-init
tags: [wiki, hooks, sessions, memory, conversations, flush, pr-f4]
---

# PR-F.4 — Хуки и память сессий

## Что делает

Подключает три автоматических хука Claude Code (`SessionStart`, `SessionEnd`, `PreCompact`), которые при каждой сессии инжектируют wiki-индексы в контекст агента и сохраняют уроки сессии в `memory/daily/`. В итоге агент при старте «знает» всё, что было в предыдущих сессиях.

## Когда вызывать / в каком этапе

Это план реализации инфраструктурного слоя wiki. Применяется автоматически после установки хуков в `.claude/settings.json`. Не зависит от конкретного этапа лендинг-проекта.

## Что на вход / на выход

**Вход:**
- `landing-system/.claude/settings.json` и `template/.claude/settings.json` (добавляются хуки)
- Транскрипт сессии (JSON Lines, передаётся Claude Code автоматически через `stdin`)
- `wiki/index.md` системы и/или проекта

**Выход:**
- `scripts/wiki/hooks/session_start.py` — читает `wiki/index.md` и `memory/daily/` последнего дня, печатает в stdout (инжектируется в системный контекст Claude)
- `scripts/wiki/hooks/session_end.py` + `pre_compact.py` — запускают `flush.py` в фоне (detached)
- `scripts/wiki/flush.py` — через SDK извлекает уроки из транскрипта и дописывает в `memory/daily/YYYY-MM-DD.md`
- `scripts/wiki/conversations_compiler.py` — группирует daily-буллеты в концепт-статьи `memory/compiled/concepts/*.md`
- Ветка `--source-mode=conversations` в `compile.py`

**Промпты:**
- `scripts/wiki/prompts/flush.md` — инструкция SDK для извлечения уроков
- `scripts/wiki/prompts/conversations_concept.md` — инструкция SDK для группировки в концепты

## Архитектурные решения

- `SessionStart` — **синхронный**, лёгкий (<1 сек), без сетевых вызовов
- `SessionEnd` / `PreCompact` — запускают `flush.py` **detached** (`start_new_session=True`), не блокируют
- Хуки всегда возвращают exit 0 и глотают `json.JSONDecodeError` — не ломают запуск Claude Code
- `${LANDING_SYSTEM_DIR}` в команде хука (с фоллбеком на `.`)
- Параллельные запуски `flush.py` безопасны

## Тест-покрытие

- `tests/wiki/test_hooks.py` — 5 smoke-тестов (пустой stdin, невалидный JSON, инжект индекса)
- `tests/wiki/test_flush.py` — 4 теста с моком SDK
- `tests/wiki/test_conversations_compiler.py` — 3 теста с моком SDK

## Связанные концепты

- [[wiki]] — системный wiki-индекс, который инжектируется SessionStart
- [[memory]] — папка `memory/` проекта, куда пишет flush.py

## Источник

- `docs/superpowers/plans/2026-05-15-wiki-graph-pr-f4-plan.md`