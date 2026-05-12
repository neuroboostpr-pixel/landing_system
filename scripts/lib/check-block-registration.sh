#!/usr/bin/env bash
# Hard-check #2: at least one register_block_type call in functions.php.
# Bypassed by legacy:true in .landing-state.yaml.
set -u

PROJECT="${1:?project path required}"

if [ -f "$PROJECT/.landing-state.yaml" ] && grep -q "^[[:space:]]*legacy:[[:space:]]*true" "$PROJECT/.landing-state.yaml" 2>/dev/null; then
    exit 0
fi

FN="$PROJECT/08_КОД/wp-theme/functions.php"
if [ ! -f "$FN" ]; then
    echo "functions.php not found at $FN — no block registration possible" >&2
    exit 1
fi
if grep -qE "register_block_type" "$FN"; then
    exit 0
fi
echo "no register_block_type call found in functions.php" >&2
exit 1
