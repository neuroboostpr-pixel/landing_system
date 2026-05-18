---
type: agent
name: niche-analyst
sources: ["agents/niche-analyst.md"]
updated: 2026-05-15
triggers: []
stage: "01a"
uses:
  - landing-orchestrator
  - brand-architect
  - content-writer
  - wp-builder
  - niche-analysis
tags: ["research", "positioning", "competitors", "market-profile", "zero-touch"]
---

# niche-analyst — Автоматический анализ ниши

## Что делает

Исследует нишу, конкурентов и рынок полностью в автоматическом режиме — без единого вопроса к пользователю. По итогам выдаёт 6 структурированных артефактов, которые используют все последующие этапы: от бренд-кита до генерации блоков WordPress.

## Когда вызывать / в каком этапе

Активируется на этапе **01a** — после того как готов `00_БРИФ/brief.md` и (опционально) `01_КОНТЕКСТ/context.md`. Запускается через `landing-orchestrator` автоматически или вручную. После завершения оркестратор вызывает `scripts/gate-check.sh 01a_niche_analysis` и ждёт подтверждения пользователя для перехода к этапу 02.

## Что на вход / на выход

**Вход:**
- `00_БРИФ/brief.md` — обязательно
- `01_КОНТЕКСТ/context.md` — если есть

**Выход** (6 артефактов в `01a_АНАЛИЗ_НИШИ/`):
1. `niche-analysis.md` — обзор 400–800 слов: тип бренда, ниша, допущения
2. `competitors.yaml` — 15–25 конкурентов в 7 ролях
3. `market-profile.md` — 8 секций: accessibility tier, consideration cycle, emotional load, cultural context и др.
4. `positioning.md` — шаблон одного из трёх режимов: `rational`, `emotional_aspiration`, `trust_authority` (или `hybrid`)
5. `landing-structure.md` — карта блоков лендинга по типу бренда × режиму
6. `visual-requirements.md` — визуальные правила: focal, photography, people, red flags

Все артефакты проходят валидацию через Python-скрипты в `skills/niche-analysis/scripts/`.

## Алгоритм (кратко)

12 шагов: парсинг брифа → определение региона и языка → классификация бренда (Тип 1/2/3) → сбор конкурентов через WebSearch + Firecrawl → скрейп каждого конкурента → построение market-profile (с расчётом `ratio = цена / медианный доход` для определения accessibility tier) → синтез positioning mode через матрицу + override-индикаторы из брифа → генерация landing-structure по таблице Тип × Mode → визуальные требования → итоговый `niche-analysis.md`. При нехватке данных ставит `[ДОПУЩЕНИЕ]` вместо вопроса.

## Связанные концепты

- [[landing-orchestrator]] — запускает агента и проверяет gate после завершения
- [[brand-architect]] — потребляет `positioning.md` и `niche-analysis.md` как вход
- [[content-writer]] — использует `landing-structure.md` для адаптации текстов
- [[wp-builder]] — использует `landing-structure.md` для генерации block.php
- [[niche-analysis]] — скилл, содержащий валидаторы и конфиги (`positioning-modes.yaml`, `niche-visual-rules.yaml`)

## Источник

- `agents/niche-analyst.md`