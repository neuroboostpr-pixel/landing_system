---
type: block
name: gallery-corporate-cards-portfolio-kdm1-ru-4
sources: ["block-library/gallery/gallery-corporate-cards-portfolio-kdm1-ru-4/meta.yaml"]
updated: 2026-05-16
triggers: []
stage: "07a"
uses:
  - ux-composer
  - block-composer
  - wireframe-rendering
  - block-composition
tags:
  - gallery
  - cards
  - corporate
  - ecommerce
  - services
  - ru-market
  - dark-background
---

# Карточная витрина товаров (тёмный фон, ценовые зоны, CTA)

## Что делает
Отображает товары или услуги в виде карточной сетки на тёмном фоне: крупный заголовок секции, фото, ценовая зона и кнопка CTA на каждой карточке. Подходит для каталогов, прайс-листов и портфолио услуг.

## Когда вызывать / в каком этапе
Используется на этапе **07a (Wireframe)** и **07b (Compose)**, когда прототип требует секции-каталога с карточками. Подбирается агентом [[ux-composer]] из block-library по категории `gallery` и паттерну `cards`. Также используется [[block-composer]] при финальной сборке `composed.html`.

Подходит для ниш:
- **ecommerce** — витрина товаров с ценами
- **services** — прайс-лист услуг с фото и CTA

## Что на вход / на выход

**Вход:**
- Обязательный слот `heading` (тип `text`) — крупный заголовок секции
- Товарные карточки: фото, название, цена, кнопка CTA (подразумеваются в шаблоне блока)

**Выход:**
- HTML-блок с карточной сеткой на тёмном фоне, встроенный в `wireframe.html` или `composed.html`
- Placeholders для фото заполняются на этапе **07c** ([[photo-curator]]) или **07d** ([[visual-curator]])

## Дополнительные характеристики
| Параметр | Значение |
|---|---|
| Стиль | corporate |
| Анимация | нет |
| Российский рынок | да |
| Источник | portfolio.kdm1.ru (Спецодежда Сити) |
| Метод импорта | codex-block-generation |
| Дата импорта | 2026-05-16 |

## Связанные концепты
- [[ux-composer]] — выбирает блок при построении wireframe из block-library
- [[block-composer]] — инжектирует токены и тексты в блок на этапе 07b
- [[wireframe-rendering]] — скилл рендеринга, в котором блок участвует
- [[block-composition]] — скилл сборки composed.html с подстановкой контента
- [[block-library-management]] — управляет реестром блоков, в котором зарегистрирован этот блок
- [[photo-curator]] — заполняет фото-слоты карточек на этапе 07c

## Источник
- `block-library/gallery/gallery-corporate-cards-portfolio-kdm1-ru-4/meta.yaml`