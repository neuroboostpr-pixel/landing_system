---
type: rule
name: pr-g-stage-lock-plan
sources: ["docs/superpowers/plans/2026-05-15-pr-g-stage-lock-plan.md"]
updated: 2026-05-18
triggers: []
stage: ""
uses:
  - stage-gates
  - landing-orchestrator
  - landing-go
tags: ["pr-g", "stage-lock", "auto-wiki", "gate-check", "hooks"]
---

# PR-G — Stage Lock + Auto-Wiki: план реализации

## Что делает
Описывает пошаговую реализацию дисциплины «строго по шагам»: технические этапы блокируются жёсткими lock-ами (hard), итеративные получают мягкое предупреждение (soft), а wiki автоматически обновляется при каждом коммите и закрытии этапа.

## Когда вызывать / в каком этапе
Это план-реализации (Implementation Plan), не команда. Выполняется однократно как часть PR-G в рамках ветки `feat/pr-a-prototype-block-library`. Актуален при установке системы на новой машине (нужен `bash scripts/install-git-hooks.sh`).

## Что на вход / на выход

**Вход:**
- `config/stage-gates.yaml` — существующие проверки этапов
- `scripts/gate-check.sh` — скрипт проверки гейтов
- `agents/landing-orchestrator.md` — промпт оркестратора

**Выход:**
- `config/stage-gates.yaml` — расширен полями `lock: hard/soft` и `require_approved` для всех 21 этапа
- `scripts/gate-check.sh` — добавлен soft-warning блок и auto-update project-graph wiki
- `.githooks/post-commit` — хук, пересобирающий системную wiki при коммитах в `agents/`, `skills/`, `commands/`, `template/`, `docs/standards/`
- `scripts/install-git-hooks.sh` — идемпотентный установщик хуков через `core.hooksPath`
- `agents/landing-orchestrator.md` — обязательный раздел «ОБЯЗАТЕЛЬНЫЕ предусловия» с вызовом `gate-check.sh`
- `tests/pr-g/` — 4 bats-файла: hard-lock, soft-warning, post-commit, auto-update project-graph

**Ключевые правила маппинга lock-типов:**

| Этап | lock | Зависимости |
|---|---|---|
| `07b_wireframe` | hard | `04_brand`, `05_design`, `07a_prototype` |
| `07c_composed` | hard | `05_design`, `07a_prototype`, `07b_wireframe` |
| `08_build` | hard | `07c_composed` |
| `09_deploy` | hard | `08_build`, `10_qa` |
| `10_qa` | hard | `08_build` |
| Все остальные | soft | — |

**Защита от рекурсии в хуке:** post-commit пропускает выполнение, если последний коммит уже `chore(wiki)*`.

## Связанные концепты
- [[stage-gates]] — конфиг и скрипт gate-check.sh, которые расширяются этим планом
- [[landing-orchestrator]] — агент, в промпт которого добавляются обязательные предусловия gate-check
- [[landing-go]] — главная точка входа, использующая gate-check через оркестратор

## Источник
- `docs/superpowers/plans/2026-05-15-pr-g-stage-lock-plan.md`