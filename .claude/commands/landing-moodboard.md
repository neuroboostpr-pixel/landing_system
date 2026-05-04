---
description: Generate or regenerate the visual moodboard for a landing project (stage 03). Run within a landing project folder after references are approved.
allowed-tools: Bash, Read, Write, Edit, Glob
---

# /landing-moodboard

## Pre-flight

1. Run `bash scripts/setup-flag.sh is_complete`. If exit 1 → reply "Onboarding не пройден. Запусти /landing-onboarding" and stop.
2. Determine project dir from `<project>` argument or current `landing.project` config.
3. Run: `bash scripts/gate-check.sh --stage 03_references --project <project>`.
   If exit 1 → relay the gate error to the user (which previous stage is missing) and stop.
4. Continue with existing flow below.

## Post-completion

When the agent reports stage finished and user approves, run:
`bash scripts/gate-check.sh --stage 03_references --project <project> --approve`

Run within a landing project after references are approved in `03_РЕФЕРЕНСЫ/index.yaml`.

## What I do

1. Invoke `moodboard-composer` agent.
2. Render `03_РЕФЕРЕНСЫ/moodboard.html` from approved references in `index.yaml`.
3. **HARD GATE**: show the preview path, wait for user approval before proceeding to style extraction.

## Usage

Run: `/landing-moodboard`

Requires approved references in `03_РЕФЕРЕНСЫ/index.yaml` (set status to `approved` via `/landing-references` first).

## Output

- `03_РЕФЕРЕНСЫ/moodboard.html` — visual moodboard HTML preview
