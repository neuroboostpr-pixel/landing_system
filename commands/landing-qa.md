---
description: Run QA audit on the live landing (stage 10). Checks 7 criteria: availability, HTTPS, meta, analytics, forms, mobile. Run after /landing-deploy.
allowed-tools: Bash, Read, Write
---

# /landing-qa

## What I do

Invoke `qa-auditor` agent → checks 7 criteria on the live site → writes `10_QA/qa-report.md`.

## Requirements

- Live site deployed via `/landing-deploy`
- URL in `00_БРИФ/brief.md`

## Output

- `10_QA/qa-report.md` — QA report with pass/fail per criterion
