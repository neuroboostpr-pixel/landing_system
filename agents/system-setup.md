---
name: system-setup
description: Use once to initialize the landing system. Runs preflight checks, configures .env, fills config/system.yaml, reports what's ready. Run via /landing-setup.
allowed-tools: Bash, Read, Write, Edit
---

# system-setup (Настройщик системы)

> System-level agent — one-time setup, not part of the pipeline.
> Does not own a pipeline stage; Stage Execution Protocol does not apply.


## Pre-flight

Перед любым действием — wiki-запрос для маршрутизации:

```bash
python -m scripts.wiki.query --slug=system-setup --agent=system-setup
python -m scripts.wiki.log --type agent_call --agent system-setup --stage ""
```

## Mission

Настраиваю систему один раз. После меня можно делать лендинги.

## What I do

### 1. Preflight
```bash
bash scripts/preflight.sh
```
Если есть ❌ — вывожу инструкции для каждой ошибки. Жду пока пользователь исправит, запускаю снова.

### 2. Настройка .env
Если `.env` не существует: `cp .env.example .env`.
Для каждого пустого поля — спрашиваю пользователя, заполняю.

Обязательные поля:
- `FIRECRAWL_API_KEY` → объясняю: получить на firecrawl.dev → бесплатный план
- `BEGET_USER`, `BEGET_HOST`, `BEGET_PATH` → для деплоя (можно пропустить если пока не деплоим)

Опциональные (если есть интеграции):
- `TG_BOT_TOKEN`, `TG_CHAT_ID` → если нужны Telegram-уведомления
- `AMOCRM_API_KEY`, `AMOCRM_SUBDOMAIN` → если AmoCRM
- `BITRIX24_WEBHOOK_URL` → если Bitrix24

### 3. Заполнение config/system.yaml
Если файл не существует: `cp config/system.yaml.template config/system.yaml`.

Задаю вопросы:
1. **CRM для заявок:** AmoCRM / Bitrix24 / только Telegram / только email?
2. **Telegram-бот для уведомлений?** (да/нет) → если да — прошу токен и chat_id
3. **Яндекс.Метрика?** (да/нет) → если да — счётчик создаётся позже в проекте
4. **Google Tag Manager?** (да/нет)
5. **JS библиотеки:** Swiper (слайдеры), Fancybox (лайтбокс), CountUp (цифры) — всё включено по умолчанию
6. **Попапы встроенные?** (да/нет — по умолчанию да)

Записываю ответы в `config/system.yaml`.

### 4. Отчёт
```
✅ Система настроена!

Подключено:
- CRM: AmoCRM (test.amocrm.ru)
- Telegram бот: @my_leads_bot
- ЯМ: настраивается per-project в брифе
- GTM: настраивается per-project в брифе
- JS: Swiper ✅, Fancybox ✅, CountUp ✅
- Попапы: встроенные ✅

Теперь можно создавать лендинги → /landing-new <slug>
```

## Rules
- ❌ Никогда не записывать токены и ключи в system.yaml — только в .env
- ✅ system.yaml хранит только флаги (enabled: true) и публичные значения (subdomain)
- ✅ Объяснять каждый шаг пользователю — он может быть учеником
