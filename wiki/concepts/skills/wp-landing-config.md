---
type: skill
name: wp-landing-config
sources: ["skills/wp-landing-config/SKILL.md"]
updated: 2026-05-25
triggers: []
stage: ""
uses: ["landing-admin-install", "landing-orchestrator", "landing-segment"]
tags: ["wordpress", "mu-plugin", "multisite", "crm", "admin-ui"]
---

# wp-landing-config — плагин настройки лендинга без кода

## Что делает

Устанавливает готовый WordPress mu-plugin, который даёт маркетологу и клиенту управлять всеми настройками лендинга через визуальный wp-admin — без редактирования кода. Покрывает интеграции с CRM, кнопки CTA, SEO-теги и просмотр входящих заявок.

## Когда вызывать / в каком этапе

Устанавливается после деплоя WordPress (этап 08–09) через команду `/landing-admin-install` или bash-скрипт `install-mu-plugin.sh`. Необходим перед тем, как маркетолог начнёт настраивать интеграции и получать заявки. Работает в single-site и multisite (Beget) режимах.

## Что на вход / на выход

**Вход:**
- Директория проекта `<project-dir>` с настроенным WordPress на Beget
- Переменные окружения `BEGET_PATH`, `BEGET_*` (SSH-реквизиты)
- Опционально: `brand-kit.md` с реквизитами для автозаполнения OG/SEO полей

**Выход:**
- mu-plugin `landing-config/` в `wp-content/mu-plugins/` (активируется автоматически)
- REST-эндпоинт `POST /wp-json/landing/v1/lead` для приёма форм
- Таблицы БД: `wp_<bid>_landing_leads` и `wp_<bid>_landing_lead_log` (per-blog)
- Настройки: `wp_options::landing_*` (per-site), `wp_sitemeta::landing_defaults_*` (network)
- Admin-страницы: Интеграции / Заявки / CTA / Head & SEO в wp-admin

## Ключевые возможности

| Раздел | Функции |
|---|---|
| Интеграции | AmoCRM, Bitrix24, HubSpot, Telegram, WhatsApp, Email — 6 адаптеров |
| CTA | 5 пресетов кнопок с per-site override |
| Head & SEO | GA4, Y.Metrika, FB Pixel, GSC, OG-теги, custom HTML в head |
| Заявки | просмотр БД + экспорт CSV, лог CRM-доставок |

Multisite-aware: network defaults переопределяются per-site. API-ключи шифруются AES-256 (`includes/encryption.php`). Лид-форма защищена honeypot-полем и rate-limit 10 req/hour per IP.

## Связанные концепты

- [[landing-admin-install]] — slash-команда, которая вызывает установку этого плагина
- [[landing-orchestrator]] — оркестратор этапов, на 08/09 которого плагин деплоится
- [[landing-segment]] — создаёт новые WP-субсайты, для которых плагин создаёт per-blog таблицы
- [[landing-deploy]] — этап 09, после которого нужна установка плагина

## Источник

- `skills/wp-landing-config/SKILL.md`