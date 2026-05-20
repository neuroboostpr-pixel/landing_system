---
type: agent
name: system-setup
sources: ["agents/system-setup.md"]
updated: 2026-05-20
triggers: ["настроить систему", "первый запуск", "инициализация landing-system", "/landing-setup"]
stage: ""
uses: ["landing-new", "landing-orchestrator"]
tags: ["setup", "onboarding", "one-time", "system"]
---

# system-setup — Настройщик системы

## Что делает

Разовый агент для первоначальной настройки всей landing-system: проверяет зависимости, заполняет `.env` ключами и конфигурирует `config/system.yaml`. После его работы система готова к созданию лендингов.

## Когда вызывать / в каком этапе

Вызывается **один раз** при первом запуске системы через команду `/landing-setup`. Не является частью основного pipeline и не подчиняется Stage Execution Protocol. Запускать до любых `/landing-new` или `/landing-go`.

## Что на вход / на выход

**Вход:**
- Пустая или частично заполненная папка landing-system
- Ответы пользователя на вопросы по ходу настройки
- (Опционально) уже существующий `.env` или `config/system.yaml`

**Выход:**
- Заполненный `.env` (API-ключи, токены — только здесь, не в yaml)
- `config/system.yaml` — флаги интеграций и публичные значения (CRM, GTM, Telegram, JS-библиотеки)
- Итоговый отчёт о состоянии системы в чате

**Шаги работы:**

1. **Preflight** — запускает `scripts/preflight.sh`. При ❌ объясняет как исправить и ждёт повтора.
2. **Настройка `.env`** — копирует из `.env.example`, для каждого пустого поля спрашивает значение. Обязательные: `FIRECRAWL_API_KEY`, `BEGET_USER`, `BEGET_HOST`, `BEGET_PATH`. Опциональные: Telegram-бот, AmoCRM, Bitrix24.
3. **Заполнение `config/system.yaml`** — задаёт 6 вопросов: CRM, Telegram, Яндекс.Метрика, GTM, JS-библиотеки (Swiper/Fancybox/CountUp), встроенные попапы.
4. **Отчёт** — выводит список подключённых интеграций и подсказку `/landing-new <slug>`.

**Правило безопасности:** токены и API-ключи хранятся **только** в `.env`, в `system.yaml` — исключительно флаги и публичные значения.

## Связанные концепты

- [[landing-setup]] — slash-команда, которая триггерит этого агента
- [[landing-new]] — следующий шаг после успешной настройки системы
- [[landing-orchestrator]] — основной оркестратор, который начинает работать после setup
- [[landing-onboarding-wizard]] — wizard для новых проектов, запускается после setup

## Источник

- `agents/system-setup.md`