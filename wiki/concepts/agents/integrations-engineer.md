---
type: agent
name: integrations-engineer
sources: ["agents/integrations-engineer.md"]
updated: 2026-05-26
triggers: []
stage: "08_build"
uses: ["wp-builder", "landing-orchestrator", "stage-execution-protocol"]
tags: ["integrations", "fluent-forms", "telegram", "crm", "webhooks", "stage-08"]
---

# Integrations Engineer (Инженер интеграций)

## Что делает

Настраивает отправку лидов с лендинга во внешние системы: добавляет в WordPress PHP-хуки, которые при заполнении формы отправляют данные в Telegram-чат и/или CRM через вебхук.

## Когда вызывать / в каком этапе

Запускается на **этапе 08 (08_build)**, после того как `wp-builder` создал базовую тему и файл `functions.php`. Вызывается агентом `landing-orchestrator` автоматически или вручную при наличии формы в `block-spec.yaml`.

Предусловия перед выполнением:
1. `current_stage == 08_build` в `.landing-state.yaml`.
2. Успешный `gate-check.sh --stage 08_build`.
3. Наличие `08_КОД/wp-theme/functions.php` с плейсхолдером `// [FLUENT_WEBHOOK]`.
4. Наличие `08_КОД/block-spec.yaml` с блоком `form` и полем `form_id`.
5. Переменные окружения в `.env`: `TELEGRAM_BOT_TOKEN`, `TELEGRAM_LEADS_CHAT_ID` и/или `CRM_WEBHOOK_URL`.

## Что на вход / на выход

**Вход:**
- `.env` проекта с токенами Telegram и/или адресом CRM-вебхука
- `08_КОД/wp-theme/functions.php` (подготовлен `wp-builder`)
- `08_КОД/block-spec.yaml` — для определения наличия блока формы

**Выход:**
- Дополненный `08_КОД/wp-theme/functions.php` с PHP-хуками:
  - `fluentform/submission_inserted` → отправка лида в Telegram (`wp_remote_post` к Bot API)
  - Опциональный второй хук → `wp_remote_post` на `CRM_WEBHOOK_URL`

**HARD GATE:** перед записью агент показывает добавленный код и ждёт явного утверждения пользователем.

**Правила безопасности:**
- Токены читаются только через `getenv()` — хардкод запрещён
- Все пользовательские данные экранируются через `esc_html()` перед отправкой

## Связанные концепты

- [[wp-builder]] — создаёт `functions.php` с плейсхолдером `// [FLUENT_WEBHOOK]`, который этот агент заполняет
- [[landing-orchestrator]] — диспатчит агента как часть pipeline этапа 08
- [[stage-execution-protocol]] — обязательный протокол проверки gate-check и показа Mermaid-карты перед любым Write/Edit

## Источник

- `agents/integrations-engineer.md`