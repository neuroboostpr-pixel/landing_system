---
type: block
name: features-minimal-grid-2-sskrusgun-ru-10
sources: ["block-library/features/features-minimal-grid-2-sskrusgun-ru-10/meta.yaml"]
updated: 2026-05-16
triggers: []
stage: "07a"
uses: ["ux-composer", "wireframe-rendering", "block-composition"]
tags: ["features", "grid-2", "minimal", "ecommerce", "services", "ru-market"]
---

# Features: Две карточки с подарками (minimal grid-2)

## Что делает
Отображает две карточки рядом — каждая с продуктовым изображением, кратким описанием и кнопкой действия. Подходит для витрины двух ключевых продуктов или офферов в подарочном стиле.

## Когда вызывать / в каком этапе
Используется на этапе **07a (Wireframe)** и **07b (Compose)** — агенты [[ux-composer]] и [[block-composer]] выбирают этот блок из библиотеки, когда прототип предполагает секцию «features» с двухколоночной сеткой и минималистичным настроением. Особенно уместен для ниш **ecommerce** и **services** на российском рынке.

## Что на вход / на выход

**Вход:**
- `heading` (text, обязательный) — заголовок секции над карточками
- Два набора контента на карточку: изображение продукта, краткое описание, текст кнопки (берутся из `prototype.yaml` или подставляются как placeholders)

**Выход:**
- HTML-фрагмент с двумя карточками в сетке (grid-2), оформленными в минималистичном стиле
- В составе `wireframe.html` — один из вариантов блока features для выбора пользователем
- В составе `composed.html` — финальная разметка с токенами дизайна и текстами из прототипа

## Ключевые характеристики

| Параметр | Значение |
|---|---|
| Категория | features |
| Стиль | minimal |
| Сетка | grid-2 (две колонки) |
| Анимация | нет |
| Российский рынок | да |
| Ниши | ecommerce, services |
| Источник | sskrusgun.ru |
| Метод импорта | codex-block-generation |

## Связанные концепты
- [[ux-composer]] — выбирает блок из библиотеки при построении wireframe.html
- [[block-composer]] — инжектирует дизайн-токены и тексты прототипа в composed.html
- [[wireframe-rendering]] — скилл, отвечающий за рендер интерактивного wireframe с вариантами блоков
- [[block-composition]] — скилл, отвечающий за финальную сборку composed.html
- [[block-library-management]] — управление библиотекой блоков, куда входит данный блок

## Источник
- `block-library/features/features-minimal-grid-2-sskrusgun-ru-10/meta.yaml`