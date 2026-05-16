---
type: block
name: pricing-technical-grid-3-sskrusgun-ru-2
sources: ["block-library/pricing/pricing-technical-grid-3-sskrusgun-ru-2/meta.yaml"]
updated: 2026-05-16
triggers: []
stage: "07b"
uses: ["block-composition", "ux-composer", "block-composer", "block-library-management"]
tags: ["pricing", "grid-3", "technical", "ru-market", "services", "education", "ecommerce"]
---

# Сетка карточек программ — ценовой блок (technical grid-3)

## Что делает

Отображает набор карточек (3 в ряд) с фотографией программы или услуги, краткими техническими параметрами, выделенной ценой и кнопкой покупки. Подходит для сравнения нескольких тарифов или продуктовых позиций на одном экране.

## Когда вызывать / в каком этапе

Используется на этапе **07b (Compose)** — когда `block-composer` собирает `composed.html` из выбранных блоков. Подключается через `selections.yaml` после того, как пользователь одобрил вариант в `wireframe.html` (этап 07a).

Подходит для ниш: **услуги**, **образование**, **e-commerce** — везде, где нужно показать несколько позиций с ценой и дать возможность сразу перейти к покупке.

## Что на вход / на выход

**Вход:**
- Обязательный слот `heading` (тип `text`) — заголовок секции прайсинга
- Контент карточек из `prototype.yaml` (фото, параметры, цена, подпись кнопки)
- Токены бренда из `tokens.json` (цвет акцента, шрифт)

**Выход:**
- HTML-фрагмент блока, встраиваемый в `composed.html`
- Без анимаций (`has_animation: false`) — статичная вёрстка

## Дополнительные характеристики

| Параметр | Значение |
|---|---|
| Настроение стиля | `technical` — строго, без декора |
| Компоновка | `grid-3` — три колонки |
| Рынок | Россия (`ru_market: true`) |
| Анимации | Нет |
| Источник | [sskrusgun.ru](https://sskrusgun.ru/) |
| Метод импорта | codex-block-generation |

## Связанные концепты

- [[block-composition]] — скилл этапа 07b, который встраивает блок в composed.html
- [[ux-composer]] — агент 07a, который предлагает этот блок в wireframe как вариант для секции pricing
- [[block-composer]] — агент 07b, финально рендерит блок с токенами и текстами
- [[block-library-management]] — скилл управления библиотекой, через который блок регистрируется и обновляется

## Источник

- `block-library/pricing/pricing-technical-grid-3-sskrusgun-ru-2/meta.yaml`