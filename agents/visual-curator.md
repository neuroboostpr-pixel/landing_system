---
name: visual-curator
description: Stage 07d orchestrator (PR-C). Scans composed.html for icon/infographic slots, dispatches icon-generator and infographic-builder, manages STATE.yaml, injects PNGs back into composed.html. Triggered by /landing-visuals.
---

# visual-curator


## Pre-flight

Перед любым действием — wiki-запрос для маршрутизации:

```bash
python -m scripts.wiki.query --slug=visual-curator
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

Orchestrate visual generation pipeline (stage 07d). No identity-safe rules — visuals don't contain people.

## Gate (hard prerequisites)

Before running anything, verify:
- `<project>/.landing-state.yaml:stages.05_design.status == approved` — иначе exit с русским сообщением «Сначала утверди дизайн-систему».
- `<project>/07b_COMPOSED/composed.html` exists — иначе exit «Сначала запусти `/landing-compose` (PR-A)».

If either gate fails: exit 1 with the relevant Russian message.

## Process

1. **Scan.**
   ```bash
   python3 skills/visual-generation/scripts/slot-scanner.py \
     --html <project>/07b_COMPOSED/composed.html \
     --out <project>/07d_VISUALS/_slots.yaml
   ```

2. **Generate icons.** For each icon slot:
   - Dispatch `icon-generator` agent with (slot_name, hint).
   - Cache lookup first via `visual-cache.py`; skip codex if cached.
   - On generation: copy result also to `.cache/<hash>.png`.

3. **Generate infographics.** Same for infographic slots, dispatch `infographic-builder` agent.

4. **Inject.**
   ```bash
   python3 skills/block-composition/scripts/compose-blocks.py --project <project>
   ```
   This now reads `07d_VISUALS/icons/` and `07d_VISUALS/infographics/`. Backward compatible: if 07d_VISUALS missing, placeholder behavior preserved.

5. Mark `STATE.yaml:stages.inject` done. Print Russian summary.

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
