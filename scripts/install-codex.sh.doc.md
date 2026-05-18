---
type: script
name: install-codex
language: bash
sources: ["scripts/install-codex.sh"]
updated: 2026-05-18
---

# install-codex.sh

install-codex.sh — verify codex CLI is installed; install via npm if not.

Usage:
bash install-codex.sh             # check + install if missing + prompt login
bash install-codex.sh --check     # just report status, no install
bash install-codex.sh --dry-run   # print what would happen

## Источник

- `scripts/install-codex.sh`
