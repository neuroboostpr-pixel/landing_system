---
name: landing-onboarding
description: First-time setup of landing-system on a new machine. Validates local deps, MCP servers, superpowers plugin, and all API keys.
---

# landing-onboarding

## Pre-flight

```bash
python -m scripts.wiki.log --type skill_call --skill landing-onboarding --stage ""
```

## Mission

Настроить landing-system на новой машине: зависимости, плагины, MCP, API.

## Scripts

- `scripts/wizard.sh` — interactive flow
- `scripts/validate-all.sh` — runs all 15 API validators
- `scripts/setup-flag.sh` — manages `~/.landing-system/setup_complete`

## Used by

- `/landing-onboarding` slash command
- Auto-redirected from any `/landing-*` if setup_complete missing

## What it produces

`~/.landing-system/setup_complete` — flag with ISO timestamp. Other commands check this file before proceeding.

---

## PR-D Onboarding additions (2026-05-13)

С PR-D флоу упрощается: **одна команда `/landing-go` ведёт через все этапы**.

### Шаг 1 — установка codex CLI

```bash
bash scripts/install-codex.sh
```

Скрипт проверяет что `codex` есть на PATH. Если нет — устанавливает `npm i -g @openai/codex` и запускает `codex login`. Без codex `/landing-photos` и `/landing-visuals` не работают.

### Шаг 2 — новый prototype-first флоу

В прежнем флоу маркетолог запускал по очереди: `/landing-new` → `/landing-niche` → ... → 12_seo.

В новом flow (prototype-first):

1. Маркетолог получает уже готовый `prototype.pdf` (сделан внешне).
2. Кладёт его в `<project>/07_ПРОТОТИП/source/`.
3. Запускает **`/landing-go`** — оркестратор ведёт через все этапы автоматически, останавливаясь только там где нужно вмешательство.

Этапы 00 (бриф) / 01 (контекст) / 01a (анализ ниши) / 02 (материалы клиента) помечены `n/a` — они происходят до landing-system.

### Шаг 3 — smoke test

```bash
SKIP_OPEN=1 USE_CODEX_MOCK=1 bash scripts/test-pipeline.sh smoke-onboarding tests/phase-pra/fixtures/prototype-sample.md
```

### Полезное

- `/landing-photos`, `/landing-visuals` остаются как ручные entry points.
- Auto-fix на гейтах работает автоматически.
- 07d_photos и 07e_visuals идут параллельно.
