---
type: command
name: landing-niche
sources: ["commands/landing-niche.md"]
updated: 2026-05-15
triggers:
  - "запустить анализ ниши"
  - "исследовать рынок для лендинга"
  - "провести анализ конкурентов"
  - "этап 01a нишевой анализ"
stage: "01a"
uses:
  - niche-analyst
  - gate-check
  - niche-analysis
tags:
  - niche
  - analysis
  - competitors
  - positioning
  - stage-01a
---

# /landing-niche — Анализ ниши (этап 01a)

## Что делает

Запускает автоматический анализ рыночной ниши для текущего проекта-лендинга: изучает конкурентов, формирует профиль рынка и выбирает стратегию позиционирования. Агент работает без уточняющих вопросов — недостающие данные помечаются `[ДОПУЩЕНИЕ]`.

## Когда вызывать / в каком этапе

Вызывается на этапе **01a** — после того, как этап `00_brief` переведён в статус `approved`. Запускается вручную командой `/landing-niche` из папки проекта. Если анализ уже был выполнен и одобрен, команда запросит подтверждение перезапуска перед перезаписью артефактов.

**Предусловия:**
- Пройден onboarding (`~/.landing-system/setup_complete`)
- В текущей папке есть `.landing-state.yaml`
- Этап `00_brief` имеет статус `approved`

## Что на вход / на выход

**Вход:**
- `00_БРИФ/brief.md` — бриф проекта
- `01_КОНТЕКСТ/context.md` — контекст (если присутствует)

**Выход:**
- `01a_АНАЛИЗ_НИШИ/niche-analysis.md` — полный анализ ниши
- `01a_АНАЛИЗ_НИШИ/competitors.yaml` — список конкурентов с характеристиками
- `01a_АНАЛИЗ_НИШИ/positioning.md` — выбранный режим позиционирования

**Внутренние шаги:**
1. Gate-check этапа `00_brief`
2. Пометка `01a_niche_analysis` → `in_progress`
3. Диспатч агента `niche-analyst`
4. Валидация: `python skills/niche-analysis/scripts/validate-competitors.py`
5. Gate-check `01a_niche_analysis` (`bash scripts/gate-check.sh`)
6. Summary + запрос approval для перехода на этап 02

## Связанные концепты

- [[niche-analyst]] — специализированный агент, выполняющий фактическую работу анализа ниши zero-touch
- [[niche-analysis]] — скилл с логикой анализа и скриптом валидации конкурентов
- [[landing-go]] — мастер-команда, которая вызывает `/landing-niche` автоматически через оркестратор
- [[landing-orchestrator]] — управляет последовательностью этапов и HARD GATE между ними

## Источник

- `commands/landing-niche.md`