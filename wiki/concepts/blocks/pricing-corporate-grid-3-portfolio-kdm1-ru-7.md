---
type: block
name: pricing-corporate-grid-3-portfolio-kdm1-ru-7
sources: ["block-library/pricing/pricing-corporate-grid-3-portfolio-kdm1-ru-7/meta.yaml"]
updated: 2026-05-16
triggers: []
stage: "07b"
uses: ["block-composer", "ux-composer", "block-composition"]
tags: ["pricing", "corporate", "grid-3", "ru-market", "education", "services", "b2b-saas", "tech"]
---

# Pricing Corporate Grid-3 — Три тарифных карточки с преимуществами

## Что делает
Показывает три тарифных пакета в виде карточек-колонок: у каждой карточки — название, цена, список преимуществ и яркая кнопка-призыв. Подходит для страниц, где клиент должен выбрать один из трёх вариантов услуги.

## Когда вызывать / в каком этапе
Используется на этапе **07b (Compose)** — когда `block-composer` собирает `composed.html` из выбранных блоков. Блок подключается автоматически, если в `selections.yaml` (из wireframe.html) выбран этот вариант секции pricing. Вручную ссылаться не нужно.

## Что на вход / на выход

**Вход:**
- Обязательный текстовый слот `heading` — заголовок секции (например, «Выберите тариф»).
- Контент карточек (название пакета, цена, список фич, текст кнопки) берётся из `prototype.yaml` на этапе подстановки токенов.
- Дизайн-токены из `tokens.json` (цвета, шрифты) — инжектируются `block-composer`ом.

**Выход:**
- HTML-фрагмент блока pricing, встроенный в `07b_COMPOSED/composed.html`.
- Визуальных слотов (фото/иконки) нет — блок текстово-кнопочный, без анимаций (`has_animation: false`).

## Детали блока

| Параметр | Значение |
|---|---|
| Категория | pricing |
| Раскладка | grid-3 (три колонки) |
| Стиль | corporate |
| Анимация | нет |
| Рынок | RU |
| Ниши | education, services, b2b-saas, tech |
| Источник импорта | portfolio.kdm1.ru (PDF, codex-block-generation) |

## Связанные концепты
- [[block-composer]] — агент, который встраивает этот блок в `composed.html` на этапе 07b
- [[block-composition]] — скилл, описывающий полный процесс сборки блоков с токенами
- [[ux-composer]] — агент wireframe (07a), где пользователь выбирает этот блок среди вариантов
- [[block-library-management]] — скилл управления библиотекой; здесь хранится этот блок

## Источник
- `block-library/pricing/pricing-corporate-grid-3-portfolio-kdm1-ru-7/meta.yaml`