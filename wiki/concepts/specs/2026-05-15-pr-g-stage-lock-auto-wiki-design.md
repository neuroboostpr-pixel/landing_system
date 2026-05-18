---
type: rule
name: pr-g-stage-lock-auto-wiki
sources: ["docs/superpowers/specs/2026-05-15-pr-g-stage-lock-auto-wiki-design.md"]
updated: 2026-05-15
triggers: []
stage: ""
uses: ["stage-gates", "landing-orchestrator", "wiki"]
tags: ["infrastructure", "automation", "stage-lock", "git-hooks"]
---

# PR-G — Stage Lock + Auto-Wiki

## Что делает

Добавляет **жёсткий замок между этапами**: агент не может перейти на следующий шаг, пока не закрыты все зависимости. Одновременно автоматизирует пересборку системной wiki — после каждого `git commit`, затрагивающего агентов или скиллы, `wiki/` обновляется сама.

## Когда вызывать / в каком этапе

Это инфраструктурный PR — не вызывается руками. Механизм активируется автоматически:

- **Stage lock** — при каждом вызове `scripts/gate-check.sh`. Если следующий этап помечен `lock: hard` и его зависимости не в статусе `approved` — `gate-check` возвращает `exit 1` и выводит список чего не хватает.
- **Auto-wiki** — через `.githooks/post-commit`: если коммит трогает `agents/`, `skills/*/SKILL.md`, `commands/` или `template/*/README.md` — wiki пересобирается автоматически и авто-коммитится.
- **Граф проекта** — после успешного `gate-check` (exit 0) граф `<project>/wiki/index.md` обновляется.

Установка одноразовая: `bash scripts/install-git-hooks.sh`.

## Что на вход / на выход

**Вход:**
- `config/stage-gates.yaml` — конфиг этапов с новыми полями `lock` и `requires_approved`
- `.landing-state.yaml` проекта — текущие статусы этапов
- Коммит, затрагивающий источники wiki

**Выход:**
- `gate-check.sh` с логикой hard/soft лока:
  - Hard-лок → `exit 1` + список незакрытых зависимостей
  - Soft-лок → предупреждение `⚠️`, в `--auto` режиме проходит молча
- `.githooks/post-commit` — хук пересборки wiki
- `scripts/install-git-hooks.sh` — идемпотентная установка хука
- Обновлённый `agents/landing-orchestrator.md` — правило «сначала проверь gate-check»
- 4 bats-теста в `tests/wiki/test_pr_g/`

## Связанные концепты

- [[stage-gates]] — конфигурационный файл `config/stage-gates.yaml`, расширяемый полями `lock` и `requires_approved`
- [[landing-orchestrator]] — агент, которому добавляется обязательная проверка gate-check перед любым действием
- [[wiki]] — системная wiki, пересборка которой автоматизируется через post-commit hook

## Источник

- `docs/superpowers/specs/2026-05-15-pr-g-stage-lock-auto-wiki-design.md`