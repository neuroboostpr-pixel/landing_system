---
type: block
name: hover-effect-07-item-7
sources: ["block-library/_patterns/hover-effect-07-item-7/meta.yaml"]
updated: 2026-05-25
triggers: []
stage: ""
uses: []
tags: ["pattern", "hover", "css", "animation", "block-library"]
---

# Hover Effect 07 — Item 7 (Hover-эффект)

## Что делает
Готовый CSS-паттерн hover-эффекта, извлечённый с реального сайта. Применяется к элементам блоков для добавления визуальной реакции при наведении курсора.

## Когда вызывать / в каком этапе
Используется на этапе **08 Build** при сборке WordPress-темы и Lazy Blocks блоков. Подключается дизайнером или block-composer'ом когда нужно добавить анимацию hover к карточкам, кнопкам или интерактивным элементам лендинга. Выбирается из block-library вручную или через `/landing-wireframe` при выборе вариантов блоков.

## Что на вход / на выход

**Вход:**
- Мета-файл `meta.yaml` с описанием паттерна
- CSS-исходник паттерна в папке `hover-effect-07-item-7/`

**Выход:**
- CSS-правила hover-эффекта, готовые к встраиванию в тему или inline-стили блока
- Визуальный эффект при наведении на целевой DOM-элемент

## Связанные концепты
- [[landing-design]] — этап генерации дизайн-системы, где определяются допустимые hover-стили
- [[landing-wireframe]] — wireframe-этап, на котором выбираются варианты блоков из block-library
- [[landing-compose]] — composed.html этап, куда встраиваются паттерны
- [[landing-build]] — финальная сборка темы, где CSS-паттерны интегрируются в блоки

## Источник
- `block-library/_patterns/hover-effect-07-item-7/meta.yaml`