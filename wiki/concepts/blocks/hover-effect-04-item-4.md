---
type: block
name: hover-effect-04-item-4
sources: ["block-library/_patterns/hover-effect-04-item-4/meta.yaml"]
updated: 2026-05-25
triggers: []
stage: ""
uses: []
tags: ["pattern", "hover", "css-effect", "animation", "block-library"]
---

# Hover 4 — CSS-эффект при наведении

## Что делает
Готовый визуальный CSS-паттерн hover-эффекта, извлечённый с реального сайта. Применяется к элементам блоков лендинга для создания интерактивной анимации при наведении курсора.

## Когда вызывать / в каком этапе
Используется на этапе **07b (Compose)** и **08 (Build)** при сборке composed.html и генерации WordPress-темы. Подключается к блокам, которым нужна визуальная интерактивность — карточки услуг, преимущества, элементы галереи. Выбирается вручную через wireframe-вариант или указывается в design-system.

## Что на вход / на выход

**Вход:**
- `meta.yaml` с метаданными паттерна (id, type, name, description, import_method)
- CSS-файл паттерна в папке `block-library/_patterns/hover-effect-04-item-4/`

**Выход:**
- CSS-классы / стили, которые инжектируются в composed.html и итоговую тему
- Визуальный hover-эффект на целевом элементе блока

## Связанные концепты
- [[landing-compose]] — этап 07b, где паттерны применяются к блокам composed.html
- [[landing-wireframe]] — этап 07a, где пользователь выбирает варианты блоков с эффектами
- [[landing-design]] — этап 05, формирует design-system, определяет допустимые визуальные паттерны
- [[landing-build]] — этап 08, финальная сборка темы с подключёнными CSS-паттернами

## Источник
- `block-library/_patterns/hover-effect-04-item-4/meta.yaml`