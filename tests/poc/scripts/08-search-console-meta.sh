#!/usr/bin/env bash
# 08-search-console-meta.sh
# Per-subsite Google Search Console verification meta tag (no cross-leak).

set -euo pipefail
HERE="$(cd "$(dirname "$0")" && pwd)"
source "$HERE/../lib/env.sh"
source "$HERE/../lib/ssh.sh"
source "$HERE/../lib/assert.sh"

export CURRENT_TEST="08-search-console-meta"
LOG="$LOGS_DIR/${CURRENT_TEST}.log"
exec > >(tee "$LOG") 2>&1
echo "=== $CURRENT_TEST started ==="

info "Step 1: deploy mu-plugin storing GSC verification per-blog"

cat > /tmp/poc-gsc.php <<'PHP'
<?php
/**
 * Plugin Name: POC GSC verification per-blog
 */
add_action('wp_head', function () {
    $token = get_option('poc_gsc_token', '');
    if (!$token) return;
    echo "\n<meta name=\"google-site-verification\" content=\"" . esc_attr($token) . "\" />\n";
}, 1);
PHP

scp_to /tmp/poc-gsc.php "/home/e/esper21/${TEST_DOMAIN}/public_html/wp-content/mu-plugins/poc-gsc.php" > /dev/null 2>&1
pass "mu-plugin uploaded"

info "Step 2: set distinct verification token per subsite"
declare -A TOKENS
TOKENS[ailexi.ru]="GSC-ROOT-AAAA1111"
TOKENS[alpha.ailexi.ru]="GSC-ALPHA-BBBB2222"
TOKENS[bravo.ailexi.ru]="GSC-BRAVO-CCCC3333"

for host in "${!TOKENS[@]}"; do
    tok="${TOKENS[$host]}"
    ssh_run "cd ~/${TEST_DOMAIN}/public_html && $REMOTE_WP --url=http://$host option update poc_gsc_token '$tok' 2>&1 | tail -1" > /dev/null
done

info "Step 3: verify HTML on each subsite has its OWN token and not the others"

for host in ailexi.ru alpha.ailexi.ru bravo.ailexi.ru; do
    own="${TOKENS[$host]}"
    HTML=$(curl -s -L --max-time 15 "http://$host/?_=$RANDOM" || echo "")

    if echo "$HTML" | grep -qF "content=\"$own\""; then
        pass "$host: own token $own present"
    else
        fail "$host: own token $own MISSING"
    fi

    for other_host in ailexi.ru alpha.ailexi.ru bravo.ailexi.ru; do
        [ "$other_host" = "$host" ] && continue
        other_tok="${TOKENS[$other_host]}"
        if echo "$HTML" | grep -qF "content=\"$other_tok\""; then
            fail "$host LEAKS $other_host token '$other_tok' (CRITICAL CROSS-SITE LEAK)"
        fi
    done
done

finish_test
