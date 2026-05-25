---
type: agent
name: niche-analyst
sources: ["agents/niche-analyst.md"]
updated: 2026-05-25
triggers: []
stage: "01a"
uses:
  - landing-orchestrator
  - niche-analysis
tags: ["niche", "research", "positioning", "competitors", "market-profile"]
---

# Niche Analyst — Автоматический анализ ниши (этап 01a)

## Что делает

Агент самостоятельно исследует нишу клиента: изучает конкурентов, определяет тип бренда, строит рыночный профиль и выбирает режим позиционирования. Всё — без единого вопроса пользователю. Там, где данных не хватает, ставит пометку `[ДОПУЩЕНИЕ]`.

## Когда вызывать / в каком этапе

Активируется на этапе **01a** — после заполнения брифа (`00_БРИФ/brief.md`) и до перехода на этап `02_МАТЕРИАЛЫ_КЛИЕНТА`. Запускается через `landing-orchestrator`, который сверяется с `.landing-state.yaml` и проверяет, что `current_stage == 01a_niche_analysis`. Если предшествующий этап не закрыт — агент останавливается.

## Что на вход / на выход

**Вход:**
- `00_БРИФ/brief.md` — обязательно
- `01_КОНТЕКСТ/context.md` — если есть

**Выход** (6 артефактов в `01a_АНАЛИЗ_НИШИ/`):
1. `niche-analysis.md` — обзор ниши, тип бренда, выбранный режим, список допущений (400–800 слов)
2. `competitors.yaml` — 15–25 конкурентов в 7 ролях (manufacturer, direct, local_competitor и др.)
3. `market-profile.md` — 8 секций: accessibility tier, consideration cycle, decision unit, regulated, emotional load, cultural context, predicted mode, источники
4. `positioning.md` — один из трёх шаблонов позиционирования: `rational`, `emotional_aspiration`, `trust_authority` или гибрид
5. `landing-structure.md` — карта блоков лендинга по комбинации Тип бренда × Mode
6. `visual-requirements.md` — правила визуала: hero, фотостиль, люди в кадре, red flags, preferences

Каждый артефакт проходит Python-валидатор из `skills/niche-analysis/scripts/`. Все 5 валидаторов должны вернуть exit 0.

## Алгоритм в двух словах

Агент парсит бриф → классифицирует бренд (Тип 1/2/3 по охвату Wikipedia и упоминаниям) → собирает конкурентов через WebSearch и скрейпит их через Firecrawl → рассчитывает accessibility tier (цена / медианный доход региона) → выбирает режим позиционирования по матрице из `config/positioning-modes.yaml` → применяет override-индикаторы из брифа → генерирует все 6 артефактов → передаёт управление оркестратору.

## Связанные концепты

- [[landing-orchestrator]] — запускает агента, проверяет gate-check и запрашивает approval у пользователя для перехода 01a → 02
- [[niche-analysis]] — скилл со вспомогательными скриптами-валидаторами
- [[stage-execution-protocol]] — обязательный протокол: чтение state.yaml, Mermaid-карта, TodoWrite, gate-check перед любым Write/Edit

## Источник

- `agents/niche-analyst.md`