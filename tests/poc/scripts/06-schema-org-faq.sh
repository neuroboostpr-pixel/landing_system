#!/usr/bin/env bash
# 06-schema-org-faq.sh
# JSON-LD Schema.org (Organization + FAQPage) injected via mu-plugin appears in HTML.

set -euo pipefail
HERE="$(cd "$(dirname "$0")" && pwd)"
source "$HERE/../lib/env.sh"
source "$HERE/../lib/ssh.sh"
source "$HERE/../lib/assert.sh"

export CURRENT_TEST="06-schema-org-faq"
LOG="$LOGS_DIR/${CURRENT_TEST}.log"
exec > >(tee "$LOG") 2>&1
echo "=== $CURRENT_TEST started ==="

info "Step 1: deploy mu-plugin that emits Organization + FAQPage JSON-LD"

cat > /tmp/poc-schema.php <<'PHP'
<?php
/**
 * Plugin Name: POC Schema.org JSON-LD
 */
add_action('wp_head', function () {
    $host = parse_url(home_url(), PHP_URL_HOST);
    $org = [
        '@context' => 'https://schema.org',
        '@type'    => 'Organization',
        'name'     => get_bloginfo('name'),
        'url'      => home_url('/'),
        '@id'      => home_url('/#organization'),
    ];
    $faq = [
        '@context' => 'https://schema.org',
        '@type'    => 'FAQPage',
        'mainEntity' => [
            [
                '@type' => 'Question',
                'name'  => 'POC question for ' . $host,
                'acceptedAnswer' => [
                    '@type' => 'Answer',
                    'text'  => 'POC answer specific to ' . $host . ' (blog_id=' . get_current_blog_id() . ')',
                ],
            ],
        ],
    ];
    echo "\n<script type=\"application/ld+json\">" . wp_json_encode($org) . "</script>\n";
    echo "<script type=\"application/ld+json\">" . wp_json_encode($faq) . "</script>\n";
}, 5);
PHP

scp_to /tmp/poc-schema.php "/home/e/esper21/${TEST_DOMAIN}/public_html/wp-content/mu-plugins/poc-schema.php" > /dev/null 2>&1
pass "mu-plugin uploaded"

info "Step 2: each subsite emits Organization + FAQPage with its own host"

for host in ailexi.ru alpha.ailexi.ru bravo.ailexi.ru; do
    HTML=$(curl -s -L --max-time 15 "http://$host/?_=$RANDOM" || echo "")
    if echo "$HTML" | grep -qF '"@type":"Organization"'; then
        pass "$host: Organization JSON-LD present"
    else
        fail "$host: Organization JSON-LD missing"
    fi
    if echo "$HTML" | grep -qF '"@type":"FAQPage"'; then
        pass "$host: FAQPage JSON-LD present"
    else
        fail "$host: FAQPage JSON-LD missing"
    fi
    if echo "$HTML" | grep -qF "POC answer specific to $host"; then
        pass "$host: FAQ answer text matches host"
    else
        fail "$host: FAQ answer text wrong host (cache leak?)"
    fi
done

finish_test
