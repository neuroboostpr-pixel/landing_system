---
type: skill
name: landing-onboarding
sources: ["skills/landing-onboarding/SKILL.md"]
updated: 2026-05-25
triggers: []
stage: ""
uses: ["landing-go", "landing-photos", "landing-visuals", "landing-orchestrator"]
tags: ["setup", "onboarding", "dependencies", "api-keys"]
---

# Landing Onboarding — первичная настройка системы на новой машине

## Что делает
Настраивает landing-system с нуля на новой машине: проверяет локальные зависимости, MCP-серверы, плагин superpowers и все API-ключи. После успешного прохождения создаёт флаг-файл, без которого остальные `/landing-*` команды не запустятся.

## Когда вызывать / в каком этапе
Вызывается один раз при первичной установке системы. Если флаг `~/.landing-system/setup_complete` отсутствует, любая `/landing-*` команда автоматически перенаправляет сюда. Запускается через слеш-команду `/landing-onboarding`.

## Что на вход / на выход

**Вход:**
- Новая машина без настроенного окружения
- Доступ к интернету для установки зависимостей
- API-ключи (передаются интерактивно во время wizard)

**Выход:**
- `~/.landing-system/setup_complete` — флаг-файл с ISO-таймстампом, подтверждающий успешную настройку
- Установленный `codex` CLI на PATH (если отсутствовал)
- Валидированные MCP-серверы и API-ключи (15 проверок)

## Ключевые скрипты

| Скрипт | Назначение |
|---|---|
| `scripts/wizard.sh` | Интерактивный мастер настройки |
| `scripts/validate-all.sh` | Прогоняет все 15 API-валидаторов |
| `scripts/setup-flag.sh` | Управляет флаг-файлом `setup_complete` |
| `scripts/install-codex.sh` | Устанавливает `@openai/codex` CLI и запускает `codex login` |

## PR-D: prototype-first флоу

После онбординга маркетолог переходит на упрощённый воркфлоу:
1. Получить готовый `prototype.pdf` извне системы
2. Положить в `<project>/07_ПРОТОТИП/source/`
3. Запустить `/landing-go` — оркестратор сам ведёт через все этапы

Этапы 00–02 (бриф, контекст, анализ ниши, материалы) помечены `n/a` — они происходят до landing-system.

**Smoke-тест после установки:**
```bash
SKIP_OPEN=1 USE_CODEX_MOCK=1 bash scripts/test-pipeline.sh smoke-onboarding tests/phase-pra/fixtures/prototype-sample.md
```

## Связанные концепты
- [[landing-go]] — главная команда после онбординга; single entry point для всего pipeline
- [[landing-orchestrator]] — ведёт через все этапы после успешной настройки
- [[landing-photos]] — ручная команда для обработки фото; требует codex CLI из онбординга
- [[landing-visuals]] — ручная команда AI-генерации визуалов; требует codex CLI из онбординга

## Источник
- `skills/landing-onboarding/SKILL.md`