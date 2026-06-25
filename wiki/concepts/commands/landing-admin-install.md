---
slug: landing-admin-install
type: command
name: "Установить mu-plugin landing-config"
stage: "09"
tags: [mu-plugin, wordpress, beget, crm, rest-api, landing-config]
triggers: [/landing-admin-install]
inputs: [09-deploy]
outputs: [wp-landing-config]
gates: []
pre_reqs: [09-deploy, wp-landing-config]
related: [landing-deploy, landing-build, 08-kod, 13-segmenty-tsa]
sources: ["commands/landing-admin-install.md"]
updated: 2026-06-22
confidence: {stage: low}
---

# Установить mu-plugin landing-config

## Что делает

Разворачивает mu-plugin `landing-config` на сервере Beget через rsync из папки `skills/wp-landing-config/mu-plugin/landing-config/`. После копирования плагин активируется автоматически (mu-plugins always-active), создаёт per-blog таблицы `wp_<bid>_landing_leads` на всех subsites мультисайта и регистрирует REST endpoint `/wp-json/landing/v1/lead`. Финальный дымовой тест проверяет, что таблица и эндпоинт живы перед тем, как передать управление маркетологу.

## Когда вызывается

Вызывается вручную из корня landing-проекта (где лежит `.env`) после того, как WordPress уже задеплоен на Beget и базовая установка готова. Типичный момент — сразу после `/landing-deploy` или при первой настройке multisite-сегментов через `/landing-segment`.

## Вход → выход

**Вход:** корень landing-проекта с валидным `.env` (содержит BEGET_* credentials), задеплоенный WordPress на Beget (single-site или multisite).

**Выход:** mu-plugin `landing-config` установлен и активен; таблица `wp_<bid>_landing_leads` создана на каждом subsite; REST endpoint `/wp-json/landing/v1/lead` возвращает 200 на валидный POST с `pd_consent=1`; в wp-admin доступно меню «Лендинг» с подстраницами (Заявки / CTA / Head / Интеграции).

## Failure modes

- `.env` отсутствует или содержит неверные BEGET_* — rsync упадёт с auth-ошибкой, плагин не скопируется.
- WordPress ещё не задеплоен — `install-mu-plugin.sh` скопирует файлы в несуществующую папку, миграция БД не выполнится.
- В multisite не задан `BEGET_SITE_ID` — скрипт не определит blog_id subsites, таблицы создадутся только для главного сайта.
- REST endpoint возвращает 404 — некорректный `.htaccess` (нет `RewriteBase /slug/`); лечится по beget-cookbook §7.
- Smoke-тест падает с 400 — отсутствует поле `pd_consent` в тестовом POST-запросе; не баг плагина, а баг тест-скрипта.

## Related

- [[landing-deploy]] — предшествует установке; WP должен быть на сервере
- [[wp-landing-config]] — исходный скилл с mu-plugin кодом, скриптами установки и тестами
- [[08-kod]] — этап генерации темы; landing-config дополняет тему, не заменяет её
- [[13-segmenty-tsa]] — при мультисайте mu-plugin создаёт отдельные таблицы лидов на каждый сегмент