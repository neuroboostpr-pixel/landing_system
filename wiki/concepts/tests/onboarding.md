---
type: rule
name: tests-onboarding
sources: ["tests/onboarding/README.md"]
updated: 2026-05-18
triggers: []
stage: ""
uses: ["landing-onboarding", "system-setup", "landing-start", "onboarding-guide"]
tags: ["testing", "bats", "onboarding", "qa"]
---

# Тесты onboarding

## Что делает
Группа автотестов, которая проверяет корректность работы onboarding-процесса: флаг завершения настройки, валидацию всех параметров системы и интерактивный wizard первого запуска.

## Когда вызывать / в каком этапе
Запускается при разработке и изменении onboarding-компонентов (агент `onboarding-guide`, скилл `landing-onboarding`, команда `/landing-start`, скрипт `wizard.sh`). Обязательно запускать перед коммитом, если были изменены файлы в `skills/landing-onboarding/`, `agents/landing-onboarding-wizard.md`, `.claude/commands/landing-start.md` или `scripts/` связанные с настройкой.

## Что на вход / на выход

**Вход:**
- Установленный `bats-core` (bash-тестовый фреймворк)
- Опционально: `pytest` для Python-тестов (`test_*.py`)
- Корректно настроенная среда (`~/.landing-system/` и переменные окружения)

**Выход:**
- Отчёт `bats` по трём файлам:
  - `test-setup-flag.bats` — проверяет создание и чтение флага `~/.landing-system/setup_complete`
  - `test-validate-all.bats` — валидирует все параметры конфигурации системы (API-ключи, пути, зависимости)
  - `test-wizard.bats` — тестирует интерактивный wizard (шаги welcome → имя проекта → материалы → финиш)

## Запуск

```bash
# Все bats-тесты группы
bats tests/onboarding/

# Python-тесты (если появятся test_*.py)
pytest tests/onboarding/
```

## Связанные концепты
- [[landing-onboarding]] — скилл, логику которого покрывают эти тесты
- [[onboarding-guide]] — агент onboarding-wizard, тестируемый в `test-wizard.bats`
- [[system-setup]] — агент системной настройки, флаг которого проверяет `test-setup-flag.bats`
- [[landing-start]] — команда, запускающая wizard (точка входа для пользователя)
- [[stage-gates]] — общие правила прохождения этапов, которые onboarding защищает через флаг `setup_complete`

## Источник
- `tests/onboarding/README.md`