---
type: command
name: landing-new
sources: ["commands/landing-new.md"]
updated: 2026-05-26
triggers:
  - "создать новый лендинг"
  - "новый проект лендинга"
  - "начать проект с нуля"
  - "landing-new <slug>"
stage: "00"
uses:
  - landing-project-init
  - landing-orchestrator
  - landing-onboarding
tags:
  - команда
  - инициализация
  - проект
---

# /landing-new — Создать новый проект лендинга

## Что делает

Создаёт папку нового проекта лендинга со всей структурой и передаёт управление оркестратору для старта этапа 00 (бриф). Продвинутая команда: в отличие от `/landing-start`, не запускает интерактивный wizard.

## Когда вызывать / в каком этапе

Вызывается вручную опытным пользователем, который уже прошёл onboarding (`/landing-onboarding`). Запускается до первого этапа (`00_brief`). Если onboarding не пройден — команда останавливается и просит запустить `/landing-onboarding` первым.

Принимает обязательный аргумент `<project-slug>` в kebab-case (например, `lp-курс-марафон`) и необязательный флаг `--cinematic` для включения премиум-режима.

## Что на вход / на выход

**Вход:**
- Аргумент `<slug>` — имя проекта в kebab-case.
- Флаг `--cinematic` (опционально).
- Наличие установленного onboarding-флага (`~/.landing-system/setup_complete`).

**Выход:**
- Папка проекта `~/Lendings/<slug>/` с полной структурой из шаблона.
- Файл `.landing-state.yaml` с заполненными полями `project` и `created`.
- Проверка gate-check для этапа `00_brief` (наличие `brief.md`).
- Запущенный агент `landing-orchestrator` для ведения через этап 00.

## Как работает внутри

1. **Pre-flight:** проверяет флаг завершённости onboarding через `scripts/setup-flag.sh is_complete`.
2. **Разрешает путь:** если slug — абсолютный или относительный путь, использует как есть; иначе разворачивает в `~/Lendings/<slug>/`.
3. **Запускает скилл:** вызывает `skills/landing-project-init/scripts/init.sh` с аргументами.
4. **Post-creation:** копирует `.landing-state.yaml` из шаблона, проставляет `project` и `created` через `yq`, запускает gate-check.
5. **Передаёт управление:** диспатчит агента `landing-orchestrator` для Stage 00.

## Связанные концепты

- [[landing-project-init]] — скилл, создающий физическую структуру папок проекта
- [[landing-orchestrator]] — агент, ведущий через все 12 этапов после создания проекта
- [[landing-onboarding]] — обязательный wizard, который нужно пройти перед этой командой
- [[landing-start]] — альтернативная точка входа для новичков с интерактивным wizard'ом

## Источник

- `commands/landing-new.md`