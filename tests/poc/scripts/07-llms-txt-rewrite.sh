#!/usr/bin/env bash
# 07-llms-txt-rewrite.sh
# mu-plugin serves /llms.txt per-subsite via WP rewrite hook.

set -euo pipefail
HERE="$(cd "$(dirname "$0")" && pwd)"
source "$HERE/../lib/env.sh"
source "$HERE/../lib/ssh.sh"
source "$HERE/../lib/assert.sh"

export CURRENT_TEST="07-llms-txt-rewrite"
LOG="$LOGS_DIR/${CURRENT_TEST}.log"
exec > >(tee "$LOG") 2>&1
echo "=== $CURRENT_TEST started ==="

info "Step 1: deploy mu-plugin that serves /llms.txt"

cat > /tmp/poc-llms.php <<'PHP'
<?php
/**
 * Plugin Name: POC llms.txt server
 */
add_action('init', function () {
    add_rewrite_rule('^llms\.txt$', 'index.php?poc_llms=1', 'top');
});

add_filter('query_vars', function ($vars) {
    $vars[] = 'poc_llms';
    return $vars;
});

add_action('template_redirect', function () {
    if (!get_query_var('poc_llms')) return;
    header('Content-Type: text/plain; charset=utf-8');
    $host = parse_url(home_url(), PHP_URL_HOST);
    echo "# " . get_bloginfo('name') . " (host=$host)\n\n";
    echo "> " . get_bloginfo('description') . "\n\n";
    echo "## Pages\n\n";
    $pages = get_posts(['post_type'=>'page','numberposts'=>10,'post_status'=>'publish']);
    foreach ($pages as $p) {
        echo "- [" . $p->post_title . "](" . get_permalink($p) . ")\n";
    }
    exit;
});

// Force rewrite rules to be regenerated on first hit (no admin click needed).
register_activation_hook(__FILE__, function () { flush_rewrite_rules(); });
add_action('init', function () {
    if (get_option('poc_llms_flushed') !== '1') {
        flush_rewrite_rules();
        update_option('poc_llms_flushed', '1');
    }
}, 99);
PHP

scp_to /tmp/poc-llms.php "/home/e/esper21/${TEST_DOMAIN}/public_html/wp-content/mu-plugins/poc-llms.php" > /dev/null 2>&1
pass "mu-plugin uploaded"

info "Step 2: flush rewrite rules on each subsite"
for host in ailexi.ru alpha.ailexi.ru bravo.ailexi.ru; do
    ssh_run "cd ~/${TEST_DOMAIN}/public_html && $REMOTE_WP --url=http://$host rewrite flush --hard 2>&1 | tail -1" > /dev/null
done
sleep 2

info "Step 3: GET /llms.txt on each subsite"

for host in ailexi.ru alpha.ailexi.ru bravo.ailexi.ru; do
    URL="http://$host/llms.txt"
    BODY=$(curl -s -L --max-time 15 "$URL" || echo "")
    CT=$(curl -sI --max-time 10 "$URL" | grep -i content-type | head -1)

    if echo "$CT" | grep -q 'text/plain'; then
        pass "$URL Content-Type: text/plain"
    else
        fail "$URL Content-Type wrong (got: $CT)"
    fi

    if echo "$BODY" | grep -q "host=$host"; then
        pass "$URL body identifies host=$host"
    else
        fail "$URL body does NOT identify $host (got first 300 chars below)"
        echo "$BODY" | head -c 300; echo
    fi
done

finish_test
