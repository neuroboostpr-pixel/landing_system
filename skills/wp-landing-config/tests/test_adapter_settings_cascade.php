<?php
require_once __DIR__ . '/fixtures/wp-bootstrap.php';
require_once __DIR__ . '/../mu-plugin/landing-config/includes/cascade.php';
require_once __DIR__ . '/../mu-plugin/landing-config/includes/encryption.php';
require_once __DIR__ . '/../mu-plugin/landing-config/includes/integrations.php';
require_once __DIR__ . '/../mu-plugin/landing-config/adapters/AdapterInterface.php';
require_once __DIR__ . '/../mu-plugin/landing-config/adapters/TelegramAdapter.php';

use LandingConfig\Adapters\TelegramAdapter;
use function LandingConfig\Integrations\save_integration;

$failures = 0; $tests = 0;
function assert_test($c, $m) { global $failures, $tests; $tests++; if (!$c) { echo "FAIL: $m\n"; $failures++; } }

function reset_ad() {
    $GLOBALS['_mock_posts'] = [];
    $GLOBALS['_mock_post_meta'] = [];
    $GLOBALS['_mock_next_post_id'] = 1;
    $GLOBALS['_mock_current_blog_id'] = 1;
    putenv('WP_LANDING_CONFIG_KEY=' . str_repeat('a', 32));
}

// T1: field_definitions returns schema with encrypt flag
$def = TelegramAdapter::field_definitions();
assert_test(isset($def['bot_token']['encrypt']) && $def['bot_token']['encrypt'] === true, 'T1 bot_token marked encrypt');

// T2: settings() reads via cascade
reset_ad();
save_integration('telegram', 'telegram', '', ['bot_token' => 'NETBOT', 'chat_id' => '-100'], true, 1, ['bot_token']);
$s = TelegramAdapter::settings();
assert_test($s['bot_token'] === 'NETBOT', 'T2 network settings via cascade');

$GLOBALS['_mock_current_blog_id'] = 2;
save_integration('telegram', 'telegram', '', ['bot_token' => 'SITEBOT', 'chat_id' => '-200'], false, 2, ['bot_token']);
$s = TelegramAdapter::settings();
assert_test($s['bot_token'] === 'SITEBOT', 'T2b site override via cascade');

// T3: legacy wp_options fallback when no CPT row exists
reset_ad();
\update_option('landing_integration_telegram_chat_id', '-9999');
$s = TelegramAdapter::settings();
assert_test($s['chat_id'] === '-9999', 'T3 legacy wp_options fallback reads per-field key');

echo "$tests tests, $failures failures\n";
exit($failures > 0 ? 1 : 0);
