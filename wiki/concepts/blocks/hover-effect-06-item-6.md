---
type: block
name: hover-effect-06-item-6
sources: ["block-library/_patterns/hover-effect-06-item-6/meta.yaml", "block-library/_patterns/hover-effect-06-item-6/styles.css", "block-library/_patterns/hover-effect-06-item-6/index.html"]
updated: 2026-05-16
triggers: []
stage: ""
uses: []
tags: ["pattern", "hover", "css", "interaction", "ui-effect"]
---

# Hover 6 — CSS-паттерн эффекта при наведении

## Что делает
Добавляет плавный эффект при наведении курсора на элемент: меняет фоновый цвет с анимацией `transition: all 0.3s ease`. Паттерн извлечён из реального сайта методом CSS-экстракции.

## Когда вызывать / в каком этапе
Используется на этапе 07b (Compose) и 08 (Код) — когда нужно добавить интерактивность к карточкам, кнопкам или блокам списка без JavaScript. Подключается через класс `.item-6` к любому HTML-элементу.

## Что на вход / на выход

**Вход:**
- HTML-элемент с классом `item-6`
- CSS-переменные темы: `--t396-bgcolor-hover-color`, `--t396-bgcolor-color` (если заданы — используются как цвет фона при hover; иначе `transparent`)

**Выход:**
- Элемент с плавным переходом `0.3s ease` при наведении
- Изменение фонового цвета через CSS Custom Properties (совместимо с `tokens.json` дизайн-системы)

**Файлы паттерна:**
- `styles.css` — одно правило `.item-6` + hover-вариант
- `index.html` — минимальный пример `<div class="item-6">Hover me</div>`
- `meta.yaml` — метаданные (id, тип, дата импорта)

## Связанные концепты
- [[block-composition]] — паттерн подключается при сборке composed.html на этапе 07b
- [[design-tokens-generation]] — CSS-переменные `--t396-bgcolor-*` должны совпадать с токенами из `tokens.json`
- [[block-library-management]] — паттерн хранится в `block-library/_patterns/` и управляется через этот скилл

## Источник
- `block-library/_patterns/hover-effect-06-item-6/meta.yaml`
- `block-library/_patterns/hover-effect-06-item-6/styles.css`
- `block-library/_patterns/hover-effect-06-item-6/index.html`