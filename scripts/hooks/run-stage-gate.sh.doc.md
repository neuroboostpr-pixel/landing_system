---
type: script
name: run-stage-gate
language: bash
sources: ["scripts/hooks/run-stage-gate.sh"]
updated: 2026-05-18
---

# run-stage-gate.sh

scripts/hooks/run-stage-gate.sh
Cross-platform wrapper for the stage-gate PreToolUse hook. Resolves
Python via scripts/lib/python-cmd.sh. Invoked from .claude/settings.json.

## Источник

- `scripts/hooks/run-stage-gate.sh`
