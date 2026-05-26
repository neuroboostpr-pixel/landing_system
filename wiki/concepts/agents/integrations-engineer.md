---
slug: integrations-engineer
type: agent
stage: "08"
tags: [integrations, telegram, crm, fluent-forms, webhooks, stage-08, php]
triggers: [landing-build]
inputs:
  - 08_КОД/wp-theme/functions.php
  - 08_КОД/block-spec.yaml
  - .env
outputs:
  - 08_КОД/wp-theme/functions.php
gates: [integrations-approved]
pre_reqs: [wp-builder]
related: [landing-build, landing-deploy]
sources: ["agents/integrations-engineer.md"]
updated: 2026-05-26
confidence:
  triggers: low
  pre_reqs: low
---

# Integrations Engineer (Инженер интеграций)

## Что делает

Агент настраивает интеграцию форм лендинга с внешними сервисами: Telegram-ботом и CRM-системой через вебхуки. Работает на этапе 08 после того, как `wp-builder` создал базовую тему. Дополняет `functions.php` PHP-хуками на событие отправки формы Fluent Forms, чтобы каждый новый лид мгновенно уходил в Telegram-чат и/или CRM. Токены и URL не хардкодятся — агент читает их из переменных окружения `.env` проекта.

## Когда вызывается

Вызывается вручную или оркестратором на этапе `08_build`, после того как `wp-builder` создал `functions.php` и в нём присутствует placeholder `// [FLUENT_WEBHOOK]`. Требует, чтобы в `.env` были заданы `TELEGRAM_BOT_TOKEN` и `TELEGRAM_LEADS_CHAT_ID` (для Telegram) и/или `CRM_WEBHOOK_URL` (для CRM).

## Вход → выход

**Вход:** `08_КОД/wp-theme/functions.php` с placeholder-ом `// [FLUENT_WEBHOOK]`; `08_КОД/block-spec.yaml` с блоком `form`; `.env` (или `.env.example`) с ключами `TELEGRAM_BOT_TOKEN`, `TELEGRAM_LEADS_CHAT_ID`, `CRM_WEBHOOK_URL`.

**Выход:** дополненный `functions.php` с PHP-функциями `lp_send_lead_to_telegram` и/или `lp_send_lead_to_crm`, привязанными к хуку `fluentform/submission_inserted`. После показа кода пользователю и его одобрения этап помечается `approved`.

## Чем закрывается этап (gates)

- `integrations-approved` — агент показывает добавленный PHP-код пользователю и ждёт явного утверждения (HARD GATE). Без утверждения переход к следующему этапу заблокирован.

## Failure modes

- `.env` не содержит нужных ключей — агент падает с предупреждением, интеграция не добавляется; нужно вручную заполнить `.env` и перезапустить.
- `// [FLUENT_WEBHOOK]` placeholder отсутствует в `functions.php` — агент не знает куда вставить код; нужно проверить, что `wp-builder` отработал корректно.
- `current_stage != 08_build` в `.landing-state.yaml` — агент останавливается по Stage Execution Protocol и сообщает о нарушении порядка этапов.
- `gate-check.sh` возвращает ненулевой exit — агент не начинает Write/Edit, пока не устранены причины.
- Токены попадают в код напрямую (нарушение security rules) — агент явно запрещает это и использует только `getenv()`.

## Related

- [[landing-build]] — команда этапа 08, в рамках которой вызывается агент
- [[landing-deploy]] — следующий этап после закрытия 08; интеграции должны быть утверждены до деплоя