<?php
require __DIR__ . '/fixtures/lead-reliability-bootstrap.php';

if (!defined('LP_FALLBACK_ENABLED')) { define('LP_FALLBACK_ENABLED', true); }
if (!defined('LP_FALLBACK_TEST_MODE')) { define('LP_FALLBACK_TEST_MODE', true); }
if (!defined('LP_FALLBACK_SITE_ID')) { define('LP_FALLBACK_SITE_ID', 'hybridautos-ae'); }
if (!defined('LP_FALLBACK_SIGNING_SECRET')) { define('LP_FALLBACK_SIGNING_SECRET', str_repeat('0123456789abcdef', 4)); }
if (!defined('LP_FALLBACK_STATUS_SECRET')) { define('LP_FALLBACK_STATUS_SECRET', str_repeat('abcdef0123456789', 4)); }

$module = __DIR__ . '/../mu-plugin/landing-config/includes/rest-fallback-token.php';
if (is_file($module)) { require_once $module; }

$failures = 0;
$assert = static function (bool $condition, string $message) use (&$failures): void {
    if (!$condition) { $failures++; fwrite(STDERR, "FAIL: {$message}\n"); }
};

$exists = function_exists('LandingConfig\\FallbackToken\\handle_token');
$assert($exists, 'fallback token endpoint exists');
if (!$exists) { echo "FAILURES: {$failures}\n"; exit(1); }

$secret = str_repeat('0123456789abcdef', 4);
$decoded = \LandingConfig\FallbackSecurity\decode_hmac_hex_secret($secret);
$assert(is_string($decoded) && strlen($decoded) === 32, 'lowercase 64-hex key decodes to exactly 32 bytes');
foreach (['', strtoupper($secret), substr($secret, 1), str_repeat('z', 64)] as $invalid) {
    $assert(\LandingConfig\FallbackSecurity\decode_hmac_hex_secret($invalid) === null, 'invalid HMAC key is rejected');
}
$vector = \LandingConfig\FallbackToken\sign_token_components(
    $secret, 1784190000, 1784233200, '0123456789abcdef0123456789abcdef', 'live'
);
$assert($vector === '4b587335b411b0f49bdee162682edb098865cdf84cecb236c8553e09fd1b1859', 'shared decoded-key HMAC vector matches');
$wrong = hash_hmac('sha256', "v1\nhybridautos-ae\n1784190000\n1784233200\n0123456789abcdef0123456789abcdef\nlive", $secret);
$assert($wrong !== $vector, 'using 64-byte hex text as key does not match');
$assert(!\LandingConfig\FallbackToken\secrets_are_valid($secret, $secret), 'equal signing and status keys are rejected');

lr_reset_state();
$GLOBALS['_lr_logged_in'] = false;
$GLOBALS['_lr_capabilities'] = [];
$visitor = new WP_REST_Request([], '', ['Origin' => 'https://hybridautos.test', 'Sec-Fetch-Site' => 'same-origin']);
$assert(\LandingConfig\FallbackToken\resolve_token_mode_for_flags($visitor, false, false) === null, 'both flags false is disabled');
$assert(\LandingConfig\FallbackToken\resolve_token_mode_for_flags($visitor, false, true) === null, 'test flag alone never opens public token');
$assert(\LandingConfig\FallbackToken\resolve_token_mode_for_flags($visitor, true, false) === 'live', 'live flag gives public live mode');
$assert(\LandingConfig\FallbackToken\resolve_token_mode_for_flags($visitor, true, true) === 'live', 'ordinary visitor stays live when both flags true');

$GLOBALS['_lr_logged_in'] = true;
$GLOBALS['_lr_capabilities'] = ['manage_options' => true];
$GLOBALS['_lr_valid_nonces'] = ['valid-rest-nonce' => 2];
$admin = new WP_REST_Request([], '', [
    'Origin' => 'https://hybridautos.test', 'Sec-Fetch-Site' => 'same-origin', 'X-WP-Nonce' => 'valid-rest-nonce',
]);
$assert(\LandingConfig\FallbackToken\resolve_token_mode_for_flags($admin, false, true) === 'test', 'authorized administrator receives test mode');
$bad_nonce = new WP_REST_Request([], '', ['X-WP-Nonce' => 'bad']);
$assert(\LandingConfig\FallbackToken\resolve_token_mode_for_flags($bad_nonce, false, true) === null, 'bad nonce with test-only flag is generic disabled');
$GLOBALS['_lr_capabilities'] = [];
$assert(\LandingConfig\FallbackToken\resolve_token_mode_for_flags($admin, false, true) === null, 'non-admin cannot use test mode');

$bundle = \LandingConfig\FallbackToken\build_token_bundle('live', 1784190000);
$assert(is_array($bundle) && array_keys($bundle) === ['ok','site_id','protocol_version','privacy_policy_version','mode','issued_at','expires_at','nonce','token'], 'bundle has exact ordered public contract');
$assert(($bundle['expires_at'] ?? 0) - ($bundle['issued_at'] ?? 0) === 43200, 'token lifetime is exactly 12 hours');
$assert(preg_match('/^[a-f0-9]{32}$/', (string)($bundle['nonce'] ?? '')) === 1, 'nonce is 16 random bytes in lowercase hex');
$expected_signature = \LandingConfig\FallbackToken\sign_token_components(
    $secret, (int)$bundle['issued_at'], (int)$bundle['expires_at'], (string)$bundle['nonce'], 'live'
);
$assert(str_ends_with((string)$bundle['token'], '.' . $expected_signature), 'bundle token uses decoded secret and canonical bytes');

lr_reset_state();
$_SERVER['REMOTE_ADDR'] = '198.51.100.77';
$GLOBALS['_lr_logged_in'] = false;
$GLOBALS['_lr_capabilities'] = [];
$cross = \LandingConfig\FallbackToken\handle_token(new WP_REST_Request([], '', [
    'Origin' => 'https://evil.invalid', 'Sec-Fetch-Site' => 'cross-site',
]));
$assert($cross->get_status() === 403, 'cross-origin request is rejected');
$assert(($cross->headers['cache-control'] ?? '') === 'no-store, private, max-age=0', 'error response is no-store');

$ok = \LandingConfig\FallbackToken\handle_token($visitor);
$assert($ok->get_status() === 200 && ($ok->get_data()['mode'] ?? '') === 'live', 'same-origin visitor receives live token');
$assert(($ok->headers['cache-control'] ?? '') === 'no-store, private, max-age=0', 'success response is no-store');
$assert(!array_key_exists('access-control-allow-origin', $ok->headers), 'endpoint emits no CORS wildcard');
$public_text = json_encode($ok->get_data()) . json_encode($ok->headers);
$assert(!str_contains((string)$public_text, LP_FALLBACK_SIGNING_SECRET), 'response contains no signing secret');

for ($i = 1; $i < 60; $i++) { \LandingConfig\FallbackToken\handle_token($visitor); }
$limited = \LandingConfig\FallbackToken\handle_token($visitor);
$assert($limited->get_status() === 429, '61st successful bundle in one hour is limited');
$stored = json_encode([$GLOBALS['_mock_transients'], $GLOBALS['wpdb']->query_log]);
$assert(!str_contains((string)$stored, '198.51.100.77'), 'rate state and lock contain no raw IP');

echo $failures === 0 ? "PASS: REST fallback token\n" : "FAILURES: {$failures}\n";
exit($failures === 0 ? 0 : 1);
