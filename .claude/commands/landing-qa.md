---
description: Run QA audit on the live landing (stage 10). Checks 7 criteria: availability, HTTPS, meta, analytics, forms, mobile. Run after /landing-deploy.
allowed-tools: Bash, Read, Write
---

# /landing-qa

## Pre-flight

1. Run `bash scripts/setup-flag.sh is_complete`. If exit 1 → reply "Onboarding не пройден. Запусти /landing-onboarding" and stop.
2. Determine project dir from `<project>` argument or current `landing.project` config.
3. Run: `bash scripts/gate-check.sh --stage 10_qa --project <project>`.
   If exit 1 → relay the gate error to the user (which previous stage is missing) and stop.
4. Continue with existing flow below.

## Post-completion

When the agent reports stage finished and user approves, run:
`bash scripts/gate-check.sh --stage 10_qa --project <project> --approve`

## What I do

Invoke `qa-auditor` agent → checks 7 criteria on the live site → writes `10_QA/qa-report.md`.

## Requirements

- Live site deployed via `/landing-deploy`
- URL in `00_БРИФ/brief.md`

## Output

- `10_QA/qa-report.md` — QA report with pass/fail per criterion
