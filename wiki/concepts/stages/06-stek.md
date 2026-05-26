---
type: stage
name: 06-stack
sources: ["template/06_СТЕК/README.md"]
updated: 2026-05-26
triggers: []
stage: "06"
uses: ["stack-planner", "landing-orchestrator"]
tags: ["stack", "автоматический", "wordpress", "gutenberg"]
---

# 06_СТЕК — Выбор технологического стека

## Что делает
Фиксирует выбранный технологический стек для лендинга: WordPress, Gutenberg, Lazy Blocks и связанные инструменты. Также определяет режим отображения — стандартный или кинематографический.

## Когда вызывать / в каком этапе
Этап 06 запускается автоматически агентом `landing-orchestrator` после завершения этапа 05 (design-system). Вмешательство пользователя не требуется — `stack-planner` формирует артефакты самостоятельно.

## Что на вход / на выход

**Вход:**
- Утверждённая дизайн-система (этап 05)
- Параметры проекта из `.landing-state.yaml`

**Выход:**
- `design-stack.yaml` — декларация выбранного стека технологий (WordPress + Gutenberg + Lazy Blocks + дополнительные плагины)
- Поле `mode` — режим темы (`standard` или `cinematic`)

## Связанные концепты
- [[stack-planner]] — агент, который автоматически создаёт артефакты этапа
- [[landing-orchestrator]] — оркестратор, запускающий этап 06 в общем pipeline

## Источник
- `template/06_СТЕК/README.md`