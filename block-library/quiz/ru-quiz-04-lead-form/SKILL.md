---
name: ru-quiz-04-lead-form
description: Финальный экран квиза — собирает контакты. Только Telegram + Max Messenger + телефон (запрещённые мессенджеры исключены).
---

# ru-quiz-04-lead-form

## Когда применять

Последний шаг квиза после всех вопросов — точка сбора лида.

## Slots

- `headline` (text, ≤80 char) — призыв оставить контакт. Обязательный.
- `subhead` (text, ≤140 char) — что получит пользователь.
- `phone-input` — поле телефона. Обязательное.
- `name-input` — поле имени. Опциональное.
- `channel-choice` — radio-кнопки: Telegram / Max / звонок. Обязательное.
- `submit-cta` (cta, default "Получить расчёт") — обязательная.
- `agreement-text` (text) — согласие на обработку ПД.

## Conversion notes

- **Только разрешённые мессенджеры** — Telegram и Max (запрещённые платформы исключены).
- Max Messenger обязателен (растущая аудитория в РФ).
- Согласие на ПД — checkbox по умолчанию НЕ отмечен (152-ФЗ требует opt-in).

## Mobile considerations

Поля во всю ширину, channel-choice вертикальный stack.
