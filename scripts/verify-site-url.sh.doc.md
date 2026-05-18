---
type: script
name: verify-site-url
language: bash
sources: ["scripts/verify-site-url.sh"]
updated: 2026-05-18
---

# verify-site-url.sh

verify-site-url.sh — curl HEAD on deployed URL from .landing-state.yaml.

Usage: verify-site-url.sh <path-to-.landing-state.yaml>
Exit codes:
0 — URL returns 2xx
1 — URL not reachable or non-2xx
2 — state.yaml missing or no deploy_url

## Источник

- `scripts/verify-site-url.sh`
