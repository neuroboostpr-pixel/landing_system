---
description: Single entry point для конвейера landing-system. Читает .landing-state.yaml, диспатчит следующий этап через landing-orchestrator. Поддерживает auto-fix и параллельную диспетчеризацию 07d⇆07e.
---

# /landing-go

Главная команда оркестратора. Запусти её один раз — и она проведёт тебя по всем этапам от прототипа до live сайта на Бегете.

## Использование

```
/landing-go [--project <slug>] [--auto-fix yes|no] [--skip-gate <id>]
```

**Флаги:**
- `--project <slug>` — папка проекта (по умолчанию текущая).
- `--auto-fix yes` — применять авто-фиксы без подтверждения.
- `--skip-gate <id>` — пропустить конкретный гейт-чек (для отладки).

## Вход (prototype-first)

Положи `prototype.pdf` или `prototype.md` в `<project>/07_ПРОТОТИП/source/`.

Этапы 00 (бриф), 01 (контекст), 01a (анализ ниши), 02 (материалы клиента) автоматически помечаются `n/a` — они происходят до landing-system.

### Mark upstream stages n/a (prototype-first)

Перед стартом оркестратора проверь флоу. Если в `<project>/07_ПРОТОТИП/source/` лежит `prototype.pdf` или `prototype.md` — флоу определяется как **prototype-first**. В этом случае явно помечай upstream-этапы как `n/a`, чтобы `gate-check.sh` не пытался их валидировать:

```bash
PROJECT="${1:-$PWD}"  # либо --project <slug>
if [ -f "$PROJECT/07_ПРОТОТИП/source/prototype.pdf" ] || \
   [ -f "$PROJECT/07_ПРОТОТИП/source/prototype.md" ]; then
  for stage in 00_brief 01_context 01a_niche_analysis 02_assets; do
    # TODO: pass legacy_reason after Phase 4 Task 4.4 lands
    bash scripts/gate-state.sh set "$PROJECT" "$stage" n/a
  done
fi
```

Если флоу полный (есть бриф, нужен анализ ниши) — оставь статусы `locked`, `gate-check` пройдёт по ним нормально. Раньше эти статусы по умолчанию стояли `n/a` в шаблоне, что молча обходило 14 hard-checks этапа `01a_niche_analysis` (audit gap). Теперь дефолт — `locked`, а переход в `n/a` происходит явно здесь.

## Что происходит

Команда вызывает `landing-orchestrator` агента:

1. Читает `<project>/.landing-state.yaml` через `scripts/landing-go-next-stage.py` → находит следующий этап.
2. Показывает что сделать (одно действие + одно ожидание).
3. Проверяет гейт через `scripts/gate-check.sh`.
4. Если гейт упал — предлагает auto-fix (auto-resume после исправления).
5. На этапе 07d_photos/07e_visuals — диспатчит оба субагента параллельно.

## Этапы

> **Полный канонический порядок этапов — `config/stages.yaml`** (single source
> of truth, E1). Карта прогресса: `bash scripts/render-pipeline-map.sh
> <project>/.landing-state.yaml`. Таблица ниже — смысловая группировка.

| # | Stage | Кто делает | Чем |
|---|---|---|---|
| 07a_prototype | prototype | АВТО | `/landing-prototype` |
| 03 | references | Руками | references-curator |
| 04 | brand | Руками + AI | brand-architect |
| 05 | design | Руками + AI | design-system-generator |
| 06 | stack | АВТО | stack-planner |
| 07 | content | АВТО | content-writer |
| 07c | composed | АВТО | `/landing-compose` |
| **07d** ⇆ **07e** | photos + visuals | **ПАРАЛЛЕЛЬНО** | `/landing-photos` ‖ `/landing-visuals` |
| 07f | composed_final | АВТО | `/landing-compose` |
| 08 | build | АВТО | wp-builder |
| 09 | deploy | Бегет creds | wp-deployer |
| 10-12 | QA / Analytics / SEO | АВТО | существующие агенты |

## Auto-fix mechanism

При падении гейта оркестратор смотрит `fix_hint` из `config/stage-gates.yaml`:
- Если начинается с `auto_fix:` → предлагает запустить указанную команду.
- На `yes` — выполняет, re-runs gate-check.

## Ручные команды сохраняются

`/landing-photos`, `/landing-visuals`, `/landing-prototype`, `/landing-compose` продолжают работать как ручные точки входа.

См. [spec](../docs/superpowers/specs/2026-05-13-pr-d-orchestrator-integration-design.md), [plan](../docs/superpowers/plans/2026-05-13-pr-d-orchestrator-integration-plan.md).
