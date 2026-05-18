---
type: command
name: migrate-state-for-prd
sources: ["scripts/migrate-state-for-prd.sh"]
updated: 2026-05-18
triggers: ["нужно мигрировать старый проект на PR-D", "обновить .landing-state.yaml до schema v2", "добавить новые этапы в state-файл существующего проекта"]
stage: ""
uses: ["landing-go", "landing-orchestrator"]
tags: ["migration", "state", "pr-d", "bash"]
---

# migrate-state-for-prd — миграция state-файла на схему PR-D

## Что делает

Обновляет файл `.landing-state.yaml` существующего лендинг-проекта: добавляет новые этапы, введённые в PR-D (оркестратор), и поднимает версию схемы до `2`. Уже существующие этапы при этом остаются нетронутыми.

## Когда вызывать / в каком этапе

Используется **один раз** при переходе существующего проекта на workflow PR-D. Запускается вручную из командной строки перед первым вызовом `/landing-go` на старом проекте. Если проект создан уже после выхода PR-D — миграция не нужна, `schema_version: 2` выставляется автоматически при инициализации.

```bash
bash scripts/migrate-state-for-prd.sh ~/Lendings/<slug>/.landing-state.yaml
```

## Что на вход / на выход

| Направление | Артефакт |
|---|---|
| **Вход** | Путь к `.landing-state.yaml` существующего проекта (schema_version 1) |
| **Выход** | Тот же файл, дополненный новыми этапами со статусом `locked`; `schema_version` поднят до `2` |

**Идемпотентность:** скрипт можно запускать повторно — уже присутствующие этапы не дублируются и не сбрасываются.

## Связанные концепты

- [[landing-go]] — главная точка входа PR-D; читает `.landing-state.yaml` и требует `schema_version: 2`
- [[landing-orchestrator]] — оркестратор, управляющий этапами из state-файла

## Источник

- `scripts/migrate-state-for-prd.sh`