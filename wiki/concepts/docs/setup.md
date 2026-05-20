---
type: rule
name: setup-guide
sources: ["docs/SETUP.md"]
updated: 2026-05-20
triggers: []
stage: ""
uses:
  - landing-onboarding
  - landing-orchestrator
  - landing-new
  - landing-go
  - landing-build
  - landing-deploy
  - wp-deployer
  - qa-auditor
  - analytics-engineer
  - seo-optimizer
tags: [setup, onboarding, installation, api, workflow-lock, stage-gate]
---

# Setup Guide — Руководство по установке системы

## Что делает
Пошаговый гайд по первой установке landing-system на новой машине: проверяет зависимости, объясняет API-ключи, описывает механику workflow lock и HARD GATE между этапами пайплайна.

## Когда вызывать / в каком этапе
Читается **один раз** при первом знакомстве с системой — до создания первого проекта. Является предусловием для `/landing-onboarding`. Без пройденного onboarding'а команда `/landing-new` не запустится — перенаправит сюда.

Также актуален при:
- переносе системы на новую машину;
- отладке заблокированного PreToolUse-хука;
- настройке ACF-полей для контент-менеджеров после деплоя.

## Что на вход / на выход

**Вход:** чистая машина без настроек, клонированный репозиторий `landing-system`.

**Выход:**
- Заполненный `.env` с валидными API-ключами (Firecrawl, Pexels, Yandex, Telegram и др.)
- Флаг `~/.landing-system/setup_complete` (создаёт `wizard.sh`)
- Настроенный SSH-доступ к серверу Бегет
- Установленные локальные зависимости: `wp-cli`, `rsync`, `python`, `jq`
- Подключённый PreToolUse-хук `enforce_stage_gate.py` в `.claude/settings.json`

**API-ключи (все free tier):** Firecrawl, Pexels, Unsplash, Pixabay, HuggingFace, Yandex Wordstat, Yandex Metrika, Telegram Bot, amoCRM/Bitrix24, Beget API, Cloudflare/Reg.ru.

## Ключевые правила из документа

- **Workflow lock:** в каждом проекте — `.landing-state.yaml` со статусами этапов (`locked` / `in_progress` / `approved`). Перепрыгивать этапы нельзя.
- **PreToolUse-хук** физически блокирует Write/Edit к файлам этапа, у которого не закрыты предшественники. При ошибке чтения — fail-open (пропускает с warning).
- **ACF-поля для менеджеров:** после деплоя весь редактируемый контент доступен через боковую панель WP-блоков без правки PHP. Схема полей — `08_КОД/acf-fields.json`.
- **Wiki-слои:** `landing-system/wiki/` (архитектура системы), `~/Lendings/<slug>/wiki/` (граф лендинга), `~/Lendings/<slug>/memory/` (память сессий).

## Связанные концепты
- [[landing-onboarding]] — wizard, который проходит все проверки и создаёт флаг setup_complete
- [[landing-go]] — главная точка входа после onboarding
- [[landing-orchestrator]] — дирижёр 12 этапов, использует `.landing-state.yaml`
- [[landing-build]] — требует `approved` для этапов 02–07 перед запуском
- [[wp-deployer]] — деплой на Бегет через SSH+rsync+wp-cli
- [[qa-auditor]] — этап 10, проверяет live-сайт

## Источник
- `docs/SETUP.md`