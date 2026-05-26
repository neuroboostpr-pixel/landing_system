---
type: block
name: animation-00-button-icon-fade-in
sources: ["block-library/_patterns/animation-00-button-icon-fade-in/meta.yaml"]
updated: 2026-05-25
triggers: []
stage: ""
uses: []
tags: ["animation", "pattern", "css", "button", "icon", "keyframe"]
---

# Animation: Button Icon Fade In

## Что делает
CSS-анимация на keyframe'ах, которая плавно появляет иконку внутри кнопки. Добавляет живость и визуальный акцент на CTA-элементах лендинга без JavaScript.

## Когда вызывать / в каком этапе
Применяется на этапе 08 (сборка темы) при вёрстке блоков с кнопками, содержащими SVG-иконки или inline-иконки (стрелки, чекмарки, лупы и т.п.). Подключается как CSS-паттерн к любому блоку, где нужно анимированное появление иконки при загрузке страницы или при hover.

## Что на вход / на выход
**Вход:** нет входных данных — паттерн представляет собой готовый CSS-фрагмент (keyframe + utility-класс).

**Выход:** CSS-правила `@keyframes button-icon-fade-in` и соответствующий класс-применитель, который разработчик темы подключает к нужному элементу кнопки.

## Связанные концепты
Нет явных обратных ссылок в исходнике.

## Источник
- `block-library/_patterns/animation-00-button-icon-fade-in/meta.yaml`