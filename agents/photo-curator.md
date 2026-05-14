---
name: photo-curator
description: Stage 07c orchestrator (PR-B). Runs intake, dispatches photo-classifier/photo-matcher/photo-preview-board, manages STATE.yaml, renders photo-board.html, waits for user approve. Triggered by /landing-photos.
---

# photo-curator

## Mission

Orchestrate the full photo pipeline (stage 07c) for the landing project. Identity-safe rules per [`skills/photo-curation/IDENTITY_SAFE.md`](../skills/photo-curation/IDENTITY_SAFE.md).

## Gate (hard prerequisites)

Before running anything, verify:
- `<project>/.landing-state.yaml:stages.05_design.status == approved` — иначе exit с русским сообщением «Сначала утверди дизайн-систему».
- `<project>/.landing-state.yaml:stages.07a_wireframe.status == approved` (или эквивалент — wireframe selections.yaml exists) — иначе exit «Сначала выбери варианты блоков в wireframe.html».

If either gate fails: exit 1 with the relevant Russian message.

## Process

1. **Bootstrap.** Ensure `<project>/07c_PHOTOS/inbox/` exists with all subfolders (`_свалка`, `портреты_и_команда`, `процесс_работы`, `объекты_и_продукты`, `интерьер_экстерьер`, `до_после`, `документы_сертификаты`). Print where to put photos.

2. **Dual-path intake.** Also scan `<project>/02_МАТЕРИАЛЫ_КЛИЕНТА/photos/original/` — copy any photos into `07c_PHOTOS/inbox/_свалка/` for backward compatibility with old projects.

3. **Intake.** Run:
   ```bash
   python3 skills/photo-curation/scripts/intake.py \
     --inbox <project>/07c_PHOTOS/inbox \
     --intake <project>/07c_PHOTOS/intake
   ```
   Update `STATE.yaml:stages.intake`.

4. **Classify.** For each photo in `intake/` with `tag_source: pending_ai_classify` — dispatch `photo-classifier` (in batches of 5, sleep 2s between). Update `catalog.yaml` progressively.

5. **Match.** Dispatch `photo-matcher` once over the full catalog + slots derived from `07_ПРОТОТИП/prototype.yaml` filtered by `07a_WIREFRAME/selections.yaml`. Produces `selections.draft.yaml`.

6. **Render gallery.**
   ```bash
   python3 skills/photo-curation/scripts/gallery-render.py \
     --catalog <project>/07c_PHOTOS/catalog.yaml \
     --draft <project>/07c_PHOTOS/selections.draft.yaml \
     --out <project>/07c_PHOTOS/photo-board.html
   ```

7. **HARD GATE.** Print: `Открой 07c_PHOTOS/photo-board.html в браузере. Расставь фотки по слотам, нажми «Подтвердить и скачать selections.yaml», положи selections.yaml в 07c_PHOTOS/.` Wait for user.

8. **Validate.** Run `python3 skills/photo-curation/scripts/selections-validator.py 07c_PHOTOS/selections.yaml`. If invalid — print errors and return to step 7.

9. **Process.** Dispatch `photo-preview-board`.

10. **HARD GATE.** Print: `Открой 07c_PHOTOS/photo-preview.html — проверь как фотки лягут в макет. После approve — composed.html будет перерендерен.` Wait for user.

11. **Re-render composed.** Run `python3 skills/block-composition/scripts/compose-blocks.py --project <project>` (existing PR-A; it now reads `07c_PHOTOS/selections.yaml`).

12. Mark `STATE.yaml:stages.process` done. Print success summary in Russian.

## State

`07c_PHOTOS/STATE.yaml` tracks per-stage status:
- `stages.{intake,classify,match,approval,process}`: `status, finished, counts, errors`
- `warnings: []`
- `errors: []`

## Idempotency

On restart: read STATE.yaml, resume from first non-done stage.
`--force-stage <name>` resets that stage and re-runs from there.

## Sub-agents

- `photo-classifier` — image classification via codex CLI `--image`
- `photo-matcher` — slot-to-photo matching via codex
- `photo-preview-board` — processing + photo-preview.html rendering

## Tools

Bash, Read, Write, Edit, Glob, Task (for dispatching the 3 sub-agents).
