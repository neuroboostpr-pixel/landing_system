---
slug: landing-new
type: command
name: "/landing-new — создать новый проект лендинга"
stage: "00"
tags: [project-init, onboarding, orchestrator, cli]
triggers: ["/landing-new"]
inputs: []
outputs: ["~/Lendings/<slug>/", "<slug>/.landing-state.yaml"]
gates: []
pre_reqs: [system-setup, landing-onboarding]
related: [landing-project-init, landing-orchestrator, landing-from-context, landing-onboarding-wizard]
sources: ["commands/landing-new.md"]
updated: 2026-05-26
confidence: {}
---

# /landing-new — создать новый проект лендинга

## Что делает

Команда создаёт пустой проект лендинга для опытных пользователей, которые не нуждаются в пошаговом онбординге. Принимает kebab-case slug проекта, разрешает целевую директорию (по умолчанию `~/Lendings/<slug>/`), запускает скрипт инициализации из скилла `landing-project-init` и копирует канонический `.landing-state.yaml` из шаблона. После создания папки управление передаётся агенту `landing-orchestrator` для прохождения этапа 00 (бриф). Дополнительный флаг `--cinematic` включает кинематографический премиум-режим.

## Когда вызывается

Пользователь вводит `/landing-new <slug>` в Claude Code. Команда рассчитана на тех, кто уже знаком с системой и хочет создать проект напрямую, минуя интерактивный wizard (`/landing-start`). Обязательное условие — пройденный онбординг (файл-флаг `~/.landing-system/setup_complete`). Если онбординг не завершён, команда останавливается с подсказкой запустить `/landing-onboarding`.

## Вход → выход

**Вход:** slug проекта в виде аргумента командной строки (обязателен); опционально флаг `--cinematic`; скрипт `skills/landing-project-init/scripts/init.sh` доступен в рабочей директории; онбординг завершён.

**Выход:** директория `~/Lendings/<slug>/` с 18 подпапками по шаблону (`00_БРИФ/` … `12_АНАЛИТИКА/`); заполненный `.landing-state.yaml` с полями `project` и `created`; результат `gate-check.sh --stage 00_brief` — верификация наличия `brief.md`; запущенный `landing-orchestrator` для этапа 00.

## Failure modes

- **Онбординг не пройден** — `setup-flag.sh` возвращает exit 1, команда останавливается до запуска `/landing-onboarding`.
- **Slug не передан** — скрипт печатает Usage и завершается с ошибкой, папка не создаётся.
- **Скрипт `init.sh` не найден** — bash завершается с ошибкой «No such file», если `CLAUDE_PROJECT_DIR` указан неверно.
- **Директория уже существует** — `init.sh` может перезаписать содержимое или упасть в зависимости от реализации; риск потери данных существующего проекта.
- **`gate-check.sh` не проходит** — если `brief.md` отсутствует после инициализации, этап 00 не подтверждается и оркестратор не двигается дальше.

## Related

- [[landing-project-init]] — скилл, чей `init.sh` выполняет фактическое создание структуры папок
- [[landing-orchestrator]] — агент, принимающий управление после инициализации и ведущий через все этапы
- [[landing-from-context]] — альтернатива для создания проекта из существующего контекста агентства
- [[landing-onboarding-wizard]] — интерактивный вариант создания проекта для новичков (`/landing-start`)