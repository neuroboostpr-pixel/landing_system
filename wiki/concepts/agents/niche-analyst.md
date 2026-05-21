---
type: agent
name: niche-analyst
sources: ["agents/niche-analyst.md"]
updated: 2026-05-20
triggers: []
stage: "01a"
uses: ["landing-orchestrator", "brand-architect", "content-writer", "wp-builder", "niche-analysis", "landing-niche"]
tags: ["research", "positioning", "competitors", "market-profile", "stage-01a"]
---

# niche-analyst — Автоматический анализ ниши

## Что делает
Агент самостоятельно исследует нишу бизнеса: находит конкурентов, определяет тип бренда, вычисляет ценовую доступность продукта и выбирает режим позиционирования. Всё без вопросов пользователю — при нехватке данных ставит пометку `[ДОПУЩЕНИЕ]`.

## Когда вызывать / в каком этапе
Этап **01a** — сразу после того как заполнен `00_БРИФ/brief.md`. Запускается командой `/landing-niche` или автоматически через `landing-orchestrator` при переходе из этапа 01 в 01a. Предшественник — `01_КОНТЕКСТ`, преемник — `02_МАТЕРИАЛЫ_КЛИЕНТА`.

## Что на вход / на выход

**Входы:**
- `00_БРИФ/brief.md` — обязательно
- `01_КОНТЕКСТ/context.md` — если есть

**Выходы (6 артефактов в `01a_АНАЛИЗ_НИШИ/`):**
1. `niche-analysis.md` — обзор 400–800 слов: тип бренда, ниша, режим, допущения
2. `competitors.yaml` — 15–25 конкурентов в 7 ролях со скрейпом каждого
3. `market-profile.md` — 8 секций: accessibility tier, consideration cycle, decision unit, emotional load, cultural context, predicted mode
4. `positioning.md` — один из трёх шаблонов: rational / emotional_aspiration / trust_authority (или hybrid)
5. `landing-structure.md` — карта блоков лендинга по формуле Тип бренда × Mode
6. `visual-requirements.md` — правила фотографии и визуала для этапов 07b–07d

После записи артефактов агент запускает 5 Python-валидаторов (`validate-competitors.py`, `validate-market-profile.py`, `validate-positioning.py`, `validate-landing-structure.py`, `validate-visual-requirements.py`) — все должны вернуть exit 0.

## Ключевые алгоритмы
- **Тип бренда** (1/2/3) определяется по Wikipedia-покрытию и количеству упоминаний, а не по языку брифа.
- **Accessibility tier** вычисляется как ratio = цена клиента / медианный доход региона; 6 тиров от `utility_essential` до `ultra_luxury`.
- **Mode** выбирается по матрице из `config/positioning-modes.yaml`; явный override из брифа («статус», «ROI», «сертификат») перевешивает матрицу.
- **landing-structure** строится по комбинации Тип × Mode из фиксированной таблицы + cultural adjustments.

## Связанные концепты
- [[landing-orchestrator]] — запускает агента и проверяет gate-check после завершения
- [[niche-analysis]] — скилл с детальным описанием алгоритма и конфигами
- [[brand-architect]] — получает `niche-analysis.md` и `positioning.md` как вход на этапе 04
- [[content-writer]] — использует `landing-structure.md` и `positioning.md` на этапе 07
- [[wp-builder]] — читает `landing-structure.md` для генерации template-parts на этапе 08
- [[landing-niche]] — slash-команда для ручного запуска этого агента

## Источник
- `agents/niche-analyst.md`