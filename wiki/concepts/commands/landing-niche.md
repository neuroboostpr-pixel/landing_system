---
slug: landing-niche
type: command
name: "Анализ ниши /landing-niche"
stage: "01a"
tags: [niche, analysis, competitors, positioning, stage-01a]
triggers: ["/landing-niche"]
inputs: ["00_БРИФ/.landing-state.yaml"]
outputs: ["01a_АНАЛИЗ_НИШИ/niche-analysis.md", "01a_АНАЛИЗ_НИШИ/competitors.yaml", "01a_АНАЛИЗ_НИШИ/positioning.md"]
gates: []
pre_reqs: [landing-onboarding, niche-analysis]
related: [niche-analyst, niche-analysis, landing-orchestrator, landing-onboarding]
sources: ["commands/landing-niche.md"]
updated: 2026-05-26
confidence: {gates: low}
---

# Анализ ниши /landing-niche

## Что делает

Команда запускает этап `01a_АНАЛИЗ_НИШИ` для текущего проекта-лендинга. Она проверяет, что этап `00_brief` одобрен, затем передаёт управление агенту `niche-analyst`, который в режиме zero-touch анализирует нишу, собирает конкурентов и формирует позиционирование. После записи артефактов автоматически запускается валидация конкурентов и gate-check. Если все hard-проверки пройдены, команда предлагает пользователю подтвердить переход на этап 02.

## Когда вызывается

Вызывается вручную командой `/landing-niche` из папки проекта. Условия: onboarding завершён (`~/.landing-system/setup_complete`), в папке есть `.landing-state.yaml`, этап `00_brief` имеет статус `approved`. Если этап `01a` уже одобрен — команда уточнит, нужен ли перезапуск.

## Вход → выход

**Вход:** файл `.landing-state.yaml` с этапом `00_brief` в статусе `approved`; бриф и контекст проекта, собранные на этапе 00.

**Выход:** три артефакта в папке `01a_АНАЛИЗ_НИШИ/` — `niche-analysis.md` (анализ ниши), `competitors.yaml` (список конкурентов), `positioning.md` (позиционирование). Статус этапа `01a_niche_analysis` обновляется до `approved` при успехе.

## Failure modes

- Этап `00_brief` не одобрен — команда завершается с ошибкой до передачи агенту.
- `validate-competitors.py` падает из-за невалидного YAML в `competitors.yaml` — нужно ручное исправление файла.
- `gate-check.sh` возвращает ненулевой exit code — hard-check провален, этап не переходит в `approved`.
- Нет файла `.landing-state.yaml` в текущей папке — команда не запускается.
- Агент `niche-analyst` помечает критически важные данные как `[ДОПУЩЕНИЕ]` без реальных источников — требуется ревью перед утверждением.

## Related

- [[niche-analyst]] — агент, выполняющий основную работу анализа
- [[niche-analysis]] — скилл/концепт, описывающий логику анализа ниши
- [[landing-orchestrator]] — оркестратор, в контекст которого вписывается этот этап
- [[landing-onboarding]] — onboarding, который должен быть пройден до запуска