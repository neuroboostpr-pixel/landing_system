---
type: skill
name: wp-cli-deployer
sources: ["skills/wp-cli-deployer/SKILL.md"]
updated: 2026-05-15
triggers: []
stage: "09"
uses: ["wp-deployer", "landing-deploy", "wp-builder"]
tags: ["deploy", "wordpress", "beget", "rsync", "wp-cli"]
---

# wp-cli-deployer — Деплой WordPress-темы на Бегет

## Что делает

Автоматически разворачивает готовую WordPress-тему на хостинге Бегет: синхронизирует файлы, активирует тему и плагины, импортирует изображения в Media Library и наполняет главную страницу финальным Gutenberg-контентом.

## Когда вызывать / в каком этапе

Этап **09 (Deploy)**. Вызывается командой `/landing-deploy` или агентом [[wp-deployer]] после того, как этап 08 (Build) завершён и `08_КОД/wp-theme/` содержит готовую тему. Требует заполненных переменных `BEGET_USER`, `BEGET_HOST`, `BEGET_PATH` в файле `.env`.

## Что на вход / на выход

**Вход:**
- `08_КОД/wp-theme/` — собранная тема WordPress
- `08_КОД/page-content.html` — Gutenberg-контент главной страницы с плейсхолдерами `__IMAGE_ATTACHMENT_ID__<file>__`
- `theme/assets/img/*` — изображения, которые нужно импортировать в Media Library
- `.env` с SSH-кредами

**Выход:**
- Тема активирована на сервере через `wp theme activate`
- Плагины `lazy-blocks` (и `lp-preview-panel`) установлены и активированы
- Изображения импортированы в Media Library (идемпотентно: повторный прогон не дублирует)
- Главная страница создана/обновлена (`wp post create / update`), плейсхолдеры заменены на реальные attachment ID
- Фронтпейдж переключён через `wp option update show_on_front page`
- Кэш сброшен (`wp cache flush`)

## Ключевые детали реализации

- **Идемпотентность:** медиа-импорт проверяет slug перед загрузкой; страница ищется по slug и обновляется, если уже существует — повторный деплой безопасен.
- **lp-preview-panel:** панель превью активируется автоматически, но по умолчанию скрыта от анонимов. Перед передачей клиенту рекомендуется проверить в режиме инкогнито.
- **ACF:** плагин остаётся установлен как no-op; `wp acf import` больше не вызывается (упрощение от предыдущей версии).
- Точка входа — `scripts/deploy-wordpress.sh <project-dir>`.

## Связанные концепты

- [[wp-deployer]] — агент этапа 09, вызывает этот скилл
- [[landing-deploy]] — slash-команда, триггерящая деплой
- [[wp-builder]] — предшествующий скилл этапа 08, создаёт `08_КОД/wp-theme/`

## Источник

- `skills/wp-cli-deployer/SKILL.md`