---
name: landing-project-init
description: Use when user wants to create a new landing project from scratch. Creates a project folder by copying the template and initializes it with metadata.
---

# landing-project-init

## Pre-flight

```bash
python -m scripts.wiki.log --type skill_call --skill landing-project-init --stage ""
```

## Когда использовать

- Пользователь сказал «создай новый лендинг», `/landing-new <slug>`, или эквивалент.
- Нужна **чистая** папка проекта (не из существующего контекста — для этого есть `landing-from-context`).

## Что делаю

1. Принимаю slug проекта (например, `lp-курс-марафон`).
2. Запрашиваю базовые поля: ниша, клиент, желаемый домен (опционально на старте).
3. Запускаю `scripts/init.sh <slug>`:
   - Создаёт `~/Lendings/<slug>/` со структурой template/.
   - Инициализирует git-репо.
   - Заполняет placeholder в README.md и CLAUDE.md проекта.
4. Открываю в проекте файл `00_БРИФ/brief.md` для заполнения первого этапа.
5. Передаю управление `landing-orchestrator` для запуска workflow с этапа 00.

## Аргументы

- `<slug>` — имя папки и проекта (kebab-case рекомендуется)
- `--cinematic` (опционально) — флаг premium-режима

## Side effects

- Создаётся новая папка вне `landing-system/`. Папка проекта **не вкладывается** в мастер-систему.
- Инициализируется git-репо проекта.

## Что НЕ делаю

- Не создаю WordPress (это Phase 5: `wp-deployer`).
- Не запрашиваю домен жёстко (можно отложить до этапа 09).
- Не вызываю других агентов кроме передачи `landing-orchestrator`.

## Скрипт

См. [`scripts/init.sh`](scripts/init.sh).
