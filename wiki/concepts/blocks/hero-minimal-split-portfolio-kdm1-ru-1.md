---
type: block
name: hero-minimal-split-portfolio-kdm1-ru-1
sources: ["block-library/hero/hero-minimal-split-portfolio-kdm1-ru-1/meta.yaml"]
updated: 2026-05-16
triggers: []
stage: "07a"
uses: ["ux-composer", "wireframe-rendering", "block-composition"]
tags: ["hero", "minimal", "split", "ru-market", "ecommerce", "services", "premium-auto"]
---

# Hero Minimal Split — Светлый первый экран с предметной композицией

## Что делает

Светлый hero-блок с разделённой компоновкой (split layout): крупный заголовок и CTA-кнопка слева, предметная фотография с выносными маркерами преимуществ — справа. Подходит для продуктовых и сервисных лендингов в минималистичном стиле.

## Когда вызывать / в каком этапе

Используется на этапе **07a (Wireframe)** и **07b (Compose)**. Агент [[ux-composer]] подбирает блок автоматически, если прототип содержит hero-секцию с минималистичным стилем и split-раскладкой. Также может быть выбран вручную через `selections.yaml` после просмотра `wireframe.html`.

Подходит для ниш: интернет-магазины (`ecommerce`), услуги (`services`), премиум-авто (`premium-auto`). Ориентирован на российский рынок (`ru_market: true`).

## Что на вход / на выход

**Вход:**
- Слот `heading` (тип `text`, обязательный) — главный заголовок первого экрана
- Фотография предмета/продукта (фото-слот из [[photo-curator]], заполняется на этапе 07c)
- Маркеры преимуществ (текстовые выноски — наполняются из `prototype.yaml`)

**Выход:**
- HTML-секция блока, встроенная в `wireframe.html` (этап 07a) или `composed.html` (этап 07b)
- Плейсхолдеры для фото остаются до прохождения этапа [[07c-photos]]

## Особенности

- Анимация отсутствует (`has_animation: false`) — статичная, быстрая загрузка
- Стиль: минимализм (`minimal`), светлая цветовая схема
- Раскладка: split (заголовок + фото рядом)
- Импортирован из портфолио kdm1.ru методом codex-block-generation

## Связанные концепты

- [[ux-composer]] — выбирает блок на этапе 07a при формировании wireframe
- [[block-composer]] — инжектирует токены и тексты из прототипа на этапе 07b
- [[wireframe-rendering]] — рендерит блок в интерактивный `wireframe.html`
- [[block-composition]] — скилл, управляющий финальной сборкой `composed.html`
- [[photo-curator]] — заполняет фото-слот предметной съёмкой на этапе 07c

## Источник

- `block-library/hero/hero-minimal-split-portfolio-kdm1-ru-1/meta.yaml`