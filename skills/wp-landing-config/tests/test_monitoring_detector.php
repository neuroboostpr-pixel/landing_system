<?php
require __DIR__ . '/fixtures/lead-reliability-bootstrap.php';
require_once __DIR__ . '/../mu-plugin/landing-config/includes/db.php';
require_once __DIR__ . '/../mu-plugin/landing-config/includes/rest-fallback-token.php';
require_once __DIR__ . '/../mu-plugin/landing-config/includes/monitoring-alerts.php';

if (!defined('LP_FALLBACK_STATUS_URL')) { define('LP_FALLBACK_STATUS_URL', 'https://fallback.invalid'); }
if (!defined('LP_FALLBACK_STATUS_SECRET')) { define('LP_FALLBACK_STATUS_SECRET', str_repeat('abcdef0123456789', 4)); }
if (!defined('LP_FALLBACK_SITE_ID')) { define('LP_FALLBACK_SITE_ID', 'hybridautos-ae'); }

$failures = 0;
$assert = static function (bool $condition, string $message) use (&$failures): void {
    if (!$condition) { $failures++; fwrite(STDERR, "FAIL: {$message}\n"); }
};

$exists = function_exists('LandingConfig\\Monitoring\\classify_timeline');
$assert($exists, 'missing-lead timeline detector exists');
if (!$exists) { echo "FAILURES: {$failures}\n"; exit(1); }

$assert(\LandingConfig\Monitoring\classify_timeline([
    ['event_sequence' => 1, 'event_name' => 'form_started', 'event_detail' => ''],
]) === null, 'form_started alone is ordinary abandonment');
$assert(\LandingConfig\Monitoring\classify_timeline([
    ['event_sequence' => 1, 'event_name' => 'validation_failed', 'event_detail' => 'phone'],
]) === null, 'validation failure without request is not an incident');
$stall = \LandingConfig\Monitoring\classify_timeline([
    ['event_sequence' => 1, 'event_name' => 'submit_attempt', 'event_detail' => ''],
]);
$assert(($stall['kind'] ?? '') === 'javascript_stall' && ($stall['severity'] ?? '') === 'warning', 'submit without request is javascript stall');
$missing = \LandingConfig\Monitoring\classify_timeline([
    ['event_sequence' => 1, 'event_name' => 'submit_attempt', 'event_detail' => ''],
    ['event_sequence' => 2, 'event_name' => 'request_started', 'event_detail' => ''],
    ['event_sequence' => 3, 'event_name' => 'request_failed', 'event_detail' => 'network'],
]);
$assert(($missing['kind'] ?? '') === 'missing_lead' && ($missing['safe_status'] ?? '') === 'request_failed', 'request without lead is critical missing lead');

$uuid = '11111111-1111-4111-8111-111111111111';
$path = '/api/v1/receipts/' . $uuid;
$signature = \LandingConfig\Monitoring\receipt_status_signature($path, 1784190000);
$assert($signature === 'b7f697a76e4fc52b194c284dd14b9e9ae54f2a1879b2e81b356825f126da51c5', 'receipt status uses shared decoded-key HMAC vector');
$cross_status_path = '/api/v1/receipts/d9428888-122b-4b3e-a105-4d4f0a13262f';
$cross_status = function_exists('LandingConfig\\Monitoring\\sign_receipt_status_components')
    ? \LandingConfig\Monitoring\sign_receipt_status_components(
        str_repeat('0123456789abcdef', 4), $cross_status_path, 1789000000
    )
    : null;
$assert($cross_status === 'a954e8f42b2b873dd99489c98989ced365b860ca983ed17779dce014d86ed172',
    'literal cross-runtime receipt status vector matches byte-for-byte');

lr_reset_state();
update_option('landing_monitor_enabled', '1');
lr_set_http(['response' => ['code' => 200], 'body' => json_encode([
    'ok' => true, 'submission_id' => $uuid, 'exists' => true, 'stored' => true, 'delivery_state' => 'pending',
]), 'headers' => []]);
$receipt = \LandingConfig\Monitoring\fetch_external_receipt_status($uuid, 1784190000);
$assert($receipt === ['lookup' => 'ok', 'exists' => true, 'stored' => true, 'delivery_state' => 'pending'], 'valid receipt is normalized to safe exact fields');
$request = $GLOBALS['_lr_http_requests'][0] ?? [];
$assert(($request['method'] ?? '') === 'GET' && ($request['url'] ?? '') === 'https://fallback.invalid' . $path, 'receipt lookup uses exact canonical URL');
$assert(($request['args']['timeout'] ?? 0) === 4 && ($request['args']['redirection'] ?? -1) === 0, 'receipt lookup has strict timeout and no redirects');
$headers = $request['args']['headers'] ?? [];
$assert(($headers['X-LP-Signature'] ?? '') === $signature, 'receipt lookup sends exact HMAC');

lr_set_http(['response' => ['code' => 200], 'body' => '{"ok":true,"submission_id":"wrong","exists":true,"stored":true,"delivery_state":"pending"}', 'headers' => []]);
$malformed = \LandingConfig\Monitoring\fetch_external_receipt_status($uuid, 1784190000);
$assert(($malformed['lookup'] ?? '') === 'unknown' && ($malformed['stored'] ?? true) === false, 'mismatched/malformed receipt never suppresses alert');

function detector_reset(): void {
    lr_reset_state();
    update_option('landing_monitor_enabled', '1');
}
function detector_incidents(): array {
    return lr_rows(\LandingConfig\DB\get_monitor_alerts_table_name());
}

detector_reset();
$classification = ['kind' => 'missing_lead', 'severity' => 'critical', 'safe_status' => 'request_failed', 'safe_category' => 'missing_wordpress_lead'];
\LandingConfig\Monitoring\apply_receipt_lifecycle($uuid, $classification,
    ['lookup' => 'ok', 'exists' => true, 'stored' => true, 'delivery_state' => 'pending'],
    false, 1784190000, null);
$rows = detector_incidents();
$watch = array_values(array_filter($rows, static fn($row) => ($row['incident_kind'] ?? '') === 'fallback_receipt_watch'));
$missing_rows = array_values(array_filter($rows, static fn($row) => ($row['incident_kind'] ?? '') === 'missing_lead'));
$assert(count($watch) === 1 && ($watch[0]['telegram_status'] ?? '') === 'watching', 'pending stored receipt creates only a non-Telegram watch');
$assert(strtotime((string)($watch[0]['due_at'] ?? '')) === 1784190300, 'pending watch is due again in five minutes');
$assert($missing_rows === [], 'stored pending receipt suppresses immediate missing alert but is non-terminal');

detector_reset();
\LandingConfig\Monitoring\apply_receipt_lifecycle($uuid, $classification,
    ['lookup' => 'ok', 'exists' => true, 'stored' => true, 'delivery_state' => 'pending'],
    false, 1784190000, 1784189401);
$stuck = array_values(array_filter(detector_incidents(), static fn($row) => ($row['incident_kind'] ?? '') === 'fallback_delivery_stuck'));
$assert($stuck === [], 'pending at 9:59 does not alert stuck delivery');
\LandingConfig\Monitoring\apply_receipt_lifecycle($uuid, $classification,
    ['lookup' => 'ok', 'exists' => true, 'stored' => true, 'delivery_state' => 'pending'],
    false, 1784190000, 1784189400);
$stuck = array_values(array_filter(detector_incidents(), static fn($row) => ($row['incident_kind'] ?? '') === 'fallback_delivery_stuck'));
$assert(count($stuck) === 1, 'pending at 10:00 creates one stuck fallback alert');

detector_reset();
\LandingConfig\Monitoring\apply_receipt_lifecycle($uuid, $classification,
    ['lookup' => 'ok', 'exists' => true, 'stored' => true, 'delivery_state' => 'unknown'],
    false, 1784190000, 1784189900);
$uncertain = array_values(array_filter(detector_incidents(), static fn($row) => ($row['incident_kind'] ?? '') === 'fallback_delivery_uncertain'));
$assert(count($uncertain) === 1, 'unknown stored receipt immediately alerts uncertainty');
$assert(count(array_filter(detector_incidents(), static fn($row) => ($row['incident_kind'] ?? '') === 'fallback_receipt_watch')) === 1, 'unknown stored receipt keeps recoverable watch');

\LandingConfig\Monitoring\apply_receipt_lifecycle($uuid, $classification,
    ['lookup' => 'ok', 'exists' => true, 'stored' => true, 'delivery_state' => 'delivered'],
    false, 1784190060, 1784189900);
$open = array_values(array_filter(detector_incidents(), static fn($row) => empty($row['resolved_at'])));
$assert($open === [], 'delivered stored receipt terminally resolves watch and alerts');

detector_reset();
\LandingConfig\Monitoring\apply_receipt_lifecycle($uuid, $classification,
    ['lookup' => 'ok', 'exists' => false, 'stored' => false, 'delivery_state' => 'expired'],
    false, 1784190000, null);
$expired_missing = array_values(array_filter(detector_incidents(), static fn($row) => ($row['incident_kind'] ?? '') === 'missing_lead' && empty($row['resolved_at'])));
$assert(count($expired_missing) === 1, 'expired unstored receipt creates/reopens missing lead');

\LandingConfig\Monitoring\apply_receipt_lifecycle($uuid, $classification,
    ['lookup' => 'unknown', 'exists' => false, 'stored' => false, 'delivery_state' => null],
    true, 1784190060, null);
$open = array_values(array_filter(detector_incidents(), static fn($row) => empty($row['resolved_at'])));
$assert($open === [], 'matching WordPress lead is terminal wordpress_lead_saved recovery');

// Scanner enforces the exact grace boundary independently of SQL.
detector_reset();
lr_queue_results([['submission_id' => $uuid, 'last_event_at' => '2026-07-15 11:55:01', 'watch_started_at' => null, 'wordpress_exists' => 0]]);
$at_299 = \LandingConfig\Monitoring\run_missing_lead_scan(100, strtotime('2026-07-15 12:00:00 UTC'));
$assert(($at_299['classified'] ?? -1) === 0, 'age 299 seconds is not classified');

detector_reset();
lr_queue_results([['submission_id' => $uuid, 'last_event_at' => '2026-07-15 11:55:00', 'watch_started_at' => null, 'wordpress_exists' => 0]]);
lr_queue_results([
    ['id' => 1, 'event_sequence' => 1, 'event_name' => 'submit_attempt', 'event_detail' => ''],
    ['id' => 2, 'event_sequence' => 2, 'event_name' => 'request_started', 'event_detail' => ''],
    ['id' => 3, 'event_sequence' => 3, 'event_name' => 'request_failed', 'event_detail' => 'http_4xx'],
]);
lr_set_http(['response' => ['code' => 404], 'body' => '', 'headers' => []]);
$at_300 = \LandingConfig\Monitoring\run_missing_lead_scan(100, strtotime('2026-07-15 12:00:00 UTC'));
$assert(($at_300['classified'] ?? 0) === 1, 'age exactly 300 seconds is classified');
$missing_alerts = array_values(array_filter(detector_incidents(), static fn($row) => ($row['incident_kind'] ?? '') === 'missing_lead'));
$assert(count($missing_alerts) === 1, 'missing external receipt leaves one safe missing alert');
$assert(($missing_alerts[0]['safe_status'] ?? '') === 'request_failed',
    'failed protected request, including rate limit, remains visible to the missing-lead monitor');

$serialized = json_encode([detector_incidents(), $GLOBALS['_lr_http_requests'], $GLOBALS['wpdb']->query_log]);
foreach (['+971501111111','contact@example.com','provider raw body'] as $pii) {
    $assert(!str_contains((string)$serialized, $pii), "detector state excludes {$pii}");
}

echo $failures === 0 ? "PASS: monitoring detector\n" : "FAILURES: {$failures}\n";
exit($failures === 0 ? 0 : 1);
