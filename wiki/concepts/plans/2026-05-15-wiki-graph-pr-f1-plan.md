---
type: rule
name: pr-f1-wiki-infrastructure-plan
sources: ["docs/superpowers/plans/2026-05-15-wiki-graph-pr-f1-plan.md"]
updated: 2026-05-15
triggers: []
stage: ""
uses:
  - scripts-wiki-compile
  - scripts-wiki-config
  - scripts-wiki-utils
  - wiki-graph-markup-design
  - landing-orchestrator
tags: [wiki, infrastructure, plan, pr-f1, python, tdd]
---

# PR-F.1 — Инфраструктура Wiki (фундамент)

## Что делает

Создаёт базовую инфраструктуру Python-модуля `scripts/wiki/` в landing-system: конфигурационный файл с тремя режимами компиляции, утилиты для работы с frontmatter, CLI-скелет на argparse. Логика компиляции на этом шаге не реализуется — только заготовка.

## Когда вызывать / в каком этапе

Это план реализации первого из пяти PR серии PR-F (Wiki Graph). Выполняется разработчиком вручную как отдельная ветка до интеграции wiki-системы в остальные этапы. Следующий этап — PR-F.2 (реализация `--source-mode=system`).

## Что на вход / на выход

**На вход:**
- Репозиторий landing-system без папки `scripts/wiki/`
- Spec: `docs/superpowers/specs/2026-05-15-wiki-graph-markup-design.md`

**На выход (5 задач, TDD-стиль):**
- `scripts/wiki/__init__.py` — делает директорию Python-пакетом
- `scripts/wiki/config.py` — `REPO_ROOT`, `WIKI_DIR`, `SOURCE_MODES` (три режима), `SYSTEM_SOURCES` (6 категорий), `PROJECT_SOURCES` (7 артефактов)
- `scripts/wiki/utils.py` — `slugify` (кириллица → kebab-case), `parse_frontmatter`, `write_with_frontmatter`, `atomic_write`
- `scripts/wiki/compile.py` — CLI: `--source-mode`, `--project`, `--dry-run`; логика заглушена с указанием PR-F.2/F.3/F.4
- `scripts/wiki/README.md` — таблица трёх режимов + roadmap по PR
- `tests/wiki/` — 18+ pytest-тестов (по TDD: сначала fail, потом pass)
- Дополнение `CLAUDE.md` упоминанием `scripts/wiki/`

**Не делает:**
- Не вызывает `claude-agent-sdk` (добавится в PR-F.2)
- Не пишет в `wiki/` (только stub-печать)
- Не трогает `.claude/settings.json` и `template/`

## Связанные концепты

- [[wiki-graph-markup-design]] — spec, определяющий архитектуру трёх режимов
- [[landing-orchestrator]] — оркестратор, который в будущем (PR-F.4) будет триггерить компилятор через хуки
- [[stage-gates]] — система гейтов, с которой wiki синхронизируется в рамках CLAUDE.md-правила

## Источник

- `docs/superpowers/plans/2026-05-15-wiki-graph-pr-f1-plan.md`