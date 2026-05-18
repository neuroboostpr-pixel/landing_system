---
type: script
name: mark-legacy-projects
language: bash
sources: ["scripts/mark-legacy-projects.sh"]
updated: 2026-05-18
---

# mark-legacy-projects.sh

Mark Lendings/* projects as legacy:true if they fail stage-08 gate.
One-shot, idempotent. Run once after merging the systemic fix.

Usage: mark-legacy-projects.sh [<lendings-root>]

## Источник

- `scripts/mark-legacy-projects.sh`
