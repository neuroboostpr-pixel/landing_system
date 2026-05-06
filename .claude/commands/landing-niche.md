---
description: Run niche analysis (stage 01a) for current landing project. Reads brief and context, outputs niche-analysis.md, competitors.yaml, positioning.md.
---

# /landing-niche

Запустить этап **01a_АНАЛИЗ_НИШИ** для текущего проекта-лендинга.

## Что делает

1. Запускает gate-check этапа `00_brief` → должен быть `approved`.
2. Если этап `01a_niche_analysis` уже `approved` — спрашивает подтверждение перезапуска.
3. Помечает этап `01a_niche_analysis` как `in_progress`.
4. Передаёт работу агенту `niche-analyst`.
5. После записи артефактов запускает `python skills/niche-analysis/scripts/validate-competitors.py`.
6. Запускает `bash scripts/gate-check.sh --stage 01a_niche_analysis --project <PWD>`.
7. Если все hard-checks прошли — показывает summary и спрашивает approval для перехода на 02.

## Артефакты после выполнения

- `01a_АНАЛИЗ_НИШИ/niche-analysis.md`
- `01a_АНАЛИЗ_НИШИ/competitors.yaml`
- `01a_АНАЛИЗ_НИШИ/positioning.md`

## Условия запуска

- Onboarding пройден (`~/.landing-system/setup_complete`)
- Текущая папка содержит `.landing-state.yaml`
- Этап `00_brief` имеет статус `approved`

## Принцип

Агент работает zero-touch — не задаёт уточняющих вопросов. Все недостающие данные помечаются `[ДОПУЩЕНИЕ]`.
