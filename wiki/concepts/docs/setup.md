---
type: rule
name: setup-guide
sources: ["docs/SETUP.md"]
updated: 2026-05-20
triggers: []
stage: ""
uses: ["landing-onboarding", "system-setup", "landing-orchestrator", "landing-new", "landing-build", "landing-deploy", "landing-qa", "wp-deployer", "analytics-engineer", "seo-optimizer"]
tags: ["setup", "onboarding", "api", "workflow-lock", "acf", "wiki"]
---

# Setup Guide — Установка и первый запуск

## Что делает

Полный гайд по первичной установке landing-system на новой машине. Описывает зависимости, API-ключи, порядок onboarding'а и workflow-lock — систему, которая не даёт пропускать обязательные этапы.

## Когда вызывать / в каком этапе

Читается один раз при первом развёртывании системы на машине — до запуска любой `/landing-*` команды. Без прохождения onboarding'а команды будут падать с ошибкой и направлять сюда.

## Что на вход / на выход

**На вход:**
- Клонированный репозиторий `landing-system`
- Доступ к Beget SSH, аккаунтам Firecrawl / Pexels / Yandex / Telegram

**На выход:**
- Файл флага `~/.landing-system/setup_complete` — подтверждение готовности
- Заполненный `.env` с валидными API-ключами
- Настроенный Firecrawl MCP в `~/.claude/settings.json`
- Установленный хук `.githooks/post-commit` для авто-синхронизации wiki

**Ключевые концепции, описанные в гайде:**

1. **Workflow lock** — `.landing-state.yaml` в каждом проекте фиксирует статусы 13 этапов (`locked` / `in_progress` / `approved`). `/landing-build` не запустится, пока этапы 02–07 не имеют статус `approved`.

2. **API-список** — 13 сервисов (Firecrawl, Pexels, Unsplash, Pixabay, HuggingFace, Yandex Wordstat, Yandex Metrika, Telegram Bot, amoCRM/Bitrix24, Beget API, Cloudflare, Reg.ru) — все с free tier.

3. **ACF и Gutenberg** — после деплоя менеджеры редактируют тексты через WP-admin без PHP. Если поля исчезли — импортировать `08_КОД/acf-fields.json` через deploy-скрипт.

4. **Wiki-слои** — три уровня: `landing-system/wiki/` (архитектура), `~/Lendings/<slug>/wiki/` (проект), `~/Lendings/<slug>/memory/` (сессии). Bootstrap занимает ~30 мин.

5. **PreToolUse hook** — с 2026-05-20 хук `enforce_stage_gate.py` блокирует Write/Edit в файлы этапа, чьи предыдущие этапы не закрыты.

## Связанные концепты

- [[landing-onboarding]] — команда первичной настройки, описана в этом гайде
- [[system-setup]] — агент, запускаемый внутри `/landing-onboarding`
- [[landing-orchestrator]] — главный дирижёр, работает только после setup_complete
- [[landing-new]] — создание проекта, требует пройденного onboarding'а
- [[landing-build]] — этап 08, проверяет workflow-lock перед запуском
- [[wp-deployer]] — деплой на Beget, упоминается в troubleshooting
- [[analytics-engineer]] — использует Yandex Metrika API из `.env`
- [[seo-optimizer]] — использует Yandex Wordstat API из `.env`

## Источник

- `docs/SETUP.md`