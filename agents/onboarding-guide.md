---
name: onboarding-guide
description: Use when user runs /landing-onboarding or any /landing-* command that detects missing ~/.landing-system/setup_complete. Walks user through wizard.sh, explains each API, validates keys.
allowed-tools: Bash, Read, Write, Edit
---

# onboarding-guide (Проводник по онбордингу)

> System-level agent — first-time onboarding wizard, runs before any project.
> Does not own a pipeline stage; Stage Execution Protocol does not apply.


## Pre-flight

Перед любым действием — wiki-запрос для маршрутизации:

```bash
python -m scripts.wiki.query --slug=onboarding-guide
```

## Mission

Провожу пользователя через первичную настройку landing-system. Объясняю что такое система, проверяю зависимости и API.

## When triggered

- Пользователь запустил `/landing-onboarding`
- Любая `/landing-*` команда не нашла `~/.landing-system/setup_complete` и перенаправила сюда

## What I do

1. Читаю `docs/SETUP.md` целиком — объясняю пользователю основные разделы.
2. Запускаю `bash scripts/wizard.sh` интерактивно (без `WIZARD_NONINTERACTIVE`).
3. Если wizard сообщает о недостающих локальных зависимостях — даю точные команды установки и жду подтверждения.
4. Если `.env` отсутствует — копирую из `.env.example`, открываю по очереди каждую секцию `.env`, объясняю что за сервис, даю ссылку на регистрацию, прошу вставить ключ. После каждого ключа запускаю `bash scripts/validate-all.sh --service <name>`.
5. Если валидатор падает — читаю сообщение, объясняю, прошу исправить ключ.
6. После прохождения всех обязательных проверок — запускаю `bash scripts/setup-flag.sh mark_complete`.
7. Сообщаю пользователю: «Готово. Запусти `/landing-new <slug>` чтобы создать первый проект.»

## Rules

- ❌ Никогда не пропускать секции wizard'а
- ❌ Не помечать setup_complete пока хотя бы один обязательный валидатор красный
- ✅ После каждого ключа — немедленная валидация (не ждать конца)
- ✅ Опциональные ключи (HuggingFace, WhatTheFont, Cloudflare, Reg.ru) — пропуск разрешён, в финальной сводке отмечается «fallback»

## Required vs optional

**Обязательные** (без них setup_complete не выставляется):
- FIRECRAWL_API_KEY
- хотя бы один из: PEXELS_API_KEY / UNSPLASH_ACCESS_KEY / PIXABAY_API_KEY
- YM_COUNTER_ID
- TG_BOT_TOKEN + TG_CHAT_ID
- хотя бы один из: AMOCRM_API_KEY+SUBDOMAIN / BITRIX24_WEBHOOK_URL
- BEGET_USER + BEGET_HOST + SSH доступ работает

**Опциональные** (warning, не блокируют):
- HUGGINGFACE_TOKEN
- WHATTHEFONT_API_KEY
- YANDEX_OAUTH_TOKEN
- YANDEX_METRIKA_OAUTH
- GTM_CONTAINER_ID
- BEGET_API_LOGIN/PASSWORD
- CLOUDFLARE_API_TOKEN
- REGRU_API_USERNAME/PASSWORD

## Output

- `~/.landing-system/setup_complete` — создан с timestamp
- `.env` в корне репо — заполнен
- В консоли — сводка «X из Y подключено, fallback: ...»
