---
type: stage
name: pr-e-onboarding-wizard-plan
sources: ["docs/superpowers/plans/2026-05-14-pr-e-onboarding-wizard-plan.md"]
updated: 2026-05-14
triggers: []
stage: "pr-e"
uses:
  - landing-onboarding-wizard
  - landing-start
  - landing-project-init
  - landing-go
  - prototype-importer
tags:
  - onboarding
  - wizard
  - pr-e
  - новый-проект
  - материалы
---

# PR-E: Onboarding Wizard — план реализации

## Что делает

Описывает полный план создания интерактивного wizard-а для новичков: от приветствия до папки с материалами. Маркетолог запускает `/landing-start` — система объясняет себя, создаёт папку проекта и ведёт через 4 шага подготовки материалов (прототип → фото → логотип → референсы) с автоматической проверкой на каждом шаге.

## Когда вызывать / в каком этапе

PR-E — первый PR, с которого начинается работа над **новым** лендинг-проектом. Срабатывает при вызове `/landing-start`. Все задачи плана должны быть выполнены до того, как `/landing-go` станет основным входом в pipeline.

Задачи 1 и 2 можно выполнять **параллельно**. Задачи 3–6 — строго последовательно, каждая зависит от предыдущей.

## Что на вход / на выход

**Вход:**
- `docs/superpowers/specs/2026-05-14-pr-e-onboarding-wizard-design.md` — дизайн-спецификация
- `template/` — каноничный шаблон проекта
- Существующий скилл `landing-project-init` для создания папки

**Выход (6 задач, 15+ новых файлов):**

| Задача | Основные артефакты |
|--------|-------------------|
| 1 | `scripts/wizard-check-materials.py` — проверка 4 шагов; `tests/phase-pre/test-wizard-check-materials.py` (10 тестов) |
| 2 | `template/04_БРЕНД/logos/` + README-файлы во **всех 18 папках** шаблона; `tests/phase-pre/test-template-readmes.bats` (5 тестов) |
| 3 | `agents/landing-onboarding-wizard.md` — полный flow агента с 5 фазами; `tests/phase-pre/test-wizard-agent.bats` (7 тестов) |
| 4 | `commands/landing-start.md` — slash-команда; `tests/phase-pre/test-landing-start.bats` (5 тестов) |
| 5 | `scripts/migrate-template-readmes.sh` — бэкпорт README для старых проектов (идемпотентный); `tests/phase-pre/test-migrate-readmes.bats` (4 теста) |
| 6 | Обновлённый `CLAUDE.md` — `/landing-start` выдвинут первой командой |

**Прототип** — единственный обязательный шаг wizard-а (exit 1 при попытке пропустить). Шаги 2–4 поддерживают «пропустить» — AI сгенерирует fallback позже.

## Связанные концепты

- [[landing-onboarding-wizard]] — агент, реализующий пошаговый walkthrough
- [[landing-start]] — slash-команда, точка входа для маркетолога
- [[landing-project-init]] — скилл создания папки `~/Lendings/<slug>/`
- [[landing-go]] — следующая команда после wizard, запускает pipeline
- [[prototype-importer]] — парсит prototype.pdf/md на этапе 07a (после wizard)
- [[07-prototip]] — этап 07a_prototype, куда ведёт шаг 1 wizard-а

## Источник

- `docs/superpowers/plans/2026-05-14-pr-e-onboarding-wizard-plan.md`