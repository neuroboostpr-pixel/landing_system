---
type: block
name: features-technical-grid-3-portfolio-kdm1-ru-2
sources: ["block-library/features/features-technical-grid-3-portfolio-kdm1-ru-2/meta.yaml"]
updated: 2026-05-16
triggers: []
stage: "07a"
uses: ["ux-composer", "block-composition", "wireframe-rendering"]
tags: ["features", "grid-3", "technical", "dark", "ru-market", "b2b-saas", "services", "education", "tech"]
---

# Features: Тёмная сетка проблемных карточек (technical-grid-3)

## Что делает
Отображает секцию «Проблемы / Возможности» в тёмном фоне: крупный заголовок и сетка из трёх карточек с минималистичными маркерами. Подходит для лаконичного перечисления болей клиента или ключевых тезисов без визуального шума.

## Когда вызывать / в каком этапе
Используется на этапе **07a (Wireframe)** агентом [[ux-composer]] при подборе блока для секции «Features» / «Проблемы». Подключается автоматически через [[wireframe-rendering]] по совпадению категории `features` + layout `grid-3` + mood `technical`. Может быть выбран вручную через [[block-composition]] на этапе 07b.

Нишевые сигналы активации: проект в категории `services`, `b2b-saas`, `education` или `tech` + прототип содержит раздел с перечнем проблем клиента.

## Что на вход / на выход

**Вход:**
- Слот `heading` (text, обязательный) — крупный заголовок секции
- Дизайн-токены из `tokens.json` (цвета, шрифты) — инжектируются автоматически на этапе 07b

**Выход:**
- HTML-фрагмент тёмной секции с сеткой 3-колонок для встраивания в `wireframe.html` / `composed.html`
- Блок помечен `has_animation: false` — никакой JS-анимации не требуется

## Технические характеристики
| Параметр | Значение |
|---|---|
| Категория | features |
| Layout | grid-3 |
| Стиль | technical |
| Анимация | нет |
| Рынок | RU |
| Источник импорта | codex-block-generation (portfolio.kdm1.ru, 2026-05-16) |

## Связанные концепты
- [[ux-composer]] — выбирает блок из библиотеки при построении wireframe
- [[wireframe-rendering]] — рендерит интерактивный wireframe.html с этим блоком
- [[block-composition]] — инжектирует токены и тексты прототипа в блок на этапе 07b
- [[block-library-management]] — управляет реестром блоков, включая этот

## Источник
- `block-library/features/features-technical-grid-3-portfolio-kdm1-ru-2/meta.yaml`