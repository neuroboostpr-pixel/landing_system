---
type: agent
name: niche-analyst
sources: ["agents/niche-analyst.md"]
updated: 2026-05-26
triggers: []
stage: "01a"
uses: ["landing-orchestrator", "brand-architect", "content-writer", "wp-builder"]
tags: ["research", "positioning", "competitors", "market-profile", "stage-01a"]
---

# Niche Analyst — Агент анализа ниши (Stage 01a)

## Что делает
Автоматически исследует рынок, конкурентов и определяет стратегию позиционирования лендинга. Работает без уточняющих вопросов — при нехватке данных помечает допущения меткой `[ДОПУЩЕНИЕ]` и продолжает.

## Когда вызывать / в каком этапе
Запускается на этапе **01a** — между `01_КОНТЕКСТ` и `02_МАТЕРИАЛЫ_КЛИЕНТА`. Активируется автоматически через `landing-orchestrator` после того, как заполнены бриф (`00_БРИФ/brief.md`) и опциональный контекст (`01_КОНТЕКСТ/context.md`). Вручную не вызывается. Требует, чтобы `.landing-state.yaml` показывал `current_stage == 01a_niche_analysis`.

## Что на вход / на выход

**Вход:**
- `00_БРИФ/brief.md` — обязательно
- `01_КОНТЕКСТ/context.md` — если есть
- `config/niche-visual-rules.yaml` — справочник визуальных правил по категориям
- `config/positioning-modes.yaml` — матрица режимов позиционирования

**Выход** (6 артефактов в `01a_АНАЛИЗ_НИШИ/`):
- `niche-analysis.md` — обзор ниши, тип бренда, режим, ключевые допущения (400–800 слов)
- `competitors.yaml` — 15–25 конкурентов в 7 ролях с позиционированием и визуальными заметками
- `market-profile.md` — 8 секций: accessibility tier (с расчётом ratio цена/доход), цикл принятия решения, регулируемость, эмоциональная нагрузка, культурный контекст, predicted mode
- `positioning.md` — выбранный режим (`rational` / `emotional_aspiration` / `trust_authority` / `hybrid`) с заполненным шаблоном
- `landing-structure.md` — карта блоков лендинга по комбинации «Тип бренда × Mode»
- `visual-requirements.md` — требования к фото и визуалу с red flags и preferences

Агент классифицирует бренд по типам: **1 — глобальный**, **2 — региональный**, **3 — локальный без бренда**. Для каждой комбинации Тип × Mode генерируется своя карта блоков (например, Тип 3 + trust_authority → Hero, About, Process, Cases, Reviews, Pricing, CTA, FAQ, Footer).

После записи всех артефактов запускает 5 Python-валидаторов (`validate-competitors.py`, `validate-market-profile.py`, `validate-positioning.py`, `validate-landing-structure.py`, `validate-visual-requirements.py`) и ждёт exit 0 от каждого. Финальный gate-check через `scripts/gate-check.sh 01a_niche_analysis` — и передаёт управление обратно оркестратору.

## Связанные концепты
- [[landing-orchestrator]] — запускает агента и принимает управление после hand-off
- [[brand-architect]] — downstream-потребитель `positioning.md` и `market-profile.md` на этапе 04
- [[content-writer]] — использует `landing-structure.md` и `positioning.md` на этапе 07
- [[wp-builder]] — читает `landing-structure.md` для генерации блоков на этапе 08
- [[landing-niche]] — slash-команда, связанная с этим этапом

## Источник
- `agents/niche-analyst.md`