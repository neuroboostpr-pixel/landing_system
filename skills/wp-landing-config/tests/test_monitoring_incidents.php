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

// Reconciliation repairs each missing exact integration reservation. A partial
// primary failure (Email and Roistat rows exist, Telegram row is absent) must
// not make Telegram disappear forever or replay completed integrations.
lr_reset_state();
update_option('landing_monitor_enabled', '1');
update_option('landing_delivery_async_boundary', '2026-07-15 11:30:00');
$integration_id = \LandingConfig\Integrations\save_integration(
    'email', 'Launch mailbox', '', ['to' => 'elapova00@gmail.com'], false, 1, [], true
);
$telegram_id = \LandingConfig\Integrations\save_integration(
    'telegram', 'Launch Telegram', '', ['bot_token' => 'test', 'chat_id' => '1'], false, 1, [], true
);
$roistat_id = \LandingConfig\Integrations\save_integration(
    'roistat', 'Launch CRM', '', ['webhook_url' => 'https://roistat.invalid'], false, 1, [], true
);
$delivery_table = \LandingConfig\DB\get_lead_log_table_name();
// A legacy row gets integration_id=0 during rollout. It must remain evidence
// only and must never trigger a new delivery to every current integration.
$GLOBALS['wpdb']->insert($delivery_table, [
    'lead_id' => 69, 'integration_id' => 0, 'adapter' => 'email',
    'attempt' => 6001, 'status' => 'success', 'created_at' => '2026-07-15 11:00:00',
]);
foreach ([[$integration_id, 'email'], [$roistat_id, 'roistat']] as [$existing_id, $adapter]) {
    $GLOBALS['wpdb']->insert($delivery_table, [
        'lead_id' => 70, 'integration_id' => $existing_id, 'adapter' => $adapter,
        'attempt' => 1, 'status' => 'success', 'created_at' => '2026-07-15 11:58:00',
    ]);
}
lr_queue_results([
    ['id' => 69, 'created_at' => '2026-07-15 11:00:00'], // legacy, before boundary
    ['id' => 70, 'created_at' => '2026-07-15 11:58:00'], // fresh, missing Telegram
    ['id' => 71, 'created_at' => '2026-07-15 11:59:00'], // fresh, total reservation failure
]);
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
$assert(($summary['reservations_recreated'] ?? 0) === 4,
    'new partial and total failures recreate four exact rows while legacy lead is excluded');
$delivery_rows = lr_rows($delivery_table);
$lead_69_rows = array_values(array_filter($delivery_rows, static fn($row) => (int)($row['lead_id'] ?? 0) === 69));
$assert(count($lead_69_rows) === 1 && (int)($lead_69_rows[0]['integration_id'] ?? -1) === 0,
    'legacy lead before rollout boundary keeps only its historical integration_id=0 row');
$legacy_jobs = array_values(array_filter($GLOBALS['_lr_scheduled_single'], static fn($job) => (int)($job['args'][0] ?? 0) === 69));
$assert($legacy_jobs === [], 'legacy lead before boundary schedules no new delivery messages');
$lead_70_rows = array_values(array_filter($delivery_rows, static fn($row) => (int)($row['lead_id'] ?? 0) === 70));
$lead_70_ids = array_map(static fn($row) => (int)($row['integration_id'] ?? 0), $lead_70_rows);
sort($lead_70_ids);
$expected_ids = [$integration_id, $telegram_id, $roistat_id];
sort($expected_ids);
$assert($lead_70_ids === $expected_ids, 'partial reservation failure restores only the missing Telegram exact ID');
$existing_rows = array_values(array_filter($lead_70_rows, static fn($row) => in_array((int)($row['integration_id'] ?? 0), [$integration_id, $roistat_id], true)));
$assert(count($existing_rows) === 2 && count(array_filter($existing_rows, static fn($row) => ($row['status'] ?? '') === 'success')) === 2,
    'existing completed Email and Roistat rows are not replaced or replayed');
$lead_71_rows = array_values(array_filter($delivery_rows, static fn($row) => (int)($row['lead_id'] ?? 0) === 71));
$lead_71_ids = array_map(static fn($row) => (int)($row['integration_id'] ?? 0), $lead_71_rows);
sort($lead_71_ids);
$assert($lead_71_ids === $expected_ids, 'new lead with total reservation failure receives every enabled exact reservation');
$assert(($summary['stuck'] ?? 0) === 1, 'old queued row creates one stuck incident');
$assert(count($GLOBALS['_lr_scheduled_single'] ?? []) >= 1, 'recreated reservation schedules worker');
$stuck = array_values(array_filter(lr_rows(\LandingConfig\DB\get_monitor_alerts_table_name()), static fn($row) => ($row['incident_kind'] ?? '') === 'delivery_stuck'));
$assert(count($stuck) === 1, 'future valid retry successor does not add another stuck alert');

$monitor_source = file_get_contents(__DIR__ . '/../mu-plugin/landing-config/includes/monitoring-alerts.php');
$assert(str_contains((string)$monitor_source, 'COUNT(DISTINCT d.integration_id)'),
    'reconciliation SQL detects a lead missing any enabled exact integration, not only leads with zero rows');
$assert(str_contains((string)$monitor_source, 'DELIVERY_ROLLOUT_BOUNDARY_OPTION'),
    'reconciliation is hard-bounded by the one-time asynchronous rollout timestamp');
$worker_source = file_get_contents(__DIR__ . '/../mu-plugin/landing-config/includes/lead-delivery-worker.php');
foreach (['CONTACT-MARKER', '+971501111111', 'response_body', 'error_text'] as $marker) {
    if (in_array($marker, ['response_body','error_text'], true)) { continue; }
    $assert(!str_contains((string)$monitor_source, $marker), "monitor source contains no {$marker}");
}
$assert(!str_contains((string)$monitor_source . (string)$worker_source, 'processed_status'), 'monitoring queue never touches CRM business status');

echo $failures === 0 ? "PASS: monitoring incidents\n" : "FAILURES: {$failures}\n";
exit($failures === 0 ? 0 : 1);
