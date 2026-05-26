---
type: agent
name: onboarding-guide
sources: ["agents/onboarding-guide.md"]
updated: 2026-05-26
triggers: ["/landing-onboarding", "любая /landing-* команда при отсутствии setup_complete"]
stage: ""
uses: ["landing-orchestrator", "landing-new"]
tags: ["onboarding", "setup", "wizard", "api-keys"]
---

# Onboarding Guide (Проводник по первичной настройке)

## Что делает
Проводит пользователя через первичную настройку landing-system: объясняет систему, проверяет зависимости, помогает заполнить `.env` с API-ключами и валидирует каждый ключ сразу после ввода.

## Когда вызывать / в каком этапе
Активируется в двух случаях: пользователь явно запустил `/landing-onboarding`, либо любая команда `/landing-*` обнаружила отсутствие файла `~/.landing-system/setup_complete` и перенаправила сюда. Это системный агент — он не относится ни к одному этапу pipeline и не подчиняется Stage Execution Protocol.

## Что на вход / на выход

**Вход:**
- `docs/SETUP.md` — документация по установке (агент читает и объясняет пользователю)
- `scripts/wizard.sh` — интерактивный скрипт настройки
- `.env.example` — шаблон переменных окружения
- `scripts/validate-all.sh --service <name>` — валидатор конкретного сервиса
- `scripts/setup-flag.sh mark_complete` — скрипт выставления флага готовности

**Выход:**
- `~/.landing-system/setup_complete` — файл-флаг с timestamp (создаётся только если все обязательные проверки прошли)
- `.env` в корне репо — заполненный файл с ключами
- Консольная сводка: «X из Y подключено, fallback: ...»

**Обязательные ключи** (без них `setup_complete` не выставляется):
`FIRECRAWL_API_KEY`, хотя бы один фото-сток (Pexels / Unsplash / Pixabay), `YM_COUNTER_ID`, `TG_BOT_TOKEN` + `TG_CHAT_ID`, хотя бы одна CRM (AmoCRM или Bitrix24), SSH-доступ на Beget.

**Опциональные ключи** (предупреждение, не блокируют):
HuggingFace, WhatTheFont, Yandex OAuth, GTM, Cloudflare, Reg.ru и др. — отмечаются как «fallback» в финальной сводке.

## Связанные концепты
- [[landing-orchestrator]] — следующий агент после онбординга, ведёт через 12 этапов проекта
- [[landing-new]] — первая команда после успешного онбординга для создания проекта

## Источник
- `agents/onboarding-guide.md`