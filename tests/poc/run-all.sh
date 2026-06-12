#!/usr/bin/env bash
# Run all POC tests sequentially. Emit a final summary.
set -uo pipefail
HERE="$(cd "$(dirname "$0")" && pwd)"

RESULTS=()
for script in "$HERE"/scripts/[0-9][0-9]-*.sh; do
    name=$(basename "$script")
    echo
    echo "==================================================================="
    echo "RUNNING: $name"
    echo "==================================================================="
    if bash "$script"; then
        RESULTS+=("GREEN: $name")
    else
        RESULTS+=("RED:   $name")
    fi
done

echo
echo "==================================================================="
echo "POC GAUNTLET SUMMARY"
echo "==================================================================="
for r in "${RESULTS[@]}"; do
    echo "  $r"
done
echo
GREEN=$(printf '%s\n' "${RESULTS[@]}" | grep -c '^GREEN' || true)
RED=$(printf '%s\n' "${RESULTS[@]}" | grep -c '^RED' || true)
echo "Total: $GREEN green, $RED red, out of ${#RESULTS[@]}"
[ "$RED" -eq 0 ]
