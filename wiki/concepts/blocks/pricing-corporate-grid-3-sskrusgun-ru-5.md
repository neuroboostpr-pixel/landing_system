---
type: block
name: pricing-corporate-grid-3-sskrusgun-ru-5
sources: ["block-library/pricing/pricing-corporate-grid-3-sskrusgun-ru-5/meta.yaml"]
updated: 2026-05-16
triggers: []
stage: "07a, 07b"
uses: ["block-library-management", "block-composition", "ux-composer"]
tags: ["pricing", "corporate", "grid-3", "ru-market", "services", "education"]
---

# Pricing — Корпоративная сетка из 3 карточек (sskrusgun)

## Что делает
Отображает раздел с тремя карточками специализированных программ или услуг — каждая карточка содержит фотофон, ценовой маркер и кнопку призыва к действию. Предназначен для сравнения тарифов или пакетов в корпоративном стиле.

## Когда вызывать / в каком этапе
Используется на этапах **07a (Wireframe)** и **07b (Compose)** при сборке лендинга. Подключается через `ux-composer` (выбор блока из библиотеки) и затем рендерится через `block-composer` с подстановкой токенов и текста прототипа. Подходит для ниш **services** и **education** на русском рынке.

## Что на вход / на выход

**Вход:**
- Обязательный слот `heading` (тип: `text`) — заголовок раздела с ценами
- Токены дизайна из `tokens.json` (цвета, шрифты)
- Контент из `prototype.yaml` (тексты карточек, цены, подписи к кнопкам)

**Выход:**
- HTML-фрагмент блока, встроенный в `wireframe.html` (этап 07a) или `composed.html` (этап 07b)
- Лейаут: сетка из 3 колонок (`grid-3`), стиль `corporate`, без анимации (`has_animation: false`)

## Дополнительные характеристики
| Параметр | Значение |
|---|---|
| Категория | pricing |
| Лейаут | grid-3 |
| Стиль / mood | corporate |
| Анимация | нет |
| Рынок | ru_market = true |
| Источник | sskrusgun.ru (codex-block-generation, 2026-05-16) |

## Связанные концепты
- [[block-library-management]] — управляет каталогом блоков, регистрирует этот блок как доступный
- [[block-composition]] — скилл этапа 07b, подставляет токены и тексты в блок при сборке composed.html
- [[ux-composer]] — агент 07a, выбирает блок из библиотеки при построении wireframe

## Источник
- `block-library/pricing/pricing-corporate-grid-3-sskrusgun-ru-5/meta.yaml`