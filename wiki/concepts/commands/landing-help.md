---
slug: landing-help
type: command
name: "Справка по командам системы"
tags: [help, commands, reference, entry-point]
triggers: [/landing-help]
inputs: []
outputs: []
pre_reqs: []
related: [landing-project-init, landing-from-context, landing-versioning-and-cloning, landing-orchestrator, qa-auditor, wp-cli-deployer]
sources: ["commands/landing-help.md"]
updated: 2026-05-26
---

# Справка по командам системы

## Что делает

Выводит полный список slash-команд landing-system с кратким описанием каждой. Команда не запускает никаких агентов и не меняет состояние проекта — только печатает справочный текст. Охватывает все категории: точки входа в проект, поэтапные команды (03–08), операционные команды деплоя и сервисные утилиты.

## Когда вызывается

Запускается вручную пользователем в любой момент работы с системой. Типичные поводы: первое знакомство с системой, забытое имя команды для конкретного этапа, быстрая ориентация по доступным операциям. Не зависит от состояния проекта и не требует `.landing-state.yaml`.

## Вход → выход

**Вход:** ничего не требуется — команда не читает файлы проекта.

**Выход:** текстовый блок в чат со сгруппированным списком команд: ENTRY POINTS (new / from-context / clone), PER-STAGE (references → build), OPERATIONS (deploy / rollback / qa), SERVICE (status / help / update). Указывает, что большинство команд за пределами Phase 1 ещё не реализованы.

## Failure modes

- Пользователь видит команду `/landing-update` как доступную, хотя она явно помечена «еще не реализован» — может вызвать недоумение.
- Список команд не обновляется автоматически при добавлении новых slash-команд — требует ручного редактирования файла.
- Команды PR-A/PR-B/PR-C/PR-D (`/landing-prototype`, `/landing-visuals`, `/landing-go` и др.) отсутствуют в выводе — справка устарела относительно реального состояния системы.
- При использовании вне проектной папки не предупреждает, что часть команд требует контекст проекта.

## Related

- [[landing-project-init]] — инициализирует новый проект, описан в справке как `/landing-new`
- [[landing-from-context]] — создаёт проект из папки агентства, описан в справке
- [[landing-versioning-and-cloning]] — команда `/landing-clone`, упомянута в ENTRY POINTS
- [[landing-orchestrator]] — координирует поэтапный процесс, на который ссылаются PER-STAGE команды
- [[qa-auditor]] — реализует `/landing-qa` из секции OPERATIONS
- [[wp-cli-deployer]] — реализует `/landing-deploy` из секции OPERATIONS