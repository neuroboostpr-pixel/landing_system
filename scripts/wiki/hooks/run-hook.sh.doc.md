---
type: script
name: run-hook
language: bash
sources: ["scripts/wiki/hooks/run-hook.sh"]
updated: 2026-05-18
---

# run-hook.sh

scripts/wiki/hooks/run-hook.sh <hook-name>
Cross-platform wrapper for wiki session hooks. Resolves Python via
scripts/lib/python-cmd.sh and runs the named hook from this directory.
Used from .claude/settings.json hooks.

## Источник

- `scripts/wiki/hooks/run-hook.sh`
