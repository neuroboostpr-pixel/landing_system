---
description: Deploy the landing to Beget via SSH+rsync+wp-cli (stage 09). Run within a landing project folder after /landing-build is approved.
allowed-tools: Bash, Read
---

# /landing-deploy

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
