---
type: script
name: verify-php-syntax
language: bash
sources: ["scripts/verify-php-syntax.sh"]
updated: 2026-05-18
---

# verify-php-syntax.sh

verify-php-syntax.sh — run `php -l` on every .php file in a directory.

Usage: verify-php-syntax.sh <dir>
Exit codes:
0 — all PHP files parse cleanly
1 — at least one syntax error
2 — dir missing OR php not installed

## Источник

- `scripts/verify-php-syntax.sh`
