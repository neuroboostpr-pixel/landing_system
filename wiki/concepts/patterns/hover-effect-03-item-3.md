---
type: block
name: hover-effect-03-item-3
sources: ["block-library/_patterns/hover-effect-03-item-3/meta.yaml"]
updated: 2026-05-16
triggers: []
stage: ""
uses: []
tags: ["pattern", "hover", "css", "interaction", "ui-effect"]
---

# Hover 3 — CSS-паттерн ховер-эффекта

## Что делает
Готовый CSS-паттерн ховер-эффекта, извлечённый с реального сайта. Добавляет интерактивную реакцию элемента при наведении курсора мыши — используется для карточек, кнопок, иконок и других блоков лендинга.

## Когда вызывать / в каком этапе
Применяется на этапе **07b (Compose)** и **08 (Build)** — когда block-composer или frontend-builder собирают интерактивные блоки с hover-состояниями. Подключается как переиспользуемый CSS-паттерн из библиотеки `block-library/_patterns/`.

## Что на вход / на выход
**Вход:**
- `meta.yaml` — описание паттерна (id, тип, название, метод импорта)
- CSS-файлы паттерна в папке `hover-effect-03-item-3/`

**Выход:**
- Готовые CSS-правила, подключаемые к блоку лендинга
- Hover-состояние для целевого элемента без дополнительного JS

## Связанные концепты
- [[block-composition]] — этап 07b, где паттерны встраиваются в composed.html
- [[block-library-management]] — управление библиотекой паттернов и блоков
- [[frontend-builder]] — агент, который применяет CSS-паттерны при сборке блоков
- [[design-tokens-generation]] — токены (цвета, радиусы) влияют на визуал ховера

## Источник
- `block-library/_patterns/hover-effect-03-item-3/meta.yaml`