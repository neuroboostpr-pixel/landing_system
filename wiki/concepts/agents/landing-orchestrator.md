---
type: agent
name: landing-orchestrator
sources: ["agents/landing-orchestrator.md"]
updated: 2026-05-19
triggers: []
stage: "00–12"
uses:
  - niche-analyst
  - client-assets-collector
  - photo-stylist
  - references-curator
  - moodboard-composer
  - style-extractor
  - brand-architect
  - design-system-generator
  - scene-director
  - stack-planner
  - content-writer
  - wp-builder
  - integrations-engineer
  - analytics-engineer
  - seo-optimizer
  - wp-deployer
  - qa-auditor
  - lifecycle-keeper
  - prototype-importer
  - photo-curator
  - visual-curator
  - block-composer
  - landing-go
  - landing-build
  - landing-deploy
  - landing-qa
  - landing-rollback
  - landing-clone
  - stage-execution-protocol
  - gate-check
tags: [orchestrator, workflow, pipeline, core]
---

# landing-orchestrator (Главный дирижёр)

## Что делает

Ведёт проект-лендинг через все 12 этапов производственного конвейера — от брифа до SEO. На каждом шаге диспатчит нужного специализированного агента, проверяет качество результата и не даёт перепрыгнуть этап без явного одобрения маркетолога.

## Когда вызывать / в каком этапе

Активируется после инициализации проекта (`landing-project-init` или `landing-from-context`). Основная точка входа — команда `/landing-go`, которая читает `.landing-state.yaml` и продолжает с того этапа, где остановились. Отдельные этапы также запускаются через `/landing-build`, `/landing-deploy`, `/landing-qa`, `/landing-rollback`, `/landing-clone`.

## Что на вход / на выход

**Вход:**
- Инициализированная папка проекта (`~/Lendings/<slug>/`) со структурой template/
- `.landing-state.yaml` с текущим статусом этапов
- `config/stage-gates.yaml` — правила переходов между этапами

**Выход:**
- Последовательно заполненные папки `00_БРИФ/` → `12_SEO/`
- HTML-превью на каждом ключевом этапе (moodboard.html, brand-kit.html, design-preview.html, composed.html, build-preview.html)
- Полностью задеплоенный WordPress-сайт на Бегете

## Как работает (протокол)

Перед каждым действием оркестратор обязан:
1. Прочитать `.landing-state.yaml`, показать Mermaid-карту pipeline через `render-pipeline-map.sh`.
2. Создать TodoWrite-список всех оставшихся этапов.
3. Запустить `gate-check.sh` для текущего этапа; при провале — предложить авто-fix.
4. После verify и явного одобрения пользователя — закрыть этап через `gate-check.sh --approve` и перейти к следующему.

В prototype-first режиме (PR-D) этапы 00–02 помечаются `n/a`, старт — с `07a_prototype`. Этапы `07d_photos` и `07e_visuals` диспатчатся **параллельно** через `superpowers:dispatching-parallel-agents`.

HARD GATE — нельзя пропустить этап даже по просьбе пользователя. Пропуск «сойдёт» — недопустим.

## Связанные концепты

- [[niche-analyst]] — этап 01a, анализ ниши
- [[brand-architect]] — этап 04, бренд-кит
- [[design-system-generator]] — этап 05, токены и DESIGN.md
- [[wp-builder]] — этап 08, генерация WordPress-темы
- [[photo-curator]] — этап 07d, обработка клиентских фото
- [[visual-curator]] — этап 07e, генерация иконок и инфографики
- [[block-composer]] — этап 07b, сборка composed.html
- [[qa-auditor]] — этап 10, аудит live-сайта
- [[stage-execution-protocol]] — обязательный протокол 4 шагов перед каждым действием
- [[gate-check]] — скрипт проверки и утверждения этапов
- [[landing-go]] — команда-триггер для prototype-first режима

## Источник

- `agents/landing-orchestrator.md`