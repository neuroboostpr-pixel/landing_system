---
type: script
name: check-wiki-sync
language: bash
sources: ["scripts/check-wiki-sync.sh"]
updated: 2026-05-18
---

# check-wiki-sync.sh

scripts/check-wiki-sync.sh
Проверяет что hash источников совпадает с записями в wiki/.cache.json.
Exit 0 — синхрон, exit 1 — есть desync.

## Источник

- `scripts/check-wiki-sync.sh`
