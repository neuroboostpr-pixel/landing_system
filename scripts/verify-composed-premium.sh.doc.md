---
type: script
name: verify-composed-premium
language: bash
sources: ["scripts/verify-composed-premium.sh"]
updated: 2026-05-18
---

# verify-composed-premium.sh

verify-composed-premium.sh — тонкая обёртка над verify_composed_premium.py (v2).
Имя сохранено: его вызывают гейты 07c_composed / 07f_composed_final.

Usage: verify-composed-premium.sh <path-to-composed.html>
Exit: 0 PASS · 1 FAIL · 2 файл не найден.

Стандарт: docs/standards/premium-07b-checklist.md (v2, reference-driven).

## Источник

- `scripts/verify-composed-premium.sh`
