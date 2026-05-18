---
type: rule
name: pr-d-orchestrator-integration-plan
sources: ["docs/superpowers/plans/2026-05-13-pr-d-orchestrator-integration-plan.md"]
updated: 2026-05-18
triggers: []
stage: ""
uses:
  - landing-go
  - landing-orchestrator
  - visual-generation
  - stage-gates
  - landing-onboarding
  - prototype-import
  - photo-curation
tags: ["plan", "pr-d", "orchestrator", "prototype-first", "lucide", "parallel-dispatch"]
---

# PR-D: Plan реализации интеграции оркестратора

## Что делает

Описывает пошаговый план реализации PR-D: подключение пайплайнов PR-A (прототип/wireframe/compose), PR-B (фото), PR-C (иконки/инфографика) в единую команду `/landing-go`. Вводит prototype-first поток, параллельный запуск 07d⇆07e, механизм авто-фикса и установку codex CLI.

## Когда вызывать / в каком этапе

Документ служит техническим заданием для реализации PR-D. Используется как референс при любой доработке оркестратора, `stage-gates.yaml`, `.landing-state.yaml` или скриптов pipeline.

## Что на вход / на выход

**Входные артефакты:**
- `template/.landing-state.yaml` (schema v1, без PR-D стадий)
- `config/stage-gates.yaml` (без 07a–07f)
- `scripts/gate-check.sh` / `gate-state.sh` (без поддержки статуса `n/a`)
- `skills/visual-generation/scripts/prompt-picker.py` (без Lucide-ветки)

**Выходные артефакты (12 задач):**
- `template/.landing-state.yaml` — schema v2, 7 новых стадий (07a–07f), статус `n/a` для этапов 00/01/01a/02
- `config/stage-gates.yaml` — гейты для 07a_prototype, 07b_wireframe, 07c_composed, 07d_photos, 07e_visuals, 07f_composed_final; усилены 08/09
- `scripts/gate-check.sh` / `gate-state.sh` — поддержка `n/a` как эквивалент `approved` в `require_approved`
- `scripts/derive-landing-structure.py` — мост prototype.yaml → landing-structure.md для wp-builder
- `scripts/verify-composed-has-visuals.sh`, `verify-php-syntax.sh`, `verify-gutenberg-json.sh`, `verify-site-url.sh` — проверки для гейтов 07f/08/09
- `skills/visual-generation/scripts/lucide-fetcher.py` — загрузка SVG из Lucide + рендер в PNG с брендовым цветом
- `skills/visual-generation/scripts/prompt-picker.py` — Lucide как первый шаг водопада (если `Library=Lucide` в icons.csv → пропустить codex)
- `scripts/install-codex.sh` — авто-установка codex CLI через npm с fallback на sudo-подсказку
- `commands/landing-go.md` — slash-команда + `scripts/landing-go-next-stage.py`
- `agents/landing-orchestrator.md` — PR-D секция: prototype-first таблица диспетчеризации, параллельный запуск 07d‖07e, auto-fix mechanism
- `skills/landing-onboarding/SKILL.md` — объяснение нового потока, шаг install-codex
- `scripts/migrate-state-for-prd.sh` — идемпотентная миграция существующих проектов с v1 на v2
- `THIRD_PARTY_NOTICES.md` — attribution для Lucide (ISC)
- `CLAUDE.md` — документация нового потока PR-D

**Тест-покрытие:** 25+ новых тестов (bats + pytest) в `tests/phase-prd/`.

## Связанные концепты

- [[landing-go]] — главная команда, создаваемая в этом плане
- [[landing-orchestrator]] — агент, расширяемый prototype-first логикой и параллельным dispatching
- [[visual-generation]] — скилл, получающий Lucide-ветку в prompt-picker
- [[stage-gates]] — конфиг, расширяемый 7 новыми гейтами и проверками 08/09
- [[landing-onboarding]] — скилл, обновляемый с объяснением нового потока и codex install
- [[prototype-import]] — PR-A, становится первым этапом (07a_prototype) в новом потоке
- [[photo-curation]] — PR-B (07d_photos), запускается параллельно с PR-C
- [[visual-qa]] — PR-C (07e_visuals), запускается параллельно с PR-B

## Источник

- `docs/superpowers/plans/2026-05-13-pr-d-orchestrator-integration-plan.md`