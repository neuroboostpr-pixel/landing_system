---
type: rule
name: setup-guide
sources: ["docs/SETUP.md"]
updated: 2026-05-20
triggers: []
stage: ""
uses:
  - landing-onboarding
  - landing-orchestrator
  - landing-go
  - landing-new
  - system-setup
  - onboarding-guide
  - wp-deployer
tags: [setup, onboarding, api, workflow-lock, stage-gates, enforcement]
---

# Setup Guide — Гайд по первой установке системы

## Что делает

Полная инструкция по установке `landing-system` на новой машине: настройка API-ключей, проверка зависимостей, объяснение workflow lock и принудительного gate-enforcement. Это точка входа для любого разработчика, который впервые разворачивает систему.

## Когда вызывать / в каком этапе

Вызывать **один раз** при первом развёртывании системы, до запуска любых `/landing-*` команд. Если onboarding не пройден (нет флага `~/.landing-system/setup_complete`) — система направит сюда автоматически при попытке создать проект.

## Что на вход / на выход

**Вход:**
- Клонированный репозиторий `landing-system`
- Доступ к API-сервисам (Firecrawl, Pexels, Beget, Yandex Metrika и др.)

**Выход:**
- Заполненный `.env` с проверенными ключами
- Флаг `~/.landing-system/setup_complete`
- Настроенный `~/.claude/settings.json` с Firecrawl MCP
- Установленный git-хук `.githooks/post-commit` для авто-wiki

**Ключевые зависимости:** `wp-cli`, `ssh`, `rsync`, `python`, `jq`, плагин `superpowers`.

**Быстрый старт:**
```bash
bash scripts/wizard.sh
# или внутри Claude Code:
/landing-onboarding
```

## Важные механики

**Workflow lock:** каждый проект имеет `.landing-state.yaml` со статусами этапов (`locked` / `in_progress` / `approved`). Перепрыгивать этапы нельзя — `/landing-build` падает, если этапы 02–07 не имеют статус `approved`.

**Stage gate enforcement (с 2026-05-20):** хук `scripts/hooks/enforce_stage_gate.py` физически блокирует Write/Edit/Bash-операции к файлам этапа, чьи предшественники не одобрены. Fail-open при corrupt YAML — чтобы не заблокировать починку state-файла.

**Wiki auto-sync:** хук `.githooks/post-commit` запускает `compile.py --source-mode=system` при каждом коммите, затрагивающем источники wiki.

## Связанные концепты

- [[landing-onboarding]] — команда первичной настройки (один раз на машину)
- [[system-setup]] — агент, выполняющий preflight-проверки и конфигурацию
- [[onboarding-guide]] — агент, ведущий пользователя через wizard.sh
- [[landing-orchestrator]] — главный дирижёр, использует `.landing-state.yaml`
- [[landing-go]] — главная точка входа после онбординга
- [[landing-new]] — создание нового проекта (требует пройденного онбординга)
- [[wp-deployer]] — деплой на Beget (требует SSH-ключей из `.env`)

## Источник

- `docs/SETUP.md`