---
type: stage
name: 01a-niche-analysis
sources: ["template/01a_АНАЛИЗ_НИШИ/README.md"]
updated: 2026-05-15
triggers: []
stage: "01a"
uses: ["niche-analyst", "landing-niche", "references-curator", "moodboard-composer", "brand-architect", "content-writer", "wp-builder", "seo-optimizer", "client-assets-collector"]
tags: ["niche", "analysis", "positioning", "competitors", "brand-type"]
---

# 01a. Анализ ниши

## Что делает
Автоматически исследует рынок: определяет тип бренда, анализирует конкурентов, выбирает режим позиционирования (rational / emotional_aspiration / trust_authority) и формирует структуру будущего лендинга. Пользователь не отвечает ни на один вопрос — агент работает самостоятельно.

## Когда вызывать / в каком этапе
Этап **01a** — запускается командой `/landing-niche` после того, как заполнен `00_БРИФ/brief.md`. Является первым аналитическим этапом перед сбором референсов (03) и построением бренд-кита (04).

## Что на вход / на выход

**Вход:**
- `00_БРИФ/brief.md` — обязательно
- `01_КОНТЕКСТ/context.md` — если есть

**Выход (6 артефактов):**
- `niche-analysis.md` — нарративный отчёт 400–800 слов: тип бренда, описание ниши, рекомендации по давлению, список допущений
- `competitors.yaml` — база 15–25 игроков в 7 ролях (direct, local_dealer, manufacturer, analog, category_leader, local_competitor, indirect)
- `market-profile.md` — рыночный профиль: 8 секций (accessibility tier, consideration cycle, decision unit, emotional load и др.)
- `positioning.md` — шаблон позиционирования с обязательным заголовком `**Mode:** <режим>`
- `landing-structure.md` — порядок блоков лендинга под конкретный тип бренда × режим (контракт с wp-builder)
- `visual-requirements.md` — требования к визуалу: hero focal point, photography style, red flags

**Принцип:** при нехватке данных агент помечает поля `[ДОПУЩЕНИЕ]`, не останавливаясь для уточнений.

## Связанные концепты
- [[niche-analyst]] — агент, выполняющий 12-шаговый алгоритм исследования
- [[landing-niche]] — команда-триггер для запуска этапа
- [[references-curator]] — читает `competitors.yaml` и `visual-requirements.md` на этапе 03
- [[moodboard-composer]] — читает `niche-analysis.md` и `visual-requirements.md` на этапе 03
- [[brand-architect]] — читает `positioning.md`, `market-profile.md`, `landing-structure.md` на этапе 04
- [[content-writer]] — читает `positioning.md`, `landing-structure.md`, `market-profile.md`, `competitors.yaml` на этапе 07
- [[wp-builder]] — использует `landing-structure.md` как контракт template-parts на этапе 08
- [[seo-optimizer]] — читает `competitors.yaml` на этапе 12
- [[client-assets-collector]] — читает `visual-requirements.md` на этапе 02

## Источник
- `template/01a_АНАЛИЗ_НИШИ/README.md`