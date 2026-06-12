#!/usr/bin/env bash
# verify-composed-premium.sh — тонкая обёртка над verify_composed_premium.py (v2).
# Имя сохранено: его вызывают гейты 07c_composed / 07f_composed_final.
#
# Usage: verify-composed-premium.sh <path-to-composed.html>
# Exit: 0 PASS · 1 FAIL · 2 файл не найден.
#
# Стандарт: docs/standards/premium-07b-checklist.md (v2, reference-driven).

set -uo pipefail

__SCRIPT_DIR__="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
# shellcheck source=lib/python-cmd.sh
. "$__SCRIPT_DIR__/lib/python-cmd.sh"

exec "$PYTHON_CMD" "$__SCRIPT_DIR__/verify_composed_premium.py" "${1:?ERROR: composed.html path required}"
