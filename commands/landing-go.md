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

Этапы 00 (бриф), 01 (контекст), 01a (анализ ниши), 02 (материалы клиента) автоматически помечены `n/a` — они происходят до landing-system.

## Что происходит

Команда вызывает `landing-orchestrator` агента:

1. Читает `<project>/.landing-state.yaml` через `scripts/landing-go-next-stage.py` → находит следующий этап.
2. Показывает что сделать (одно действие + одно ожидание).
3. Проверяет гейт через `scripts/gate-check.sh`.
4. Если гейт упал — предлагает auto-fix (auto-resume после исправления).
5. На этапе 07d_photos/07e_visuals — диспатчит оба субагента параллельно.

## Этапы

| # | Stage | Кто делает | Чем |
|---|---|---|---|
| 07a_prototype | prototype | АВТО | `/landing-prototype` |
| 03 | references | Руками | references-curator |
| 04 | brand | Руками + AI | brand-architect |
| 05 | design | Руками + AI | design-system-generator |
| 06 | stack | АВТО | stack-planner |
| 07 | content | АВТО | content-writer |
| 07b | wireframe | Маркетолог | `/landing-wireframe` |
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

`/landing-photos`, `/landing-visuals`, `/landing-prototype`, `/landing-wireframe`, `/landing-compose` продолжают работать как ручные точки входа.

См. [spec](../docs/superpowers/specs/2026-05-13-pr-d-orchestrator-integration-design.md), [plan](../docs/superpowers/plans/2026-05-13-pr-d-orchestrator-integration-plan.md).
