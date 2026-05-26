#!/usr/bin/env bash
# verify-gutenberg-json.sh — validate every block.json in a directory parses as JSON.
#
# Usage: verify-gutenberg-json.sh <dir>
# Exit codes:
#   0 — all block.json files valid (or dir is empty)
#   1 — at least one invalid JSON
#   2 — dir missing

set -euo pipefail


# Cross-platform python detection (sets PYTHON_CMD).
__SCRIPT_DIR__="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
# shellcheck source=lib/python-cmd.sh
. "$__SCRIPT_DIR__/lib/python-cmd.sh"
DIR="${1:?ERROR: directory required}"

[ -d "$DIR" ] || {
    echo "ERROR: dir not found: $DIR" >&2
    exit 2
}

errors=0
while IFS= read -r -d '' f; do
    if ! $PYTHON_CMD -c "import json,sys; json.load(open(sys.argv[1]))" "$f" 2>/dev/null; then
        echo "✗ Invalid JSON: $f" >&2
        errors=$((errors+1))
    fi
done < <(find "$DIR" -name "block.json" -print0)

if [ "$errors" -gt 0 ]; then
    echo "FAIL: $errors block.json file(s) are invalid" >&2
    exit 1
fi

echo "OK: all block.json files in $DIR are valid"
