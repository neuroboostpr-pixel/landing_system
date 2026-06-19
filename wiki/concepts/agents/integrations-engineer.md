---
slug: integrations-engineer
type: agent
name: "Инженер интеграций"
stage: "08"
tags: [integrations, telegram, crm, fluent-forms, webhooks, stage-08]
triggers: [landing-build]
inputs:
  - 08_КОД/wp-theme/functions.php
  - 08_КОД/block-spec.yaml
  - .env
outputs:
  - 08_КОД/wp-theme/functions.php
gates: []
pre_reqs: [wp-builder, 08-kod]
related: [wp-builder, frontend-builder, landing-build, landing-deploy]
sources: ["agents/integrations-engineer.md"]
updated: 2026-06-19
confidence: {triggers: low}
---

# Инженер интеграций

## Что делает

Настраивает формы захвата лидов и вебхуки для готовой WordPress-темы в рамках этапа 08. Читает переменные окружения проекта, генерирует PHP-сниппеты для отправки заявок в Telegram и/или CRM, вставляет хуки в `functions.php` вместо плейсхолдера `// [FLUENT_WEBHOOK]`. Работает строго после `wp-builder`, который создаёт `functions.php`. Перед записью любых изменений обязательно показывает сгенерированный код пользователю и ждёт явного подтверждения (HARD GATE).

## Когда вызывается

Запускается вручную или оркестратором в рамках этапа `08_build`, после того как `wp-builder` сформировал тему и `block-spec.yaml` содержит блок `form` с полем `form_id`. Условие активации: в `.landing-state.yaml` поле `current_stage == 08_build`.

## Вход → выход

**Вход:** `08_КОД/wp-theme/functions.php` с плейсхолдером `// [FLUENT_WEBHOOK]`; `08_КОД/block-spec.yaml` с описанием формы; `.env` (или `.env.example`) с переменными `TELEGRAM_BOT_TOKEN`, `TELEGRAM_LEADS_CHAT_ID` и/или `CRM_WEBHOOK_URL`.

**Выход:** `08_КОД/wp-theme/functions.php` дополнен рабочим PHP-хуком на `fluentform/submission_inserted` — отправляет данные лида в Telegram-бот и/или на CRM-вебхук через `wp_remote_post`.

## Failure modes

- **Отсутствует плейсхолдер** `// [FLUENT_WEBHOOK]` в `functions.php` — агент не знает куда вставить код и останавливается с ошибкой.
- **Нет токенов в `.env`** — при отсутствии `TELEGRAM_BOT_TOKEN` / `CRM_WEBHOOK_URL` хук добавляется, но runtime-отправка беззвучно пропускается (условие `if (!$token)` внутри функции).
- **`current_stage` не `08_build`** — `enforce_stage_gate.py` физически блокирует Write/Edit, агент должен сообщить об этом, а не пытаться обойти.
- **Пользователь отказал на HARD GATE** — изменения не вносятся; агент ждёт правки или новых инструкций.
- **Двойной вызов** — повторное добавление хука вызывает дублирование PHP-функции и фатальную ошибку WP; агент обязан проверить, нет ли уже `lp_send_lead_to_telegram` в файле.

## Related

- [[wp-builder]] — создаёт `functions.php` и `block-spec.yaml`, обязательный предшественник
- [[landing-build]] — родительский скилл этапа 08, диспатчит инженера интеграций
- [[frontend-builder]] — собирает тему рядом с этим агентом в рамках того же этапа
- [[landing-deploy]] — следующий этап после 08, деплоит тему на Бегет с готовыми интеграциями