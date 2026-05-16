---
type: block
name: hero-playful-split-opt-ecowash-ru-1
sources: ["block-library/hero/hero-playful-split-opt-ecowash-ru-1/meta.yaml"]
updated: 2026-05-16
triggers: []
stage: "07a, 07b"
uses:
  - ux-composer
  - block-composer
  - block-composition
  - wireframe-rendering
tags:
  - hero
  - playful
  - split
  - ecommerce
  - services
  - ru-market
  - 3d-visual
  - opt-form
---

# Hero Playful Split — крупный оффер с 3D-визуализацией и формой

## Что делает

Первый экран лендинга: слева — крупный оффер, список преимуществ (буллеты) и 3D-визуализация продукта, справа — форма заявки. Игривый стиль (playful), двухколоночная компоновка (split). Подходит для интернет-магазинов и сервисных компаний на русскоязычный рынок.

## Когда вызывать / в каком этапе

Используется на **этапе 07a** (wireframe) как кандидат для слота `hero` и на **этапе 07b** (compose) при сборке composed.html. Агент `ux-composer` подбирает этот блок, если в prototype.yaml указан стиль `playful` и/или layout `split`. Блок выбирается пользователем в `wireframe.html` через radio-toggle и фиксируется в `selections.yaml`.

## Что на вход / на выход

**Вход:**
- `prototype.yaml` с описанием первого экрана (оффер, буллеты, призыв к действию)
- `tokens.json` с цветами и типографикой бренда
- Обязательный слот `heading` (тип `text`, required: true)

**Выход:**
- HTML-блок hero в составе `wireframe.html` (этап 07a) с 2–3 вариантами
- Финальный блок в `composed.html` (этап 07b) с подставленными токенами и текстами из прототипа
- Слоты для фото (3D-визуализация) остаются как labeled placeholder до этапа 07c (PR-B)

## Связанные концепты

- [[ux-composer]] — подбирает этот блок под hero-слот wireframe
- [[block-composer]] — встраивает блок в composed.html с токенами и текстами
- [[block-composition]] — скилл этапа 07b, управляет инъекцией токенов
- [[wireframe-rendering]] — скилл этапа 07a, рендерит интерактивный wireframe.html
- [[photo-curator]] — заполняет 3D-/продуктовый photo-slot на этапе 07c
- [[07a-wireframe]] — этап выбора варианта блока пользователем
- [[07b-composed]] — этап сборки финального HTML с контентом

## Источник

- `block-library/hero/hero-playful-split-opt-ecowash-ru-1/meta.yaml`