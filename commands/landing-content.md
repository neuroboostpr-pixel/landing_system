---
description: Adapt the landing prototype text to Gutenberg blocks (stage 07). Run within a landing project folder after stack is approved.
allowed-tools: Bash, Read, Write, Edit, Glob
---

# /landing-content

## Pre-flight

1. Run `bash scripts/setup-flag.sh is_complete`. If exit 1 → reply "Onboarding не пройден. Запусти /landing-onboarding" and stop.
2. Determine project dir from `<project>` argument or current `landing.project` config.
3. Run: `bash scripts/gate-check.sh --stage 07_content --project <project>`.
   If exit 1 → relay the gate error to the user (which previous stage is missing) and stop.
4. Continue with existing flow below.

## Post-completion

When the agent reports stage finished and user approves, run:
`bash scripts/gate-check.sh --stage 07_content --project <project> --approve`

Run within a landing project after `06_СТЕК/design-stack.yaml` is approved.

## What I do

1. Invoke `content-writer` agent.
2. Read `07_КОНТЕНТ/prototype.md` and block structure from `DESIGN.md`.
3. Read real testimonials from `02_МАТЕРИАЛЫ_КЛИЕНТА/testimonials/`.
4. Produce `07_КОНТЕНТ/final-copy.md` — text laid out per Gutenberg block.
5. Produce `07_КОНТЕНТ/seo-copy.md` — SEO titles, descriptions, h1 variants.
6. **HARD GATE**: show `final-copy.md`, wait for user approval before proceeding to stage 08.

## Usage

Run: `/landing-content`

Requires:
- `07_КОНТЕНТ/prototype.md` — source prototype text
- `06_СТЕК/design-stack.yaml` — block definitions (run after `/landing-stack`)

## Output

- `07_КОНТЕНТ/final-copy.md` — final copy per block
- `07_КОНТЕНТ/seo-copy.md` — SEO copy variants
