---
name: wp-landing-config
description: Pre-built mu-plugin landing-config for WordPress Multisite — admin UI for CRM/CTA/head/SEO configuration without code. Use this skill to install the plugin on Beget and to integrate with deploy/segment scripts.
---

# wp-landing-config

mu-plugin `landing-config/` даёт маркетологу/клиенту настраивать:
- Интеграции (AmoCRM, Bitrix24, HubSpot, Telegram, WhatsApp, Email)
- Заявки (просмотр БД + экспорт CSV)
- CTA-кнопки (5 пресетов с per-site override)
- Head & SEO (GA4, Y.Metrika, FB Pixel, GSC, OG-теги, custom HTML)

Multisite-aware: network defaults + per-site override. Per-blog таблицы заявок.

Spec: [docs/superpowers/specs/2026-05-19-s2a-landing-config-revised.md](../../docs/superpowers/specs/2026-05-19-s2a-landing-config-revised.md)

## Установка на проект

```bash
bash skills/wp-landing-config/scripts/install-mu-plugin.sh <project-dir>
```

Или через slash-команду из текущего проекта:

```
/landing-admin-install
```

mu-plugin копируется в `<BEGET_PATH>/wp-content/mu-plugins/landing-config/` и автоматически активируется (mu-plugins always-active).

## Содержимое mu-plugin

- `landing-config.php` — bootstrap
- `includes/db.php` — таблицы wp_<bid>_landing_leads + lead_log
- `includes/encryption.php` — AES-256 для API-ключей
- `includes/helpers.php` — landing_config_get(), landing_get_cta(), landing_render_head_extras()
- `includes/rest-lead.php` — POST /wp-json/landing/v1/lead
- `includes/admin-{integrations,leads,cta,head-seo}.php` — admin страницы
- `adapters/` — 6 CRM/messenger adapters

## Артефакты на WP

- `wp_<bid>_landing_leads` — таблица заявок per-blog
- `wp_<bid>_landing_lead_log` — лог CRM-доставок per-blog
- `wp_options::landing_*` — per-site настройки
- `wp_sitemeta::landing_defaults_*` — network defaults
