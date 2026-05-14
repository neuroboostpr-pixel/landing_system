---
name: ru-quiz-02-progress-top
description: Sticky progress bar сверху квиза: текст "Вопрос N из M" слева и CSS progress bar справа.
---

# ru-quiz-02-progress-top

## Когда применять

Заголовок квиза — фиксированная полоса прогресса, которая всегда видна при прокрутке. Используется на всех шагах квиза.

## Slots

- `progress-text` (text, ≤20 char) — текст "Вопрос 2 из 5".

## Conversion notes

- Progress bar снижает отказы (пользователь видит прогресс и хочет завершить).
- Sticky позиция — всегда виден без прокрутки.
- CSS-only: width задаётся через inline style или CSS переменную.

## Mobile considerations

На mobile то же поведение, полная ширина экрана.
