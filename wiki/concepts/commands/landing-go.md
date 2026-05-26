---
slug: landing-go
type: command
name: "/landing-go — Главная команда оркестратора"
tags: [orchestrator, entry-point, pipeline, dispatch, prototype-first]
triggers: [landing-go]
inputs: ["07_ПРОТОТИП/source/prototype.pdf", "07_ПРОТОТИП/source/prototype.md", ".landing-state.yaml"]
outputs: [".landing-state.yaml"]
pre_reqs: [landing-project-init, landing-onboarding-wizard]
related: [landing-orchestrator, prototype-importer, brand-architect, design-system-generator, stack-planner, content-writer, block-composer, photo-curator, visual-curator, wp-builder, wp-deployer, seo-tech-audit, wireframe-rendering]
sources: ["commands/landing-go.md"]
updated: 2026-05-26
confidence: {stage: low}
---

# /landing-go — Главная команда оркестратора

## Что делает

Единая точка входа в производственный конвейер лендинга. Читает `.landing-state.yaml`, определяет текущий статус проекта и диспатчит следующий этап через `landing-orchestrator`. В режиме prototype-first автоматически помечает upstream-этапы (00, 01, 01a, 02) как `n/a`, чтобы не проваливать gate-check по ненужным шагам. На этапах 07d/07e запускает субагентов фото и визуалов параллельно. При падении гейта предлагает авто-фикс из `config/stage-gates.yaml` и автоматически перезапускает проверку после исправления.

## Когда вызывается

Пользователь запускает `/landing-go` вручную — один раз в начале или после каждого шага, требующего ручного подтверждения (выбор вариантов в wireframe, утверждение brand-kit). Повторный запуск безопасен: оркестратор сам находит незакрытый этап и продолжает с него.

## Вход → выход

**Вход:** Папка проекта с файлом `prototype.pdf` или `prototype.md` в `07_ПРОТОТИП/source/`. Файл `.landing-state.yaml` должен существовать (создаётся командой `/landing-new` или `/landing-start`).

**Выход:** Последовательно закрытые этапы конвейера: prototype → references → brand → design → stack → content → wireframe → composed → photos + visuals → composed_final → build → deploy → QA → SEO. На каждом шаге обновляется `.landing-state.yaml`, появляются артефакты соответствующего этапа.

## Failure modes

- **Prototype не найден** — скрипт `landing-go-next-stage.py` не может определить флоу, оркестратор останавливается с ошибкой «нет источника прототипа».
- **Upstream-этапы не помечены `n/a`** — `gate-check.sh` пытается валидировать бриф и анализ ниши, которых нет в prototype-first потоке, и падает с ложными hard-check ошибками.
- **Гейт упал без `fix_hint`** — авто-фикс не предлагается, пользователь видит ошибку без инструкций по устранению.
- **Параллельный запуск 07d/07e** — если один субагент зависает, второй завершится, а оркестратор ждёт оба; тайм-аут не определён явно.
- **Флаг `--skip-gate` в продакшне** — позволяет обойти hard-check, что нарушает контракт stage-gates и может привести к деплою недоделанного проекта.

## Related

- [[landing-orchestrator]] — агент, которого диспатчит эта команда; выполняет реальную работу по этапам
- [[prototype-importer]] — первый авто-этап (07a), вызываемый оркестратором
- [[brand-architect]] — этап 04, интерактивный, требует ручного подтверждения
- [[design-system-generator]] — этап 05, генерирует токены и палитру
- [[photo-curator]] — этап 07d, параллельный с 07e
- [[visual-curator]] — этап 07e, параллельный с 07d
- [[wp-builder]] — этап 08, сборка WordPress-темы
- [[wp-deployer]] — этап 09, деплой на Бегет
- [[landing-onboarding-wizard]] — создаёт проект и `.landing-state.yaml` до первого вызова `/landing-go`
- [[wireframe-rendering]] — этап 07b, пользователь выбирает варианты блоков вручную