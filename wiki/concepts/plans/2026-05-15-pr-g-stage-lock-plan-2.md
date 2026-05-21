---
type: rule
name: pr-g-stage-lock-auto-wiki
sources: ["docs/superpowers/plans/2026-05-15-pr-g-stage-lock-plan 2.md"]
updated: 2026-05-19
triggers: []
stage: ""
uses: ["landing-orchestrator", "gate-check", "design-tokens-generation", "niche-analysis"]
tags: ["stage-lock", "wiki", "gate-check", "automation", "pr-g"]
---

# PR-G — Блокировка этапов и авто-обновление wiki

## Что делает
Вводит строгую дисциплину прохождения этапов лендинг-проекта: технически важные шаги теперь нельзя пропустить, а wiki автоматически обновляется при каждом коммите и закрытии этапа.

## Когда вызывать / в каком этапе
Это системное правило, действующее на протяжении всего pipeline. Активируется неявно при запуске `bash scripts/gate-check.sh` и через git post-commit hook. Установка хуков — один раз командой `bash scripts/install-git-hooks.sh`.

## Что на вход / на выход

**Вход:**
- `config/stage-gates.yaml` — конфиг всех этапов (существующий)
- `scripts/gate-check.sh` — скрипт проверки ворот (существующий)
- `.landing-state.yaml` проекта — текущий статус этапов

**Выход:**
- Расширенный `config/stage-gates.yaml` с полями `lock: hard|soft` и `require_approved` для каждого этапа
- Обновлённый `scripts/gate-check.sh` с soft-warning блоком и авто-обновлением project-graph wiki
- `.githooks/post-commit` — git hook, пересобирающий системную wiki после коммитов, затрагивающих `agents/`, `skills/`, `commands/`, `template/`, `docs/standards/`
- `scripts/install-git-hooks.sh` — идемпотентный установщик хуков через `core.hooksPath`
- Обновлённый промпт `agents/landing-orchestrator.md` с обязательной секцией gate-check
- `tests/pr-g/*.bats` — 7+ bats-тестов на hard-lock, soft-warning и авто-обновление графа

**Механика блокировок:**

| Тип | Этапы | Поведение |
|---|---|---|
| **hard** | 07b, 07c, 08, 09, 10 | exit != 0, пока зависимости не approved |
| **soft** | все остальные | ⚠️ предупреждение + y/N в интерактиве; `--auto` пропускает |

**Защита от рекурсии в хуке:** если последний коммит уже `chore(wiki)` — hook молча выходит.

## Связанные концепты
- [[landing-orchestrator]] — получает новый обязательный раздел «предусловия gate-check» в промпте; запрещено действовать вне `current_stage`
- [[landing-build]] — этап `08_build` теперь hard-lock, требует `07c_composed: approved`
- [[wp-deployer]] — этап `09_deploy` hard-lock, требует И `08_build` И `10_qa`
- [[qa-auditor]] — этап `10_qa` hard-lock, требует `08_build`
- [[block-composition]] — этап `07c_composed` hard-lock, требует `05_design + 07a_prototype + 07b_wireframe`

## Источник
- `docs/superpowers/plans/2026-05-15-pr-g-stage-lock-plan 2.md`