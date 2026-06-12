#!/usr/bin/env bash
# 05-rank-math-network.sh
# RankMath SEO plugin: network-active, per-site title/meta works independently.

set -euo pipefail
HERE="$(cd "$(dirname "$0")" && pwd)"
source "$HERE/../lib/env.sh"
source "$HERE/../lib/ssh.sh"
source "$HERE/../lib/assert.sh"

export CURRENT_TEST="05-rank-math-network"
LOG="$LOGS_DIR/${CURRENT_TEST}.log"
exec > >(tee "$LOG") 2>&1
echo "=== $CURRENT_TEST started ==="

info "Step 1: confirm RankMath plugin is network-active"
LIST=$(ssh_run "cd ~/${TEST_DOMAIN}/public_html && $REMOTE_WP plugin list --format=csv 2>&1" | grep seo-by-rank-math || echo "")
if echo "$LIST" | grep -q 'active-network'; then
    pass "seo-by-rank-math is active-network"
else
    fail "seo-by-rank-math is NOT active-network (got: $LIST)"
fi

info "Step 2: set distinct site title + tagline per subsite"

declare -A TITLES
TITLES[ailexi.ru]="Root POC"
TITLES[alpha.ailexi.ru]="Alpha Segment"
TITLES[bravo.ailexi.ru]="Bravo Segment"

for host in "${!TITLES[@]}"; do
    t="${TITLES[$host]}"
    ssh_run "cd ~/${TEST_DOMAIN}/public_html && $REMOTE_WP --url=http://$host option update blogname '$t' 2>&1 | tail -1" > /dev/null
    ssh_run "cd ~/${TEST_DOMAIN}/public_html && $REMOTE_WP --url=http://$host option update blogdescription 'Tagline for $host' 2>&1 | tail -1" > /dev/null
    info "set blogname=$t for $host"
done

info "Step 3: verify each subsite renders its own title in HTML"

for host in ailexi.ru alpha.ailexi.ru bravo.ailexi.ru; do
    want="${TITLES[$host]}"
    HTML=$(curl -s -L --max-time 15 "http://$host/?_=$RANDOM" || echo "")
    if echo "$HTML" | grep -qF "$want"; then
        pass "http://$host/ contains its title '$want'"
    else
        fail "http://$host/ does NOT contain '$want'"
    fi
done

info "Step 4: no title leak between subsites"

ALPHA_HTML=$(curl -s -L --max-time 15 "http://alpha.ailexi.ru/?_=$RANDOM" || echo "")
if echo "$ALPHA_HTML" | grep -qF "Root POC"; then
    fail "alpha leaks Root POC title (cache leak)"
else
    pass "alpha does NOT leak Root POC title"
fi
if echo "$ALPHA_HTML" | grep -qF "Bravo Segment"; then
    fail "alpha leaks Bravo Segment title (cache leak)"
else
    pass "alpha does NOT leak Bravo Segment title"
fi

finish_test
