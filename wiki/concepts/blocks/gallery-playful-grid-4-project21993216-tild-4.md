---
type: block
name: gallery-playful-grid-4-project21993216-tild-4
sources: ["block-library/gallery/gallery-playful-grid-4-project21993216-tild-4/meta.yaml"]
updated: 2026-05-16
triggers: []
stage: ""
uses:
  - ux-composer
  - block-composer
  - block-library-management
tags: ["gallery", "grid-4", "playful", "ecommerce", "services", "luxury", "ru_market"]
---

# Витрина вкусов — галерея с круглыми изображениями (grid-4, playful)

## Что делает
Отображает витрину из четырёх позиций: каждый вариант — круглое предметное фото с подписью. Подходит для демонстрации вкусов, продуктов, тарифов или услуг в игривом, визуально лёгком стиле.

## Когда вызывать / в каком этапе
Используется на этапе **07a (wireframe)** при подборе блоков в [[ux-composer]] и на этапе **07b (composed)** при сборке финального макета в [[block-composer]]. Выбирается когда прототип содержит галерею товаров/вариантов, а бренд задаёт настроение `playful`. Подходит для ниш: e-commerce, услуги, luxury.

## Что на вход / на выход

**Вход:**
- `heading` (text, обязательный) — заголовок секции-витрины
- Слоты визуала: круглые предметные фотографии (4 шт.) + подписи — заполняются на этапах PR-B (фото) и PR-C (иконки/инфографика)

**Выход:**
- HTML-блок галереи `grid-4` с круглыми изображениями и подписями, готовый к вставке в `composed.html`
- Анимация: отсутствует (`has_animation: false`) — блок статичный, без GSAP

## Связанные концепты
- [[ux-composer]] — выбирает этот блок из библиотеки при рендере wireframe.html
- [[block-composer]] — инжектит токены и тексты при сборке composed.html
- [[block-library-management]] — управляет библиотекой, в которой хранится этот блок
- [[photo-curator]] — заполняет слоты круглых фото на этапе 07c
- [[visual-curator]] — заполняет декоративные визуальные слоты на этапе 07d

## Источник
- `block-library/gallery/gallery-playful-grid-4-project21993216-tild-4/meta.yaml`