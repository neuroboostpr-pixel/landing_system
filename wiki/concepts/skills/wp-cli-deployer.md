---
slug: wp-cli-deployer
type: skill
name: "WP-CLI Deployer"
stage: "09"
tags: [deploy, wordpress, beget, rsync, wp-cli, media-import]
triggers: [landing-deploy]
inputs:
  - 08_КОД/wp-theme/
  - 08_КОД/page-content.html
  - theme/assets/img/
  - .env
outputs:
  - deployed-wordpress-theme
  - media-library-attachments
  - front-page-seeded
gates: []
pre_reqs: [wp-builder, frontend-builder]
related: [wp-builder, qa-auditor, landing-orchestrator, frontend-builder]
sources: ["skills/wp-cli-deployer/SKILL.md"]
updated: 2026-05-26
confidence: {pre_reqs: low}
---

# WP-CLI Deployer

## Что делает

Скилл деплоит готовый WordPress-лендинг на хостинг Бегет: по SSH синхронизирует тему через `rsync`, активирует её, устанавливает необходимые плагины (`lazy-blocks`, ACF Free), импортирует изображения в Media Library, подставляет их attachment-ID в `page-content.html` и сидирует главную страницу как Gutenberg-страницу. После деплоя сбрасывает кэш и активирует `lp-preview-panel` (по умолчанию — только для администратора).

## Когда вызывается

Запускается командой `/landing-deploy` после того как этап 08 (генерация темы и page-content) одобрен пользователем. Является основным исполнителем девятого этапа pipeline.

## Вход → выход

**Вход:** собранная тема в `08_КОД/wp-theme/`, файл `08_КОД/page-content.html` с плейсхолдерами `__IMAGE_ATTACHMENT_ID__<file>__`, изображения в `theme/assets/img/`, переменные окружения `BEGET_USER`, `BEGET_HOST`, `BEGET_PATH` из `.env`.

**Выход:** задеплоенный WordPress-сайт с активной темой, медиа-файлы в Media Library с корректными ID, главная страница опубликована как Gutenberg-страница (front page), `lp-preview-panel` активирован.

## Failure modes

- **SSH/rsync недоступен** — неверные `BEGET_USER`/`BEGET_HOST` в `.env` или сервер не отвечает; деплой прерывается полностью.
- **Плейсхолдеры не подставлены** — если `wp media import` вернул неожиданный результат, page-content остаётся с буквальной строкой `__IMAGE_ATTACHMENT_ID__...`, и блоки не рендерятся.
- **Дублирование страниц** — при неидемпотентном прогоне (если slug front-page уже существует, но логика `wp post update` не сработала) создаются дубли страниц.
- **Плагины не установились** — `lazy-blocks` не найден в репозитории WP или нет интернета на сервере; блоки рендерятся пустыми.
- **`lp-preview-panel` показывает анонимам** — если флаг `visible_to_anon` включён случайно в продакшне, клиент видит дев-панель.

## Related

- [[wp-builder]] — генерирует тему и page-content, которые этот скилл деплоит
- [[frontend-builder]] — собирает CSS/JS ассеты темы до деплоя
- [[qa-auditor]] — запускается после деплоя и проверяет результат
- [[landing-orchestrator]] — управляет порядком этапов и запускает этот скилл на stage-09