---
type: block
name: hover-effect-04-item-4
sources: ["block-library/_patterns/hover-effect-04-item-4/meta.yaml"]
updated: 2026-05-16
triggers: []
stage: ""
uses: []
tags: ["pattern", "hover", "css", "ui-effect", "block-library"]
---

# Hover 4 — CSS-паттерн эффекта наведения

## Что делает
Готовый CSS-паттерн эффекта при наведении курсора, извлечённый с реального сайта. Используется для добавления интерактивности к элементам блоков лендинга без написания кода с нуля.

## Когда вызывать / в каком этапе
Применяется на этапе **07b (Compose)** и **08 (Build)** при сборке блоков с интерактивными элементами. `block-composer` и `frontend-builder` могут подключать паттерн к любому блоку, которому нужен hover-эффект (карточки, кнопки, иконки, превью услуг).

## Что на вход / на выход
**Вход:** ссылка на паттерн по id `hover-effect-04-item-4` из block-library.

**Выход:** CSS-правила эффекта наведения, готовые к встраиванию в `block.php` или `tokens.json`-совместимый стиль.

**Метаданные:**
- `id`: hover-effect-04-item-4
- `import_method`: css-pattern-extraction
- `imported_at`: 2026-05-16

## Связанные концепты
- [[block-library-management]] — управляет коллекцией паттернов и их версионированием
- [[block-composition]] — этап, на котором паттерны встраиваются в composed.html
- [[frontend-builder]] — агент, применяющий паттерны при генерации CSS блоков
- [[design-tokens-generation]] — токены, с которыми должен быть совместим паттерн

## Источник
- `block-library/_patterns/hover-effect-04-item-4/meta.yaml`