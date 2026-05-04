---
description: Plan the WordPress plugin and library stack for a landing project (stage 06). Run within a landing project folder after design system is approved.
allowed-tools: Bash, Read, Write, Edit, Glob
---

# /landing-stack

## Pre-flight

1. Run `bash scripts/setup-flag.sh is_complete`. If exit 1 → reply "Onboarding не пройден. Запусти /landing-onboarding" and stop.
2. Determine project dir from `<project>` argument or current `landing.project` config.
3. Run: `bash scripts/gate-check.sh --stage 06_stack --project <project>`.
   If exit 1 → relay the gate error to the user (which previous stage is missing) and stop.
4. Continue with existing flow below.

## Post-completion

When the agent reports stage finished and user approves, run:
`bash scripts/gate-check.sh --stage 06_stack --project <project> --approve`

Run within a landing project after `05_ДИЗАЙН-СИСТЕМА/DESIGN.md` is approved.

## What I do

1. Invoke `stack-planner` agent.
2. Produce `06_СТЕК/design-stack.yaml` — list of WordPress plugins, JS libs, icon library, font CDN.
3. Produce supporting docs: `component-library-plan.md`, `effects-plan.md`, `font-and-color-plan.md`.
4. **HARD GATE**: show `design-stack.yaml`, wait for user approval before proceeding to stage 07.

## Usage

Run: `/landing-stack`

Requires `05_ДИЗАЙН-СИСТЕМА/DESIGN.md` produced by `design-system-generator` (run after `/landing-design` is approved).

## Output

- `06_СТЕК/design-stack.yaml` — plugin and library registry
- `06_СТЕК/component-library-plan.md`
- `06_СТЕК/effects-plan.md`
- `06_СТЕК/font-and-color-plan.md`
