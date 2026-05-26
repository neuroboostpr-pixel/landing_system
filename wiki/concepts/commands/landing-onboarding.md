---
slug: landing-onboarding
type: command
name: "Команда первичной настройки /landing-onboarding"
stage: "00"
tags: [onboarding, setup, wizard, dependencies]
triggers: [landing-onboarding]
inputs: [docs/SETUP.md]
outputs: []
gates: []
pre_reqs: []
related: [onboarding-guide, system-setup, landing-project-init, landing-orchestrator]
sources: ["commands/landing-onboarding.md"]
updated: 2026-05-26
confidence: {stage: low, outputs: low}
---

# Команда первичной настройки /landing-onboarding

## Что делает

Запускает интерактивный wizard первичной настройки landing-system на новой машине. Читает `docs/SETUP.md`, объясняет пользователю, что такое система, затем диспатчит агента `onboarding-guide`, который прогоняет скрипт `wizard.sh`. После успешного прохождения всех проверок ставит флаг `~/.landing-system/setup_complete`, подтверждающий готовность среды. Если флаг уже существует — спрашивает, нужно ли перезапустить (например, для добавления новых API-ключей).

## Когда вызывается

Вызывается вручную пользователем командой `/landing-onboarding` перед первым запуском любой `/landing-*` команды. Системный gate-check требует наличия флага `setup_complete` — без него остальные команды заблокированы.

## Вход → выход

**Вход:** свежая копия репозитория landing-system, доступ к терминалу, файл `docs/SETUP.md`.

**Выход:** флаг `~/.landing-system/setup_complete` (если все validators прошли) или список недостающих зависимостей и API-ключей.

## Failure modes

- `docs/SETUP.md` недоступен или не читается — агент не получает брифинг и может пропустить шаги.
- `scripts/wizard.sh` падает с ошибкой (не установлены зависимости, нет прав) — флаг не выставляется, пользователь не получает внятного сообщения.
- `scripts/setup-flag.sh mark_complete` не выполняется — онбординг визуально завершается, но флага нет; последующие `/landing-*` команды отказывают.
- Пользователь прерывает wizard на середине — валидаторы частично пройдены, состояние неопределённо.
- Флаг уже есть, но среда изменилась (новые ключи не добавлены) — wizard не запустится без явного подтверждения, проблема может остаться незамеченной.

## Related

- [[onboarding-guide]] — агент, которого диспатчит команда; ведёт пользователя по wizard.sh
- [[system-setup]] — концепт настройки системы, с которым onboarding тесно связан
- [[landing-project-init]] — следующий шаг после онбординга: создание нового проекта
- [[landing-orchestrator]] — главный дирижёр pipeline, требует пройденного онбординга