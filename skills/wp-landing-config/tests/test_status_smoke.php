<?php
require __DIR__ . '/fixtures/lead-reliability-bootstrap.php';

if (!defined('LP_FALLBACK_TEST_MODE')) { define('LP_FALLBACK_TEST_MODE', true); }
if (!defined('LP_FALLBACK_STATUS_SECRET')) { define('LP_FALLBACK_STATUS_SECRET', str_repeat('abcdef0123456789', 4)); }
if (!defined('LP_FALLBACK_SITE_ID')) { define('LP_FALLBACK_SITE_ID', 'hybridautos-ae'); }

require_once __DIR__ . '/../mu-plugin/landing-config/includes/db.php';
require_once __DIR__ . '/../mu-plugin/landing-config/includes/encryption.php';
require_once __DIR__ . '/../mu-plugin/landing-config/includes/helpers.php';
require_once __DIR__ . '/../mu-plugin/landing-config/includes/cascade.php';
require_once __DIR__ . '/../mu-plugin/landing-config/includes/integrations.php';
require_once __DIR__ . '/../mu-plugin/landing-config/includes/rest-fallback-token.php';
require_once __DIR__ . '/../mu-plugin/landing-config/includes/monitoring-alerts.php';
require_once __DIR__ . '/../mu-plugin/landing-config/includes/lead-delivery-worker.php';
require_once __DIR__ . '/../mu-plugin/landing-config/includes/rest-lead.php';
require_once __DIR__ . '/../mu-plugin/landing-config/includes/rest-health.php';
require_once __DIR__ . '/../mu-plugin/landing-config/includes/admin-monitoring.php';

$failures = 0;
$assert = static function (bool $condition, string $message) use (&$failures): void {
    if (!$condition) { $failures++; fwrite(STDERR, "FAIL: {$message}\n"); }
};

$required = [
    'LandingConfig\\MonitoringAdmin\\arm_status_smoke_at',
    'LandingConfig\\MonitoringAdmin\\consume_status_smoke_failure_at',
    'LandingConfig\\MonitoringAdmin\\handle_arm_status_smoke',
];
foreach ($required as $function) { $assert(function_exists($function), "status smoke function {$function} exists"); }
if ($failures > 0) { echo "FAILURES: {$failures}\n"; exit(1); }

$uuid = '66666666-6666-4666-8666-666666666666';
$other_uuid = '77777777-7777-4777-8777-777777777777';
$now = 1789000000;

// Only a privileged POST with the exact nonce can arm a UUID supplied in the
// request body. The redirect contains no UUID, nonce, or control query.
lr_reset_state();
$GLOBALS['_lr_logged_in'] = true;
$GLOBALS['_lr_capabilities'] = ['manage_options' => true];
$GLOBALS['_lr_current_user_id'] = 55;
$GLOBALS['_lr_nonce_actions'] = [\LandingConfig\MonitoringAdmin\STATUS_SMOKE_ACTION => true];
$_SERVER['REQUEST_METHOD'] = 'POST';
$_POST = ['smoke_submission_id' => $uuid];
\LandingConfig\MonitoringAdmin\handle_arm_status_smoke();
$assert(count($GLOBALS['_mock_transients']) === 1, 'authorized POST arms exactly one UUID-scoped transient');
$assert(max($GLOBALS['_mock_transient_ttls']) <= 180, 'armed smoke state expires within 180 seconds');
$redirect = $GLOBALS['_lr_redirects'][0] ?? [];
$assert(($redirect['status'] ?? 0) === 303 && !str_contains((string)($redirect['url'] ?? ''), $uuid),
    'admin redirect is clean and contains no UUID');
$state_serialized = json_encode([$GLOBALS['_mock_transients'], $GLOBALS['_mock_transient_ttls'], $GLOBALS['wpdb']->query_log, $GLOBALS['_lr_redirects']]);
$assert(!str_contains((string)$state_serialized, $uuid), 'transient keys, locks, and redirects never store raw UUID');

// Capability and nonce are independently mandatory.
lr_reset_state();
$GLOBALS['_lr_logged_in'] = true;
$GLOBALS['_lr_capabilities'] = [];
$GLOBALS['_lr_current_user_id'] = 55;
$GLOBALS['_lr_nonce_actions'] = [\LandingConfig\MonitoringAdmin\STATUS_SMOKE_ACTION => true];
$_SERVER['REQUEST_METHOD'] = 'POST';
$_POST = ['smoke_submission_id' => $uuid];
try { \LandingConfig\MonitoringAdmin\handle_arm_status_smoke(); } catch (RuntimeException $ignored) {}
$assert($GLOBALS['_mock_transients'] === [], 'non-admin cannot arm status smoke');

lr_reset_state();
$GLOBALS['_lr_logged_in'] = true;
$GLOBALS['_lr_capabilities'] = ['manage_options' => true];
$GLOBALS['_lr_current_user_id'] = 55;
$GLOBALS['_lr_nonce_actions'] = [];
$_SERVER['REQUEST_METHOD'] = 'POST';
$_POST = ['smoke_submission_id' => $uuid];
try { \LandingConfig\MonitoringAdmin\handle_arm_status_smoke(); } catch (RuntimeException $ignored) {}
$assert($GLOBALS['_mock_transients'] === [], 'bad nonce cannot arm status smoke');

lr_reset_state();
$GLOBALS['_lr_logged_in'] = true;
$GLOBALS['_lr_capabilities'] = ['manage_options' => true];
$GLOBALS['_lr_current_user_id'] = 55;
$GLOBALS['_lr_nonce_actions'] = [\LandingConfig\MonitoringAdmin\STATUS_SMOKE_ACTION => true];
$_SERVER['REQUEST_METHOD'] = 'POST';
$_POST = ['smoke_submission_id' => 'not-a-uuid'];
try { \LandingConfig\MonitoringAdmin\handle_arm_status_smoke(); } catch (RuntimeException $ignored) {}
$assert($GLOBALS['_mock_transients'] === [], 'invalid UUID cannot arm status smoke');

// Exact UUID: first valid signed status request is one generic 503, second is
// the normal missing result. A different UUID never consumes the state.
lr_reset_state();
$assert(\LandingConfig\MonitoringAdmin\arm_status_smoke_at($uuid, 180, $now), 'exact UUID arms at deterministic time');
$other_path = '/wp-json/landing/v1/submission-status/' . $other_uuid;
$other_signature = \LandingConfig\Health\signed_request_signature('GET', $other_path, $now, '');
lr_queue_row(0);
$other_request = new WP_REST_Request(['submission_id' => $other_uuid], '', [
    'X-LP-Site-Id' => 'hybridautos-ae', 'X-LP-Timestamp' => (string)$now, 'X-LP-Signature' => $other_signature,
]);
$other = \LandingConfig\Health\handle_submission_status_at($other_request, $now);
$assert($other->get_status() === 200 && ($other->get_data()['exists'] ?? true) === false,
    'different signed UUID follows normal missing path and does not consume arm');

$path = '/wp-json/landing/v1/submission-status/' . $uuid;
$signature = \LandingConfig\Health\signed_request_signature('GET', $path, $now, '');
$request = new WP_REST_Request(['submission_id' => $uuid], '', [
    'X-LP-Site-Id' => 'hybridautos-ae', 'X-LP-Timestamp' => (string)$now, 'X-LP-Signature' => $signature,
]);
$bad_request = new WP_REST_Request(['submission_id' => $uuid], '', [
    'X-LP-Site-Id' => 'hybridautos-ae', 'X-LP-Timestamp' => (string)$now, 'X-LP-Signature' => str_repeat('0', 64),
]);
$bad = \LandingConfig\Health\handle_submission_status_at($bad_request, $now);
$assert($bad->get_status() === 401, 'invalid HMAC cannot consume the armed exact UUID');
$first = \LandingConfig\Health\handle_submission_status_at($request, $now);
$assert($first->get_status() === 503
    && $first->get_data() === ['ok' => false, 'error' => 'temporarily_unavailable'],
    'first correctly signed exact status request gets generic ambiguous 503');
$assert(($first->headers['cache-control'] ?? '') === 'no-store, private, max-age=0', 'smoke 503 is strictly no-store');
lr_queue_row(0);
$second = \LandingConfig\Health\handle_submission_status_at($request, $now);
$assert($second->get_status() === 200 && ($second->get_data()['exists'] ?? true) === false,
    'second correctly signed exact status request returns normal missing');

// The explicit expiry timestamp is checked even if an object cache serves a
// stale transient, and an atomic named lock permits at most one 503.
lr_reset_state();
$assert(\LandingConfig\MonitoringAdmin\arm_status_smoke_at($uuid, 180, $now - 180), 'expiry-boundary fixture arms in the past');
$assert(!\LandingConfig\MonitoringAdmin\consume_status_smoke_failure_at($uuid, $now), 'arm is expired at exactly 180 seconds and cannot produce 503');
$assert(\LandingConfig\MonitoringAdmin\arm_status_smoke_at($uuid, 180, $now), 'parallel fixture arms');
$first_claim = \LandingConfig\MonitoringAdmin\consume_status_smoke_failure_at($uuid, $now);
$second_claim = \LandingConfig\MonitoringAdmin\consume_status_smoke_failure_at($uuid, $now);
$assert($first_claim === true && $second_claim === false, 'atomic one-shot state cannot produce two parallel 503 claims');
$assert(str_contains(implode("\n", $GLOBALS['wpdb']->query_log), 'GET_LOCK'), 'one-shot transition is protected by a named lock');

$admin_source = file_get_contents(__DIR__ . '/../mu-plugin/landing-config/includes/admin-monitoring.php');
$health_source = file_get_contents(__DIR__ . '/../mu-plugin/landing-config/includes/rest-health.php');
$assert(!str_contains((string)$admin_source, 'register_rest_route'), 'arming has no public REST control route');
foreach ([$uuid, '+971501111111', 'contact@example.com'] as $unsafe) {
    $assert(!str_contains((string)$admin_source . (string)$health_source, $unsafe), "smoke production source excludes {$unsafe}");
}

echo $failures === 0 ? "PASS: signed status live smoke\n" : "FAILURES: {$failures}\n";
exit($failures === 0 ? 0 : 1);
