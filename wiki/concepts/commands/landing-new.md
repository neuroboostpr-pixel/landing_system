---
type: command
name: landing-new
sources: ["commands/landing-new.md"]
updated: 2026-05-25
triggers:
  - "создать новый лендинг"
  - "начать проект с нуля"
  - "новый лендинг-проект"
  - "создать пустой проект"
stage: ""
uses:
  - landing-project-init
  - landing-orchestrator
  - landing-onboarding
tags: ["команда", "инициализация", "проект"]
---

# /landing-new — Создать новый лендинг-проект

## Что делает
Создаёт пустую папку нового лендинга со всей структурой из шаблона и запускает оркестратор на этапе 00 (бриф). Это команда для опытных пользователей — без wizard-подсказок.

## Когда вызывать / в каком этапе
Вызывается вручную пользователем перед началом работы над новым проектом. Требует предварительно пройденного onboarding (`/landing-onboarding`). Для новичков рекомендуется `/landing-start` — там есть пошаговый мастер.

Принимает аргументы:
- `<slug>` — обязательное имя проекта в kebab-case (например, `lp-курс-марафон`)
- `--cinematic` — опционально, включает режим cinematic premium

## Что на вход / на выход

**Вход:**
- Аргумент `<slug>` — имя нового проекта
- Флаг `--cinematic` (опционально)
- Требует: setup-флаг `is_complete` (onboarding пройден)

**Выход:**
- Папка проекта `~/Lendings/<slug>/` с полной структурой из `template/`
- Файл `.landing-state.yaml` с заполненными полями `project` и `created`
- Gate-check для этапа `00_brief`
- Передача управления агенту `landing-orchestrator` на Stage 00

**Pre-flight проверки:**
1. Проверяет `bash scripts/setup-flag.sh is_complete` — если onboarding не пройден, останавливается
2. После создания папки копирует `template/.landing-state.yaml` в проект
3. Запускает `gate-check.sh --stage 00_brief` — проверяет наличие `brief.md`

## Связанные концепты
- [[landing-project-init]] — скилл, который создаёт структуру папок через `init.sh`
- [[landing-orchestrator]] — агент, принимающий управление после создания проекта (Stage 00)
- [[landing-onboarding]] — должен быть пройден до вызова этой команды
- [[landing-start]] — альтернатива с wizard для новичков

## Источник
- `commands/landing-new.md`