---
type: block
name: header-minimal-split-project21993216-tild-0
sources: ["block-library/header/header-minimal-split-project21993216-tild-0/meta.yaml"]
updated: 2026-05-16
triggers: []
stage: "07a"
uses: ["ux-composer", "wireframe-rendering", "block-composition"]
tags: ["header", "minimal", "split", "ru_market", "navigation"]
---

# Компактная верхняя навигация (header-minimal-split)

## Что делает
Отображает шапку сайта: логотип слева, пункты меню по центру, контактный телефон и яркая кнопка действия справа. Минималистичный стиль, без анимаций — чисто, быстро, понятно.

## Когда вызывать / в каком этапе
Используется на **этапе 07a (Wireframe)** и **07b (Compose)** при выборе блока для верхней навигации. `ux-composer` автоматически предлагает этот блок как кандидата для слота `header`, если прототип описывает компактную шапку с разделённой компоновкой (split-layout).

Подходит для проектов в нишах: **услуги (services)**, **ecommerce**, **b2b-saas**. Ориентирован на российский рынок (`ru_market: true`).

## Что на вход / на выход

**На вход:**
- Обязательный слот `heading` (тип `text`) — название компании или логотип-текст, отображается в левой части шапки.
- Пункты меню, контактный номер и текст кнопки берутся из `prototype.yaml` при compose.

**На выход:**
- HTML-блок шапки, готовый к вставке в `wireframe.html` (этап 07a) и `composed.html` (этап 07b).
- В wireframe.html — интерактивный preview с CSS-переключением вариантов.
- В composed.html — tokens из `tokens.json` инжектируются в переменные цветов и шрифтов.

## Связанные концепты
- [[ux-composer]] — отбирает блок по критериям стиля и ниши при построении wireframe
- [[wireframe-rendering]] — рендерит этот блок в интерактивный `wireframe.html`
- [[block-composition]] — инжектирует design-токены и прототипный текст в блок при compose
- [[block-library-management]] — управляет каталогом, добавляет и обновляет блоки

## Источник
- `block-library/header/header-minimal-split-project21993216-tild-0/meta.yaml`