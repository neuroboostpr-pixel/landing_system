---
type: script
name: verify-composed-has-visuals
language: bash
sources: ["scripts/verify-composed-has-visuals.sh"]
updated: 2026-05-18
---

# verify-composed-has-visuals.sh

verify-composed-has-visuals.sh — fail if composed.html still contains placeholder markers.

Usage: verify-composed-has-visuals.sh <path-to-composed.html>
Exit codes:
0 — composed.html is clean
1 — composed.html still has placeholders → PR-B or PR-C not finished
2 — file missing

## Источник

- `scripts/verify-composed-has-visuals.sh`
