---
type: block
name: hover-effect-02-item-2
sources: ["block-library/_patterns/hover-effect-02-item-2/meta.yaml"]
updated: 2026-05-25
triggers: []
stage: ""
uses: []
tags: ["pattern", "hover", "css", "effect", "block-library"]
---

# Hover Effect 02 — Item 2

## Что делает
Готовый CSS-паттерн hover-эффекта, извлечённый с реального сайта. Применяется к блокам лендинга для добавления анимации при наведении курсора, повышая визуальную интерактивность элементов.

## Когда вызывать / в каком этапе
Используется на этапе **07b (Compose)** и **08 (Build)** при сборке composed.html и генерации WordPress-темы. Подключается к блоку через атрибут паттерна в block-library, когда дизайнер или оркестратор выбирает hover-анимацию для карточек, кнопок или секций.

## Что на вход / на выход
**Вход:**
- Метаданные паттерна из `meta.yaml` (id, тип, описание, дата импорта)
- CSS-исходник hover-эффекта, хранящийся в папке паттерна

**Выход:**
- CSS-классы, подключаемые к HTML-элементам в composed.html
- Готовые стили для инъекции в `assets/css/main.css` темы WordPress

## Связанные концепты
- [[landing-compose]] — этап 07b, где паттерны hover-эффектов инъектируются в composed.html
- [[landing-design]] — этап 05, где формируется дизайн-система и выбираются визуальные паттерны
- [[landing-build]] — этап 08, где CSS-паттерны входят в финальную тему WordPress

## Источник
- `block-library/_patterns/hover-effect-02-item-2/meta.yaml`