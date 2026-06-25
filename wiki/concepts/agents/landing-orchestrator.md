---
slug: landing-orchestrator
type: agent
name: "landing-orchestrator (Главный дирижёр)"
tags: [orchestrator, pipeline, workflow, dispatch, hard-gate, state-machine]
triggers: [landing-go, landing-new, landing-build, landing-deploy, landing-qa, landing-rollback, landing-clone]
inputs: [.landing-state.yaml, config/stage-gates.yaml, config/stages.yaml]
outputs: [00_БРИФ/brief.md, wiki/pipeline-map.md, .stage-decisions/*.md]
pre_reqs: [landing-project-init]
related:
  - landing-go
  - stage-execution-protocol
  - brand-architect
  - design-system-generator
  - content-writer
  - wp-builder
  - wp-deployer
  - qa-auditor
  - prototype-importer
  - block-composer
  - photo-curator
  - visual-curator
  - niche-analyst
  - stack-planner
sources: ["agents/landing-orchestrator.md"]
updated: 2026-06-19
confidence: {stage: low}
---

# landing-orchestrator (Главный дирижёр)

## Что делает

Центральный агент-оркестратор всего производственного конвейера лендинга. Читает `.landing-state.yaml`, определяет текущий этап, диспатчит нужного специализированного агента (brand-architect, wp-builder, qa-auditor и т.д.) и принудительно применяет HARD GATE между каждым этапом — не даёт перешагнуть вперёд без явного утверждения пользователя. В prototype-first режиме (PR-D) вход в конвейер начинается с этапа 07a (парсинг прототипа), а этапы 00–02 помечаются `n/a`. Параллельно диспатчит photo-curator и visual-curator (07d ⇆ 07e) через механизм `superpowers:dispatching-parallel-agents`.

## Когда вызывается

Основной триггер — `/landing-go` (PR-D, auto-resume по state). Также вызывается из `/landing-new`, `/landing-build`, `/landing-deploy`, `/landing-qa`, `/landing-rollback`, `/landing-clone`. Любой запуск начинается с чтения `.landing-state.yaml` — это условие без исключений.

## Вход → выход

**Вход:** инициализированный проект (`landing-project-init` пройден), `.landing-state.yaml` с текущим статусом этапов, `config/stage-gates.yaml` (hard/soft checks), опционально `prototype.pdf` в `07_ПРОТОТИП/source/`.

**Выход:** цепочка утверждённых артефактов этапов (brief.md → brand-kit.md → DESIGN.md → composed.html → wp-theme → задеплоенный сайт), обновлённый `wiki/pipeline-map.md`, записи решений в `.stage-decisions/`.

## Чем закрывается этап (gates)

Оркестратор не привязан к одному этапу — он закрывает каждый через:
- `gate-check.sh --stage <id> --project <project> --approve` (после verify-скрипта)
- `log-decisions.py` — фиксирует отклонения агента в `decisions.log.md`
- Для 07c/07f: обязателен exit 0 от `verify-composed-premium.sh` (13 фич) до approve

## Failure modes

- **Прыжок через этап** — state.yaml не содержит `approved` для зависимости; оркестратор отказывает и называет незакрытый этап.
- **Auto-fix цикл** — при падении hard_check и нескольких попытках авто-фикса срабатывает защита: один auto-fix per check_id per `/landing-go`.
- **Зависший 07c gate** — `verify-composed-premium.sh` не выходит в 0; блок-композер дорабатывает фичи, а не получает approve «и так сойдёт».
- **Потеря контекста** — пропуск шагов 1–2 протокола (render-pipeline-map + TodoWrite) ведёт к незамеченным этапам и потере истории решений.
- **Параллельный дедлок** — если один из субагентов (07d/07e) завис, оба гейта не пройдут; оркестратор ждёт оба DONE перед переходом к 07f.

## Related

- [[landing-go]] — slash-команда-точка входа, запускает оркестратор
- [[stage-execution-protocol]] — обязательный 4-шаговый протокол перед каждым действием
- [[prototype-importer]] — агент этапа 07a, парсинг прототипа
- [[block-composer]] — агент 07c/07f, рисует composed.html; оркестратор возвращает ему задачу при fail premium-gate
- [[photo-curator]] — параллельный субагент 07d
- [[visual-curator]] — параллельный субагент 07e
- [[wp-builder]] — агент этапа 08, сборка WP-темы
- [[premium-07b-checklist]] — эталон качества для 07c/07f hard gate