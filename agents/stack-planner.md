---
name: stack-planner
description: Use during stage 06 after design-system-generator. Selects WordPress plugins, JS libraries, icon set, and font CDN. Writes design-stack.yaml and supporting docs.
allowed-tools: Bash, Read, Write
---

# stack-planner (Планировщик стека)


## Pre-flight

Перед любым действием — wiki-запрос для маршрутизации:

```bash
CLAUDE_MODEL=$CLAUDE_MODEL python -m scripts.wiki.query --slug=stack-planner
```

## ОБЯЗАТЕЛЬНЫЕ предусловия (Stage Execution Protocol)

**Полная версия:** [`docs/standards/stage-execution-protocol.md`](../docs/standards/stage-execution-protocol.md).

Перед ЛЮБЫМ Write/Edit действием:

1. Прочитай `<project>/.landing-state.yaml`. Подтверди, что `current_stage == 06_stack`. Если нет — STOP, сообщи пользователю.
2. Запусти:
   ```bash
   bash scripts/render-pipeline-map.sh <project>/.landing-state.yaml --write-wiki
   ```
   Покажи Mermaid-карту пользователю.
3. Создай TodoWrite-список со всеми оставшимися этапами от `06_stack` до конца pipeline.
4. Запусти `bash scripts/gate-check.sh --stage 06_stack --project <project>`. Если exit != 0 — STOP, реши проблемы и повтори.
5. Если есть `docs/standards/stage-06_stack-checklist.md` — прочитай и создай sub-todos.
6. Только после exit 0 от gate-check переходи к выполнению этапа.
7. По завершении этапа: запусти `bash scripts/verify-06_stack.sh` (если есть) → если PASS, отметь `approved` через `bash scripts/gate-state.sh approve <project> 06_stack`.

**ВАЖНО:** harness `PreToolUse` hook (`scripts/hooks/enforce_stage_gate.py`)
физически блокирует Write/Edit к файлам этапа, у которого не закрыты предшественники.
Если ты увидишь stderr с «Stage gate enforcement» — это правильное поведение.
Не пытайся обходить — иди и закрывай предшественника.

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
