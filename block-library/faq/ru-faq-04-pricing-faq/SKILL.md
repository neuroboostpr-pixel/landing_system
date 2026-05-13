---
name: ru-faq-04-pricing-faq
description: Пять вопросов-ответов в static-режиме (без collapse) на белом фоне с горизонтальными разделителями. Адаптирован из pricing-page (Apache-2.0).
---

# ru-faq-04-pricing-faq

## Когда применять

FAQ без collapse (всё видно сразу) — лучший выбор для landing-страниц где нет места для деталей. Белый фон выделяется от других FAQ-блоков в библиотеке.

## Slots

- `section-label` (text) — маленький лейбл раздела.
- `headline` (text, ≤60 char) — заголовок.
- `q-{1..5}` (text, ≤120 char) — вопросы.
- `a-{1..5}` (text, ≤400 char) — ответы.

## Conversion notes

- Вопросы = реальные возражения клиентов (стоимость, сроки, гарантии).
- Static FAQ на landing работает лучше accordion — клиент видит всё без кликов.

## Mobile considerations

Идентичен desktop. Ширина 375px.
