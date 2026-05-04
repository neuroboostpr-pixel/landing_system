---
description: Rollback a landing to a previous version (stage 09/ops). Run within a landing project folder.
allowed-tools: Bash, Read
---

# /landing-rollback

## Usage

```
/landing-rollback v1.0
```

## What I do

1. List available versions: `ls 09_ВЕРСИИ/`
2. Restore: `cp -r 09_ВЕРСИИ/<version>/wp-theme 08_КОД/wp-theme`
3. Redeploy: run `scripts/deploy.sh .`
4. Verify site is live after rollback
