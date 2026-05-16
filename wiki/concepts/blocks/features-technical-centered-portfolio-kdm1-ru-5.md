---
type: block
name: features-technical-centered-portfolio-kdm1-ru-5
sources: ["block-library/features/features-technical-centered-portfolio-kdm1-ru-5/meta.yaml"]
updated: 2026-05-16
triggers: []
stage: "07a"
uses: ["ux-composer", "block-composition", "block-library-management", "block-composer"]
tags: ["features", "technical", "centered", "ecommerce", "tech", "premium-auto", "animation", "ru-market", "interactive"]
---

# Большое предметное фото с интерактивными точками и карточкой детали (features-technical-centered-portfolio-kdm1-ru-5)

## Что делает
Блок-секция «Характеристики» с большим предметным фото в центре, поверх которого расставлены интерактивные точки-маркеры. При наведении или клике на точку появляется карточка с описанием конкретной детали продукта. Создаёт технически выверенный, «инженерный» визуальный язык.

## Когда вызывать / в каком этапе
Используется на **этапе 07a (Wireframe)** — агент [[ux-composer]] выбирает этот блок из библиотеки, когда прототип описывает технический showcase продукта. Особенно подходит для ниш **ecommerce**, **tech** и **premium-auto** (в т.ч. автомобильные лендинги). На этапе **07b (Compose)** агент [[block-composer]] наполняет блок токенами дизайна и текстами из `prototype.yaml`.

## Что на вход / на выход

**Вход:**
- Обязательный текстовый слот `heading` — заголовок секции характеристик
- Предметное фото продукта (фото-слот подставляется через [[photo-curator]] / [[photo-preview-board]] на этапе 07c)
- Описания деталей для каждой интерактивной точки (из `prototype.yaml`)
- Токены дизайна (`tokens.json`) — цвета, типографика из [[design-system-generator]]

**Выход:**
- Готовый HTML-фрагмент блока (вставляется в `wireframe.html` → `composed.html`)
- Анимация точек (`has_animation: true`) — CSS/JS эффекты при hover/click
- Карточки описания деталей — появляются по интерактивным маркерам

## Связанные концепты
- [[ux-composer]] — выбирает этот блок при построении wireframe.html на этапе 07a
- [[block-composer]] — наполняет блок токенами и текстами на этапе 07b
- [[block-composition]] — скилл, который описывает логику сборки блоков в composed.html
- [[block-library-management]] — скилл управления пополнением и форматом библиотеки блоков
- [[photo-curator]] — подставляет предметное фото клиента или AI-fallback в фото-слоты блока
- [[07a-wireframe]] — этап, на котором блок включается в сборку
- [[07b-composed]] — этап, на котором блок получает финальное наполнение

## Источник
- `block-library/features/features-technical-centered-portfolio-kdm1-ru-5/meta.yaml`