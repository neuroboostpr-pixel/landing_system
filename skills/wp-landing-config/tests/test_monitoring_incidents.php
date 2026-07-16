<?php
require __DIR__ . '/fixtures/lead-reliability-bootstrap.php';
require_once __DIR__ . '/../mu-plugin/landing-config/includes/db.php';
require_once __DIR__ . '/../mu-plugin/landing-config/includes/encryption.php';
require_once __DIR__ . '/../mu-plugin/landing-config/includes/helpers.php';
require_once __DIR__ . '/../mu-plugin/landing-config/includes/cascade.php';
require_once __DIR__ . '/../mu-plugin/landing-config/includes/integrations.php';
foreach (glob(__DIR__ . '/../mu-plugin/landing-config/adapters/*.php') as $adapter_file) {
    if (str_ends_with($adapter_file, 'AdapterInterface.php')) { require_once $adapter_file; }
}
foreach (glob(__DIR__ . '/../mu-plugin/landing-config/adapters/*.php') as $adapter_file) {
    if (!str_ends_with($adapter_file, 'AdapterInterface.php')) { require_once $adapter_file; }
}
if (is_file(__DIR__ . '/../mu-plugin/landing-config/includes/monitoring-alerts.php')) {
    require_once __DIR__ . '/../mu-plugin/landing-config/includes/monitoring-alerts.php';
}
require_once __DIR__ . '/../mu-plugin/landing-config/includes/lead-delivery-worker.php';
require_once __DIR__ . '/../mu-plugin/landing-config/includes/rest-lead.php';

$failures = 0;
$assert = static function (bool $condition, string $message) use (&$failures): void {
    if (!$condition) { $failures++; fwrite(STDERR, "FAIL: {$message}\n"); }
};

$exists = function_exists('LandingConfig\\Monitoring\\record_incident');
$assert($exists, 'privacy-safe monitoring incident core exists');
if (!$exists) { echo "FAILURES: {$failures}\n"; exit(1); }

lr_reset_state();
update_option('landing_monitor_enabled', '1');
$alerts = \LandingConfig\DB\get_monitor_alerts_table_name();

$id = \LandingConfig\Monitoring\record_incident(
    'integration_failure', 'critical', null, 41, 11, 'email',
    'unknown', 'transport_error', null, '', strtotime('2026-07-15 12:00:00 UTC')
);
$assert($id > 0, 'unknown exact integration creates an incident');
$rows = lr_rows($alerts);
$assert(count($rows) === 1, 'one incident row is stored');
$assert((int)($rows[0]['lead_id'] ?? 0) === 41 && (int)($rows[0]['integration_id'] ?? 0) === 11, 'incident keeps exact safe IDs');

\LandingConfig\Monitoring\record_incident(
    'integration_failure', 'critical', null, 41, 11, 'email',
    'unknown', 'transport_error', null, '', strtotime('2026-07-15 12:01:00 UTC')
);
$rows = lr_rows($alerts);
$assert(count($rows) === 1 && (int)($rows[0]['occurrence_count'] ?? 0) === 2, 'duplicate increments occurrence without another row');

\LandingConfig\Monitoring\observe_delivery_result(41, 12, 'roistat', 'failed_permanent', 'provider_4xx', 400);
$assert(count(lr_rows($alerts)) === 2, 'different integration has a different fingerprint');
\LandingConfig\Monitoring\observe_delivery_result(41, 11, 'email', 'accepted', '', 200);
$rows = lr_rows($alerts);
$first = array_values(array_filter($rows, static fn($row) => (int)($row['integration_id'] ?? 0) === 11))[0] ?? [];
$assert(($first['resolution'] ?? '') === 'delivery_recovered' && !empty($first['resolved_at']), 'confirmed delivery resolves its exact incident');

$invalid = \LandingConfig\Monitoring\record_incident(
    'integration_failure', 'critical', null, 41, 11, 'email',
    'unknown', 'CONTACT-MARKER +971501111111', null
);
$assert($invalid === 0, 'free-text/PII category is rejected');
$assert(count(lr_rows($alerts)) === 2, 'invalid incident stores nothing');

$generation_one = \LandingConfig\Monitoring\record_external_incident(
    'external_outage', 'redis_outage', 100, strtotime('2026-07-15 12:02:00 UTC')
);
\LandingConfig\Monitoring\record_external_incident(
    'external_outage', 'redis_outage', 100, strtotime('2026-07-15 12:03:00 UTC')
);
$generation_two = \LandingConfig\Monitoring\record_external_incident(
    'external_outage', 'redis_outage', 200, strtotime('2026-07-15 12:04:00 UTC')
);
$assert($generation_one > 0 && $generation_two > 0, 'external generations are accepted only through dedicated API');
$external = array_values(array_filter(lr_rows($alerts), static fn($row) => ($row['incident_kind'] ?? '') === 'external_outage'));
$assert(count($external) === 2, 'repeat in an episode deduplicates but later generation creates a new row');
$assert((int)($external[0]['fingerprint_scope'] ?? 0) === 100 && (int)($external[1]['fingerprint_scope'] ?? 0) === 200, 'privacy-safe generation is stored numerically');

$bad_external = \LandingConfig\Monitoring\record_external_incident(
    'missing_lead', 'redis_outage', 300, strtotime('2026-07-15 12:05:00 UTC')
);
$assert($bad_external === 0, 'external scope cannot be applied to another incident kind');

// Reconciliation queues reservations for old saved leads with no delivery rows,
// alerts old queued work, and does not alert a bounded retry with a future successor.
lr_reset_state();
update_option('landing_monitor_enabled', '1');
$integration_id = \LandingConfig\Integrations\save_integration(
    'email', 'Launch mailbox', '', ['to' => 'elapova00@gmail.com'], false, 1, [], true
);
lr_queue_results([['id' => 70]]); // saved leads missing all delivery rows
lr_queue_results([[
    'id' => 80, 'lead_id' => 71, 'integration_id' => $integration_id,
    'adapter' => 'email', 'status' => 'queued', 'attempt' => 1,
]]);
lr_queue_results([[
    'id' => 81, 'lead_id' => 72, 'integration_id' => $integration_id,
    'adapter' => 'email', 'status' => 'retry_wait', 'attempt' => 1,
]]);
lr_queue_row(['id' => 82, 'status' => 'queued', 'next_attempt_at' => '2026-07-15 12:10:00']);
$summary = \LandingConfig\Monitoring\reconcile_delivery_rows(strtotime('2026-07-15 12:00:00 UTC'));
$assert(($summary['reservations_recreated'] ?? 0) === 1, 'old lead missing delivery rows is re-reserved');
$assert(($summary['stuck'] ?? 0) === 1, 'old queued row creates one stuck incident');
$assert(count($GLOBALS['_lr_scheduled_single'] ?? []) >= 1, 'recreated reservation schedules worker');
$stuck = array_values(array_filter(lr_rows(\LandingConfig\DB\get_monitor_alerts_table_name()), static fn($row) => ($row['incident_kind'] ?? '') === 'delivery_stuck'));
$assert(count($stuck) === 1, 'future valid retry successor does not add another stuck alert');

$monitor_source = file_get_contents(__DIR__ . '/../mu-plugin/landing-config/includes/monitoring-alerts.php');
$worker_source = file_get_contents(__DIR__ . '/../mu-plugin/landing-config/includes/lead-delivery-worker.php');
foreach (['CONTACT-MARKER', '+971501111111', 'response_body', 'error_text'] as $marker) {
    if (in_array($marker, ['response_body','error_text'], true)) { continue; }
    $assert(!str_contains((string)$monitor_source, $marker), "monitor source contains no {$marker}");
}
$assert(!str_contains((string)$monitor_source . (string)$worker_source, 'processed_status'), 'monitoring queue never touches CRM business status');

echo $failures === 0 ? "PASS: monitoring incidents\n" : "FAILURES: {$failures}\n";
exit($failures === 0 ? 0 : 1);
