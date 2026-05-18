---
type: script
name: migrate-template-readmes
language: bash
sources: ["scripts/migrate-template-readmes.sh"]
updated: 2026-05-18
---

# migrate-template-readmes.sh

migrate-template-readmes.sh — copy missing READMEs from template/ into an existing project.

Idempotent: existing READMEs preserved (no overwrite). Creates missing subfolders
(e.g. 04_БРЕНД/logos/) if absent.

Usage: bash migrate-template-readmes.sh <project_dir>

## Источник

- `scripts/migrate-template-readmes.sh`
