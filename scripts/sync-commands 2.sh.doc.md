---
type: script
name: sync-commands 2
language: bash
sources: ["scripts/sync-commands 2.sh"]
updated: 2026-05-18
---

# sync-commands 2.sh

Sync commands/*.md (source of truth) → .claude/commands/*.md (Claude Code runtime).
Source: commands/ — the version humans edit, lives in git, in wiki sources.
Target: .claude/commands/ — what Claude Code actually executes at runtime.

Run automatically by .githooks/post-commit (after wiki sync).
Can also be invoked manually: bash scripts/sync-commands.sh [--check]

Modes:
default     : copy all source → runtime, report changes
--check     : exit 1 if any divergence (CI mode)

## Источник

- `scripts/sync-commands 2.sh`
