---
type: block
name: features-technical-grid-3-portfolio-kdm1-ru-5
sources: ["block-library/features/features-technical-grid-3-portfolio-kdm1-ru-5/meta.yaml"]
updated: 2026-05-16
triggers: []
stage: "07a"
uses:
  - ux-composer
  - block-composer
  - block-composition
tags: [features, grid-3, technical, dark-background, ru-market, education, b2b-saas, services, tech]
---

# Информационный блок: тёмный фон, большой заголовок, три карточки

## Что делает

Секция «Фичи/Преимущества» с тёмным фоном: крупный заголовок вверху и три карточки контента в сетке. Подходит для технических и деловых лендингов, где нужно акцентированно показать три ключевых тезиса или продуктовых преимущества.

## Когда вызывать / в каком этапе

Используется на **этапе 07a (Wireframe)** — агент `ux-composer` выбирает блок из библиотеки при сборке `wireframe.html`. Также применяется на **этапе 07b (Compose)** — агент `block-composer` подставляет реальный контент из `prototype.yaml` в слот `heading` и рендерит `composed.html`.

Подходит для ниш: **education**, **services**, **b2b-saas**, **tech**. Ориентирован на русскоязычный рынок (`ru_market: true`). Анимации отсутствуют (`has_animation: false`), что ускоряет загрузку и упрощает верстку.

## Что на вход / на выход

**Вход:**

| Слот | Тип | Обязателен | Описание |
|------|-----|-----------|----------|
| `heading` | text | ✅ да | Большой заголовок секции |

Карточки контента подразумеваются структурой шаблона (grid-3), но их содержимое берётся из `prototype.yaml` через `block-composition`.

**Выход:**

HTML-фрагмент блока с тёмным фоном и сеткой из трёх карточек. Встраивается в `wireframe.html` (как кандидат) или в `composed.html` (как финальный блок с токенами дизайна).

## Метаданные импорта

Блок сгенерирован методом `codex-block-generation` из PDF-источника:
- Источник: `portfolio.kdm1.ru` (онлайн-школа Дмитрия Выходцева)
- Дата импорта: 2026-05-16

## Связанные концепты

- [[ux-composer]] — отбирает этот блок при построении wireframe на этапе 07a
- [[block-composer]] — рендерит финальный composed.html, подставляя контент в слоты
- [[block-composition]] — скилл, описывающий правила сборки блоков с токенами и текстами
- [[block-library-management]] — скилл управления библиотекой, в которой живёт этот блок

## Источник

- `block-library/features/features-technical-grid-3-portfolio-kdm1-ru-5/meta.yaml`