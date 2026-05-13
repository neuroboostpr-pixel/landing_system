#!/usr/bin/env bash
# verify-composed-has-visuals.sh — fail if composed.html still contains placeholder markers.
#
# Usage: verify-composed-has-visuals.sh <path-to-composed.html>
# Exit codes:
#   0 — composed.html is clean
#   1 — composed.html still has placeholders → PR-B or PR-C not finished
#   2 — file missing

set -euo pipefail

FILE="${1:?ERROR: composed.html path required}"

[ -f "$FILE" ] || {
    echo "ERROR: composed.html not found at $FILE" >&2
    exit 2
}

if grep -qE '\[SLOT:|\[INFOGRAPHIC:|\[photo slot:' "$FILE"; then
    echo "FAIL: $FILE still contains placeholders. Run /landing-photos and /landing-visuals first." >&2
    exit 1
fi

echo "OK: $FILE has no leftover placeholders"
