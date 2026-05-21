---
type: agent
name: landing-onboarding-wizard
sources: ["agents/landing-onboarding-wizard.md"]
updated: 2026-05-20
triggers: ["/landing-start", "новый проект", "создать проект", "начать лендинг"]
stage: ""
uses: ["landing-project-init", "prototype-importer", "landing-go", "landing-orchestrator"]
tags: ["onboarding", "wizard", "bootstrap", "new-project"]
---

# Landing Onboarding Wizard

## Что делает

Интерактивный гид для маркетолога: объясняет систему за три параграфа, создаёт папку нового проекта и последовательно проводит через 4 шага сбора материалов — прототип, фото, логотип, референсы. В финале подсказывает запустить `/landing-go`.

## Когда вызывать / в каком этапе

Запускается командой `/landing-start` перед стартом любого нового проекта. Это нулевой (pre-pipeline) шаг — Stage Execution Protocol к нему не применяется. Wizard работает **только** с новыми проектами; существующие не трогает.

Порядок активации:
1. Маркетолог вводит `/landing-start`.
2. Wizard проверяет наличие codex CLI и репозитория (`template/`).
3. Спрашивает имя проекта (kebab-case), создаёт папку.
4. Проводит через 4 шага, верифицируя каждый скриптом `wizard-check-materials.py`.
5. Завершает подсказкой `/landing-go`.

## Что на вход / на выход

**Вход:**
- Ответы маркетолога в чате (имя проекта, «готово» / «пропустить» на каждом шаге).
- Файлы, которые пользователь кладёт вручную: `prototype.pdf` или `prototype.md`, фото в `07c_PHOTOS/inbox/`, логотип в `04_БРЕНД/logos/`, референсы в `03_РЕФЕРЕНСЫ/`.

**Выход:**
- Папка `~/Lendings/<slug>/` с 18 подпапками (копия `template/`).
- Материалы разложены по нужным папкам.
- Статус каждого шага (pass / warn / fail) от `wizard-check-materials.py`.
- Финальный summary с итогом по шагам.

**Важное ограничение:** шаг 1 (прототип) — обязательный, пропуск не принимается.

## Связанные концепты

- [[landing-project-init]] — скилл, создающий структуру папки проекта (`init.sh`)
- [[prototype-importer]] — парсит прототип на этапе 07a (wizard его не вызывает)
- [[landing-go]] — следующая команда после wizard; запускает полный pipeline
- [[landing-orchestrator]] — ведёт через 12 этапов после `/landing-go`
- [[landing-start]] — slash-команда, триггерящая этот агент

## Источник

- `agents/landing-onboarding-wizard.md`