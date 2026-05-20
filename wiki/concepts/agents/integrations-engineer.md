---
type: agent
name: integrations-engineer
sources: ["agents/integrations-engineer.md"]
updated: 2026-05-20
triggers: []
stage: "08"
uses: ["wp-builder", "analytics-engineer", "landing-build"]
tags: ["integrations", "fluent-forms", "telegram", "crm", "webhook", "stage-08"]
---

# Integrations Engineer — Агент интеграций форм и вебхуков

## Что делает
Настраивает формы захвата лидов на лендинге: подключает Fluent Forms к Telegram-боту и CRM-системе. После его работы каждая заявка с лендинга автоматически уходит в чат и/или CRM.

## Когда вызывать / в каком этапе
Запускается на **этапе 08 (08_build)** после того, как [[wp-builder]] создал тему и `functions.php`. Следует за wp-builder, предшествует [[analytics-engineer]]. Вызывается в рамках команды [[landing-build]] (или `/landing-go`).

Перед запуском агент обязан:
1. Проверить `.landing-state.yaml` — убедиться, что `current_stage == 08_build`.
2. Показать Mermaid-карту pipeline через `render-pipeline-map.sh`.
3. Пройти gate-check (`gate-check.sh --stage 08_build`) — при exit ≠ 0 остановиться.

## Что на вход / на выход

**Вход:**
- `08_КОД/wp-theme/functions.php` — создан wp-builder, содержит placeholder `// [FLUENT_WEBHOOK]`
- `08_КОД/block-spec.yaml` — блок `form` с полем `form_id`
- `.env` проекта с переменными `TELEGRAM_BOT_TOKEN`, `TELEGRAM_LEADS_CHAT_ID` и/или `CRM_WEBHOOK_URL`

**Выход:**
- `08_КОД/wp-theme/functions.php` — дополнен PHP-хуком `lp_send_lead_to_telegram` для отправки лида в Telegram, и опционально — хуком для CRM через `wp_remote_post`

**Ограничения безопасности:**
- Токены и URL хранятся только в переменных окружения (`getenv()`), не хардкодятся.
- Все данные пользователя экранируются через `esc_html()` перед отправкой.

**HARD GATE:** агент показывает добавленный код и ждёт явного утверждения пользователя перед записью в файл.

## Связанные концепты
- [[wp-builder]] — создаёт `functions.php` и wp-тему, которую дополняет этот агент
- [[analytics-engineer]] — следующий агент в цепочке этапа 08
- [[landing-build]] — скилл-оркестратор этапа 08, в контексте которого запускается агент

## Источник
- `agents/integrations-engineer.md`