---
slug: system-setup
type: agent
name: "Настройщик системы"
tags: [setup, system, one-time, onboarding, env, config]
triggers: [landing-setup]
inputs:
  - scripts/preflight.sh
  - .env.example
  - config/system.yaml.template
outputs:
  - .env
  - config/system.yaml
gates: []
pre_reqs: []
related:
  - landing-orchestrator
  - landing-onboarding-wizard
  - onboarding-guide
sources:
  - "agents/system-setup.md"
updated: 2026-05-26
confidence:
  stage: low
---

# Настройщик системы

## Что делает

Одноразовый системный агент, который готовит окружение landing-system к работе. Запускает preflight-скрипт и проверяет все зависимости, затем интерактивно собирает у пользователя ключи и настройки: заполняет `.env` (API-ключи, Beget-параметры, CRM-токены) и `config/system.yaml` (флаги интеграций — CRM, Telegram, ЯМ, GTM, JS-библиотеки, попапы). Завершает работу сводным отчётом о том, что подключено. Не является частью pipeline; протокол Stage Execution Protocol к нему не применяется.

## Когда вызывается

Вызывается вручную через команду `/landing-setup` один раз — при первоначальной настройке системы на новой машине или для нового пользователя. Повторный запуск возможен, если конфигурация сломана или нужно добавить интеграцию.

## Вход → выход

**Вход:** шаблоны `.env.example` и `config/system.yaml.template`, скрипт `scripts/preflight.sh`, интерактивные ответы пользователя (API-ключи, выбор CRM, флаги интеграций).

**Выход:** заполненный `.env` с секретами (никогда не попадают в system.yaml), заполненный `config/system.yaml` с публичными флагами и значениями, финальный текстовый отчёт о статусе системы.

## Failure modes

- Preflight возвращает ❌ из-за отсутствующих системных зависимостей (PHP, WP-CLI, rsync) — агент ждёт ручного исправления и перезапускает проверку.
- Пользователь пропустил обязательные поля `.env` (например, `FIRECRAWL_API_KEY`) — интеграции, зависящие от этих ключей, будут недоступны без явного предупреждения.
- Секреты случайно записаны в `system.yaml` вместо `.env` — нарушение правила; при последующем git-коммите токены попадут в репозиторий.
- `config/system.yaml.template` не существует — агент не сможет создать конфиг, нужна ручная проверка структуры репозитория.
- Пользователь прерывает wizard на середине — файлы могут остаться частично заполненными, следующий запуск `/landing-new` упадёт на проверке конфига.

## Related

- [[landing-orchestrator]] — запускается после настройки; ведёт проекты по pipeline
- [[landing-onboarding-wizard]] — wizard для новых проектов, вызывается после system-setup
- [[onboarding-guide]] — пользовательский гайд, объясняет контекст системы