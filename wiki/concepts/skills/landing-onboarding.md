---
type: skill
name: landing-onboarding
sources: ["skills/landing-onboarding/SKILL.md"]
updated: 2026-05-15
triggers:
  - "/landing-onboarding"
  - "автоматически при любом /landing-* если setup_complete отсутствует"
stage: ""
uses:
  - landing-go
  - landing-photos
  - landing-visuals
tags:
  - onboarding
  - setup
  - codex
  - api-keys
  - validation
---

# landing-onboarding — первоначальная настройка системы

## Что делает

Настраивает landing-system на новой машине: проверяет локальные зависимости, MCP-серверы, плагин superpowers и все API-ключи. По завершении создаёт флаг `~/.landing-system/setup_complete`, без которого ни одна `/landing-*` команда не запустится.

## Когда вызывать / в каком этапе

Вызывается **один раз** при первом запуске системы на машине — вручную через `/landing-onboarding`. Если флаг `setup_complete` отсутствует, любая другая `/landing-*` команда автоматически перенаправляет сюда. После успешного прохождения onboarding повторный запуск не требуется.

## Что на вход / на выход

**На вход:**
- Нет пользовательских файлов — скрипты сами проверяют окружение
- Интерактивный ввод при работе `scripts/wizard.sh`

**На выход:**
- `~/.landing-system/setup_complete` — флаг с ISO-таймстампом (основной результат)
- Установленный `codex` CLI (если отсутствовал)
- Подтверждение работоспособности всех 15 API-валидаторов

**Скрипты:**
| Скрипт | Назначение |
|---|---|
| `scripts/wizard.sh` | Интерактивный мастер-поток настройки |
| `scripts/validate-all.sh` | Запускает все 15 API-валидаторов |
| `scripts/setup-flag.sh` | Управляет файлом `setup_complete` |
| `scripts/install-codex.sh` | Устанавливает `@openai/codex` и запускает `codex login` |

## Prototype-first дополнения (PR-D)

С версии PR-D onboarding расширен тремя обязательными шагами:

1. **Установка codex CLI** — `bash scripts/install-codex.sh`. Без codex не работают `/landing-photos` и `/landing-visuals`.
2. **Новый прототип-first флоу** — маркетолог кладёт `prototype.pdf` в `07_ПРОТОТИП/source/` и запускает `/landing-go`. Этапы 00/01/01a/02 помечены `n/a` (выполняются до системы).
3. **Smoke-тест пайплайна:**
   ```bash
   SKIP_OPEN=1 USE_CODEX_MOCK=1 bash scripts/test-pipeline.sh smoke-onboarding tests/phase-pra/fixtures/prototype-sample.md
   ```

## Связанные концепты

- [[landing-go]] — главная команда после onboarding; ведёт через все 12 этапов автоматически
- [[landing-photos]] — требует установленного codex; не работает без `setup_complete`
- [[landing-visuals]] — требует установленного codex; не работает без `setup_complete`

## Источник

- `skills/landing-onboarding/SKILL.md`