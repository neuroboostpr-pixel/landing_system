---
type: agent
name: lifecycle-keeper
sources: ["agents/lifecycle-keeper.md"]
updated: 2026-05-20
triggers: []
stage: ""
uses: ["landing-rollback", "landing-clone", "landing-versioning-and-cloning", "wp-deployer"]
tags: ["ops", "versions", "rollback", "clone", "ab-test"]
---

# lifecycle-keeper (Хранитель версий)

## Что делает
Сохраняет снапшоты лендинга в любой момент, откатывает проект на предыдущую версию и создаёт A/B-клоны на отдельных поддоменах. Работает вне основного пайплайна — как ops-инструмент.

## Когда вызывать / в каком этапе
Не привязан к конкретному этапу pipeline. Вызывается вручную через команды:
- `/landing-rollback` — когда нужно откатить проект до сохранённой версии.
- `/landing-clone` — когда нужно создать A/B-копию лендинга на новом поддомене.

Может использоваться в любой момент жизненного цикла проекта — до или после деплоя. Stage Execution Protocol на него не распространяется.

## Что на вход / на выход

**Вход:**
- Путь к папке проекта (`<project-dir>`).
- Имя версии (например, `v1.0`) или новый slug для клона.
- Существующие артефакты в `08_КОД/wp-theme`.

**Выход:**
- **Версия:** снапшот сохраняется в `09_ВЕРСИИ/<version-name>/`.
- **Откат:** файлы из `09_ВЕРСИИ/v1.0/wp-theme` копируются обратно в `08_КОД/wp-theme`, после чего запускается `/landing-deploy`.
- **A/B-клон:** создаётся полная копия проекта с новым slug → деплоится на новый поддомен.

**Инструменты:** `Bash`, `Read` (только эти два).

**Скрипты:**
- `skills/landing-versioning-and-cloning/scripts/create-version.sh` — создание снапшота.
- `skills/landing-versioning-and-cloning/scripts/clone-landing.sh` — создание A/B-клона.

## Связанные концепты
- [[landing-rollback]] — slash-команда, которая вызывает агента для отката версии
- [[landing-clone]] — slash-команда для создания A/B-клона
- [[landing-versioning-and-cloning]] — скилл с bash-скриптами, которые агент исполняет
- [[wp-deployer]] — используется после отката для повторного деплоя темы

## Источник
- `agents/lifecycle-keeper.md`