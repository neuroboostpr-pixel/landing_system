---
type: rule
name: phase-1-tests
sources: ["tests/phase-1/README.md"]
updated: 2026-05-18
triggers: []
stage: ""
uses: ["landing-from-context", "landing-setup", "system-setup"]
tags: ["тесты", "bats", "pytest", "ci", "phase-1"]
---

# Тесты Phase-1

## Что делает

Набор автоматических тестов для первой фазы системы: проверяет работоспособность slash-команд, зависимостей, шаблона окружения и интеграции между компонентами. Запускается через Bats (bash) и опционально через pytest.

## Когда вызывать / в каком этапе

Запускается вручную или в CI после любых изменений в командах, скриптах зависимостей, конфигурации окружения и скилле `landing-from-context`. Перед коммитом изменений в phase-1 компоненты системы рекомендуется прогнать весь набор.

```bash
# Bats-тесты
bats tests/phase-1/

# Pytest (если есть test_*.py)
pytest tests/phase-1/
```

## Что на вход / на выход

**Вход:** исходный код системы (команды, скрипты, `.env.template`, скилл `landing-from-context`).

**Выход:** pass/fail отчёт по каждому тесту. При падении — диагностика конкретного компонента.

### Файлы тестов

| Файл | Что тестирует |
|---|---|
| `test-commands.bats` | Регистрация и базовый вызов slash-команд |
| `test-deps.bats` | Наличие системных зависимостей (wp-cli, rsync и др.) |
| `test-env-template.bats` | Корректность `.env.template` — все ключи на месте |
| `test-from-context.bats` | Скилл `landing-from-context`: создание проекта из контекста агентства |
| `test-integration.bats` | Интеграция между компонентами первой фазы |

## Связанные концепты

- [[landing-from-context]] — напрямую покрывается `test-from-context.bats`
- [[landing-setup]] — зависимости и окружение проверяются в `test-deps.bats` и `test-env-template.bats`
- [[system-setup]] — агент первичной настройки системы, чьи артефакты валидирует `test-env-template.bats`

## Источник

- `tests/phase-1/README.md`