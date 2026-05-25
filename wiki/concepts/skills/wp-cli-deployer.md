---
type: skill
name: wp-cli-deployer
sources: ["skills/wp-cli-deployer/SKILL.md"]
updated: 2026-05-25
triggers: []
stage: "09"
uses: ["landing-deploy", "landing-orchestrator", "landing-build"]
tags: ["deploy", "wordpress", "beget", "rsync", "wp-cli", "theme", "media"]
---

# wp-cli-deployer — деплой WordPress-лендинга на Бегет

## Что делает

Автоматически разворачивает готовый лендинг на хостинг Бегет: синхронизирует тему, активирует плагины, импортирует изображения в Media Library, подставляет их ID в page-content и создаёт главную страницу как Gutenberg-страницу.

## Когда вызывать / в каком этапе

Вызывается командой `/landing-deploy` на этапе **09 — деплой**. Запускается после того, как этап 08 (сборка темы) утверждён пользователем. `landing-orchestrator` передаёт управление этому скиллу автоматически.

## Что на вход / на выход

**На вход:**
- `08_КОД/wp-theme/` — собранная WordPress-тема
- `08_КОД/page-content.html` — Gutenberg page-content с placeholders `__IMAGE_ATTACHMENT_ID__<file>__`
- `.env` — переменные `BEGET_USER`, `BEGET_HOST`, `BEGET_PATH`

**На выход:**
- Активная тема на сервере Бегет
- Плагины установлены и активированы (`lazy-blocks`, `lp-preview-panel`)
- Изображения импортированы в WP Media Library (идемпотентно)
- Главная страница создана/обновлена как Gutenberg-страница с реальными attachment ID вместо placeholders
- Кэш сброшен

## Ключевые шаги скрипта

1. **rsync** — синхронизация темы на сервер по SSH
2. **`wp theme activate`** — активация темы
3. **Plugins** — установка `lazy-blocks`; ACF Free остаётся как no-op (без `wp acf import`)
4. **Media import** — `wp media import` для каждого файла в `assets/img/*`, идемпотентно (пропускает уже загруженные по slug)
5. **Page-content substitution** — замена placeholders на integer attachment ID
6. **Front page seed** — создание или обновление главной страницы, установка как front page через `wp option update`
7. **`wp cache flush`** — сброс кэша

## Плагин lp-preview-panel

После активации плагин по умолчанию показывает превью-панель только администратору. Для клиентского доступа — вручную включить в admin → Settings → Превью-панель. Перед анонсом деплоя: проверить поведение панели в incognito-окне.

## Связанные концепты

- [[landing-deploy]] — slash-команда, которая запускает этот скрипт
- [[landing-orchestrator]] — оркестратор, вызывающий деплой на этапе 09
- [[landing-build]] — предшествующий этап 08, результат которого деплоится

## Источник

- `skills/wp-cli-deployer/SKILL.md`