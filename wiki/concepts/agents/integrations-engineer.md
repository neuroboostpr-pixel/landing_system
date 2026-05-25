---
type: agent
name: integrations-engineer
sources: ["agents/integrations-engineer.md"]
updated: 2026-05-25
triggers: []
stage: "08"
uses: ["landing-orchestrator", "wp-builder", "stage-execution-protocol"]
tags: ["integrations", "telegram", "crm", "fluent-forms", "stage-08", "webhooks"]
---

# Integrations Engineer (Инженер интеграций)

## Что делает
Настраивает передачу заявок с лендинга в Telegram и CRM: добавляет вебхуки в WordPress-тему так, чтобы каждый новый лид сразу уходил менеджеру в мессенджер или в CRM-систему.

## Когда вызывать / в каком этапе
Вызывается на **этапе 08 (build)** — после того как `wp-builder` создал файл `functions.php` темы. Агент не запускается сам: его вызывает `landing-orchestrator` в рамках stage 08. Требуется, чтобы `current_stage == 08_build` в `.landing-state.yaml`; если нет — агент останавливается и сообщает об ошибке.

## Что на вход / на выход

**Вход:**
- `08_КОД/wp-theme/functions.php` — создан `wp-builder`, содержит плейсхолдер `// [FLUENT_WEBHOOK]`
- `08_КОД/block-spec.yaml` — блок `form` с полем `form_id`
- `.env` проекта с переменными `TELEGRAM_BOT_TOKEN`, `TELEGRAM_LEADS_CHAT_ID` и/или `CRM_WEBHOOK_URL`

**Выход:**
- `08_КОД/wp-theme/functions.php` — дополнен PHP-хуком на событие `fluentform/submission_inserted`: отправка лида в Telegram и/или CRM через `wp_remote_post`

## Как работает (шаги)
1. Читает `.env` (или `.env.example`) — определяет, какие интеграции активны.
2. Генерирует PHP-сниппет для Telegram: форматирует данные лида в сообщение, вызывает Bot API через `wp_remote_post`.
3. Если задан `CRM_WEBHOOK_URL` — добавляет аналогичный хук с отправкой `form_data` на CRM-эндпоинт.
4. **HARD GATE:** показывает добавленный код пользователю и ждёт явного утверждения перед сохранением.

## Правила безопасности
- Токены и URL вебхуков — **только через `getenv()`**, никогда не хардкодятся в код.
- Все пользовательские данные экранируются через `esc_html()` перед отправкой.

## Связанные концепты
- [[wp-builder]] — создаёт `functions.php`, который этот агент дополняет
- [[landing-orchestrator]] — вызывает агента как часть pipeline stage 08
- [[stage-execution-protocol]] — обязательный протокол: проверка `.landing-state.yaml`, Mermaid-карта, gate-check перед любым изменением файлов

## Источник
- `agents/integrations-engineer.md`