---
type: script
name: gate-check
language: bash
sources: ["scripts/gate-check.sh"]
updated: 2026-05-18
---

# gate-check.sh

scripts/gate-check.sh — per-stage gate runner.
Reads config/stage-gates.yaml, executes hard_checks, prompts soft_checks.
Usage: gate-check.sh --stage <id> --project <dir> [--approve] [--auto]

## Источник

- `scripts/gate-check.sh`
