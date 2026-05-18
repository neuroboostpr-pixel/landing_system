---
type: block
name: hover-effect-02-item-2
sources: ["block-library/_patterns/hover-effect-02-item-2/meta.yaml"]
updated: 2026-05-16
triggers: []
stage: ""
uses: []
tags: ["pattern", "hover", "css", "ui-effect", "block-library"]
---

# Hover Effect 02 — Item 2

## Что делает
CSS-паттерн hover-эффекта, извлечённый с реального сайта. Применяется к элементам интерфейса для добавления интерактивной анимации при наведении курсора.

## Когда вызывать / в каком этапе
Используется на этапе сборки блоков (07b Compose / 08 Build) при необходимости добавить готовый hover-эффект к карточкам, кнопкам или другим элементам лендинга. Выбирается вручную в wireframe или при настройке composed.html.

## Что на вход / на выход
**Вход:**
- `meta.yaml` — метаданные паттерна (id, name, description, дата импорта, метод импорта)

**Выход:**
- CSS-стили hover-эффекта, готовые к подключению в блоки block-library

## Связанные концепты
- [[block-library-management]] — управление библиотекой паттернов и блоков
- [[block-composition]] — этап 07b, где паттерны вставляются в composed.html
- [[design-tokens-generation]] — токены дизайна, с которыми согласуется стилистика паттерна

## Источник
- `block-library/_patterns/hover-effect-02-item-2/meta.yaml`