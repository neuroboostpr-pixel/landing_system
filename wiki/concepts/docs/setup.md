---
type: rule
name: setup-guide
sources: ["docs/SETUP.md"]
updated: 2026-05-18
triggers:
  - "как установить систему"
  - "первый запуск на новой машине"
  - "настройка API-ключей"
  - "onboarding с нуля"
stage: ""
uses:
  - landing-orchestrator
  - landing-onboarding
  - wp-deployer
  - system-setup
  - landing-new
  - landing-build
  - landing-deploy
  - landing-qa
tags: [setup, onboarding, api, dependencies, workflow-lock]
---

# Setup Guide — Установка landing-system на новой машине

## Что делает

Пошаговый гайд по первичной настройке landing-system: установка зависимостей, регистрация API-ключей и активация workflow lock. После прохождения машина полностью готова к созданию WordPress-лендингов.

## Когда вызывать / в каком этапе

Выполняется **один раз** на новой машине до запуска любого проекта. Если флаг `~/.landing-system/setup_complete` отсутствует — команды `/landing-new` и `/landing-*` автоматически перенаправляют сюда. Триггер: `/landing-onboarding` или `bash scripts/wizard.sh`.

## Что на вход / на выход

**Вход:**
- Установленный git, Python, `wp-cli`, `ssh`, `rsync`, `jq`
- Плагин `superpowers` в Claude Code
- Firecrawl MCP в `~/.claude/settings.json`
- Заполненный `.env` (13 API-ключей: Firecrawl, Pexels, Unsplash, Pixabay, HuggingFace, Yandex Wordstat, Yandex Metrika, Telegram Bot, amoCRM/Bitrix24, Beget API, Cloudflare/Reg.ru)

**Выход:**
- Флаг `~/.landing-system/setup_complete`
- Валидированный `.env` с рабочими ключами
- Готовая рабочая среда для 12-этапного pipeline

## Ключевые правила

- **Workflow lock**: каждый проект имеет `.landing-state.yaml` со статусами этапов (`locked` / `in_progress` / `approved`). Этапы 02–07 должны быть `approved` перед `/landing-build`.
- **Нет перепрыгивания**: `landing-orchestrator` не пропускает этапы даже по явной просьбе.
- **HARD GATE**: каждый агент ждёт явного approve перед переходом к следующему этапу.
- **ACF-поля**: после деплоя все текстовые блоки редактируются в WP-админке без PHP — через боковую панель ACF.

## Связанные концепты

- [[landing-onboarding]] — команда, запускающая wizard установки
- [[landing-orchestrator]] — главный дирижёр 12-этапного pipeline
- [[system-setup]] — агент, выполняющий preflight-проверки и конфигурацию
- [[landing-new]] — создание проекта (требует пройденного onboarding)
- [[wp-deployer]] — деплой на Бегет (этап 09)
- [[memory]] — правило хранения памяти сессий проекта
- [[wiki]] — правило ведения wiki проекта

## Источник

- `docs/SETUP.md`