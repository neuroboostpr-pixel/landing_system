---
type: block
name: animation-06-fadeout
sources: ["block-library/_patterns/animation-06-fadeout/meta.yaml"]
updated: 2026-05-16
triggers: []
stage: ""
uses: []
tags: ["animation", "css", "keyframe", "pattern", "fadeout"]
---

# Animation fadeOut — анимация плавного исчезновения

## Что делает
CSS-паттерн, реализующий keyframe-анимацию плавного исчезновения элемента (`fadeOut`). Добавляет готовый `@keyframes`-блок, который можно применить к любому HTML-элементу на лендинге для создания эффекта постепенного затухания.

## Когда вызывать / в каком этапе
Используется на этапах сборки и вёрстки (этапы **07b**, **08**) — когда нужно добавить анимированный выход элементов из поля зрения. Типичные случаи: скрытие оверлеев, анимация смены блоков, exit-эффекты для popup-окон или баннеров. Подключается как CSS-паттерн внутри блоков composed.html или в тему WordPress.

## Что на вход / на выход

**Вход:**
- Мета-файл `meta.yaml` с идентификатором и описанием паттерна.
- CSS-файл паттерна (добываемый через `import_method: css-pattern-extraction`).

**Выход:**
- Готовый `@keyframes fadeOut { ... }` CSS-блок, готовый к подключению.
- Может применяться через утилитарный класс `.animate-fadeout` или через inline-стиль `animation: fadeOut <duration> <easing>`.

## Связанные концепты
- [[block-composer]] — подключает CSS-паттерны при сборке composed.html
- [[block-library-management]] — управляет импортом и версионированием паттернов из block-library
- [[design-tokens-generation]] — токены задают длительность и easing анимаций, используемые в паттерне
- [[wp-builder]] — включает паттерн в финальную тему WordPress

## Источник
- `block-library/_patterns/animation-06-fadeout/meta.yaml`