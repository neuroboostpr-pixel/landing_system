---
type: command
name: landing-help
sources: ["commands/landing-help.md"]
updated: 2026-05-15
triggers:
  - "покажи все команды системы"
  - "что умеет landing-system"
  - "справка по командам"
  - "какие команды доступны"
stage: ""
uses:
  - landing-new
  - landing-from-context
  - landing-clone
  - landing-references
  - landing-moodboard
  - landing-brand
  - landing-design
  - landing-stack
  - landing-content
  - landing-build
  - landing-deploy
  - landing-rollback
  - landing-qa
  - landing-status
tags: ["service", "help", "onboarding"]
---

# /landing-help — Справка по командам системы

## Что делает

Выводит полный список всех slash-команд landing-system с кратким описанием каждой. Ничего не создаёт и не изменяет — только справка.

## Когда вызывать / в каком этапе

Вызывать в любой момент — нет привязки к этапу. Полезно на старте, когда непонятно с чего начать, или при возврате к проекту после паузы.

## Что на вход / на выход

**Вход:** ничего не требуется.

**Выход:** фиксированный текстовый блок со всеми командами, разбитый на 4 раздела:

- **ENTRY POINTS** — точки входа: создать проект, создать из контекста агентства, клонировать A/B-копию.
- **PER-STAGE** — команды по этапам 03–08: референсы, мудборд, бренд, дизайн, стек, контент, сборка.
- **OPERATIONS** — деплой, передеплой, откат версии, QA-аудит.
- **SERVICE** — статус, справка, обновление мастер-системы.

## Связанные концепты

- [[landing-new]] — создаёт новый проект с нуля (упомянут в ENTRY POINTS)
- [[landing-from-context]] — создаёт проект из папки агентства (упомянут в ENTRY POINTS)
- [[landing-clone]] — A/B-клонирование существующего лендинга
- [[landing-status]] — текущее состояние системы и проектов
- [[landing-deploy]] — деплой на Бегет
- [[landing-rollback]] — откат к предыдущей версии
- [[landing-qa]] — QA-аудит живого сайта
- [[landing-build]] — сборка WordPress-темы (этап 08)

## Источник

- `commands/landing-help.md`