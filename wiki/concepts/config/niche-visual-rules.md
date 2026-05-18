---
type: rule
name: niche-visual-rules
sources: ["config/niche-visual-rules.yaml"]
updated: 2026-05-18
triggers: []
stage: "01a"
uses: ["niche-analyst", "visual-generation", "photo-curator", "photo-matcher"]
tags: ["visual", "niche", "photography", "composition", "config", "hero", "red-flags"]
---

# Niche Visual Rules — визуальные правила по нишам

## Что делает

Конфигурационный файл задаёт визуальные стандарты для каждой категории бизнеса: каким должен быть Hero-кадр, можно ли stock-фото, нужны ли живые люди, какие фоны допустимы, и чего категорически нельзя делать. Устраняет «дешёвые сигналы» ещё до генерации дизайна.

## Когда вызывать / в каком этапе

Файл читается агентом [[niche-analyst]] на шаге 9 анализа ниши (этап `01a`). На выходе агент заполняет `01a_АНАЛИЗ_НИШИ/visual-requirements.md`, который затем используется агентами фотоотбора и генерации визуала. Правила применяются автоматически — вручную вызывать не нужно.

## Что на вход / на выход

**Вход:** тип ниши клиента из брифа (категория выбирается из 5 вариантов).

**Выход:** структурированный набор правил для конкретной категории:
- `hero_focal` — основной объект в Hero-кадре
- `hero_composition` — описание композиции
- `photography` — стиль съёмки (studio / documentary / lifestyle)
- `people` — нужны ли люди в кадре (yes / optional)
- `background_allowed` — список допустимых фонов
- `universal_red_flags` — визуальные антипаттерны (запрещены)
- `universal_preferences` — рекомендованные приёмы

## Категории ниш

| Категория | Позиционирование | Фокус Hero | Люди |
|---|---|---|---|
| `premium_automotive` | emotional_aspiration | product (машина 50–70%) | optional |
| `local_services` | trust_authority | person_or_process | yes |
| `professional_services` | trust_authority | person_or_environment | yes |
| `b2c_consumer` | hybrid | product_or_usage | optional |
| `default` | trust_authority | product_or_person | optional |

Ключевая логика: **stock smiling actors** запрещены везде — это универсальный «дешёвый сигнал» независимо от ниши.

## Связанные концепты

- [[niche-analyst]] — единственный потребитель этого конфига; читает на шаге 9, записывает в `visual-requirements.md`
- [[photo-matcher]] — использует visual-requirements.md для ранжирования клиентских фото по слотам
- [[visual-generation]] — учитывает niche при генерации иконок и инфографики через codex
- [[photo-curator]] — фотокуратор применяет red_flags как фильтр при классификации

## Источник

- `config/niche-visual-rules.yaml`