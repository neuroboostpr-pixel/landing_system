---
type: agent
name: onboarding-guide
sources: ["agents/onboarding-guide.md"]
updated: 2026-05-25
triggers:
  - "/landing-onboarding"
  - "любая /landing-* команда при отсутствии ~/.landing-system/setup_complete"
stage: ""
uses:
  - landing-orchestrator
  - landing-new
tags: ["onboarding", "setup", "wizard", "first-run"]
---

# onboarding-guide (Проводник по онбордингу)

## Что делает

Проводит пользователя через первичную настройку landing-system: объясняет систему, проверяет зависимости, помогает заполнить `.env` с API-ключами и валидирует каждый ключ сразу после ввода. После успешного прохождения помечает установку завершённой и направляет к созданию первого проекта.

## Когда вызывать / в каком этапе

Агент не принадлежит ни одному pipeline-этапу — это системный pre-project агент. Запускается в двух случаях:

1. Пользователь явно вызвал `/landing-onboarding`.
2. Любая `/landing-*` команда не обнаружила файл `~/.landing-system/setup_complete` и автоматически перенаправила сюда.

Stage Execution Protocol (TodoWrite + Mermaid-карта) к этому агенту **не применяется**.

## Что на вход / на выход

**Вход:**
- Пустое окружение (первый запуск на новой машине)
- `docs/SETUP.md` — читается агентом целиком
- `.env.example` — шаблон для создания `.env`
- `scripts/wizard.sh` — интерактивный wizard
- `scripts/validate-all.sh` — валидатор API-ключей
- `scripts/setup-flag.sh` — утилита выставления флага завершения

**Выход:**
- `~/.landing-system/setup_complete` — файл с timestamp (признак успешного онбординга)
- `.env` в корне репо — заполненный файл с ключами
- Консольная сводка: сколько сервисов подключено, какие работают в режиме fallback

**Обязательные ключи** (без них `setup_complete` не создаётся):
- `FIRECRAWL_API_KEY`
- Хотя бы один сток-фото: `PEXELS_API_KEY` / `UNSPLASH_ACCESS_KEY` / `PIXABAY_API_KEY`
- `YM_COUNTER_ID`
- `TG_BOT_TOKEN` + `TG_CHAT_ID`
- Хотя бы одна CRM: `AMOCRM_API_KEY+SUBDOMAIN` / `BITRIX24_WEBHOOK_URL`
- `BEGET_USER` + `BEGET_HOST` + работающий SSH-доступ

**Опциональные ключи** (предупреждение, не блокируют):
- `HUGGINGFACE_TOKEN`, `WHATTHEFONT_API_KEY`, `YANDEX_OAUTH_TOKEN`, `YANDEX_METRIKA_OAUTH`, `GTM_CONTAINER_ID`, `BEGET_API_LOGIN/PASSWORD`, `CLOUDFLARE_API_TOKEN`, `REGRU_API_USERNAME/PASSWORD`

## Связанные концепты

- [[landing-new]] — следующий шаг после успешного онбординга: создание первого проекта
- [[landing-orchestrator]] — основной pipeline-агент, запускается только если `setup_complete` уже выставлен
- [[landing-start]] — wizard для нового проекта, вызывается после онбординга

## Источник

- `agents/onboarding-guide.md`