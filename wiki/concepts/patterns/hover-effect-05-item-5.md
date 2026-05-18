---
type: block
name: hover-effect-05-item-5
sources: ["block-library/_patterns/hover-effect-05-item-5/meta.yaml"]
updated: 2026-05-16
triggers: []
stage: "07b"
uses: ["block-composer", "block-composition"]
tags: ["pattern", "hover", "css", "ui-effect"]
---

# Hover 5 — эффект наведения (паттерн)

## Что делает
Готовый CSS-паттерн hover-эффекта, извлечённый с реального сайта. Применяется к элементам лендинга, чтобы при наведении мыши карточка, кнопка или блок визуально реагировали — оживляя интерфейс без JavaScript.

## Когда вызывать / в каком этапе
Используется на этапе **07b (Compose)** — при сборке `composed.html`. Агент [[block-composer]] подключает паттерн к нужным блокам, когда wireframe содержит интерактивные элементы (карточки услуг, кнопки CTA, галереи). Паттерн выбирается из библиотеки вручную или автоматически скиллом [[block-composition]] на основе типа блока.

## Что на вход / на выход

**Вход:**
- `meta.yaml` с описанием паттерна (id, name, import_method)
- CSS-файл эффекта (в той же папке паттерна)
- Контекст блока из `prototype.yaml` или `wireframe.html`

**Выход:**
- CSS-класс или фрагмент стилей, подключённый в `composed.html`
- Hover-поведение на целевых элементах страницы

## Связанные концепты
- [[block-composer]] — агент, который собирает `composed.html` и подключает паттерны
- [[block-composition]] — скилл управления выбором блоков и паттернов из библиотеки
- [[block-library-management]] — скилл добавления и обновления паттернов в библиотеке
- [[ux-composer]] — создаёт wireframe, в котором указываются слоты для hover-эффектов

## Источник
- `block-library/_patterns/hover-effect-05-item-5/meta.yaml`