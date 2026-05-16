---
type: block
name: animation-03-checkiconscale
sources: ["block-library/_patterns/animation-03-checkiconscale/meta.yaml"]
updated: 2026-05-16
triggers: []
stage: ""
uses: []
tags: ["animation", "css", "keyframe", "icon", "pattern"]
---

# Animation checkIconScale — масштабирование иконки-галочки

## Что делает
CSS-паттерн с keyframe-анимацией, который плавно масштабирует иконку-галочку (check icon) при появлении на странице. Используется для визуальной акцентировки завершённых шагов, преимуществ или подтверждений в блоках лендинга.

## Когда вызывать / в каком этапе
Применяется на этапе **07b (Compose)** и **08 (Build)**, когда в блоке нужно оживить иконку-галочку (например, в списках преимуществ, чеклистах, блоках «что вы получите»). Подключается как CSS-класс к элементу `<svg>` или `<img>` с иконкой.

## Что на вход / на выход

**Вход:**
- HTML-элемент с иконкой галочки (SVG или `<img>`)
- Опционально: переменные CSS для управления длительностью и задержкой анимации

**Выход:**
- CSS keyframe-правило `@keyframes checkIconScale` с анимацией масштаба
- Готовый CSS-класс для подключения к элементу

## Связанные концепты
- [[block-composition]] — паттерн используется при сборке composed.html
- [[block-library-management]] — управление и каталогизация паттернов в block-library
- [[design-tokens-generation]] — токены анимации (duration, easing) могут управлять параметрами keyframe
- [[wp-gutenberg-block-builder]] — паттерн встраивается в CSS блоков при генерации WordPress-темы

## Источник
- `block-library/_patterns/animation-03-checkiconscale/meta.yaml`