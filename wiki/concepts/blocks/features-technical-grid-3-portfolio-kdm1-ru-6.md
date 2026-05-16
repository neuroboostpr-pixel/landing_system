---
type: block
name: features-technical-grid-3-portfolio-kdm1-ru-6
sources: ["block-library/features/features-technical-grid-3-portfolio-kdm1-ru-6/meta.yaml"]
updated: 2026-05-16
triggers: []
stage: "07a"
uses: ["ux-composer", "block-composition", "wireframe-rendering"]
tags: ["features", "grid-3", "technical", "ru-market", "tech", "services", "ecommerce"]
---

# Технологический раздел с карточками преимуществ (grid-3)

## Что делает

Отображает раздел «Преимущества» или «Технологии» в виде трёх колонок карточек с миниатюрами производственного процесса и кнопкой-пояснением. Подходит для строгого, технического стиля без анимаций.

## Когда вызывать / в каком этапе

Используется на этапе **07a (UX Wireframe)** при выборе блока для секции «features» в прототипе. `ux-composer` подбирает его из библиотеки, если прототип содержит раздел с преимуществами/технологиями в сетке из трёх элементов. Актуален для ниш tech, services и ecommerce на русскоязычном рынке.

## Что на вход / на выход

**Вход:**
- Слот `heading` (text, обязательный) — заголовок раздела.
- Опционально: карточки с иконками/миниатюрами производства и текстами преимуществ (определяются контентом прототипа через `prototype.yaml`).

**Выход:**
- HTML-фрагмент блока, встраиваемый в `wireframe.html` (этап 07a) и `composed.html` (этап 07b) с подставленными design-tokens и текстом из прототипа.
- Плейсхолдеры для визуала (миниатюры производства), которые заполняются на этапах PR-B (фото) и PR-C (иконки/инфографика).

## Дополнительные характеристики

| Параметр | Значение |
|---|---|
| Категория | features |
| Раскладка | grid-3 |
| Настроение | technical |
| Анимация | нет |
| Русский рынок | да |
| Источник | portfolio.kdm1.ru (PDF) |
| Метод импорта | codex-block-generation |

## Связанные концепты

- [[ux-composer]] — выбирает этот блок из библиотеки при рендере wireframe.html
- [[block-composition]] — встраивает блок в composed.html с токенами и текстом
- [[wireframe-rendering]] — скилл, управляющий сборкой интерактивного wireframe
- [[block-library-management]] — отвечает за хранение и индексацию блока в библиотеке
- [[visual-curator]] — заполняет плейсхолдеры миниатюр на этапе 07d

## Источник

- `block-library/features/features-technical-grid-3-portfolio-kdm1-ru-6/meta.yaml`