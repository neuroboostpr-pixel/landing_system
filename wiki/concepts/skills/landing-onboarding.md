---
type: skill
name: landing-onboarding
sources: ["skills/landing-onboarding/SKILL.md"]
updated: 2026-05-26
triggers: []
stage: ""
uses: ["landing-go", "landing-photos", "landing-visuals", "landing-orchestrator"]
tags: ["onboarding", "setup", "dependencies", "cli"]
---

# Landing Onboarding — первичная настройка системы на новой машине

## Что делает
Проверяет и устанавливает всё необходимое для работы landing-system на новой машине: зависимости, MCP-серверы, плагин superpowers, API-ключи и codex CLI. По завершении ставит флаг готовности, без которого никакие `/landing-*` команды не запустятся.

## Когда вызывать / в каком этапе
Вызывается один раз — при первом запуске системы на новой машине через команду `/landing-onboarding`. Также срабатывает автоматически: если при запуске любой `/landing-*` команды отсутствует файл `~/.landing-system/setup_complete`, система перенаправляет сюда. После onboarding'а этот скилл больше не нужен.

## Что на вход / на выход

**Вход:**
- Новая машина без настроенного окружения
- Доступ к интернету для установки пакетов
- API-ключи (вводятся интерактивно в процессе wizard'а)

**Выход:**
- `~/.landing-system/setup_complete` — флаг с ISO-временем успешной настройки
- Установленный `codex` CLI (через `npm i -g @openai/codex`)
- Прошедшие все 15 API-валидаторов зависимости

**Скрипты:**
- `scripts/wizard.sh` — интерактивный мастер настройки
- `scripts/validate-all.sh` — прогоняет все 15 валидаторов API
- `scripts/setup-flag.sh` — управляет файлом-флагом `setup_complete`
- `scripts/install-codex.sh` — устанавливает codex CLI (шаг PR-D)
- `scripts/test-pipeline.sh` — smoke-тест пайплайна после настройки

**Smoke-тест после настройки:**
```bash
SKIP_OPEN=1 USE_CODEX_MOCK=1 bash scripts/test-pipeline.sh smoke-onboarding tests/phase-pra/fixtures/prototype-sample.md
```

## Связанные концепты
- [[landing-go]] — главная команда после онбординга; ведёт через все этапы проекта
- [[landing-orchestrator]] — оркестратор, которому нужен codex CLI для PR-D флоу
- [[landing-photos]] — ручной entry point для фото-пайплайна; требует установленного codex
- [[landing-visuals]] — ручной entry point для AI-генерации иконок; требует установленного codex

## Источник
- `skills/landing-onboarding/SKILL.md`