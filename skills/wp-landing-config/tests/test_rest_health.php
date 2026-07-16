<?php
require __DIR__ . '/fixtures/lead-reliability-bootstrap.php';
require_once __DIR__ . '/../mu-plugin/landing-config/includes/db.php';
require_once __DIR__ . '/../mu-plugin/landing-config/includes/encryption.php';
require_once __DIR__ . '/../mu-plugin/landing-config/includes/helpers.php';
require_once __DIR__ . '/../mu-plugin/landing-config/includes/cascade.php';
require_once __DIR__ . '/../mu-plugin/landing-config/includes/integrations.php';
require_once __DIR__ . '/../mu-plugin/landing-config/includes/rest-fallback-token.php';
require_once __DIR__ . '/../mu-plugin/landing-config/includes/monitoring-alerts.php';
require_once __DIR__ . '/../mu-plugin/landing-config/includes/lead-delivery-worker.php';
require_once __DIR__ . '/../mu-plugin/landing-config/includes/rest-lead.php';

if (!defined('LP_FALLBACK_STATUS_SECRET')) { define('LP_FALLBACK_STATUS_SECRET', str_repeat('abcdef0123456789', 4)); }
if (!defined('LP_FALLBACK_SITE_ID')) { define('LP_FALLBACK_SITE_ID', 'hybridautos-ae'); }

$module = __DIR__ . '/../mu-plugin/landing-config/includes/rest-health.php';
if (is_file($module)) { require_once $module; }

$failures = 0;
$assert = static function (bool $condition, string $message) use (&$failures): void {
    if (!$condition) { $failures++; fwrite(STDERR, "FAIL: {$message}\n"); }
};

$exists = function_exists('LandingConfig\\Health\\build_health_payload');
$assert($exists, 'public and signed health module exists');
if (!$exists) { echo "FAILURES: {$failures}\n"; exit(1); }

function healthy_fixture(int $heartbeat): void {
    lr_reset_state();
    update_option('landing_monitor_enabled', '1');
    update_option(\LandingConfig\Monitoring\HEARTBEAT_OPTION, $heartbeat);
    update_option(\LandingConfig\Monitoring\RUN_STATUS_OPTION, 'ok');
    lr_queue_row(1);
}

$now = 1784190000;
healthy_fixture($now - 179);
$payload = \LandingConfig\Health\build_health_payload($now);
$assert(array_keys($payload) === ['ok','site_id','site','lead_endpoint','database','monitor_heartbeat','heartbeat_age_seconds','checked_at'], 'public health has exact no-PII keys');
$assert($payload['ok'] === true && $payload['monitor_heartbeat'] === 'ok' && $payload['heartbeat_age_seconds'] === 179, 'heartbeat age 179 is healthy');
healthy_fixture($now - 180);
$assert(\LandingConfig\Health\build_health_payload($now)['ok'] === true, 'heartbeat age 180 is healthy boundary');
healthy_fixture($now - 181);
$degraded = \LandingConfig\Health\build_health_payload($now);
$assert($degraded['ok'] === false && $degraded['monitor_heartbeat'] === 'degraded', 'heartbeat age 181 is degraded');

lr_reset_state();
update_option('landing_monitor_enabled', '1');
update_option(\LandingConfig\Monitoring\HEARTBEAT_OPTION, $now);
update_option(\LandingConfig\Monitoring\RUN_STATUS_OPTION, 'ok');
lr_queue_row(0);
$db_down = \LandingConfig\Health\build_health_payload($now);
$assert($db_down['database'] === 'failed' && $db_down['ok'] === false, 'database failure degrades health');

healthy_fixture(time() - 42);
$health_response = \LandingConfig\Health\handle_health(new WP_REST_Request());
$assert($health_response->get_status() === 200, 'healthy public endpoint is HTTP 200');
$assert(($health_response->headers['cache-control'] ?? '') === 'no-store, private, max-age=0', 'public health is no-store');
$health_text = json_encode($health_response->get_data());
foreach (['phone','email','lead_id','token','secret'] as $forbidden) {
    $assert(!str_contains(strtolower((string)$health_text), $forbidden), "public health excludes {$forbidden}");
}

$uuid = '11111111-1111-4111-8111-111111111111';
$path = '/wp-json/landing/v1/submission-status/' . $uuid;
$status_signature = \LandingConfig\Health\signed_request_signature('GET', $path, $now, '');
$assert($status_signature === 'a7b21d74d5ddb84897ddc629999fd334045e90f28f56175e32e8892669b0a52c', 'submission status matches shared decoded-key HMAC vector');

lr_reset_state();
lr_queue_row(1);
$request = new WP_REST_Request(['submission_id' => $uuid], '', [
    'X-LP-Site-Id' => 'hybridautos-ae', 'X-LP-Timestamp' => (string)$now, 'X-LP-Signature' => $status_signature,
]);
$status = \LandingConfig\Health\handle_submission_status_at($request, $now);
$assert($status->get_status() === 200, 'valid signed submission lookup succeeds');
$assert($status->get_data() === ['ok' => true, 'site_id' => 'hybridautos-ae', 'submission_id' => $uuid, 'exists' => true], 'submission lookup exposes only exact existence contract');
$assert(($status->headers['cache-control'] ?? '') === 'no-store, private, max-age=0', 'signed lookup is no-store');

$bad = new WP_REST_Request(['submission_id' => $uuid], '', [
    'X-LP-Site-Id' => 'hybridautos-ae', 'X-LP-Timestamp' => (string)$now, 'X-LP-Signature' => str_repeat('0', 64),
]);
$bad_response = \LandingConfig\Health\handle_submission_status_at($bad, $now);
$assert($bad_response->get_status() === 401 && $bad_response->get_data() === ['ok' => false, 'error' => 'unauthorized'], 'bad signature reveals no existence');
$expired = new WP_REST_Request(['submission_id' => $uuid], '', [
    'X-LP-Site-Id' => 'hybridautos-ae', 'X-LP-Timestamp' => (string)($now - 301),
    'X-LP-Signature' => \LandingConfig\Health\signed_request_signature('GET', $path, $now - 301, ''),
]);
$assert(\LandingConfig\Health\handle_submission_status_at($expired, $now)->get_status() === 401, '301-second-old signature is rejected');
$invalid_uuid = new WP_REST_Request(['submission_id' => 'bad'], '', []);
$assert(\LandingConfig\Health\handle_submission_status_at($invalid_uuid, $now)->get_status() === 400, 'invalid UUID is rejected before lookup');

// The state machine is tested independently from HTTP clock skew: two full
// fail/fail/recovery episodes must each alert once and recover once.
lr_reset_state();
update_option('landing_monitor_enabled', '1');
$r1 = \LandingConfig\Monitoring\apply_external_health_observation('failed', 100, 1000);
$r2 = \LandingConfig\Monitoring\apply_external_health_observation('failed', 101, 1300);
$dup = \LandingConfig\Monitoring\apply_external_health_observation('failed', 101, 1301);
$r3 = \LandingConfig\Monitoring\apply_external_health_observation('ok', 102, 1600);
$r4 = \LandingConfig\Monitoring\apply_external_health_observation('failed', 200, 2000);
$r5 = \LandingConfig\Monitoring\apply_external_health_observation('failed', 201, 2300);
$r6 = \LandingConfig\Monitoring\apply_external_health_observation('ok', 202, 2600);
$old = \LandingConfig\Monitoring\apply_external_health_observation('failed', 150, 2700);
$external = array_values(array_filter(lr_rows(\LandingConfig\DB\get_monitor_alerts_table_name()), static fn($row) => in_array(($row['incident_kind'] ?? ''), ['external_outage','external_recovery'], true)));
$assert(($r1['duplicate'] ?? true) === false && ($r2['outage'] ?? false) === true, 'two adjacent failures open one outage');
$assert(($dup['duplicate'] ?? false) === true, 'same slot replay is accepted as duplicate');
$assert(count($external) === 4, 'two full outage cycles create exactly four queued messages');
$assert(($old['duplicate'] ?? false) === true && count($external) === 4, 'delayed lower slot cannot reopen recovered outage');

// Stale external monitoring alerts strictly after 900 seconds and recovers on
// the first newer valid observation.
lr_reset_state();
update_option('landing_monitor_enabled', '1');
\LandingConfig\Monitoring\note_monitoring_enabled(1000);
$assert((\LandingConfig\Monitoring\check_external_monitor_stale(1899)['stale'] ?? true) === false, '899 seconds is not stale');
$assert((\LandingConfig\Monitoring\check_external_monitor_stale(1900)['stale'] ?? true) === false, '900 seconds is not stale boundary');
$stale = \LandingConfig\Monitoring\check_external_monitor_stale(1901);
$assert(($stale['stale'] ?? false) === true, '901 seconds creates external monitor stale incident');
$repeat = \LandingConfig\Monitoring\check_external_monitor_stale(2000);
$assert(($repeat['created'] ?? true) === false, 'stale episode repeats deduplicate');
\LandingConfig\Monitoring\apply_external_health_observation('ok', 7, 2100);
$monitor_kinds = array_column(lr_rows(\LandingConfig\DB\get_monitor_alerts_table_name()), 'incident_kind');
$assert(in_array('external_monitor_recovery', $monitor_kinds, true), 'first valid observation closes stale episode');

// Exact signed external observation HTTP contract.
lr_reset_state();
update_option('landing_monitor_enabled', '1');
$http_now = time();
$slot = intdiv($http_now, 300);
$body = json_encode(['v' => 1, 'site_id' => 'hybridautos-ae', 'target' => 'redis', 'status' => 'failed', 'checked_at_slot' => $slot], JSON_UNESCAPED_SLASHES);
$observation_path = '/wp-json/landing/v1/external-health-observation';
$observation_signature = \LandingConfig\Health\signed_request_signature('POST', $observation_path, $http_now, hash('sha256', $body));
$observation_request = new WP_REST_Request([], $body, [
    'X-LP-Site-Id' => 'hybridautos-ae', 'X-LP-Timestamp' => (string)$http_now, 'X-LP-Signature' => $observation_signature,
]);
$observation = \LandingConfig\Health\handle_external_health_observation_at($observation_request, $http_now);
$assert($observation->get_status() === 200, 'valid signed external observation succeeds');
$assert($observation->get_data() === ['ok' => true, 'site_id' => 'hybridautos-ae', 'accepted' => true, 'duplicate' => false], 'external observation returns exact no-state contract');
$assert(($observation->headers['cache-control'] ?? '') === 'no-store, private, max-age=0', 'external observation is no-store');

$serialized = json_encode([lr_rows(\LandingConfig\DB\get_monitor_alerts_table_name()), get_option(\LandingConfig\Monitoring\EXTERNAL_HEALTH_OPTION, [])]);
foreach (['+971501111111','contact@example.com','provider body','TEST-BOT-TOKEN'] as $unsafe) {
    $assert(!str_contains((string)$serialized, $unsafe), "health state excludes {$unsafe}");
}

echo $failures === 0 ? "PASS: REST health and signed reconciliation\n" : "FAILURES: {$failures}\n";
exit($failures === 0 ? 0 : 1);
