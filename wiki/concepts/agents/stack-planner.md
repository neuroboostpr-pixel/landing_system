---
slug: stack-planner
type: agent
name: "Планировщик стека"
stage: "06"
tags: [wordpress, stack, plugins, fonts, icons, design-tokens]
triggers: [landing-stack]
inputs:
  - 05_ДИЗАЙН-СИСТЕМА/DESIGN.md
  - 05_ДИЗАЙН-СИСТЕМА/tokens.json
  - 04_БРЕНД/brand-kit.md
  - 00_БРИФ/brief.md
outputs:
  - 06_СТЕК/design-stack.yaml
  - 06_СТЕК/component-library-plan.md
  - 06_СТЕК/effects-plan.md
  - 06_СТЕК/font-and-color-plan.md
gates: [design-stack-approved]
pre_reqs: [05-dizayn-sistema]
related:
  - design-system-generator
  - landing-stack
  - landing-go
  - landing-orchestrator
  - 06-stek
sources: ["agents/stack-planner.md"]
updated: 2026-06-19
confidence: {triggers: low}
---

# Планировщик стека

## Что делает

Фиксирует технологический стек лендинга: выбирает WordPress-плагины, JS-библиотеки, набор иконок и CDN для шрифтов. Решение принимается на основе дизайн-системы (DESIGN.md, tokens.json), бренд-кита и флага режима (standard или cinematic из brief.md). Итог — файл `design-stack.yaml`, который становится единым источником истины для сборки на этапе 08.

## Когда вызывается

Запускается на этапе 06 через скилл `landing-stack` после того, как этап 05 (дизайн-система) закрыт и одобрен пользователем. `landing-orchestrator` диспатчит агента автоматически при прохождении gate-check этапа 06.

## Вход → выход

**Вход:** `DESIGN.md` и `tokens.json` из этапа 05; `brand-kit.md` с семейством шрифтов и иконками; `brief.md` с флагом cinematic.

**Выход:** `design-stack.yaml` (WordPress-тема, плагины, шрифты, иконки, JS-библиотеки); `component-library-plan.md` (откуда берётся каждый компонент); `effects-plan.md` (анимации и motion, пусто в standard-режиме); `font-and-color-plan.md` (маппинг шрифтов и цветов к токенам).

## Чем закрывается этап (gates)

- `design-stack-approved` — пользователь явно одобрил сгенерированный `design-stack.yaml` перед переходом к этапу 07.

## Failure modes

- Этап 05 не закрыт: `enforce_stage_gate.py` блокирует запись файлов, агент останавливается.
- В `brief.md` отсутствует флаг cinematic — режим определяется как standard, JS-библиотеки остаются пустым списком; при необходимости cinematic — нужно явно дописать флаг в бриф.
- В `brand-kit.md` нет секции fonts/icons — агент выбирает дефолты (Bunny Fonts + Lucide), что может не совпадать с брендом клиента.
- Запрещённые пакеты (Tailwind, Elementor, shadcn) попадают в стек из-за неверного контекста в DESIGN.md — нарушает правила сборки этапа 08.
- Пользователь пропускает HARD GATE (не утверждает design-stack.yaml) — pipeline продолжается с несогласованным стеком, что ломает сборку на этапе 08.

## Related

- [[design-system-generator]] — предшественник: генерирует DESIGN.md и tokens.json, которые читает stack-planner
- [[landing-stack]] — скилл-точка входа, через который вызывается агент
- [[landing-go]] — оркестратор, диспатчит stack-planner в рамках общего pipeline
- [[06-stek]] — этап, артефакты которого создаёт этот агент
- [[landing-orchestrator]] — управляет последовательностью этапов и gate-проверками