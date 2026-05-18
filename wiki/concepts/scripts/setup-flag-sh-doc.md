---
type: rule
name: setup-flag
sources: ["scripts/setup-flag.sh", "scripts/setup-flag.sh.doc.md"]
updated: 2026-05-18
triggers: []
stage: ""
uses: ["system-setup", "landing-onboarding", "onboarding-guide", "stage-gates"]
tags: ["bash", "script", "onboarding", "flag", "setup"]
---

# setup-flag — управление флагом завершения онбординга

## Что делает

Bash-скрипт, который создаёт, проверяет и удаляет флаговый файл `~/.landing-system/setup_complete`. Флаг сигнализирует системе, что пользователь прошёл онбординг — без него большинство `/landing-*` команд отказываются работать.

## Когда вызывать / в каком этапе

Вызывается автоматически внутри других скриптов и агентов:

- `onboarding-guide` / `system-setup` вызывают `mark_complete` после успешного завершения мастера настройки.
- `landing-orchestrator` и gate-check вызывают `is_complete` перед запуском любого этапа — если флага нет, workflow блокируется.
- `reset` используется при полном сбросе системы или при повторном онбординге.

Напрямую пользователь скрипт не вызывает, но может проверить статус вручную:

```bash
bash scripts/setup-flag.sh is_complete && echo "OK" || echo "не настроен"
bash scripts/setup-flag.sh timestamp
```

## Что на вход / на выход

**Вход:** одна из четырёх команд как первый аргумент:

| Команда | Действие |
|---|---|
| `is_complete` | exit 0 если флаг есть, exit 1 иначе |
| `mark_complete` | создаёт `~/.landing-system/setup_complete` с UTC-меткой |
| `reset` | удаляет файл флага |
| `timestamp` | печатает время создания флага или «not set» |

**Выход:** exit-код (0/1/2) и побочный эффект — наличие/отсутствие файла `~/.landing-system/setup_complete`.

## Связанные концепты

- [[system-setup]] — агент первичной настройки; вызывает `mark_complete` по итогу
- [[onboarding-guide]] — wizard онбординга; тот же триггер для `mark_complete`
- [[stage-gates]] — логика ворот этапов; проверяет `is_complete` перед каждым этапом
- [[landing-onboarding]] — команда `/landing-onboarding`; использует флаг как пре-чек

## Источник

- `scripts/setup-flag.sh`
- `scripts/setup-flag.sh.doc.md`