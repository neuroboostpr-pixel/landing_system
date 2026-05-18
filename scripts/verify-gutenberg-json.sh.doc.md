---
type: script
name: verify-gutenberg-json
language: bash
sources: ["scripts/verify-gutenberg-json.sh"]
updated: 2026-05-18
---

# verify-gutenberg-json.sh

verify-gutenberg-json.sh — validate every block.json in a directory parses as JSON.

Usage: verify-gutenberg-json.sh <dir>
Exit codes:
0 — all block.json files valid (or dir is empty)
1 — at least one invalid JSON
2 — dir missing

## Источник

- `scripts/verify-gutenberg-json.sh`
