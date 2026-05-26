---
slug: wp-landing-config
type: skill
name: "WP Landing Config — mu-plugin для настройки лендинга"
stage: "08"
tags: [wordpress, multisite, crm, cta, seo, admin-ui, mu-plugin]
triggers: [landing-admin-install]
inputs: [project-dir]
outputs: [wp-content/mu-plugins/landing-config/]
gates: []
pre_reqs: [wp-builder, wp-deployer]
related: [integrations-engineer, analytics-engineer, frontend-builder, seo-optimizer]
sources: ["skills/wp-landing-config/SKILL.md"]
updated: 2026-05-26
confidence: {stage: low, pre_reqs: low}
---

# WP Landing Config — mu-plugin для настройки лендинга

## Что делает

Устанавливает готовый mu-plugin `landing-config` в WordPress Multisite, который даёт маркетологу и клиенту настраивать ключевые параметры сайта прямо из wp-admin без правки кода. Покрывает шесть областей: CRM-интеграции (AmoCRM, Bitrix24, HubSpot, Telegram, WhatsApp, Email), просмотр и экспорт заявок из БД, CTA-кнопки с пятью пресетами, Head & SEO (GA4, Яндекс.Метрика, FB Pixel, GSC, OG-теги, custom HTML), настройки Cookie-banner и статусы заявок. Полностью multisite-aware: поддерживает network defaults и per-site override для каждого поддомена (сегмента ЦА).

## Когда вызывается

Вызывается вручную через slash-команду `/landing-admin-install` после того, как WordPress-тема задеплоена на Бегет (этап 08–09). Также может быть запущен напрямую bash-скриптом `skills/wp-landing-config/scripts/install-mu-plugin.sh <project-dir>`. Интеграция с оркестратором — задача будущего PR.

## Вход → выход

**Вход:** директория проекта (`<project-dir>`) с настроенным `.env` (переменные `BEGET_*`), задеплоенным WordPress и доступом по SSH.

**Выход:** mu-plugin скопирован в `<BEGET_PATH>/wp-content/mu-plugins/landing-config/` и активен автоматически (mu-plugins always-active). В БД созданы per-blog таблицы `wp_<bid>_landing_leads` и `wp_<bid>_landing_lead_log`. В `wp_options` и `wp_sitemeta` появляются ключи `landing_*` и `landing_defaults_*`.

## Failure modes

- **SSH/rsync ошибка** — неверные `BEGET_*` переменные или закрытый порт; скрипт упадёт на копировании файлов.
- **Таблицы не создались** — если wp-cli не запущен после копирования, `dbDelta()` не отработает; нужен `wp plugin activate` или ручной `wp eval`.
- **Multisite не активирован** — на single-site сайте network defaults и per-site cascade не работают; нужно сначала выполнить migrate-to-multisite.
- **Конфликт с B1-файлами** — старые `cookie-banner.*` и `consent-init.php` из template/08_КОД конфликтуют с mu-plugin; B2 удалил их, но на проектах до B2 нужна ручная очистка.
- **API-ключи в открытом виде** — если `includes/encryption.php` не инициализирован или константа `LANDING_ENCRYPTION_KEY` не задана, адаптеры сохраняют ключи без AES-256.

## Related

- [[wp-builder]] — генерирует тему; mu-plugin устанавливается поверх неё
- [[wp-deployer]] — деплоит файлы на Бегет; mu-plugin копируется тем же SSH-каналом
- [[integrations-engineer]] — конфигурирует CRM-адаптеры, которые реализует этот mu-plugin
- [[analytics-engineer]] — Head & SEO настройки (GA4/Метрика/Pixel) управляются через admin-ui mu-plugin
- [[seo-optimizer]] — SEO-параметры (OG, GSC, llms.txt) хранятся в опциях mu-plugin