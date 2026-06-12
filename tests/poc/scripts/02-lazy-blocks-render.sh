#!/usr/bin/env bash
# 02-lazy-blocks-render.sh
# Same as 01 but explicitly checks rendered HTML on the FRONT of each subsite.
# 01 verifies registration; 02 verifies isolated rendering with per-subsite content.

set -euo pipefail
HERE="$(cd "$(dirname "$0")" && pwd)"
source "$HERE/../lib/env.sh"
source "$HERE/../lib/ssh.sh"
source "$HERE/../lib/assert.sh"

export CURRENT_TEST="02-lazy-blocks-render"
LOG="$LOGS_DIR/${CURRENT_TEST}.log"
exec > >(tee "$LOG") 2>&1
echo "=== $CURRENT_TEST started ==="

info "Verify that each subsite front page renders our block with its own headline"

EXPECTED=(
  "http://ailexi.ru|Hello POC-1"
  "http://alpha.ailexi.ru|Hello POC-2"
  "http://bravo.ailexi.ru|Hello POC-3"
)

for pair in "${EXPECTED[@]}"; do
    url="${pair%|*}"; want="${pair##*|}"
    HTML=$(curl -s -L --max-time 20 "$url/?_=$RANDOM" || echo "")

    if echo "$HTML" | grep -qF "$want"; then
        pass "$url renders '$want'"
    else
        fail "$url does NOT render '$want'"
    fi

    if echo "$HTML" | grep -q 'lazyblock-poc-hero'; then
        pass "$url contains lazyblock-poc-hero class"
    else
        fail "$url missing lazyblock-poc-hero class"
    fi
done

finish_test
