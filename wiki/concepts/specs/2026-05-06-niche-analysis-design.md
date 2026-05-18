---
type: stage
name: 01a-analiz-nishi
sources: ["docs/superpowers/specs/2026-05-06-niche-analysis-design.md"]
updated: 2026-05-18
triggers: []
stage: "01a"
uses: ["niche-analyst", "landing-niche", "references-curator", "moodboard-composer", "brand-architect", "content-writer", "seo-optimizer", "client-assets-collector", "style-extractor"]
tags: ["niche", "competitors", "positioning", "analysis"]
---

# 01a — Анализ ниши

## Что делает
Автоматически исследует конкурентов и рынок после сбора брифа — без единого уточняющего вопроса к пользователю. Выдаёт три артефакта: нарративный отчёт о нише, машиночитаемую базу конкурентов и документ с позиционированием. Все последующие этапы (бренд, мудборд, контент, SEO) опираются на эти данные вместо субъективных суждений из брифа.

## Когда вызывать / в каком этапе
Вставляется между `01_КОНТЕКСТ` и `02_МАТЕРИАЛЫ_КЛИЕНТА`. Активируется командой `/landing-niche` после того, как `01_КОНТЕКСТ` помечен как `approved` в `.landing-state.yaml`. В pipeline orchestrator'а — переход `01 → 01a → 02`. Существующие проекты без папки `01a_АНАЛИЗ_НИШИ/` пропускают этап без блокировки.

## Что на вход / на выход

**Входы:**
- `00_БРИФ/brief.md` — обязательно
- `01_КОНТЕКСТ/context.md` — если есть

**Выходы (все в `01a_АНАЛИЗ_НИШИ/`):**
- `niche-analysis.md` — нарратив 400–800 слов: тип бренда (1/2/3), конкурентная карта, рекомендации для следующих этапов, список допущений `[ДОПУЩЕНИЕ]`
- `competitors.yaml` — 15–25 записей, роли: `direct`, `local_dealer`, `manufacturer`, `analog`, `category_leader`, `local_competitor`, `indirect`; поля: name, role, url, region, positioning, key\_messages, visual\_notes, confidence (high/medium/low)
- `positioning.md` — core promise, tone of voice, 1–2 угла отстройки, чего избегать

**Gate-проверки:** файлы существуют, `competitors.yaml` валиден, минимум 15 записей, минимум 3 разных роли, `positioning.md` содержит не более 2 углов.

## Алгоритм агента

1. Парсинг брифа: бренд, категория, регион, язык.
2. Классификация типа бренда через WebSearch (Wikipedia + объём выдачи).
3. Сбор конкурентов по типу бренда: Тип 1 — акцент на прямых + дилеры; Тип 3 — акцент на `local_competitor` (8–10 записей).
4. Скрейп сайтов конкурентов через `mcp__firecrawl__scrape` — homepage + about.
5. Синтез позиционирования: что говорят ВСЕ → туда нельзя; gaps → кандидаты на угол.
6. Запись трёх артефактов.

При нехватке данных агент не блокируется — заполняет поле как `[ДОПУЩЕНИЕ]`, снижает `confidence: low`.

## Связанные концепты
- [[niche-analyst]] — агент-исполнитель этапа, владелец всего алгоритма
- [[landing-niche]] — slash-команда, запускающая этап вручную
- [[brand-architect]] — читает `positioning.md` целиком для tone of voice
- [[moodboard-composer]] — читает `niche-analysis.md` Section 6 про занятые визуальные языки
- [[references-curator]] — читает `competitors.yaml` (visual\_notes), чтобы не клонировать визуал лидеров
- [[content-writer]] — читает `positioning.md` + `competitors.yaml` (key\_messages)
- [[seo-optimizer]] — читает `competitors.yaml` для семантики
- [[client-assets-collector]] — смежный этап 02, отзывы с Я.Карт (scope намеренно разделён)
- [[style-extractor]] — автоматический выбор палитры по конкурентам отдельно, не здесь
- [[stage-gates]] — gate-check.sh проверяет hard/soft условия закрытия этапа 01a

## Источник
- `docs/superpowers/specs/2026-05-06-niche-analysis-design.md`