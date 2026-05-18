---
type: script
name: migrate-niche-to-v2
language: bash
sources: ["scripts/migrate-niche-to-v2.sh"]
updated: 2026-05-18
---

# migrate-niche-to-v2.sh

Migrate a legacy 01a_АНАЛИЗ_НИШИ project to niche-analysis v2.

Idempotent:
- Adds **Mode:** legacy_v1 header to positioning.md if missing
- Creates market-profile.md stub if missing (does not overwrite)
- Creates landing-structure.md stub if missing (does not overwrite)

Usage: migrate-niche-to-v2.sh <project-dir>

## Источник

- `scripts/migrate-niche-to-v2.sh`
