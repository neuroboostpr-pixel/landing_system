# Landing System — Setup Guide

Полный гайд по первой установке landing-system на новой машине.

## 1. Что такое landing-system

Агентская система для производства WordPress-лендингов. Пайплайн из 12 этапов: бриф → ресёрч → бренд → дизайн → контент → код → деплой → QA. Каждый этап ведёт специализированный агент.

## 2. Как устроены агенты

- `landing-orchestrator` — главный дирижёр, проводит через все этапы
- 18 специализированных агентов (один на этап / задачу)
- Каждый агент работает в режиме HARD GATE: не идёт дальше без явного approve пользователя

## 3. Как работает workflow lock

В каждом проекте есть файл `.landing-state.yaml` — фиксирует статус каждого этапа (`locked` / `in_progress` / `approved`).

`/landing-build` проверяет, что этапы 02–07 имеют статус `approved`. Если хотя бы один не пройден — команда падает с ошибкой. **Перепрыгивать этапы нельзя**, даже по явной просьбе.

## 4. Зачем onboarding

Все API-ключи нужны до старта первого проекта. Если запустить `/landing-new` без onboarding'а, команда направит на `/landing-onboarding`.

Onboarding делает:
- Проверяет локальные зависимости (`wp-cli`, `ssh`, `rsync`, `python`, `jq`)
- Проверяет, что плагин `superpowers` установлен
- Проверяет, что Firecrawl MCP настроен в `~/.claude/settings.json`
- Создаёт `.env` из `.env.example` и просит заполнить
- Валидирует каждый API-ключ тестовым запросом
- Создаёт флаг `~/.landing-system/setup_complete`

## 5. Быстрый старт

```bash
git clone https://github.com/neuroboostpr-pixel/landing_system.git
cd landing_system
bash scripts/wizard.sh
# или внутри Claude Code:
/landing-onboarding
```

## 6. Команды (краткая справка)

| Команда | Назначение |
|---|---|
| `/landing-onboarding` | Первичная настройка (один раз на машину) |
| `/landing-new <slug>` | Создать новый проект |
| `/landing-references` | Этап 03: референсы |
| `/landing-brand` | Этап 04: бренд-кит |
| `/landing-design` | Этап 05: дизайн-система |
| `/landing-stack` | Этап 06: стек |
| `/landing-content` | Этап 07: контент |
| `/landing-build` | Этап 08: WP-сборка (механика — блоки, контент, скелеты) |
| `/landing-style` | Этап 08b: per-block CSS + layout-aware block.php (frontend-builder) |
| `/landing-deploy` | Этап 09: деплой |
| `/landing-qa` | Этап 10: QA |
| `/landing-status` | Статус проекта |

## 7. Список API (все бесплатные free tier)

| Сервис | Зачем | Где взять |
|---|---|---|
| Firecrawl | Парсинг сайтов и отзывов | https://firecrawl.dev |
| Pexels | Стоковые фото | https://www.pexels.com/api/ |
| Unsplash | Стоковые фото (alt) | https://unsplash.com/developers |
| Pixabay | Стоковые фото + векторы | https://pixabay.com/api/docs/ |
| HuggingFace | Генерация картинок (опц.) | https://huggingface.co/settings/tokens |
| WhatTheFont | Определение шрифтов | https://www.myfonts.com/pages/whatthefont-api |
| Yandex Wordstat | SEO | https://oauth.yandex.ru |
| Yandex Metrika | Аналитика | https://metrika.yandex.ru |
| Telegram Bot | Уведомления | @BotFather |
| amoCRM / Bitrix24 | CRM | https://amocrm.ru / https://bitrix24.ru |
| Beget API | DNS, SSH | https://beget.com/ru/kb/api |
| Cloudflare | DNS (опц.) | https://dash.cloudflare.com |
| Reg.ru | DNS (опц.) | https://www.reg.ru |

## 8. Troubleshooting

- `wp-cli` отсутствует → `brew install wp-cli` (macOS)
- Python пакеты не найдены → `pip install -r requirements.txt`
- SSH к Бегету не работает → проверь `ssh-copy-id user@srv.beget.ru`
- Onboarding застрял → удали `~/.landing-system/setup_complete` и запусти заново

## ACF and Gutenberg blocks for managers

After deployment, the landing page exposes every text-editable element as an ACF field in the WordPress block sidebar. Managers can:

1. Open `/wp-admin`, navigate to the page.
2. Click any landing block in the editor canvas.
3. Use the right-hand sidebar form to edit headings, body text, button labels, prices, etc.
4. Repeater fields (e.g., pricing tiers, program modules) show as a list with **+ Add** and drag handles.
5. Click **Update** to publish.

No PHP edits required. To learn what fields each block has, see `08_КОД/acf-fields.json` in the project repo.

### When fields are missing

If the WordPress editor shows an empty block sidebar:

1. Verify ACF plugin is active: WP admin → Plugins → Advanced Custom Fields → Active.
2. Verify the ACF JSON was imported: WP admin → ACF → Field Groups → there should be groups named after each landing section (Hero, Pricing, etc.).
3. If groups are missing, re-import: from the project folder run `bash skills/wp-cli-deployer/scripts/deploy-wordpress.sh <project-dir>` — the deploy script now imports ACF fields and fails loudly if it can not.

## Wiki разметка (PR-F)

Система ведёт три слоя wiki:

- `landing-system/wiki/` — карта архитектуры (агенты, скиллы, команды, этапы)
- `~/Lendings/<slug>/wiki/` — граф структуры конкретного лендинга
- `~/Lendings/<slug>/memory/` — память сессий по этому проекту

Хуки `SessionStart` / `SessionEnd` / `PreCompact` инжектят индексы и сохраняют уроки автоматически.

### Bootstrap

```bash
bash scripts/wiki/bootstrap-system.sh    # ~30 мин, использует Claude Max подписку
```

### Миграция существующего проекта

```bash
bash scripts/migrate-add-wiki.sh ~/Lendings/<slug>
```

### Obsidian (опционально)

Папки `wiki/` и `memory/` совместимы с [Obsidian](https://obsidian.md/) — можно открыть как vault и увидеть граф связей.

Опционально для удобства:
- [Obsidian Web Clipper](https://obsidian.md/clipper) — сохранять статьи прямо в `wiki/raw/` (если будешь компилировать внешние материалы)
- Плагин **Local Images Plus** — скачивать картинки в vault а не оставлять ссылки

Подробнее: [spec](superpowers/specs/2026-05-15-wiki-graph-markup-design.md), [plan](superpowers/plans/2026-05-15-wiki-graph-pr-f1-plan.md).

## Когда нужен multisite-режим

Single-site (по умолчанию):
- У клиента **один лендинг** под одну аудиторию.
- Домен — один без поддоменов.

Multisite (через `/landing-segment`):
- У клиента **несколько лендингов** под разные сегменты ЦА.
- Используются поддомены одного клиентского домена.
- Один wp-admin управляет всеми сегментами.

### Миграция single → multisite

Автоматическая. При первом запуске `/landing-segment <slug>` для проекта,
у которого `state.multisite=false`, запускается
`skills/wp-multisite/scripts/migrate-to-multisite.sh`. Он:
1. Создаёт wildcard subdomain в DNS через Beget API.
2. Активирует `WP_ALLOW_MULTISITE` в `wp-config.php`.
3. Запускает `wp core multisite-convert --subdomains`.
4. Переписывает `.htaccess` под multisite (subdomain mode).
5. Сетевая активация Lazy Blocks + RankMath SEO.
6. Флипает `state.multisite=true`.

После миграции существующий лендинг становится `blog_id=1` (главным сайтом
сети). Контент не теряется.

### Pre-requisites

Помимо стандартных переменных `.env`, нужно:
- `BEGET_SITE_ID` — числовой id «сайт-сущности» на Бегете (из `site/getList`).
- `BEGET_DOMAIN_ID` — числовой id корневого домена (из `domain/getList`).
- `ROOT_DOMAIN` — fqdn корневого клиентского домена.

### SSL после миграции

**Manual one-click через панель Beget** (Домены → SSL → бесплатный wildcard
Let's Encrypt). Покрывает все existing и future subdomains.
Beget сам обновляет каждые 60 дней. Скрейп-автоматизация — следующая фаза.

См. [docs/beget-cookbook.md §SSL](beget-cookbook.md).

## Установка mu-plugin landing-config

После создания multisite-проекта (через `/landing-segment`) — установить admin-плагин:

```
/landing-admin-install
```

Плагин копируется в `<BEGET_PATH>/wp-content/mu-plugins/landing-config/` и
автоматически активируется (mu-plugins always-active). Создаёт таблицы
`wp_<bid>_landing_leads` + `wp_<bid>_landing_lead_log` в каждом subsite.

В wp-admin появляется меню «Лендинг» с подстраницами:
- Заявки (список + CSV export)
- CTA-кнопки (5 пресетов)
- Head & SEO (счётчики, OG, GSC, raw HTML)
- Интеграции (6 адаптеров + Test connection)

Network admin показывает «Лендинг» → «Заявки (все сегменты)» — сводный просмотр со всех subsite.

### Pre-requisites

`.env` должен содержать BEGET_USER/HOST/SSH_KEY/PATH (стандартные).
Дополнительных переменных НЕ требуется — все настройки рантайм через wp-admin.

### Безопасность

API-ключи (Telegram bot token, AmoCRM access token, etc.) шифруются AES-256-GCM
с ключом из `wp_salt('secure_auth')`. В админке отображаются masked (bullets + последние 4 символа).

### Email-fallback

`wp_mail` использует PHP `mail()` если SMTP не настроен. На Beget shared
письма часто попадают в спам. Рекомендация: настроить SMTP через любой
plugin типа WP Mail SMTP, либо использовать email-fallback только как back-up.

### Retry политика

Если CRM-доставка падает (HTTP != 2xx), задача планируется через
`wp_schedule_single_event` с backoff: 60 сек → 5 мин → 30 мин (max 3 попытки).
Каждая попытка логируется в `wp_<bid>_landing_lead_log`.
