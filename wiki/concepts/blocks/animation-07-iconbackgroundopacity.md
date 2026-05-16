---
type: block
name: animation-07-iconbackgroundopacity
sources: ["block-library/_patterns/animation-07-iconbackgroundopacity/meta.yaml"]
updated: 2026-05-16
triggers: []
stage: "07b"
uses: ["block-composer", "block-composition"]
tags: ["animation", "css", "keyframe", "icon", "opacity", "pattern"]
---

# Animation: iconBackgroundOpacity

## Что делает

CSS-паттерн анимации: плавно меняет прозрачность фона за иконкой с помощью keyframe-анимации. Применяется к блокам, где иконки появляются на цветном или полупрозрачном фоне — создаёт эффект «вдыхания» или мягкого пульса подложки.

## Когда вызывать / в каком этапе

Используется на этапе **07b (Block Compose)** — при сборке `composed.html`, когда блок содержит иконки с фоновой подложкой (feature-карточки, преимущества, шаги). Подключается автоматически через систему CSS-паттернов при наличии соответствующего класса в блоке.

Паттерн импортирован методом `css-pattern-extraction` — то есть извлечён из существующего CSS и зафиксирован как переиспользуемый фрагмент.

## Что на вход / на выход

**Вход:**
- HTML-элемент с иконкой и фоновой подложкой (например, `<div class="icon-bg">`)
- CSS-класс или keyframe-имя `iconBackgroundOpacity`

**Выход:**
- Keyframe-анимация `iconBackgroundOpacity`, применённая к фону иконки
- Визуальный эффект плавного изменения прозрачности фона при загрузке или hover-состоянии

## Связанные концепты

- [[block-composer]] — агент этапа 07b, который внедряет паттерны в `composed.html`
- [[block-composition]] — скилл, управляющий сборкой блоков с токенами и паттернами
- [[design-tokens-generation]] — токены (цвет фона, радиус, opacity) питают этот паттерн
- [[block-library-management]] — система хранения и регистрации паттернов в библиотеке

## Источник

- `block-library/_patterns/animation-07-iconbackgroundopacity/meta.yaml`