---
type: block
name: animation-02-checkiconopacity
sources: ["block-library/_patterns/animation-02-checkiconopacity/meta.yaml"]
updated: 2026-05-16
triggers: []
stage: "07b"
uses: ["block-composer", "block-composition"]
tags: ["animation", "css", "keyframe", "pattern", "icon"]
---

# Animation checkIconOpacity — анимация появления иконки галочки

## Что делает
CSS-паттерн с keyframe-анимацией `checkIconOpacity`: плавно показывает иконку галочки (check icon) через изменение прозрачности. Используется для визуального подтверждения действий — галочки в чекбоксах, статусах «выполнено», шагах онбординга.

## Когда вызывать / в каком этапе
Подключается на этапе **07b (Compose)** — когда `block-composer` собирает `composed.html` и инжектит дизайн-токены. Паттерн автоматически подтягивается из библиотеки блоков, если в wireframe или прототипе есть слоты с иконкой галочки или анимированными чекбоксами.

Метод импорта: `css-pattern-extraction` — паттерн был извлечён из CSS-исходников, а не написан вручную.

## Что на вход / на выход

**Вход:**
- Слот в wireframe или composed.html, где нужна анимированная иконка-галочка.
- Дизайн-токены (цвет, время анимации) из `tokens.json`.

**Выход:**
- CSS keyframe-правило `@keyframes checkIconOpacity` (opacity от 0 до 1).
- Готовый к подключению CSS-фрагмент, который `block-composer` инлайнит в блок или подключает через `<style>`.

## Связанные концепты
- [[block-composer]] — агент, который собирает composed.html и использует паттерны из block-library на этапе 07b.
- [[block-composition]] — скилл, описывающий правила сборки блоков с токенами и паттернами.
- [[block-library-management]] — скилл управления библиотекой блоков, куда входит этот паттерн.
- [[07b-composed]] — этап, на котором паттерн фактически применяется.

## Источник
- `block-library/_patterns/animation-02-checkiconopacity/meta.yaml`