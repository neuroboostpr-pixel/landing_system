---
type: script
name: migrate-state-add-01a
language: bash
sources: ["scripts/migrate-state-add-01a.sh"]
updated: 2026-05-18
---

# migrate-state-add-01a.sh

scripts/migrate-state-add-01a.sh
Add 01a_niche_analysis stage to an existing project's .landing-state.yaml.
If 02_assets is already approved, mark 01a as 'skipped' (legacy projects).
Otherwise mark as 'locked'.

## Источник

- `scripts/migrate-state-add-01a.sh`
