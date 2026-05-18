#!/usr/bin/env bash
# 01-lazy-blocks-network.sh
# Verifies: a Lazy Blocks definition registered via a network-wide mu-plugin
# is visible in WP_Block_Type_Registry on every subsite of the network.
#
# Critical naming convention (discovered during POC):
#   - block slug MUST start with 'lazyblock/' (Lazy Blocks hardcodes namespace)
#   - registration must use add_action('init', ..., priority < 20)

set -euo pipefail
HERE="$(cd "$(dirname "$0")" && pwd)"
source "$HERE/../lib/env.sh"
source "$HERE/../lib/ssh.sh"
source "$HERE/../lib/assert.sh"

export CURRENT_TEST="01-lazy-blocks-network"
LOG="$LOGS_DIR/${CURRENT_TEST}.log"
exec > >(tee "$LOG") 2>&1
echo "=== $CURRENT_TEST started ==="

info "Step 1: deploy mu-plugin with Lazy Blocks definition"

cat > /tmp/poc-block.php <<'PHP'
<?php
/**
 * Plugin Name: POC Lazy Block (network)
 */
add_action('init', function () {
    if (!function_exists('lazyblocks')) return;

    lazyblocks()->add_block([
        'id'          => 1001,
        'title'       => 'POC Hero',
        'icon'        => 'star-filled',
        'category'    => 'common',
        'slug'        => 'lazyblock/poc-hero',
        'description' => 'POC test block',
        'keywords'    => ['poc', 'hero'],
        'code'        => [
            'output_method' => 'php',
            'frontend_callback' => function ($attributes) {
                $h = esc_html($attributes['headline'] ?? 'Hello');
                echo '<section class="lazyblock-poc-hero" data-poc="1"><h1>'. $h .'</h1></section>';
            },
        ],
        'controls'    => [
            [
                'name'    => 'headline',
                'label'   => 'Headline',
                'type'    => 'text',
                'default' => 'Hello from POC',
            ],
        ],
    ]);
}, 5);

// (render is supplied via code.frontend_callback above, no separate filter needed)
PHP

ssh_run "mkdir -p ~/${TEST_DOMAIN}/public_html/wp-content/mu-plugins"
scp_to /tmp/poc-block.php "/home/e/esper21/${TEST_DOMAIN}/public_html/wp-content/mu-plugins/poc-block.php" > /dev/null 2>&1
pass "mu-plugin uploaded"

info "Step 2: clear caches"
for url in "http://ailexi.ru" "http://alpha.ailexi.ru" "http://bravo.ailexi.ru"; do
    ssh_run "cd ~/${TEST_DOMAIN}/public_html && $REMOTE_WP --url=$url transient delete --all 2>&1 | tail -1; $REMOTE_WP --url=$url cache flush 2>&1 | tail -1" > /dev/null
done
pass "caches flushed"

info "Step 3: verify lazyblock/poc-hero is in WP_Block_Type_Registry on each site"
for url in "http://ailexi.ru" "http://alpha.ailexi.ru" "http://bravo.ailexi.ru"; do
    R=$(ssh_run "cd ~/${TEST_DOMAIN}/public_html && $REMOTE_WP --url=$url eval 'echo (WP_Block_Type_Registry::get_instance()->is_registered(\"lazyblock/poc-hero\") ? \"YES\" : \"NO\");' 2>&1" | tail -1)
    if [ "$R" = "YES" ]; then
        pass "Site $url: lazyblock/poc-hero is registered"
    else
        fail "Site $url: lazyblock/poc-hero NOT registered (got: $R)"
    fi
done

info "Step 4: insert page with the block on each site, render front, look for marker"

BLOCK_TEMPLATE='<!-- wp:lazyblock/poc-hero {"headline":"Hello PLACE"} /-->'

for pair in "ailexi.ru:1" "alpha.ailexi.ru:2" "bravo.ailexi.ru:3"; do
    host="${pair%:*}"; bid="${pair##*:}"
    title="POC-$bid"
    content="${BLOCK_TEMPLATE/PLACE/$title}"

    # Remove existing pages (clean slate)
    ssh_run "cd ~/${TEST_DOMAIN}/public_html && $REMOTE_WP --url=http://$host post list --post_type=page --field=ID 2>/dev/null | xargs -r -n1 $REMOTE_WP --url=http://$host post delete --force 2>&1" > /dev/null

    POST_ID=$(ssh_run "cd ~/${TEST_DOMAIN}/public_html && $REMOTE_WP --url=http://$host post create --post_type=page --post_status=publish --post_title='$title' --post_content='$content' --porcelain 2>&1" | tail -1)

    if echo "$POST_ID" | grep -qE '^[0-9]+$'; then
        info "$host: page id=$POST_ID created"
        ssh_run "cd ~/${TEST_DOMAIN}/public_html && $REMOTE_WP --url=http://$host option update show_on_front page 2>&1" > /dev/null
        ssh_run "cd ~/${TEST_DOMAIN}/public_html && $REMOTE_WP --url=http://$host option update page_on_front $POST_ID 2>&1" > /dev/null
    else
        fail "$host: failed to create page: $POST_ID"
        continue
    fi

    sleep 3
    HTML=$(curl -s -L --max-time 20 "http://$host/?_=$RANDOM" || echo "")
    if echo "$HTML" | grep -q 'lazyblock-poc-hero'; then
        pass "GET http://$host/ contains 'lazyblock-poc-hero' marker (rendered)"
    else
        fail "GET http://$host/ does NOT contain 'lazyblock-poc-hero' (HTML head below)"
        echo "$HTML" | head -c 700
        echo
    fi
done

finish_test
