---
type: block
name: hover-effect-07-item-7
sources: ["block-library/_patterns/hover-effect-07-item-7/meta.yaml"]
updated: 2026-05-16
triggers: []
stage: "07b"
uses: ["block-composer", "block-library-management"]
tags: ["pattern", "hover", "css", "ui-effect"]
---

# Hover 7 — CSS-эффект наведения

## Что делает
Готовый CSS-паттерн эффекта при наведении курсора (hover), извлечённый с реального сайта. Применяется к элементам лендинга для добавления интерактивности без написания кода с нуля.

## Когда вызывать / в каком этапе
Используется на этапе **07b (Block Compose)** — когда `block-composer` собирает `composed.html` из выбранных блоков. Паттерн подключается как CSS-утилита к любому блоку, которому нужна анимация при наведении (карточки услуг, кнопки, галерея, преимущества).

## Что на вход / на выход
**Вход:**
- `meta.yaml` — метаданные паттерна (id, name, import_method)
- CSS-файл паттерна в папке `_patterns/hover-effect-07-item-7/`

**Выход:**
- CSS-правила, встраиваемые в `composed.html` или подключаемые как отдельный stylesheet
- Интерактивный hover-эффект на целевом элементе страницы

## Связанные концепты
- [[block-composer]] — агент этапа 07b, который встраивает паттерны в итоговый `composed.html`
- [[block-library-management]] — скилл управления библиотекой блоков и паттернов; отвечает за импорт и хранение CSS-паттернов
- [[block-composition]] — скилл сборки блоков с токенами дизайна; использует паттерны при рендере

## Источник
- `block-library/_patterns/hover-effect-07-item-7/meta.yaml`