---
type: agent
name: integrations-engineer
sources: ["agents/integrations-engineer.md"]
updated: 2026-05-15
triggers: []
stage: "08"
uses: ["wp-builder", "analytics-engineer"]
tags: ["forms", "webhook", "telegram", "crm", "fluent-forms", "functions.php"]
---

# Integrations Engineer (Инженер интеграций)

## Что делает
Настраивает формы захвата лидов и вебхуки: подключает Fluent Forms к Telegram-боту и/или CRM, чтобы каждая заявка с лендинга мгновенно уходила в нужный канал.

## Когда вызывать / в каком этапе
Этап **08**, строго после [[wp-builder]]. Активируется автоматически через [[landing-orchestrator]] или вручную в рамках команды `/landing-build`. Требует, чтобы `wp-builder` уже создал `functions.php`.

## Что на вход / на выход

**Вход:**
- `08_КОД/wp-theme/functions.php` — файл темы, созданный `wp-builder`; должен содержать placeholder `// [FLUENT_WEBHOOK]`
- `08_КОД/acf-fields.json` — поле `form_id` для секции формы
- `.env` проекта — переменные `TELEGRAM_BOT_TOKEN`, `TELEGRAM_LEADS_CHAT_ID` и/или `CRM_WEBHOOK_URL`

**Выход:**
- `08_КОД/wp-theme/functions.php` — дополнен PHP-хуком `lp_send_lead_to_telegram()` для Fluent Forms, плюс опциональным хуком отправки в CRM

**Логика добавления:**
1. Читает `.env` (или `.env.example`) — определяет, какие токены есть.
2. Если `TELEGRAM_BOT_TOKEN` + `TELEGRAM_LEADS_CHAT_ID` — добавляет хук `fluentform/submission_inserted` → `wp_remote_post` к Telegram API.
3. Если `CRM_WEBHOOK_URL` — добавляет аналогичный хук с отправкой данных формы на CRM-эндпоинт.
4. **HARD GATE**: показывает добавленный код и ждёт явного утверждения пользователя.

**Правила безопасности:**
- Токены никогда не хардкодятся — только через `getenv()`
- Все пользовательские данные экранируются через `esc_html()` перед отправкой

## Связанные концепты
- [[wp-builder]] — создаёт `functions.php` с placeholder `// [FLUENT_WEBHOOK]`, который этот агент заменяет
- [[analytics-engineer]] — следующий этап 08; добавляет счётчик Яндекс Метрики в тот же `functions.php`
- [[landing-orchestrator]] — управляет очерёдностью запуска агентов на этапе 08

## Источник
- `agents/integrations-engineer.md`