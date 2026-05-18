---
type: block
name: animation-01-checkicondraw
sources: ["block-library/_patterns/animation-01-checkicondraw/meta.yaml"]
updated: 2026-05-16
triggers: []
stage: "07b"
uses: ["block-composer", "block-composition"]
tags: ["animation", "css", "keyframe", "pattern", "icon"]
---

# Animation checkIconDraw — анимация прорисовки галочки

## Что делает
CSS-паттерн с keyframe-анимацией, которая плавно «прорисовывает» иконку галочки (check mark) — как будто её рисуют от руки. Используется для визуального акцента на преимуществах, подтверждениях или шагах услуги.

## Когда вызывать / в каком этапе
Подключается на этапе **07b (Block Compose)** при сборке `composed.html`. Агент [[block-composer]] выбирает паттерн, когда в прототипе или wireframe есть блок с галочками — списки преимуществ, чеклисты, иконки «выполнено». Паттерн не требует отдельной команды — подключается как CSS-зависимость нужного блока.

## Что на вход / на выход

**Вход:**
- `meta.yaml` с id, типом и описанием паттерна
- Контекст блока, в котором нужна анимация галочки (из `composed.html` или `wireframe.html`)

**Выход:**
- CSS keyframe `@keyframes checkIconDraw`, готовый к встраиванию в стили блока
- Анимированный SVG- или CSS-элемент галочки в финальном `composed.html`

## Связанные концепты
- [[block-composer]] — агент-сборщик, который подключает паттерн при рендере composed.html
- [[block-composition]] — скилл этапа 07b, управляет инъекцией паттернов в блоки
- [[ux-composer]] — строит wireframe.html, где закладываются слоты под иконки-галочки
- [[design-tokens-generation]] — токены цвета и тайминга могут переопределять параметры анимации

## Источник
- `block-library/_patterns/animation-01-checkicondraw/meta.yaml`