---
name: visual-curator
description: Stage 07e orchestrator. Validates DS asset-pack, scans composed.html for visual slots, dispatches generators, manages STATE.yaml, injects PNG/SVG back into composed.html. Triggered by /landing-visuals.
---

# visual-curator


## Pre-flight

Перед любым действием — wiki-запрос для маршрутизации:

```bash
python -m scripts.wiki.query --slug=visual-curator --agent=visual-curator
python -m scripts.wiki.log --type agent_call --agent visual-curator --stage 07e
```

## ОБЯЗАТЕЛЬНЫЕ предусловия (Stage Execution Protocol)

**Полная версия:** [`docs/standards/stage-execution-protocol.md`](../docs/standards/stage-execution-protocol.md).

Перед ЛЮБЫМ Write/Edit действием:

1. Прочитай `<project>/.landing-state.yaml`. Подтверди, что `current_stage == 07e_visuals`. Если нет — STOP, сообщи пользователю.
2. Запусти:
   ```bash
   bash scripts/render-pipeline-map.sh <project>/.landing-state.yaml --write-wiki
   ```
   Покажи Mermaid-карту пользователю.
3. Создай TodoWrite-список со всеми оставшимися этапами от `07e_visuals` до конца pipeline.
4. Запусти `bash scripts/gate-check.sh --stage 07e_visuals --project <project>`. Если exit != 0 — STOP, реши проблемы и повтори.
5. Если есть `docs/standards/stage-07e_visuals-checklist.md` — прочитай и создай sub-todos.
6. Только после exit 0 от gate-check переходи к выполнению этапа.
7. По завершении этапа: запусти `bash scripts/verify-07e_visuals.sh` (если есть) → если PASS, отметь `approved` через `bash scripts/gate-state.sh approve <project> 07e_visuals`.

**ВАЖНО:** harness `PreToolUse` hook (`scripts/hooks/enforce_stage_gate.py`)
физически блокирует Write/Edit к файлам этапа, у которого не закрыты предшественники.
Если ты увидишь stderr с «Stage gate enforcement» — это правильное поведение.
Не пытайся обходить — иди и закрывай предшественника.

## Mission

Orchestrate visual generation pipeline (stage 07e) and enforce DS asset-pack quality.
Identity-safe rules apply whenever visuals include real people, products, machines,
places or other client source assets.

## Gate (hard prerequisites)

Before running anything, verify:
- `<project>/.landing-state.yaml:stages.07c_composed.status == approved` — иначе exit с русским сообщением «Сначала утверди черновой composed».
- `<project>/07b_COMPOSED/composed.html` exists — иначе exit «Сначала запусти `/landing-compose` (PR-A)».
- DS asset-pack plan passes:
  ```bash
  python experimental/ds-engine-v2/engine/verify_ds_asset_pack.py --project <project> --mode plan
  ```

If any gate fails: exit 1 with the relevant Russian message. If only asset-pack plan
is missing, create it first:

```bash
python experimental/ds-engine-v2/engine/gen_assets_report.py grooming --project <project>
```

## Process

1. **Asset-pack plan.** Проверить `docs/standards/ds-asset-pack.md`. Убедиться,
   что есть `ASSETS-TODO.md`, `asset-pack.yaml`, `assets/prompts.md`,
   `assets/source-rules.md`.

2. **Scan.**
   ```bash
   python3 skills/visual-generation/scripts/slot-scanner.py \
     --html <project>/07b_COMPOSED/composed.html \
     --out <project>/07d_VISUALS/_slots.yaml
   ```

3. **Generate icons.** For each icon slot:
   - Dispatch `icon-generator` agent with (slot_name, hint).
   - Cache lookup first via `visual-cache.py`; skip codex if cached.
   - On generation: copy result also to `.cache/<hash>.png`.

4. **Generate infographics / mood assets.** Same for infographic slots, dispatch
   `infographic-builder` agent. If the visual comes from mood asset-pack, put it
   under `05_ДИЗАЙН-СИСТЕМА/moods/<mood>/assets/` using the path from `asset-pack.yaml`.

5. **Inject.**
   ```bash
   python3 skills/block-composition/scripts/rerender-composed.py --project <project>
   ```
   This now reads `07d_VISUALS/icons/` and `07d_VISUALS/infographics/`. Backward compatible: if 07d_VISUALS missing, placeholder behavior preserved.

6. Mark `STATE.yaml:stages.inject` done. Print Russian summary.

7. Перед переходом к `07f_composed_final` убедиться, что ready-пакет пройдёт:
   ```bash
   python experimental/ds-engine-v2/engine/verify_ds_asset_pack.py --project <project> --mode ready
   ```
   Если не проходит — перечислить, каких файлов не хватает: preview desktop/mobile,
   layers, Canvas/Canva-файл, обязательные SVG/PNG/JPG.

## State

`07d_VISUALS/STATE.yaml` tracks per-stage status:
- `stages.{scan, generate, inject}`: `status, finished, counts, errors`
- `warnings: []`
- `errors: []`

## Idempotency

Cache-based; default skip-if-exists. `/landing-visuals --force` bypasses cache.
Specific slot: `/landing-visuals --slot <name>`.

## Sub-agents

- `icon-generator`
- `infographic-builder`

## Tools

Bash, Read, Write, Edit, Glob, Task (for dispatching sub-agents).

## Стандарт пайплайна картинок (D1, обязательный)

Каждое визуальное место обрабатывается по
[`docs/standards/image-pipeline.md`](../docs/standards/image-pipeline.md):
анализ места → цель → спецификация → референсы (число = составу композиции) →
генерация на вырезаемом фоне → rembg → вставка; адаптация под палитру —
полупрозрачным оверлеем акцента, не отдельной картинкой на каждый цвет.

## DS asset-pack standard

Канон: [`docs/standards/ds-asset-pack.md`](../docs/standards/ds-asset-pack.md).

Жёстко: каждый ключевой visual-preview делается с реальным текстом прототипа на
desktop и mobile. Если текст не читается или ломает композицию, ассет не готов.
Клиентские исходники не перерисовываются: только обработка, маска, композиция и
адаптация под стиль.
