---
name: photo-preview-board
description: After user approves selections.yaml, process each slot — crop/resize client photos OR codex image_gen fallback OR SVG placeholder. Render photo-preview.html for final approve. Enforces identity-safe gate.
---

# photo-preview-board

## Mission

Turn `selections.yaml` (canonical, user-approved) into `processed/<slot_id>/{desktop,mobile}.jpg` files and render `photo-preview.html` for final review.

Identity-safe gate enforcement happens here: if a `strategy: generate` slot is identity-safe AND `ai_approved_by_user: false`, silently downgrade to `strategy: placeholder`. See [`IDENTITY_SAFE.md`](../skills/photo-curation/IDENTITY_SAFE.md).

## Input

- `<project_dir>` (must have valid `07c_PHOTOS/selections.yaml`)

## Output

- `<project>/07c_PHOTOS/processed/<slot_id>/desktop.jpg`
- `<project>/07c_PHOTOS/processed/<slot_id>/mobile.jpg` (if block has `mobile_ratio`)
- `<project>/07c_PHOTOS/photo-preview.html`

## Process

1. Validate `selections.yaml` via `python3 skills/photo-curation/scripts/selections-validator.py <selections.yaml>`. Abort on invalid.

2. For each slot in `selections.yaml`:

   - **strategy: bring-your-own** —
     ```bash
     python3 skills/photo-styling/scripts/style.py \
       <intake/photo_NNN.jpg> <processed/<slot_id>/desktop.jpg> \
       --mode target-ratio --ratio <ratio> --max-dim 1920
     ```
     If `mobile_ratio` is defined in `meta.yaml` of the block:
     ```bash
     python3 skills/photo-styling/scripts/style.py \
       <intake/photo_NNN.jpg> <processed/<slot_id>/mobile.jpg> \
       --mode target-ratio --ratio <mobile_ratio> --max-dim 1080
     ```

   - **strategy: generate** —
     - Identity-safe check: if `slot_id` matches `testimonial|expert|team-member|team_member|avatar` AND `ai_approved_by_user == false` — silently switch to `placeholder` strategy.
     - Otherwise:
       ```bash
       bash skills/photo-curation/scripts/codex-generate-fallback.sh \
         <project_dir> <slot_id> <width> <height> <ratio> "<slot_hint>"
       ```
     - Update `selections.yaml:slots[].log_ref` to point to the codex log.

   - **strategy: placeholder** —
     ```bash
     python3 skills/photo-curation/scripts/svg-placeholder.py \
       --slot-id <id> --width <w> --height <h> \
       --hint "<hint>" --brand-primary <color> \
       --out <processed/<slot_id>/placeholder.png>
     ```

3. Run:
   ```bash
   python3 skills/photo-curation/scripts/preview-render.py \
     --selections <project>/07c_PHOTOS/selections.yaml \
     --out <project>/07c_PHOTOS/photo-preview.html
   ```

## Identity-safe enforcement

Per [`IDENTITY_SAFE.md`](../skills/photo-curation/IDENTITY_SAFE.md): the silent strategy downgrade in step 2 (`generate` → `placeholder` when `ai_approved_by_user == false` on identity-safe slot) is the enforcement point.

## Tools

Bash, Read, Write.
