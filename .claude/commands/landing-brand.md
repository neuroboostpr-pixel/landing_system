---
description: Build the brand kit for a landing project (stage 04). Run within a landing project folder after style extraction is complete.
allowed-tools: Bash, Read, Write, Edit, Glob
---

# /landing-brand

## Pre-flight

1. Run `bash scripts/setup-flag.sh is_complete`. If exit 1 → reply "Onboarding не пройден. Запусти /landing-onboarding" and stop.
2. Determine project dir from `<project>` argument or current `landing.project` config.
3. Run: `bash scripts/gate-check.sh --stage 04_brand --project <project>`.
   If exit 1 → relay the gate error to the user (which previous stage is missing) and stop.
4. Continue with existing flow below.

## Post-completion

When the agent reports stage finished and user approves, run:
`bash scripts/gate-check.sh --stage 04_brand --project <project> --approve`

Run within a landing project after `style-extractor` has produced `04_БРЕНД/extracted/*.yaml`.

## What I do

1. Invoke `brand-architect` agent.
2. Synthesize `04_БРЕНД/brand-kit.md` from all extracted style data with full provenance.
3. Render `04_БРЕНД/brand-kit.html` visual preview.
4. **HARD GATE**: show the preview path, wait for user approval before proceeding to stage 05.

## Usage

Run: `/landing-brand`

Requires `04_БРЕНД/extracted/*.yaml` files produced by `style-extractor` (run after `/landing-moodboard` is approved).

## Output

- `04_БРЕНД/brand-kit.md` — canonical brand kit with provenance
- `04_БРЕНД/brand-kit.html` — visual preview (palette swatches, font specimens, icon thumbnails)
