---
description: Stage 07d (PR-C) — генерация иконок и инфографики через codex image_gen для composed.html. Параметризовано tokens.json + niche. Требует approved 05 design + существующий composed.html.
---

# /landing-visuals

Генерирует иконки и инфографику для всех `data-slot type="icon"` и `type="infographic"` в `composed.html`. Stage 07d.

## Использование

```
/landing-visuals [--project <slug>] [--type icons|infographics] [--force] [--slot <name>]
```

**Флаги:**
- `--project <slug>` — папка проекта (по умолчанию текущая).
- `--type icons` — только иконки (пропустить инфографику).
- `--type infographics` — только инфографика (пропустить иконки).
- `--force` — обойти кэш, перегенерить всё.
- `--slot <name>` — только один конкретный слот по имени.

## Гейты (что должно быть готово до запуска)

1. `<project>/.landing-state.yaml:stages.05_design.status == approved` — иначе:
   > Сначала утверди дизайн-систему (`05_ДИЗАЙН-СИСТЕМА/DESIGN.md`) — без `tokens.json` codex не попадёт в стиль.

2. `<project>/07b_COMPOSED/composed.html` существует — иначе:
   > Сначала запусти `/landing-compose` (PR-A).

## Что происходит

Команда вызывает `visual-curator` агента, который:
1. Сканирует `composed.html` на icon и infographic слоты (`slot-scanner.py`).
2. Для каждого слота — cache lookup по hash(hint+style+brand_color+niche). Если cache hit — copy без вызова codex.
3. Если cache miss — диспатчит `icon-generator` или `infographic-builder` агента.
4. После всех генераций — re-render composed.html через `rerender-composed.py` (читает `07d_VISUALS/`, подставляет `[SLOT: …]`/data-slot placeholders).

См. [`agents/visual-curator.md`](../agents/visual-curator.md) для деталей.

## Артефакты

В `<project>/07d_VISUALS/`:
- `_slots.yaml` — найденные слоты (auto)
- `icons/<slot-name>.png` — иконки (auto)
- `infographics/<slot-name>.png` — инфографика (auto)
- `.cache/<hash>.png` — кэш (auto, не удаляй, экономит API)
- `prompts.yaml` — лог промптов с attribution (auto)
- `STATE.yaml` — статусы этапов (auto)
- `.logs/` — codex prompts + responses (auto)

## После выполнения

`07b_COMPOSED/composed.html` перерендерится — placeholders `[SLOT: ...]` и `[INFOGRAPHIC: ...]` заменятся на реальные `<img class="lp-icon">` / `<img class="lp-infographic">`.

## Запуск

Автоматически через `/landing-go` (рекомендуется) или вручную этой командой. Этап интегрирован в `landing-orchestrator` и `config/stage-gates.yaml`.

См. [spec](../docs/superpowers/specs/2026-05-13-visual-generation-design.md) и [plan](../docs/superpowers/plans/2026-05-13-visual-generation-plan.md).
