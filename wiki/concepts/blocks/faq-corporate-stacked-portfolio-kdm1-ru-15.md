---
type: block
name: faq-corporate-stacked-portfolio-kdm1-ru-15
sources: ["block-library/faq/faq-corporate-stacked-portfolio-kdm1-ru-15/meta.yaml"]
updated: 2026-05-16
triggers: []
stage: "07a"
uses: ["ux-composer", "block-composer", "wireframe-rendering", "block-composition"]
tags: ["faq", "corporate", "stacked", "dark-bg", "accordion", "ru-market", "b2b", "education", "services", "ecommerce"]
---

# FAQ — Компактный аккордеон на тёмном фоне (corporate stacked)

## Что делает

Отображает раздел «Вопросы и ответы» в виде компактных аккордеонных строк на тёмном фоне. Подходит для корпоративных лендингов, где важно сэкономить место и выглядеть солидно: каждый вопрос раскрывается по клику, фон тёмный, стиль строгий.

## Когда вызывать / в каком этапе

Блок подключается на этапе **07a (Wireframe)** агентом [[ux-composer]], который выбирает его из библиотеки под тип ниши. Используется повторно на этапе **07b (Compose)** агентом [[block-composer]], который подставляет реальный текст и токены дизайна.

Подходящие ниши: `services`, `education`, `b2b-saas`, `ecommerce`. Ориентирован на российский рынок (`ru_market: true`). Анимация отсутствует (`has_animation: false`), что ускоряет загрузку и упрощает вёрстку.

## Что на вход / на выход

**Вход:**
- Слот `heading` (обязательный, тип `text`) — заголовок секции FAQ.
- Пары вопрос/ответ передаются через прототип (`prototype.yaml`) или вручную в `composed.html`.
- Токены дизайна из `tokens.json` (цвета, шрифты тёмной темы).

**Выход:**
- HTML-фрагмент блока FAQ, интегрированный в `wireframe.html` (07a) и `composed.html` (07b).
- Аккордеонные строки готовы к наполнению контентом без JS-зависимостей (CSS-only или минимальный JS).

## Связанные концепты

- [[ux-composer]] — выбирает блок из библиотеки при построении wireframe.html
- [[block-composer]] — вставляет токены и тексты на этапе composed.html
- [[wireframe-rendering]] — скилл, управляющий рендером 07a
- [[block-composition]] — скилл, управляющий рендером 07b
- [[block-library-management]] — скилл поддержки и пополнения библиотеки блоков

## Источник

- `block-library/faq/faq-corporate-stacked-portfolio-kdm1-ru-15/meta.yaml`
- Импортирован из: `https://portfolio.kdm1.ru/...` методом `codex-block-generation` (2026-05-16)