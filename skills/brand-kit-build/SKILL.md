---
name: brand-kit-build
description: Use during stage 04 to synthesize brand-kit.md from extracted style data and render brand-kit.html preview. Owned by brand-architect agent.
---

# brand-kit-build

## What I do

- Read all `04_БРЕНД/extracted/*.yaml` files.
- Synthesize `brand-kit.md` with full provenance (every token traces to its source image/URL).
- Render `brand-kit.html` preview showing palette swatches, font specimens, icon thumbnails.

## Scripts

- [scripts/build.py](scripts/build.py) — synthesize brand-kit.md
- [scripts/render-html.py](scripts/render-html.py) — render brand-kit.html

## Palette selection from global library

Before extracting brand tokens, ask the user which mode to use:

```
Сколько палитр показать клиенту на согласовании?
  [1] Точечно (1-3)        — клиент знает что хочет
  [2] Несколько (4-6)      — есть направление (рекомендуется)
  [3] Весь каталог         — клиент в полном поиске
```

Modes 1-2: agent proposes candidates from `landing_system/presets/palettes.yaml`
based on niche analysis (read 01a_АНАЛИЗ_НИШИ artifacts), user confirms list,
then run:

```bash
python scripts/snapshot-palettes-to-project.py \
    --project "$PROJECT_ROOT" \
    --library "$LANDING_SYSTEM_ROOT/presets/palettes.yaml" \
    --id <id1> --id <id2> ...
```

Mode 3:

```bash
python scripts/snapshot-palettes-to-project.py \
    --project "$PROJECT_ROOT" \
    --library "$LANDING_SYSTEM_ROOT/presets/palettes.yaml" \
    --all
```

Result: `<project>/04_БРЕНД/palettes.yaml` contains the selected subset.

If `landing_system/presets/palettes.yaml` is empty (greenfield), tell the user:
"библиотека пуста — на /landing-design ты создашь первые палитры с нуля".
Skip the selection step entirely.
