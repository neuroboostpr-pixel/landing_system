---
type: script
name: gate-state
language: bash
sources: ["scripts/gate-state.sh"]
updated: 2026-05-18
---

# gate-state.sh

scripts/gate-state.sh — read/write .landing-state.yaml
Usage:
gate-state.sh get <project-dir> <stage>
gate-state.sh set <project-dir> <stage> <status>
gate-state.sh approve <project-dir> <stage>
gate-state.sh all_approved <project-dir> <comma-separated-stages>

## Источник

- `scripts/gate-state.sh`
