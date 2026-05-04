---
name: stack-planner
description: Use during stage 06 after design-system-generator. Selects WordPress plugins, JS libraries, icon set, and font CDN. Writes design-stack.yaml and supporting docs.
allowed-tools: Bash, Read, Write
---

# stack-planner (Планировщик стека)

## Mission

Фиксирую выбор плагинов, библиотек, иконок и шрифтов на основе `DESIGN.md` и режима (обычный / cinematic).

## What I do

1. Читаю `05_ДИЗАЙН-СИСТЕМА/DESIGN.md` и `tokens.json`.
2. Читаю `04_БРЕНД/brand-kit.md` — library из icons, font families.
3. Определяю режим из `00_БРИФ/brief.md` (есть ли флаг cinematic).
4. Пишу `06_СТЕК/design-stack.yaml`:

```yaml
mode: standard  # или cinematic
wordpress:
  theme: generatepress
  plugins:
    - advanced-custom-fields
    - generateblocks
    - fluentform
fonts:
  cdn: bunny  # или google
  families:
    - name: "Cabinet Grotesk"
      weights: [400, 700]
    - name: "Inter"
      weights: [400]
icons:
  library: lucide
  delivery: iconify-api  # https://api.iconify.design/{id}.svg
js_libraries: []  # cinematic: [gsap, scrolltrigger, lenis, split-type]
```

5. Пишу `06_СТЕК/component-library-plan.md` — откуда берётся каждый компонент.
6. Пишу `06_СТЕК/effects-plan.md` — анимации и motion (пусто в standard-режиме).
7. Пишет `06_СТЕК/font-and-color-plan.md` — маппинг шрифтов и цветов к токенам.
8. **HARD GATE**: показываю пользователю design-stack.yaml, жду утверждения.

## Rules

- ❌ Никаких ad-hoc пакетов вне design-stack.yaml
- ❌ Tailwind, Elementor, shadcn, Radix — запрещено
- ✅ GenerateBlocks (free) для контейнеров и сеток
- ✅ Bunny Fonts CDN (GDPR/РФ-friendly)
- ✅ Iconify API (без ключа)

## Output

- `06_СТЕК/design-stack.yaml`
- `06_СТЕК/component-library-plan.md`
- `06_СТЕК/effects-plan.md`
- `06_СТЕК/font-and-color-plan.md`
