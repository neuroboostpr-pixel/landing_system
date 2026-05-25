---
type: agent
name: stack-planner
sources: ["agents/stack-planner.md"]
updated: 2026-05-25
triggers: []
stage: "06"
uses: ["design-system-generator", "brand-kit", "landing-orchestrator", "stage-execution-protocol"]
tags: ["stage-06", "stack", "plugins", "fonts", "icons", "wordpress"]
---

# Stack Planner — Планировщик технического стека

## Что делает

Выбирает WordPress-плагины, JS-библиотеки, иконки и шрифты для лендинга на основе готового дизайн-системы. Фиксирует итоговый стек в `design-stack.yaml` и сопроводительных документах, чтобы все последующие этапы работали с одним согласованным набором технологий.

## Когда вызывать / в каком этапе

Запускается на **этапе 06 (`06_stack`)** — после того как дизайн-система (`design-system-generator`) и бренд-кит (`brand-kit`) утверждены. Активируется через `landing-orchestrator` или вручную. До запуска `current_stage` в `.landing-state.yaml` должен быть `06_stack`; иначе агент останавливается и сообщает об ошибке.

Обязательный порядок предусловий (Stage Execution Protocol):
1. Проверить `.landing-state.yaml`.
2. Отрендерить Mermaid-карту pipeline.
3. Создать TodoWrite со всеми оставшимися этапами.
4. Пройти `gate-check.sh --stage 06_stack`.

## Что на вход / на выход

**Вход:**
- `05_ДИЗАЙН-СИСТЕМА/DESIGN.md` и `tokens.json` — палитра, типографика, режим (standard / cinematic)
- `04_БРЕНД/brand-kit.md` — семейства шрифтов и иконки
- `00_БРИФ/brief.md` — флаг cinematic

**Выход:**
- `06_СТЕК/design-stack.yaml` — полный манифест стека (тема, плагины, шрифты, иконки, JS)
- `06_СТЕК/component-library-plan.md` — источники всех компонентов
- `06_СТЕК/effects-plan.md` — анимации и motion (пусто в standard-режиме; GSAP/Lenis в cinematic)
- `06_СТЕК/font-and-color-plan.md` — маппинг шрифтов и цветов к токенам

После генерации файлов агент показывает `design-stack.yaml` пользователю и ждёт явного утверждения (**HARD GATE**). Только после approve выставляет `approved` через `gate-state.sh`.

## Ключевые правила

- Запрещены: Tailwind, Elementor, Radix, shadcn, любые ad-hoc пакеты вне манифеста.
- Обязательны: GeneratePress (тема), GenerateBlocks Free (сетки), FluentForm, Bunny Fonts CDN (GDPR/РФ), Iconify API (без ключа).
- В cinematic-режиме добавляются: GSAP, ScrollTrigger, Lenis, Split-Type.

## Связанные концепты

- [[design-system-generator]] — поставляет DESIGN.md и tokens.json, которые агент читает первым делом
- [[brand-kit]] — источник шрифтов и иконок для brand-kit.md
- [[landing-orchestrator]] — вызывает агента в рамках pipeline
- [[stage-execution-protocol]] — обязательный протокол предусловий перед любыми записями

## Источник

- `agents/stack-planner.md`