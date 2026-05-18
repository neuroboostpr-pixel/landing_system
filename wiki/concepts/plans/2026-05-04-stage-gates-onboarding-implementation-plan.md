---
type: rule
name: stage-gates-onboarding-implementation-plan
sources: ["docs/superpowers/plans/2026-05-04-stage-gates-onboarding-implementation-plan.md"]
updated: 2026-05-18
triggers: []
stage: ""
uses:
  - stage-gates
  - landing-onboarding
  - onboarding-guide
  - landing-orchestrator
  - system-setup
  - setup
tags: [plan, phase-1, phase-2, phase-3, phase-4, phase-5, api-validators, gate-check, onboarding, workflow-lock]
---

# Stage Gates & Onboarding — план реализации

## Что делает

Пошаговый план по строительству принудительного workflow-замка для landing-system: одноразовый мастер онбординга валидирует все API-ключи и зависимости, а механизм gate-check на каждом этапе проекта не позволяет перепрыгивать шаги.

## Когда вызывать / в каком этапе

Это не команда — это **план реализации**, описывающий 5 фаз разработки. Реализуется через `superpowers:executing-plans` или `superpowers:subagent-driven-development`. Уже выполнен: результаты живут в `scripts/`, `tools/api_validators/`, `config/`, `template/`, `agents/`, `commands/`.

## Что на вход / на выход

**Вход:**
- Спецификация `docs/superpowers/specs/2026-05-04-stage-gates-onboarding-mcp-design.md`
- `.env.example` (базовый)
- Существующие команды `/landing-*`

**Выход (5 фаз):**

| Фаза | Что создаётся |
|---|---|
| 1 — API Validators | `tools/api_validators/` — 15 валидаторов (firecrawl, pexels, unsplash, pixabay, huggingface, whatthefont, yandex_wordstat, yandex_metrika, telegram, amocrm, bitrix24, beget_ssh, beget_api, cloudflare, regru) + `base.py` + `aggregate.py` |
| 2 — Onboarding | `scripts/wizard.sh`, `scripts/setup-flag.sh`, `scripts/validate-all.sh`, `agents/onboarding-guide.md`, `commands/landing-onboarding.md`, `skills/landing-onboarding/SKILL.md`, `docs/SETUP.md` |
| 3 — Stage Gates | `config/stage-gates.yaml` (12 этапов с hard/soft checks), `template/.landing-state.yaml`, `scripts/gate-state.sh`, `scripts/gate-check.sh` |
| 4 — Интеграция | gate-check добавлен в `landing-new`, `landing-references`, `landing-brand`, `landing-design`, `landing-stack`, `landing-content`, `landing-build`, `landing-deploy`, `landing-qa`; `landing-orchestrator` обновлён |
| 5 — Документация | `README.md`, `CLAUDE.md` обновлены секциями Workflow Lock и Onboarding |

**Флаг завершения онбординга:** `~/.landing-system/setup_complete`
**Состояние проекта:** `<project>/.landing-state.yaml` (статусы: locked → in_progress → approved)

## Связанные концепты

- [[stage-gates]] — конфигурация hard/soft проверок, созданная этим планом
- [[landing-onboarding]] — команда и скилл, созданные в Phase 2
- [[onboarding-guide]] — агент-проводник онбординга
- [[landing-orchestrator]] — модифицирован для проверки `.landing-state.yaml`
- [[setup]] — итоговый `docs/SETUP.md`, описывающий всю систему
- [[system-setup]] — смежный агент начальной настройки

## Источник

- `docs/superpowers/plans/2026-05-04-stage-gates-onboarding-implementation-plan.md`