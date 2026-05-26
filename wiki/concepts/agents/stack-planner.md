---
slug: stack-planner
type: agent
name: "Планировщик стека (Stack Planner)"
stage: "06"
tags: [stack, wordpress, plugins, fonts, icons, design-system, cinematic]
triggers: []
inputs:
  - 05_ДИЗАЙН-СИСТЕМА/DESIGN.md
  - 05_ДИЗАЙН-СИСТЕМА/tokens.json
  - 04_БРЕНД/brand-kit.md
  - 00_БРИФ/brief.md
  - .landing-state.yaml
outputs:
  - 06_СТЕК/design-stack.yaml
  - 06_СТЕК/component-library-plan.md
  - 06_СТЕК/effects-plan.md
  - 06_СТЕК/font-and-color-plan.md
gates: []
pre_reqs: [design-system-generator, brand-architect]
related: [landing-orchestrator, block-composer, frontend-builder]
sources: ["agents/stack-planner.md"]
updated: 2026-05-26
confidence: {triggers: low, gates: low}
---

# Планировщик стека (Stack Planner)

## Что делает

Фиксирует технологический стек лендинга на этапе 06: выбирает WordPress-плагины, JS-библиотеки, иконочный набор и CDN для шрифтов. Читает дизайн-систему и бренд-кит, определяет режим сборки (standard или cinematic), затем записывает четыре артефакта этапа — главный из которых `design-stack.yaml`. Все последующие агенты (сборщик, билдер) опираются именно на этот файл как единственный источник правды о стеке.

## Когда вызывается

Вызывается оркестратором `landing-orchestrator` при переходе к этапу `06_stack` — после того как дизайн-система (`05_ДИЗАЙН-СИСТЕМА`) утверждена пользователем. Предварительно проверяет `.landing-state.yaml` (поле `current_stage == 06_stack`) и завершает работу только после явного approve пользователем `design-stack.yaml`.

## Вход → выход

**Вход:** утверждённые `DESIGN.md` и `tokens.json` из этапа 05; `brand-kit.md` с описанием иконок и шрифтов из этапа 04; `brief.md` с флагом режима (cinematic или standard); `.landing-state.yaml` с текущим статусом пайплайна.

**Выход:** `06_СТЕК/design-stack.yaml` — полный манифест стека (плагины, шрифты, иконки, JS-библиотеки); `component-library-plan.md` — откуда берётся каждый компонент; `effects-plan.md` — анимации и motion (пусто в standard-режиме); `font-and-color-plan.md` — маппинг шрифтов и цветов к токенам.

## Failure modes

- **`current_stage` не `06_stack`** — агент останавливается и сообщает об ошибке; пропуск этапов не допускается.
- **Не пройден gate-check предшественника** — `enforce_stage_gate.py` физически блокирует Write, агент не может записать файлы.
- **Пользователь не дал approve** — HARD GATE держит этап открытым; переход к 07 не происходит.
- **Флаг cinematic отсутствует в brief.md** — режим определится как standard, JS-анимации (gsap, lenis) не попадут в стек; нужно уточнить у клиента.
- **Запрещённые пакеты в запросе** (Tailwind, Elementor, shadcn) — агент отклоняет их по правилам; возможна путаница если пользователь настаивает.

## Related

- [[design-system-generator]] — предшественник; поставляет DESIGN.md и tokens.json
- [[brand-architect]] — поставляет brand-kit.md с семейством шрифтов и иконками
- [[landing-orchestrator]] — диспатчит этот агент в нужный момент пайплайна
- [[block-composer]] — потребляет design-stack.yaml при сборке wireframe и composed.html
- [[frontend-builder]] — использует стек при генерации WordPress-темы на этапе 08