---
type: stage
name: niche-analysis-v2
sources: ["docs/superpowers/specs/2026-05-06-niche-analysis-v2-design.md"]
updated: 2026-05-18
triggers: []
stage: "01a"
uses:
  - niche-analyst
  - niche-analysis
  - brand-architect
  - content-writer
  - wp-builder
  - seo-optimizer
  - stage-gates
  - positioning-modes
tags:
  - positioning
  - market-profile
  - niche
  - stage-01a
  - rational
  - emotional-aspiration
  - trust-authority
---

# Анализ ниши v2 — Режимы позиционирования и рыночный профиль

## Что делает

Расширяет этап `01a_АНАЛИЗ_НИШИ`: агент теперь не просто описывает нишу и конкурентов, но и определяет **режим позиционирования** (`rational` / `emotional_aspiration` / `trust_authority` / гибрид), вычисляет **доступность категории** относительно медианного дохода региона и строит **карту блоков лендинга** под конкретный тип бренда и режим.

## Когда вызывать / в каком этапе

Этап `01a`. Вызывается через `/landing-niche` или автоматически оркестратором после создания проекта. Zero-touch: агент сам собирает рыночные данные, сам классифицирует режим, при неоднозначности ставит `[ДОПУЩЕНИЕ]`.

## Что на вход / на выход

**Вход:**
- `00_БРИФ/brief.md`
- `01_КОНТЕКСТ/context.md` (если есть)

**Выход (6 артефактов в `01a_АНАЛИЗ_НИШИ/`):**
| Файл | Что содержит |
|---|---|
| `niche-analysis.md` | Нарратив о нише (обновлён — добавлена секция о режиме) |
| `competitors.yaml` | 15–25 конкурентов |
| `market-profile.md` | **Новый.** 6 параметров: accessibility_tier, consideration_cycle, decision_unit, regulated, emotional_load, cultural_context |
| `positioning.md` | **Переписан.** Один из трёх шаблонов по выбранному режиму (rational / emotional_aspiration / trust_authority) |
| `landing-structure.md` | **Новый.** Таблица блоков лендинга в порядке отображения |
| `visual-requirements.md` | Обновлён — добавлена секция адаптации под режим |

**Gate-check:** 9 hard_checks (вместо 6 в v1), включая валидацию `market-profile.md`, `positioning.md` по шаблону режима, `landing-structure.md`.

## Ключевые правила режима

- `utility_essential` / `mass_consumer` → `rational`
- `premium` / `luxury_status` / `ultra_luxury` → **только** `emotional_aspiration`
- Регулируемая категория (`regulated=yes`) → добавляет `trust_authority` в гибрид
- Тип бренда 3 (локальный) → почти всегда `+trust_authority`
- Явный override в брифе («давим на статус») перевешивает матрицу

## Связанные концепты

- [[niche-analyst]] — агент, который реализует этот алгоритм (12 шагов)
- [[niche-analysis]] — скилл с техническими деталями выполнения
- [[positioning-modes]] — конфиг `config/positioning-modes.yaml` с матрицей выбора
- [[brand-architect]] — читает `market-profile.md` и `landing-structure.md` на этапе 04
- [[content-writer]] — пишет копирайт по структуре из `landing-structure.md`
- [[wp-builder]] — генерирует только те template-parts, что есть в карте блоков
- [[stage-gates]] — 4 новых hard_check добавлены в `config/stage-gates.yaml`

## Источник

- `docs/superpowers/specs/2026-05-06-niche-analysis-v2-design.md`