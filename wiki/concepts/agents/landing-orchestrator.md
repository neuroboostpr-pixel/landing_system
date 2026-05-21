---
type: agent
name: landing-orchestrator
sources: ["agents/landing-orchestrator.md"]
updated: 2026-05-20
triggers: ["запустить лендинг", "следующий этап", "landing-go", "продолжить проект"]
stage: ""
uses: ["niche-analyst", "client-assets-collector", "photo-stylist", "references-curator", "moodboard-composer", "style-extractor", "brand-architect", "design-system-generator", "scene-director", "stack-planner", "content-writer", "wp-builder", "integrations-engineer", "analytics-engineer", "seo-optimizer", "wp-deployer", "qa-auditor", "lifecycle-keeper", "block-composer", "photo-curator", "visual-curator", "prototype-importer"]
tags: ["orchestrator", "pipeline", "workflow", "hard-gate"]
---

# landing-orchestrator (Главный дирижёр)

## Что делает

Ведёт проект-лендинг через 12 этапов: от брифа до деплоя и SEO. На каждом этапе диспатчит нужного специализированного агента, ждёт HTML-превью, получает явное «утверждаю» от пользователя и только потом переходит дальше. Пропустить этап или перепрыгнуть вперёд — невозможно.

## Когда вызывать / в каком этапе

Активируется командой `/landing-go` (PR-D) — единственная точка входа после инициализации проекта. В режиме prototype-first стартует с этапа `07a_prototype` (этапы 00–02 помечены `n/a`). В полном flow — с этапа 00 (Бриф).

## Что на вход / на выход

**Вход:**
- `.landing-state.yaml` текущего проекта (читается перед каждым действием)
- `config/stage-gates.yaml` — список зависимостей между этапами
- Для prototype-first: `07_ПРОТОТИП/source/prototype.pdf`

**Выход (по этапам):**
- `00_БРИФ/brief.md` — зафиксированный бриф
- HTML-превью от каждого агента (`moodboard.html`, `brand-kit.html`, `design-preview.html`, `build-preview.html` и т.д.)
- Финально — задеплоенный сайт, QA-отчёт, SEO-конфиги

**Обязательный ритуал перед каждым действием (Stage Execution Protocol):**
1. Прочитать `.landing-state.yaml`, запустить `render-pipeline-map.sh --write-wiki` — показать Mermaid-карту
2. Создать TodoWrite со всеми оставшимися этапами
3. Запустить `gate-check.sh` для текущего этапа; при hard-fail — показать fix_hint
4. Verify → approve → переход к следующему этапу

**Параллельная диспетчеризация:** когда этап `07c_composed` одобрен — одновременно запускает `photo-curator` (07d) и `visual-curator` (07e) через `superpowers:dispatching-parallel-agents`.

**Premium gate 07b:** не закрывает этап `07c_composed`, пока `verify-composed-premium.sh` не вернёт exit 0 (13 обязательных фич).

## Связанные концепты

- [[landing-go]] — команда-триггер единой точки входа (PR-D)
- [[niche-analyst]] — диспатчится на этапе 01a
- [[brand-architect]] — диспатчится на этапе 04
- [[design-system-generator]] — диспатчится на этапе 05
- [[wp-builder]] — диспатчится на этапе 08
- [[photo-curator]] — параллельный субагент этапа 07d
- [[visual-curator]] — параллельный субагент этапа 07e
- [[qa-auditor]] — диспатчится на этапе 10
- [[lifecycle-keeper]] — rollback и clone (этапы 09+)
- [[block-composer]] — получает задачу доработки если premium gate 07b не пройден

## Источник

- `agents/landing-orchestrator.md`