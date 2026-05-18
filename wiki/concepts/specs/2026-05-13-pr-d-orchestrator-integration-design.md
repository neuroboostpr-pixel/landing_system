---
type: command
name: landing-go
sources: ["docs/superpowers/specs/2026-05-13-pr-d-orchestrator-integration-design.md"]
updated: 2026-05-13
triggers:
  - "запустить лендинг с нуля от прототипа"
  - "что делать дальше по проекту"
  - "следующий этап лендинга"
  - "автоматически собрать лендинг"
stage: ""
uses:
  - landing-orchestrator
  - prototype-importer
  - references-curator
  - photo-curator
  - visual-curator
  - wp-builder
  - wp-deployer
  - visual-generation
  - stage-gates
  - dispatching-parallel-agents
tags: ["pr-d", "orchestrator", "prototype-first", "pipeline", "entry-point"]
---

# landing-go — Единая точка входа в pipeline (PR-D)

## Что делает

Одна команда `/landing-go` ведёт маркетолога по всему pipeline от `prototype.pdf` до готового сайта: читает `.landing-state.yaml`, определяет текущий этап, выдаёт одну конкретную инструкцию, ждёт подтверждения и переходит дальше. При провале гейта — предлагает автофикс.

## Когда вызывать / в каком этапе

Вызывается вручную в любой момент вместо ручного перебора команд (`/landing-prototype`, `/landing-wireframe` и т.д.). Заменяет необходимость помнить порядок этапов. Прежние команды (`/landing-photos`, `/landing-visuals` и др.) сохраняются для повторных прогонов.

**Prototype-first flow:** этапы 00–02 (бриф, контекст, ниша, материалы) помечаются `n/a` — оркестратор их пропускает. Вход = готовый `prototype.pdf` в `07_ПРОТОТИП/source/`.

## Что на вход / на выход

**Вход:**
- `.landing-state.yaml` проекта с текущим статусом этапов
- `prototype.pdf` или `prototype.md` в `07_ПРОТОТИП/source/`
- Необязательно: флаги `--auto-fix yes`, `--skip-gate <id>`

**Выход (по шагам):**
- Последовательное прохождение этапов 07a → 03 → 04 → 05 → 06 → 07 → 07b → 07c → **07d + 07e параллельно** → 07f → 08 → 09 → 10–12
- Обновлённый `.landing-state.yaml` после каждого утверждённого этапа
- При 07d+07e — параллельный запуск `photo-curator` и `visual-curator` через `dispatching-parallel-agents`
- `01a_АНАЛИЗ_НИШИ/landing-structure.md` генерируется из `prototype.yaml` скриптом `derive-landing-structure.py` (нужен для `wp-builder`)

**Ключевые новые артефакты PR-D:**
- `scripts/derive-landing-structure.py` — бридж для wp-builder
- `scripts/install-codex.sh` — авто-установка codex CLI
- `skills/visual-generation/scripts/lucide-fetcher.py` — Lucide SVG → PNG без codex API
- `scripts/verify-composed-has-visuals.sh`, `verify-php-syntax.sh`, `verify-gutenberg-json.sh`, `verify-site-url.sh` — новые gate-check скрипты
- 7 новых статусов в `template/.landing-state.yaml` (07a–07f + поддержка `n/a`)

## Связанные концепты

- [[landing-orchestrator]] — диспатчит специализированных агентов по этапам; обновляется в PR-D
- [[stage-gates]] — gate-check.sh расширяется поддержкой статуса `n/a` и новых этапов 07a–07f
- [[photo-curator]] — агент 07d_photos, запускается параллельно с visual-curator
- [[visual-curator]] — агент 07e_visuals; Lucide-ветка экономит codex API
- [[prototype-importer]] — обрабатывает 07a_prototype (первый автоматический шаг)
- [[visual-generation]] — skill с обновлённым `prompt-picker.py` (Lucide как первый шаг waterfall)
- [[landing-onboarding]] — переписывается: codex install + объяснение prototype-first flow
- [[wp-builder]] — использует `landing-structure.md` из `derive-landing-structure.py`

## Источник

- `docs/superpowers/specs/2026-05-13-pr-d-orchestrator-integration-design.md`