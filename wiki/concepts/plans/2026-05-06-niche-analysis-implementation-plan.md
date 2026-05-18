---
type: stage
name: niche-analysis-implementation-plan
sources: ["docs/superpowers/plans/2026-05-06-niche-analysis-implementation-plan.md"]
updated: 2026-05-18
triggers: []
stage: "01a"
uses:
  - niche-analyst
  - niche-analysis
  - landing-niche
  - landing-orchestrator
  - references-curator
  - moodboard-composer
  - brand-architect
  - content-writer
  - seo-optimizer
  - stage-gates
tags: [plan, stage-01a, competitors, positioning, zero-touch]
---

# План реализации этапа 01a — Анализ ниши

## Что делает

Описывает пошаговую реализацию нового этапа `01a_АНАЛИЗ_НИШИ`, который автоматически исследует нишу, тип бренда и конкурентов **без участия пользователя**. Вставляется между этапами 01 (контекст) и 02 (материалы клиента) без сдвига нумерации остальных этапов.

## Когда вызывать / в каком этапе

Этап активируется командой `/landing-niche` после одобрения `00_brief`. Агент [[niche-analyst]] запускается автоматически — пользователь не отвечает ни на какие вопросы. Все неизвестные данные помечаются `[ДОПУЩЕНИЕ]`.

## Что на вход / на выход

**Вход:**
- `00_БРИФ/brief.md` (обязательно)
- `01_КОНТЕКСТ/context.md` (если есть)

**Выход (в `01a_АНАЛИЗ_НИШИ/`):**
- `niche-analysis.md` — нарративный отчёт 400–800 слов: тип бренда (1/2/3), описание ниши, рекомендация «на что давить», список допущений
- `competitors.yaml` — машиночитаемая база 15–25 игроков в 7 ролях: `direct`, `local_dealer`, `manufacturer`, `analog`, `category_leader`, `local_competitor`, `indirect`
- `positioning.md` — единый источник истины: core promise, tone of voice, 1–2 угла отстройки, чего избегать

**Создаваемые файлы системы:**
- `agents/niche-analyst.md`, `skills/niche-analysis/SKILL.md`
- `commands/landing-niche.md` + копия в `.claude/commands/`
- `skills/niche-analysis/scripts/validate-competitors.py` — валидатор схемы YAML (min 15 записей, min 3 разных роли, допустимые confidence-значения)
- `scripts/migrate-state-add-01a.sh` — backward-compat: добавляет ключ в существующие проекты; если `02_assets` уже `approved` — ставит статус `skipped`
- Bats-тесты и pytest-тесты в `tests/phase-niche/`

**Модифицируемые файлы системы:**
- `template/.landing-state.yaml` — новый ключ `01a_niche_analysis`
- `config/stage-gates.yaml` — блок `01a` + зависимость `02_assets` от `01a`
- `agents/landing-orchestrator.md` — переход 01→01a→02
- Downstream-агенты (`references-curator`, `moodboard-composer`, `brand-architect`, `content-writer`, `seo-optimizer`) — каждый получает секцию «Inputs from earlier stages» с указанием нужного артефакта из `01a_АНАЛИЗ_НИШИ/`
- `scripts/gate-state.sh` — статус `skipped` приравнивается к `approved` при проверке зависимостей

## Связанные концепты

- [[niche-analyst]] — агент-исполнитель, делает ресёрч zero-touch
- [[niche-analysis]] — skill-обёртка, запускается через команду
- [[landing-niche]] — slash-команда `/landing-niche`
- [[landing-orchestrator]] — получает новый переход 01→01a→02
- [[stage-gates]] — блок `01a_niche_analysis` добавляется с тремя hard-checks на артефакты
- [[brand-architect]] — читает `positioning.md` из 01a
- [[content-writer]] — читает `positioning.md` и `competitors.yaml`
- [[references-curator]] — читает `competitors.yaml` перед поиском референсов
- [[seo-optimizer]] — читает `competitors.yaml` для семантики

## Источник

- `docs/superpowers/plans/2026-05-06-niche-analysis-implementation-plan.md`