---
slug: onboarding-guide
type: agent
name: "Проводник по онбордингу"
tags: [onboarding, setup, wizard, api-keys, env, first-run]
triggers: [landing-onboarding, landing-start]
inputs:
  - docs/SETUP.md
  - scripts/wizard.sh
  - .env.example
outputs:
  - ~/.landing-system/setup_complete
  - .env
pre_reqs: []
related:
  - landing-new
  - landing-start
  - landing-go
sources: ["agents/onboarding-guide.md"]
updated: 2026-05-26
confidence:
  stage: low
---

# Проводник по онбордингу

## Что делает

Агент первичной настройки landing-system: проводит пользователя через интерактивный wizard, объясняет каждый внешний сервис, собирает API-ключи и немедленно валидирует каждый из них. Работает на системном уровне — не привязан ни к одному этапу pipeline. После успешного прохождения всех обязательных проверок выставляет флаг `~/.landing-system/setup_complete`, без которого ни одна `/landing-*` команда не продолжает работу.

## Когда вызывается

Вызывается явно командой `/landing-onboarding` или автоматически — когда любая `/landing-*` команда обнаруживает отсутствие файла `~/.landing-system/setup_complete` и перенаправляет пользователя сюда. Сценарий первого запуска или переустановки на новой машине.

## Вход → выход

**Вход:** отсутствие `~/.landing-system/setup_complete`; файлы `docs/SETUP.md`, `scripts/wizard.sh`, `.env.example` в корне репозитория.

**Выход:** заполненный `.env` с валидными ключами; флаговый файл `~/.landing-system/setup_complete` с timestamp; консольная сводка `X из Y подключено, fallback: ...`.

## Failure modes

- **Обязательный ключ не прошёл валидацию** — агент застревает на шаге, не помечает setup_complete; пользователь должен исправить ключ.
- **SSH-доступ к Beget недоступен** — валидатор падает, онбординг не завершается; нужно настроить SSH вручную.
- **wizard.sh не найден или не исполняем** — агент не может продолжить; требуется `chmod +x scripts/wizard.sh`.
- **Пользователь пропускает опциональные ключи** — setup_complete выставляется, но в сводке появляются записи «fallback»; часть функций системы деградирует (генерация фото, аналитика).
- **CRM не указан ни один** — ни AmoCRM, ни Bitrix24; это обязательное условие, онбординг блокируется.

## Related

- [[landing-new]] — следующий шаг после онбординга: создать первый проект
- [[landing-start]] — альтернативная точка входа с wizard'ом для новичков (включает онбординг-проверку)
- [[landing-go]] — главная команда запуска pipeline, требует наличия setup_complete