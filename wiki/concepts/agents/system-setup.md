---
type: agent
name: system-setup
sources: ["agents/system-setup.md"]
updated: 2026-05-26
triggers: ["настроить систему", "первый запуск", "инициализация системы", "/landing-setup"]
stage: ""
uses: ["landing-new", "landing-orchestrator"]
tags: ["setup", "onboarding", "system", "one-time"]
---

# System Setup (Настройщик системы)

## Что делает
Выполняет одноразовую инициализацию landing-system: проверяет окружение, заполняет `.env` с секретами и настраивает `config/system.yaml` с глобальными параметрами. После него система готова к созданию лендингов.

## Когда вызывать / в каком этапе
Запускается **один раз** через команду `/landing-setup` — до создания первого проекта. Не является частью pipeline-этапов (Stage Execution Protocol к нему не применяется). Если preflight вернул ошибки — агент ждёт исправлений и запускает проверку повторно.

## Что на вход / на выход

**Вход:**
- Установленные зависимости окружения (проверяет `scripts/preflight.sh`)
- Опционально: существующий `.env` или `.env.example`
- Опционально: `config/system.yaml.template`

**Выход:**
- Заполненный `.env` с ключами: `FIRECRAWL_API_KEY`, `BEGET_USER`, `BEGET_HOST`, `BEGET_PATH` (деплой), опционально `TG_BOT_TOKEN`, CRM-ключи
- Заполненный `config/system.yaml` с флагами CRM, Telegram-бота, ЯМ, GTM, JS-библиотек (Swiper, Fancybox, CountUp), встроенных попапов
- Финальный отчёт с перечнем подключённых интеграций и подсказкой `/landing-new <slug>`

**Правило разделения:** токены и API-ключи → только в `.env`; `system.yaml` хранит исключительно флаги (`enabled: true`) и публичные значения (subdomain). Перемешивать нельзя.

## Шаги работы

1. **Preflight** — `bash scripts/preflight.sh`; при ❌ выводит инструкции и ждёт исправления.
2. **Настройка .env** — создаёт из `.env.example` если нет; спрашивает каждое пустое поле с объяснением где взять.
3. **Настройка config/system.yaml** — 6 вопросов: CRM, Telegram-бот, Яндекс.Метрика, GTM, JS-библиотеки, попапы.
4. **Отчёт** — выводит сводку подключённого и подсказку для следующего шага.

## Связанные концепты
- [[landing-new]] — следующий шаг после setup: создать первый проект
- [[landing-orchestrator]] — ведёт проект через 12 этапов; требует готового окружения
- [[landing-start]] — wizard для новичков, вызывается после setup

## Источник
- `agents/system-setup.md`