---
type: script
name: wizard
language: bash
sources: ["scripts/wizard.sh", "scripts/wizard.sh.doc.md"]
updated: 2026-05-18
triggers: ["/landing-onboarding", "запустить онбординг", "настроить систему"]
stage: ""
uses: ["landing-onboarding", "onboarding-guide", "system-setup", "setup"]
tags: ["bash", "onboarding", "setup", "deps", "api-keys"]
---

# wizard.sh — интерактивный онбординг системы

## Что делает

Проводит пользователя через первоначальную настройку landing-system: проверяет все локальные зависимости, Python-пакеты, подключения MCP и API-ключи. По завершении успешной проверки ставит флаг `setup_complete`, после чего `/landing-*` команды начинают работать.

## Когда вызывать / в каком этапе

Запускается **один раз** при первом запуске системы на новой машине. Вызывается командой `/landing-onboarding` или вручную через `bash scripts/wizard.sh`. Без успешного прохождения скрипта все `/landing-*` команды недоступны — проверка флага `~/.landing-system/setup_complete` обязательна.

Поддерживает неинтерактивный режим через переменную окружения `WIZARD_NONINTERACTIVE=1` (полезно для CI).

## Что на вход / на выход

**Вход:**
- Доступ к терминалу (bash)
- `scripts/validate-all.sh` — скрипт валидации API-ключей
- `scripts/setup-flag.sh` — скрипт установки флага завершения
- `.env.example` — шаблон конфига с ключами
- `docs/SETUP.md` — документация по настройке

**Выход:**
- Консольный отчёт по каждой проверке (✅/❌/⚠️)
- `.env` файл (создаётся из `.env.example` если отсутствует)
- `~/.landing-system/setup_complete` — флаг успешного онбординга (если всё ок)

**Что проверяется:**
1. CLI-инструменты: `wp`, `ssh`, `rsync`, `bats`, `python3`, `jq`
2. Python-пакеты: `pyyaml`, `jinja2`, `requests`, `pillow`, `pytest`, `responses`
3. Superpowers plugin для Claude Code
4. Firecrawl MCP в `~/.claude/settings.json`
5. Наличие `.env` (создаёт автоматически при отсутствии)
6. Валидация всех API-ключей через `validate-all.sh`

**Ссылки для регистрации**, которые скрипт выводит: Firecrawl, Pexels, Unsplash, Pixabay, HuggingFace, Yandex OAuth, Telegram BotFather, amoCRM, Bitrix24, Beget.

## Связанные концепты

- [[landing-onboarding]] — slash-команда, которая вызывает этот скрипт
- [[onboarding-guide]] — агент, объясняющий настройку API и ключей
- [[system-setup]] — агент для инициализации системы через `/landing-setup`
- [[setup]] — документ `docs/SETUP.md`, на который ссылается скрипт
- [[landing-project-init]] — следующий шаг после успешного онбординга

## Источник

- `scripts/wizard.sh`
- `scripts/wizard.sh.doc.md`