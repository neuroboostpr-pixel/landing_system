---
type: block
name: animation-04-fade-in
sources: ["block-library/_patterns/animation-04-fade-in/meta.yaml"]
updated: 2026-05-16
triggers: []
stage: "07b"
uses: ["block-composer", "block-composition", "ux-composer"]
tags: ["animation", "css", "keyframe", "fade-in", "pattern"]
---

# Animation: Fade-In

## Что делает
CSS-паттерн плавного появления элементов: реализует keyframe-анимацию `fade-in`, при которой блок или элемент нарастает из прозрачности до полной видимости. Подключается к любому блоку лендинга без написания кода вручную.

## Когда вызывать / в каком этапе
Используется на этапе **07b (block-composition)** при сборке `composed.html`. `block-composer` подключает паттерн к блокам, которым нужно анимированное появление при скролле или загрузке страницы. Может также применяться на этапе **07a (wireframe)** для демонстрации интерактивности в `wireframe.html`.

## Что на вход / на выход
**Вход:**
- Мета-данные паттерна из `meta.yaml` (id, name, description)
- CSS-файл с keyframe-правилом `@keyframes fade-in` и утилитарным классом

**Выход:**
- CSS-класс, пригодный для подключения к любому HTML-элементу блока
- Готовая анимация: `opacity: 0` → `opacity: 1` по заданной длительности и easing

## Связанные концепты
- [[block-composer]] — агент этапа 07b, который применяет паттерн к блокам `composed.html`
- [[block-composition]] — скилл, оркеструющий сборку блоков с инъекцией паттернов
- [[ux-composer]] — агент этапа 07a, может использовать паттерн в `wireframe.html`
- [[block-library-management]] — скилл управления библиотекой блоков и паттернов

## Источник
- `block-library/_patterns/animation-04-fade-in/meta.yaml`