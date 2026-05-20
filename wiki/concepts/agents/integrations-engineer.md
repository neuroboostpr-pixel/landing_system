---
type: agent
name: integrations-engineer
sources: ["agents/integrations-engineer.md"]
updated: 2026-05-20
triggers: []
stage: "08_build"
uses: ["wp-builder", "analytics-engineer", "stage-execution-protocol"]
tags: ["forms", "telegram", "crm", "webhooks", "stage-08"]
---

# integrations-engineer (Инженер интеграций)

## Что делает
Настраивает формы сбора заявок и вебхуки: подключает Fluent Forms к Telegram-боту и/или CRM-системе, чтобы каждый лид с лендинга мгновенно уходил в нужный канал.

## Когда вызывать / в каком этапе
Запускается на этапе **08_build**, строго после того, как [[wp-builder]] создал `functions.php` и `acf-fields.json`. До запуска агент проверяет `.landing-state.yaml` (должен быть `current_stage == 08_build`) и выполняет полный [[stage-execution-protocol]]: читает state, рисует Mermaid-карту, создаёт TodoWrite, прогоняет `gate-check.sh`. Если предшественники не закрыты — STOP.

## Что на вход / на выход

**Вход:**
- `08_КОД/wp-theme/functions.php` — создан wp-builder, содержит placeholder `// [FLUENT_WEBHOOK]`
- `08_КОД/acf-fields.json` — поле `form_id` для секции формы
- `.env` проекта — переменные `TELEGRAM_BOT_TOKEN`, `TELEGRAM_LEADS_CHAT_ID` и/или `CRM_WEBHOOK_URL`

**Выход:**
- `08_КОД/wp-theme/functions.php` — дополнен PHP-хуком отправки лида в Telegram и/или CRM

**Ход работы:**
1. Читает `.env` (или `.env.example`) — определяет, какие интеграции нужны.
2. Генерирует `lp_send_lead_to_telegram()` с `add_action('fluentform/submission_inserted', ...)` и вставляет вместо `// [FLUENT_WEBHOOK]`.
3. Если задан `CRM_WEBHOOK_URL` — добавляет аналогичный хук с `wp_remote_post` к CRM.
4. **HARD GATE:** показывает добавленный код пользователю и ждёт утверждения перед записью.

**Правила безопасности:**
- Токены только через `getenv()`, никакого хардкода.
- Все пользовательские данные оборачиваются в `esc_html()` перед отправкой.

## Связанные концепты
- [[wp-builder]] — создаёт `functions.php` до запуска этого агента
- [[analytics-engineer]] — следующий агент в цепочке этапа 08
- [[stage-execution-protocol]] — обязательный протокол перед любым Write/Edit

## Источник
- `agents/integrations-engineer.md`