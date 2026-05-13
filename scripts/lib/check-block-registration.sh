#!/usr/bin/env bash
# Hard-check: Lazy Blocks registration present in functions.php.
# We register via lazyblocks()->add_block( inside an lzb/init action hook,
# not register_block_type. Bypassed by legacy:true in .landing-state.yaml.
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
if grep -q "lzb/init" "$FN" && grep -q "lazyblocks()->add_block(" "$FN"; then
    exit 0
fi
echo "block registration missing: functions.php must contain both 'lzb/init' action and 'lazyblocks()->add_block(' call" >&2
exit 1
