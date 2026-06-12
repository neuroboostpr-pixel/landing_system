#!/usr/bin/env bash
# 04-robots-per-site.sh
# Each subsite has its own robots.txt. AI bots (GPTBot, ClaudeBot, PerplexityBot)
# explicitly allowed via a custom mu-plugin filter.

set -euo pipefail
HERE="$(cd "$(dirname "$0")" && pwd)"
source "$HERE/../lib/env.sh"
source "$HERE/../lib/ssh.sh"
source "$HERE/../lib/assert.sh"

export CURRENT_TEST="04-robots-per-site"
LOG="$LOGS_DIR/${CURRENT_TEST}.log"
exec > >(tee "$LOG") 2>&1
echo "=== $CURRENT_TEST started ==="

info "Step 1: deploy mu-plugin that adds AI bots allow-list to robots.txt"

cat > /tmp/poc-robots.php <<'PHP'
<?php
/**
 * Plugin Name: POC robots.txt AI allow-list
 */
add_filter('robots_txt', function ($output, $public) {
    if (!$public) return $output;

    $ai_bots = ['GPTBot', 'OAI-SearchBot', 'ChatGPT-User',
                'ClaudeBot', 'Claude-User', 'Claude-SearchBot',
                'PerplexityBot', 'Google-Extended', 'Yandex-Neuro'];

    $append = "\n# AI bots explicitly allowed by POC mu-plugin\n";
    foreach ($ai_bots as $bot) {
        $append .= "User-agent: $bot\nAllow: /\n\n";
    }
    // also expose per-blog identification (cache-leak check)
    $append .= "# blog_id=" . get_current_blog_id() . " host=" . parse_url(home_url(), PHP_URL_HOST) . "\n";
    return $output . $append;
}, 10, 2);
PHP

ssh_run "mkdir -p ~/${TEST_DOMAIN}/public_html/wp-content/mu-plugins"
scp_to /tmp/poc-robots.php "/home/e/esper21/${TEST_DOMAIN}/public_html/wp-content/mu-plugins/poc-robots.php" > /dev/null 2>&1
pass "mu-plugin uploaded"

info "Step 2: verify robots.txt per-site, AI bots present, no cross-site leak"

declare -A SEEN_HOSTS
for host in ailexi.ru alpha.ailexi.ru bravo.ailexi.ru; do
    URL="http://$host/robots.txt"
    BODY=$(curl -s -L --max-time 15 "$URL" || echo "")

    if echo "$BODY" | grep -q 'GPTBot'; then
        pass "$URL contains GPTBot allow rule"
    else
        fail "$URL does NOT contain GPTBot allow rule"
        echo "$BODY" | head -c 400; echo
    fi

    for bot in ClaudeBot PerplexityBot Google-Extended; do
        if echo "$BODY" | grep -q "$bot"; then
            pass "$URL contains $bot"
        else
            fail "$URL missing $bot"
        fi
    done

    # The marker line must mention THIS host
    if echo "$BODY" | grep -q "host=$host"; then
        pass "$URL marker correctly identifies host=$host (no leak)"
    else
        fail "$URL marker does NOT identify $host (POSSIBLE CACHE LEAK)"
        echo "$BODY" | grep 'host=' || true
    fi
done

finish_test
