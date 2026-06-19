---
slug: integrations-engineer
type: agent
name: "Инженер интеграций"
stage: "08"
tags: [integrations, fluent-forms, telegram, crm, webhooks, php]
triggers: [landing-build]
inputs: [08-kod]
outputs: [08-kod]
gates: []
pre_reqs: [wp-builder, 08-kod]
related: [wp-builder, landing-build, analytics-engineer, wp-gutenberg-block-builder]
sources: ["agents/integrations-engineer.md"]
updated: 2026-06-19
confidence: {triggers: low, gates: low}
---

# Инженер интеграций

## Что делает

Настраивает приём заявок с лендинга: подключает обработчики событий Fluent Forms в `functions.php` — отправку лида в Telegram-бота и опционально в CRM через вебхук. Читает переменные окружения из `.env`, генерирует PHP-сниппеты с `wp_remote_post`, соблюдает правила безопасности (токены только через `getenv()`, вывод через `esc_html()`). После добавления кода показывает результат пользователю и ждёт явного утверждения перед продолжением.

## Когда вызывается

Запускается вручную на этапе 08 после того, как `wp-builder` создал `wp-theme/functions.php` с заглушкой `// [FLUENT_WEBHOOK]`. Требует, чтобы `block-spec.yaml` содержал блок `form`, а `.env` проекта имел `TELEGRAM_BOT_TOKEN` и `TELEGRAM_LEADS_CHAT_ID` (или `CRM_WEBHOOK_URL`).

## Вход → выход

**Вход:** `08_КОД/wp-theme/functions.php` с заглушкой `// [FLUENT_WEBHOOK]`; `08_КОД/block-spec.yaml` с блоком `form`; `.env` проекта с токенами интеграций.

**Выход:** `08_КОД/wp-theme/functions.php` дополнен хуком `fluentform/submission_inserted` — Telegram-отправка и/или CRM-вебхук через `wp_remote_post`.

## Failure modes

- `.env` не содержит `TELEGRAM_BOT_TOKEN` — сниппет добавляется, но при вызове хука ничего не отправляется (тихий пропуск через `if (!$token) return`).
- `functions.php` не содержит заглушки `// [FLUENT_WEBHOOK]` — агент не знает куда вставить код, требуется ручная правка.
- `block-spec.yaml` отсутствует или не имеет блока `form` — нет `form_id`, форма не привязана.
- Fluent Forms не активирован на сайте — хук `fluentform/submission_inserted` не срабатывает, лиды молча теряются.
- Хардкодинг токенов в коде вместо `getenv()` — нарушение security rules, токен утекает в git.

## Related

- [[wp-builder]] — создаёт `functions.php` с заглушкой, которую заполняет этот агент
- [[landing-build]] — родительский этап 08, в рамках которого вызывается агент
- [[analytics-engineer]] — параллельный агент этапа 08, настраивает аналитику
- [[wp-gutenberg-block-builder]] — генерирует `block-spec.yaml` с описанием блоков форм