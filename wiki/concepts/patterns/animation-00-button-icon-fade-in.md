---
type: block
name: animation-00-button-icon-fade-in
sources: ["block-library/_patterns/animation-00-button-icon-fade-in/meta.yaml"]
updated: 2026-05-16
triggers: []
stage: ""
uses: []
tags: ["animation", "css", "pattern", "button", "icon", "fade-in"]
---

# Animation: Button Icon Fade-in

## Что делает
CSS-паттерн анимации: иконка внутри кнопки плавно появляется через keyframe-эффект `fade-in`. Применяется для добавления визуальной динамики к кнопкам с иконками на лендинге.

## Когда вызывать / в каком этапе
Используется на этапах **07b (block-composition)** и **08 (wp-build)**, когда блок содержит кнопку с иконкой и нужна анимация появления. Подключается как CSS-паттерн — импортируется в стили блока или глобальный stylesheet темы.

## Что на вход / на выход
**Вход:**
- Кнопка (`<button>` или `<a class="btn">`) с вложенной иконкой (`<svg>` или `<img>`)

**Выход:**
- CSS keyframe-правило `@keyframes button-icon-fade-in` + класс-утилита для применения анимации
- Иконка появляется с opacity 0 → 1 при загрузке или hover (в зависимости от реализации)

## Связанные концепты
- [[block-composition]] — этап 07b, где паттерны анимации инжектятся в composed.html
- [[design-tokens-generation]] — токены (длительность, easing) могут параметризовать анимацию
- [[block-library-management]] — управление библиотекой паттернов, частью которой является этот файл
- [[wp-gutenberg-block-builder]] — на этапе 08 паттерн включается в CSS блока

## Источник
- `block-library/_patterns/animation-00-button-icon-fade-in/meta.yaml`