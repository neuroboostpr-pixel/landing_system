---
description: Deploy the landing to Beget via SSH+rsync+wp-cli (stage 09). Run within a landing project folder after /landing-build is approved.
allowed-tools: Bash, Read
---

# /landing-deploy

## Pre-flight

1. Run `bash scripts/setup-flag.sh is_complete`. If exit 1 → reply "Onboarding не пройден. Запусти /landing-onboarding" and stop.
2. Determine project dir from `<project>` argument or current `landing.project` config.
3. Run: `bash scripts/gate-check.sh --stage 09_deploy --project <project>`.
   If exit 1 → relay the gate error to the user (which previous stage is missing) and stop.
4. Continue with existing flow below.

## Post-completion

When the agent reports stage finished and user approves, run:
`bash scripts/gate-check.sh --stage 09_deploy --project <project> --approve`

## What I do

1. Run `scripts/preflight.sh` — verify environment
2. Run `scripts/deploy.sh .` — rsync theme, activate, import ACF
3. Check site is live: `curl -sI https://<domain>`
4. Check SSL, HTTP→HTTPS redirect
5. **HARD GATE**: show live URL, wait for user approval

## Requirements

- `.env` with `BEGET_USER`, `BEGET_HOST`, `BEGET_PATH`
- `08_КОД/wp-theme/` from `/landing-build`

## Output

- Live WordPress site on Beget
- Theme activated, ACF fields imported
- Cache flushed
