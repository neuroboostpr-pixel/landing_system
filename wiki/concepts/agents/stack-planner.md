---
type: agent
name: stack-planner
sources: ["agents/stack-planner.md"]
updated: 2026-05-20
triggers: []
stage: "06"
uses: ["design-system-generator", "brand-architect", "landing-stack", "stage-execution-protocol"]
tags: ["wordpress", "plugins", "fonts", "icons", "stack", "stage-06"]
---

# stack-planner — Планировщик технического стека

## Что делает
Выбирает WordPress-плагины, JS-библиотеки, иконочный набор и CDN шрифтов на основе утверждённого дизайна. Фиксирует все технические решения в одном yaml-файле до написания кода — чтобы разработчики (агенты этапа 08) не гадали, что использовать.

## Когда вызывать / в каком этапе
Запускается на **этапе 06** командой `/landing-stack`, строго после завершения этапа 05 (`design-system-generator`). Агент проверяет `current_stage == 06_stack` в `.landing-state.yaml` — если предшественники не закрыты, останавливается. Harness-хук `enforce_stage_gate.py` физически блокирует запись файлов до закрытия предшественника.

## Что на вход / на выход

**Вход:**
- `05_ДИЗАЙН-СИСТЕМА/DESIGN.md` — полная дизайн-система с блоками
- `05_ДИЗАЙН-СИСТЕМА/tokens.json` — дизайн-токены
- `04_БРЕНД/brand-kit.md` — шрифты и иконки из бренд-кита
- `00_БРИФ/brief.md` — флаг режима (`standard` или `cinematic`)

**Выход:**
- `06_СТЕК/design-stack.yaml` — полный стек: тема, плагины, шрифты, иконки, JS-библиотеки
- `06_СТЕК/component-library-plan.md` — откуда берётся каждый компонент
- `06_СТЕК/effects-plan.md` — план анимаций (заполняется только в cinematic-режиме)
- `06_СТЕК/font-and-color-plan.md` — маппинг шрифтов и цветов к токенам

После генерации — **HARD GATE**: показывает `design-stack.yaml` пользователю и ждёт явного утверждения перед продолжением.

**Жёсткие ограничения стека:**
- ✅ GeneratePress (тема) + GenerateBlocks (free) + ACF + FluentForm
- ✅ Bunny Fonts CDN (GDPR/РФ-friendly), Iconify API (без ключа)
- ✅ В cinematic-режиме: GSAP, ScrollTrigger, Lenis, SplitType
- ❌ Tailwind, Elementor, shadcn, Radix — запрещены
- ❌ Любые ad-hoc пакеты вне `design-stack.yaml`

## Связанные концепты
- [[design-system-generator]] — обязательный предшественник: создаёт DESIGN.md и tokens.json, которые читает стек-планировщик
- [[brand-architect]] — поставляет brand-kit.md со шрифтами и иконками
- [[landing-stack]] — slash-команда, которая запускает этого агента
- [[stage-execution-protocol]] — обязательный протокол: pipeline-карта, gate-check, TodoWrite перед любым действием
- [[wp-builder]] — потребитель результата: читает design-stack.yaml при генерации кода на этапе 08

## Источник
- `agents/stack-planner.md`