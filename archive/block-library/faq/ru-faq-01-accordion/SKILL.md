---
name: ru-faq-01-accordion
description: 6 вопросов-ответов в виде native HTML аккордеона через тег details. Без JavaScript.
---

# ru-faq-01-accordion

## Когда применять

Секция "Частые вопросы" для всех ниш — снимает последние возражения перед конверсией.

## Slots

- `headline` (text, ≤60 char) — заголовок секции.
- `faq-1-q` (text, ≤100 char) — вопрос 1 (внутри summary).
- `faq-1-a` (text, ≤400 char) — ответ 1.
- `faq-2-q` (text, ≤100 char) — вопрос 2.
- `faq-2-a` (text, ≤400 char) — ответ 2.
- `faq-3-q` (text, ≤100 char) — вопрос 3.
- `faq-3-a` (text, ≤400 char) — ответ 3.
- `faq-4-q` (text, ≤100 char) — вопрос 4.
- `faq-4-a` (text, ≤400 char) — ответ 4.
- `faq-5-q` (text, ≤100 char) — вопрос 5.
- `faq-5-a` (text, ≤400 char) — ответ 5.
- `faq-6-q` (text, ≤100 char) — вопрос 6.
- `faq-6-a` (text, ≤400 char) — ответ 6.

## Conversion notes

- Аккордеон через native details — без JS, доступно, SEO-friendly.
- 6 вопросов — оптимально: не перегружает, закрывает основные возражения.
- Самые частые возражения ставить первыми.

## Mobile considerations

Аккордеон работает одинаково на desktop и mobile — адаптивен по умолчанию.
