---
type: script
name: migrate-state-for-prd
language: bash
sources: ["scripts/migrate-state-for-prd.sh"]
updated: 2026-05-18
---

# migrate-state-for-prd.sh

migrate-state-for-prd.sh — add new PR-D stages to existing .landing-state.yaml.

Usage: bash migrate-state-for-prd.sh <path-to-.landing-state.yaml>
Idempotent: existing stages preserved, only missing ones added (status=locked).
Bumps schema_version to 2.

## Источник

- `scripts/migrate-state-for-prd.sh`
