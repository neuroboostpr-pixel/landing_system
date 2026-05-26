---
type: block
name: animation-07-iconbackgroundopacity
sources: ["block-library/_patterns/animation-07-iconbackgroundopacity/meta.yaml"]
updated: 2026-05-25
triggers: []
stage: ""
uses: []
tags: ["animation", "pattern", "css", "keyframe", "icon", "opacity"]
---

# Animation: iconBackgroundOpacity

## Что делает
Добавляет к иконкам плавное изменение прозрачности фонового слоя через CSS keyframe-анимацию. Фон иконки «дышит» или появляется/исчезает без JavaScript.

## Когда вызывать / в каком этапе
Применяется на этапе **07b Compose** или **08 Build** — когда нужно оживить статичные иконки на блоке (фичи, преимущества, карточки услуг). Подключается как CSS-паттерн поверх любого блока, где есть иконки с фоновым контейнером.

## Что на вход / на выход

**Вход:**
- Блок с иконками, у которых есть фоновый элемент (`.icon-bg`, `.icon-wrapper` и т.п.)
- CSS-переменные проекта (токены цвета/прозрачности из `tokens.json`)

**Выход:**
- CSS `@keyframes iconBackgroundOpacity` — анимация изменения `opacity` фона иконки
- Готовый к подключению CSS-паттерн, импортируемый в тему или `composed.html`

## Связанные концепты
*(Явных ссылок на другие концепты в исходнике нет)*

## Источник
- `block-library/_patterns/animation-07-iconbackgroundopacity/meta.yaml`