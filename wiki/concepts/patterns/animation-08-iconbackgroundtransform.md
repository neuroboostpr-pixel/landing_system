---
type: block
name: animation-08-iconbackgroundtransform
sources: ["block-library/_patterns/animation-08-iconbackgroundtransform/meta.yaml"]
updated: 2026-05-16
triggers: []
stage: "07b"
uses: ["block-composer", "design-tokens-generation"]
tags: ["animation", "css", "keyframe", "icon", "pattern"]
---

# Animation — iconBackgroundTransform

## Что делает
CSS-паттерн анимации через `@keyframes`: плавно трансформирует фон иконки (цвет, масштаб, форму или позицию) при ховере или при появлении блока на экране. Добавляет лёгкое визуальное «дыхание» к иконочным элементам без JavaScript.

## Когда вызывать / в каком этапе
Используется на этапе **07b (Compose)** — агент `block-composer` инжектирует CSS-паттерны из библиотеки в `composed.html` вместе с токенами дизайна. Паттерн подключается автоматически, если блок содержит иконки с hover-эффектами или scroll-trigger анимациями. Явно вызывать не нужно — `block-composer` сам выбирает подходящие паттерны по типу блока.

## Что на вход / на выход

**Вход:**
- `meta.yaml` — декларация паттерна (id, name, import_method)
- CSS-файл с `@keyframes iconBackgroundTransform` (в той же папке паттерна)
- Токены из `tokens.json` (цвета бренда, радиусы, тени)

**Выход:**
- CSS-класс (или `@keyframes` блок), готовый к встраиванию в `composed.html` / `block.php`
- Анимированный фон иконки: трансформация scale/color/shape по timeline ключевых кадров

## Связанные концепты
- [[block-composer]] — оркестрирует сборку `composed.html`, подключает CSS-паттерны
- [[design-tokens-generation]] — поставляет переменные цвета и размеров для keyframe-значений
- [[block-composition]] — скилл-владелец этапа 07b, управляет паттернами анимаций
- [[visual-generation]] — смежный скилл: генерирует сами иконки (PNG), которые потом анимируются этим паттерном

## Источник
- `block-library/_patterns/animation-08-iconbackgroundtransform/meta.yaml`