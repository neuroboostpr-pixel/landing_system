---
name: visual-generation
description: Stage 07d (PR-C) — generate icons + infographics via codex image_gen for composed.html slots. Parameterized by tokens.json + niche. Hash-cache. Owned by visual-curator agent.
---

# visual-generation

## Pre-flight

```bash
python -m scripts.wiki.log --type skill_call --skill visual-generation --stage 07e
```

Конвейер генерации визуалов (иконки, инфографика) для лендинга. Запускается командой `/landing-visuals` после approved `05_design` + существующего `07b_COMPOSED/composed.html`.

## Этапы

1. **scan** — `scripts/slot-scanner.py` парсит `composed.html`, выдаёт списки icon/infographic слотов в `07d_VISUALS/_slots.yaml`.
2. **generate** — `scripts/codex-generate-icon.sh` / `-infographic.sh` для каждого слота. Перед вызовом codex — кэш-lookup по hash(hint+style+brand_color+niche).
3. **inject** — `inject-content.py` (PR-A/PR-B расширенный) подставляет PNG в `composed.html` на месте placeholders.

## Identity-safe

НЕ применяется — нет людей в иконках/чартах.

## Cache

`07d_VISUALS/.cache/<hash>.png` — переиспользование сгенерированных изображений между прогонами. `FORCE=1` обходит кэш.

## Prompt-picker waterfall

- **icons:** icons.csv keyword match → generic template (skip OpenDesign — они не под иконки)
- **infographics:** OpenDesign 90 JSON tag/category match → generic template

## State management

`07d_VISUALS/STATE.yaml` отслеживает scan / generate / inject. Перезапуск продолжает с прерванного.

## Стандарт пайплайна картинок (D1, обязательный)

Каждое визуальное место обрабатывается по
[`docs/standards/image-pipeline.md`](../docs/standards/image-pipeline.md):
анализ места → цель → спецификация → референсы (число = составу композиции) →
генерация на вырезаемом фоне → rembg → вставка; адаптация под палитру —
полупрозрачным оверлеем акцента, не отдельной картинкой на каждый цвет.
