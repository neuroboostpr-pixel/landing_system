---
type: script
name: verify-composed-premium
language: bash
sources: ["scripts/verify-composed-premium.sh"]
updated: 2026-05-18
---

# verify-composed-premium.sh

verify-composed-premium.sh — проверяет, что composed.html соответствует
premium-07b-checklist.md (обязательные интерактивные фичи).

Usage: verify-composed-premium.sh <path-to-composed.html>
Exit codes:
0 — все premium-фичи найдены
1 — одна или несколько фич отсутствуют
2 — файл не найден

Полный стандарт: docs/standards/premium-07b-checklist.md

## Источник

- `scripts/verify-composed-premium.sh`
