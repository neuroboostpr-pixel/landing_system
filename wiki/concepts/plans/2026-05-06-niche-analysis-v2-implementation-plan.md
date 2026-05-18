---
type: rule
name: niche-analysis-v2-plan
sources: ["docs/superpowers/plans/2026-05-06-niche-analysis-v2-implementation-plan.md"]
updated: 2026-05-18
triggers: []
stage: "01a"
uses:
  - niche-analyst
  - brand-architect
  - content-writer
  - wp-builder
  - niche-analysis
  - stage-gates
  - positioning-modes
  - 01a-analiz-nishi
tags: [plan, niche-analysis, positioning, v2, migration]
---

# Niche Analysis v2 — план реализации

## Что делает

Описывает полный план доработки этапа `01a_АНАЛИЗ_НИШИ` до версии v2: добавляет справочник режимов позиционирования, два новых артефакта (`market-profile.md` и `landing-structure.md`), три шаблона `positioning.md` (rational / emotional_aspiration / trust_authority), классификацию режима в агенте `niche-analyst` и скрипт миграции legacy-проектов.

## Когда вызывать / в каком этапе

Документ — план внедрения, не живая команда. Используется разработчиком или subagent-driven-development при реализации PR нового функционала 01a. Затрагивает этап `01a_АНАЛИЗ_НИШИ` и downstream-агентов (04, 07, 08).

## Что на вход / на выход

**Вход:**
- `docs/superpowers/specs/2026-05-06-niche-analysis-v2-design.md` — спецификация
- существующие файлы `config/niche-visual-rules.yaml`, `config/stage-gates.yaml`, `agents/niche-analyst.md`

**Выход (создаются/изменяются):**
- `config/positioning-modes.yaml` — справочник 3 режимов + матрица предсказания
- `skills/niche-analysis/scripts/validate-market-profile.py` — валидатор рыночного профиля
- `skills/niche-analysis/scripts/validate-positioning.py` — mode-aware валидатор позиционирования
- `skills/niche-analysis/scripts/validate-landing-structure.py` — валидатор карты блоков
- `scripts/migrate-niche-to-v2.sh` — идемпотентная миграция v1-проектов
- тесты `tests/phase-niche/` (bats + pytest) для всех новых валидаторов
- фикстуры для 3 режимов + 2 невалидных кейсов
- расширенные агенты: `niche-analyst` (12 шагов), `brand-architect`, `content-writer`, `wp-builder`
- 5 новых hard_check в `config/stage-gates.yaml` для 01a
- обновлённые `template/01a_АНАЛИЗ_НИШИ/README.md` и `README.md`

## Структура плана

План состоит из **6 фаз, 22 задач**:

| Фаза | Задачи | Суть |
|------|--------|------|
| A. Foundation | 1–3 | `positioning-modes.yaml` + маркеры режима в `niche-visual-rules.yaml` |
| B. Validators & artifacts | 4–9 | 3 валидатора Python + шаблоны фикстур |
| C. Agent integration | 10–12 | Расширение `niche-analyst` до 12 шагов |
| D. Downstream contracts | 13–15 | brand-architect, content-writer, wp-builder читают новые артефакты |
| E. Gate-check & docs | 16–18 | 5 новых hard_check + README + главный README |
| F. Migration & smoke | 19–22 | Скрипт миграции + smoke на lixiang-dubai |

Каждая задача содержит TDD-цикл: сначала falling test → реализация → passing test → commit.

## Связанные концепты

- [[niche-analyst]] — агент, расширяется до 12 шагов (шаги 4, 7, 8, 9 добавляются)
- [[niche-analysis]] — скилл, реализующий этот план
- [[positioning-modes]] — справочник режимов, создаётся в задаче 1
- [[01a-analiz-nishi]] — этап pipeline, который v2 расширяет
- [[stage-gates]] — конфиг гейтов, получает 5 новых hard_check
- [[brand-architect]] — downstream: читает `market-profile.md` + `landing-structure.md`
- [[content-writer]] — downstream: mode-aware копирайтинг по `landing-structure.md`
- [[wp-builder]] — downstream: генерирует template-parts строго по карте блоков

## Источник

- `docs/superpowers/plans/2026-05-06-niche-analysis-v2-implementation-plan.md`