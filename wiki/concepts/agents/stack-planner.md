---
type: agent
name: stack-planner
sources: ["agents/stack-planner.md"]
updated: 2026-05-15
triggers: []
stage: "06"
uses: ["design-system-generator", "brand-kit-build", "design-tokens-generation"]
tags: ["wordpress", "stack", "fonts", "icons", "plugins", "stage-06"]
---

# stack-planner — Планировщик технического стека

## Что делает
Выбирает и фиксирует набор WordPress-плагинов, JS-библиотек, иконок и шрифтов на основе готовой дизайн-системы. Результат — `design-stack.yaml`, единственный разрешённый источник зависимостей для всего проекта.

## Когда вызывать / в каком этапе
Этап **06 — Стек**. Запускается вручную или оркестратором **после** того, как `design-system-generator` сгенерировал `DESIGN.md` и `tokens.json`. Завершается **HARD GATE**: агент показывает `design-stack.yaml` пользователю и ждёт явного подтверждения перед переходом к этапу 07.

## Что на вход / на выход

**Входные артефакты:**
- `05_ДИЗАЙН-СИСТЕМА/DESIGN.md` — описание дизайн-системы
- `05_ДИЗАЙН-СИСТЕМА/tokens.json` — дизайн-токены
- `04_БРЕНД/brand-kit.md` — семейства шрифтов и иконки из бренд-кита
- `00_БРИФ/brief.md` — флаг `cinematic` (если есть, подключает GSAP/Lenis)

**Выходные артефакты:**
- `06_СТЕК/design-stack.yaml` — главный файл: режим, плагины, шрифты, иконки, JS-библиотеки
- `06_СТЕК/component-library-plan.md` — откуда берётся каждый UI-компонент
- `06_СТЕК/effects-plan.md` — анимации и motion (пуст в standard-режиме; в cinematic — GSAP, ScrollTrigger, Lenis, Split-Type)
- `06_СТЕК/font-and-color-plan.md` — маппинг шрифтов и цветов к токенам

**Жёсткие правила выбора:**
- ✅ GeneratePress + GenerateBlocks, ACF, FluentForm
- ✅ Bunny Fonts CDN (GDPR и РФ-совместимый)
- ✅ Iconify API (без ключа, Lucide-набор)
- ❌ Tailwind, Elementor, shadcn, Radix — запрещены
- ❌ Любые пакеты вне `design-stack.yaml` — запрещены

## Связанные концепты
- [[design-system-generator]] — предшествующий агент, генерирует DESIGN.md и tokens.json, без него stack-planner не запускается
- [[brand-kit-build]] — поставляет шрифты и иконки из бренд-кита
- [[design-tokens-generation]] — скилл, создающий tokens.json, который читает этот агент
- [[wp-builder]] — следующий агент в цепочке, потребляет design-stack.yaml как единственный источник зависимостей

## Источник
- `agents/stack-planner.md`