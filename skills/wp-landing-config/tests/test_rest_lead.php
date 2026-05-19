<?php
require_once __DIR__ . '/fixtures/wp-bootstrap.php';
require_once __DIR__ . '/../mu-plugin/landing-config/includes/db.php';
require_once __DIR__ . '/../mu-plugin/landing-config/includes/helpers.php';
require_once __DIR__ . '/../mu-plugin/landing-config/includes/rest-lead.php';

use function LandingConfig\REST\handle_lead;

$failures = 0;
$tests = 0;

function assert_test($condition, $message) {
    global $failures, $tests;
    $tests++;
    if (!$condition) {
        echo "FAIL: $message\n";
        $failures++;
    }
}

// Reset rate-limit before each batch
function reset_state() {
    $GLOBALS['_mock_inserted_leads'] = [];
    $GLOBALS['_mock_mail_sent'] = [];
    $GLOBALS['_mock_transients'] = [];
    $GLOBALS['_mock_actions_fired'] = [];
    $_SERVER['REMOTE_ADDR'] = '203.0.113.1';
    $_SERVER['HTTP_USER_AGENT'] = 'test-agent';
}

// Test 1: missing phone+email → 400
reset_state();
$req = new WP_REST_Request(['name' => 'Bob', 'phone' => '', 'email' => '']);
$resp = handle_lead($req);
assert_test(
    $resp->get_status() === 400,
    "missing phone+email returns 400 (got: " . $resp->get_status() . ")"
);
assert_test(
    count($GLOBALS['_mock_inserted_leads']) === 0,
    "no DB insert when validation fails"
);

// Test 2: honeypot field filled → 400 (silently rejects bots)
reset_state();
$req = new WP_REST_Request(['name' => 'Bob', 'phone' => '+71111111111', 'website' => 'spam-bot-trap']);
$resp = handle_lead($req);
assert_test(
    $resp->get_status() === 400,
    "honeypot 'website' field filled returns 400"
);

// Test 3: valid request inserts lead
reset_state();
set_mock_current_blog_id(1);
$req = new WP_REST_Request([
    'name' => 'Alice',
    'phone' => '+79991234567',
    'email' => 'alice@example.com',
    'message' => 'Test message',
    'source_block' => 'hero',
    'utm_source' => 'google',
]);
$resp = handle_lead($req);
assert_test(
    $resp->get_status() === 200,
    "valid request returns 200 (got: " . $resp->get_status() . ")"
);
assert_test(
    count($GLOBALS['_mock_inserted_leads']) === 1,
    "exactly 1 DB insert"
);
$inserted = $GLOBALS['_mock_inserted_leads'][0];
assert_test(
    $inserted['data']['name'] === 'Alice' &&
    $inserted['data']['phone'] === '+79991234567' &&
    $inserted['data']['email'] === 'alice@example.com',
    "inserted data has name/phone/email"
);
assert_test(
    $inserted['data']['source_block'] === 'hero' &&
    $inserted['data']['utm_source'] === 'google',
    "inserted data has source_block + utm_source"
);
assert_test(
    $resp->get_data()['ok'] === true && isset($resp->get_data()['lead_id']),
    "response includes ok=true + lead_id"
);

// Test 4: email-fallback sent on successful insert
assert_test(
    count($GLOBALS['_mock_mail_sent']) === 1,
    "wp_mail called once on success"
);
$mail = $GLOBALS['_mock_mail_sent'][0];
assert_test(
    $mail['to'] === 'admin@example.com',
    "mail sent to admin_email"
);

// Test 4b: landing_config_lead_received action fired
$fired_hooks = array_column($GLOBALS['_mock_actions_fired'], 'hook');
assert_test(
    in_array('landing_config_lead_received', $fired_hooks, true),
    "action 'landing_config_lead_received' fired on success"
);

// Test 5: writes to per-blog table
reset_state();
set_mock_current_blog_id(2);
$req = new WP_REST_Request([
    'name' => 'BlogTwo', 'phone' => '+79993334444', 'email' => 'b2@x.com',
]);
handle_lead($req);
assert_test(
    $GLOBALS['_mock_inserted_leads'][0]['table'] === 'wp_2_landing_leads',
    "insert goes to wp_<bid>_landing_leads (got: " . $GLOBALS['_mock_inserted_leads'][0]['table'] . ")"
);

// Test 6: rate limit — 11th request from same IP within window returns 429
reset_state();
set_mock_current_blog_id(1);
for ($i = 0; $i < 10; $i++) {
    $req = new WP_REST_Request(['name' => "User$i", 'phone' => '+71000000' . sprintf('%03d', $i)]);
    $resp = handle_lead($req);
    if ($resp->get_status() !== 200) {
        echo "Unexpected status on request $i: " . $resp->get_status() . "\n";
    }
}
$req = new WP_REST_Request(['name' => 'Eleventh', 'phone' => '+71000000011']);
$resp = handle_lead($req);
assert_test(
    $resp->get_status() === 429,
    "11th request from same IP within hour returns 429 (got: " . $resp->get_status() . ")"
);

// Test 7: rate limit is per-IP (different IP not blocked)
$_SERVER['REMOTE_ADDR'] = '198.51.100.2';
$req = new WP_REST_Request(['name' => 'OtherIP', 'phone' => '+79995556677']);
$resp = handle_lead($req);
assert_test(
    $resp->get_status() === 200,
    "different IP not affected by first IP's rate limit (got: " . $resp->get_status() . ")"
);

echo "\n$tests tests, $failures failures\n";
exit($failures > 0 ? 1 : 0);
