---
type: agent
name: stack-planner
sources: ["agents/stack-planner.md"]
updated: 2026-05-26
triggers: []
stage: "06"
uses: ["design-system-generator", "landing-orchestrator", "stage-execution-protocol"]
tags: ["stack", "plugins", "fonts", "icons", "stage-06"]
---

# Stack Planner — Планировщик технологического стека

## Что делает
Выбирает WordPress-плагины, JS-библиотеки, набор иконок и шрифтовой CDN для лендинга. Фиксирует все решения в `design-stack.yaml` и трёх вспомогательных документах, чтобы весь pipeline использовал единый стек без расхождений.

## Когда вызывать / в каком этапе
Активируется на **этапе 06 (`06_stack`)** — после того как агент `design-system-generator` завершил работу и создан `DESIGN.md`. В `.landing-state.yaml` поле `current_stage` должно быть равно `06_stack`, иначе агент останавливается и сообщает об ошибке.

Перед любым действием агент обязан:
1. Прочитать `.landing-state.yaml` и вывести Mermaid-карту pipeline.
2. Пройти `gate-check.sh --stage 06_stack` (exit 0 — обязательно).
3. Развернуть TodoWrite со всеми оставшимися этапами.
4. По завершении: запустить `verify-06_stack.sh` и выставить статус `approved`.

## Что на вход / на выход

**Вход:**
- `05_ДИЗАЙН-СИСТЕМА/DESIGN.md` и `tokens.json` — дизайн-система
- `04_БРЕНД/brand-kit.md` — иконки и семейства шрифтов из бренд-кита
- `00_БРИФ/brief.md` — флаг `cinematic` (если есть, включает GSAP/Lenis и пр.)

**Выход:**
- `06_СТЕК/design-stack.yaml` — главный манифест стека (режим, плагины, шрифты, иконки, JS-библиотеки)
- `06_СТЕК/component-library-plan.md` — откуда берётся каждый UI-компонент
- `06_СТЕК/effects-plan.md` — анимации и motion (пусто в standard-режиме)
- `06_СТЕК/font-and-color-plan.md` — маппинг шрифтов и цветов к токенам

После записи файлов агент показывает `design-stack.yaml` пользователю и ждёт явного утверждения (**HARD GATE**).

## Правила и ограничения
- Tailwind, Elementor, shadcn, Radix — **запрещены**.
- Для контейнеров и сеток — только **GenerateBlocks Free**.
- Шрифты — **Bunny Fonts CDN** (GDPR- и РФ-friendly).
- Иконки — **Lucide / Iconify API** (без API-ключа).
- Никаких пакетов вне `design-stack.yaml`.

## Связанные концепты
- [[design-system-generator]] — предшественник: создаёт DESIGN.md и tokens.json, которые агент читает
- [[landing-orchestrator]] — диспатчит stack-planner как этап 06 в общем pipeline
- [[stage-execution-protocol]] — обязательный протокол предусловий перед любым Write/Edit

## Источник
- `agents/stack-planner.md`