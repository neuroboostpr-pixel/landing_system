---
type: agent
name: lifecycle-keeper
sources: ["agents/lifecycle-keeper.md"]
updated: 2026-05-25
triggers: []
stage: ""
uses: ["landing-rollback", "landing-clone", "landing-versioning-and-cloning", "landing-deploy"]
tags: ["ops", "lifecycle", "versioning", "rollback", "clone"]
---

# lifecycle-keeper (Хранитель версий)

## Что делает
Управляет версиями лендингов: создаёт снапшоты, откатывает проект к предыдущей версии, создаёт A/B-клоны для тестирования вариантов.

## Когда вызывать / в каком этапе
Агент работает **вне основного pipeline** и не привязан к конкретному этапу. Запускается командами `/landing-rollback` и `/landing-clone` — когда нужно зафиксировать стабильную версию перед рискованными изменениями, откатиться назад или создать копию лендинга для A/B-тестирования. Stage Execution Protocol к нему не применяется.

## Что на вход / на выход

**Вход:**
- Директория проекта (`<project-dir>`)
- Имя версии (например, `v1.0`) или slug нового клона

**Выход:**
- **Создание версии:** снапшот в `09_ВЕРСИИ/v1.0/` с темой и кодом
- **Откат:** восстановленный `08_КОД/wp-theme` из выбранной версии + повторный деплой через `/landing-deploy`
- **A/B клон:** полная копия проекта задеплоена на новый поддомен

**Ключевые скрипты:**
- `skills/landing-versioning-and-cloning/scripts/create-version.sh` — создание снапшота
- `skills/landing-versioning-and-cloning/scripts/clone-landing.sh` — клонирование проекта

## Связанные концепты
- [[landing-rollback]] — slash-команда, которая вызывает этот агент для отката
- [[landing-clone]] — slash-команда для создания A/B-клона
- [[landing-deploy]] — используется после отката для повторного деплоя темы на Бегет
- [[landing-versioning-and-cloning]] — скилл с bash-скриптами версионирования

## Источник
- `agents/lifecycle-keeper.md`