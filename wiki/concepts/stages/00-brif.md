---
slug: stage-00-brief
type: stage
name: "00 — Бриф проекта"
stage: "00"
tags: [brief, onboarding, prototype-first]
triggers: []
inputs: []
outputs: [brief.md]
gates: []
pre_reqs: []
related: [landing-orchestrator, landing-go, landing-onboarding, landing-new, prototype-import]
sources: ["template/00_БРИФ/README.md"]
updated: 2026-05-26
confidence: {gates: low, triggers: low}
---

# 00 — Бриф проекта

## Что делает

Этап закладывает исходную точку нового лендинга: фиксирует нишу, целевую аудиторию и ключевые KPI в файле `brief.md`. В **prototype-first flow** (PR-D) этап помечается как `n/a` — вся нужная информация автоматически извлекается из прototипа на этапе `prototype-import`. В классическом flow содержимое брифа заполняется `landing-orchestrator` интерактивно вместе с пользователем.

## Когда вызывается

В классическом flow — при старте нового проекта через `/landing-new` или `/landing-go`, когда `.landing-state.yaml` не содержит отметки о пройденном этапе 00. В prototype-first flow этап пропускается автоматически оркестратором.

## Вход → выход

**Вход:** пустая папка проекта со структурой из `template/`, намерение пользователя создать лендинг.

**Выход:** файл `00_БРИФ/brief.md` с описанием ниши, аудитории и KPI, готовый к использованию на последующих этапах (brand, content, niche-analysis).

## Failure modes

- Этап пропущен в prototype-first flow, но `.landing-state.yaml` не содержит отметки `n/a` — оркестратор зависает или повторно запрашивает бриф.
- Бриф заполнен слишком кратко (нет ниши или KPI) — downstream-агенты (`niche-analyst`, `brand-architect`) генерируют нерелевантные результаты.
- Пользователь вручную редактирует `brief.md` после того, как контент уже сгенерирован — расхождение между брифом и готовыми артефактами этапов 04–07.
- В prototype-first flow прototип не содержит информации о нише — автоматическое извлечение даёт пустой или ошибочный `brief.md`.

## Related

- [[landing-orchestrator]] — управляет прохождением этапа и записывает статус в `.landing-state.yaml`
- [[landing-go]] — единая точка входа, диспатчит этап 00 или помечает его `n/a`
- [[landing-new]] — создаёт структуру проекта перед этапом 00
- [[landing-onboarding]] — wizard, который запускается перед этапом 00 в новом проекте
- [[prototype-import]] — в prototype-first flow заменяет этап 00, извлекая бриф из прототипа