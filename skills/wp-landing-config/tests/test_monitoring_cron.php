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

$failures = 0;
$assert = static function (bool $condition, string $message) use (&$failures): void {
    if (!$condition) { $failures++; fwrite(STDERR, "FAIL: {$message}\n"); }
};

$exists = function_exists('LandingConfig\\Monitoring\\sync_monitoring_schedule');
$assert($exists, 'one-minute monitoring scheduler exists');
if (!$exists) { echo "FAILURES: {$failures}\n"; exit(1); }

lr_reset_state();
update_option('landing_monitor_enabled', '1');
\LandingConfig\Monitoring\sync_monitoring_schedule(1784190000);
$scheduled = $GLOBALS['_lr_next_scheduled'];
$assert(($scheduled[\LandingConfig\LeadDelivery\DELIVERY_HOOK] ?? 0) === 1784190005, 'delivery worker is offset +5 seconds');
$assert(($scheduled[\LandingConfig\Monitoring\SCAN_HOOK] ?? 0) === 1784190010, 'monitor scan is offset +10 seconds');
$assert(($scheduled[\LandingConfig\Monitoring\QUEUE_HOOK] ?? 0) === 1784190040, 'alert queue is offset +40 seconds');
$assert(isset($scheduled[\LandingConfig\Monitoring\CLEANUP_HOOK]), 'daily retention is scheduled');
$before = $GLOBALS['_lr_next_scheduled'];
\LandingConfig\Monitoring\sync_monitoring_schedule(1784190060);
$assert($GLOBALS['_lr_next_scheduled'] === $before, 'schedule setup is idempotent');

update_option('landing_monitor_enabled', '0');
\LandingConfig\Monitoring\sync_monitoring_schedule(1784190120);
// Delivery is a sales-critical service and must keep running while only the
// optional monitoring/alert layer is disabled during staged rollout.
$assert(isset($GLOBALS['_lr_next_scheduled'][\LandingConfig\LeadDelivery\DELIVERY_HOOK]), 'disabled monitor keeps asynchronous lead delivery scheduled');
foreach ([\LandingConfig\Monitoring\SCAN_HOOK, \LandingConfig\Monitoring\QUEUE_HOOK] as $hook) {
    $assert(!isset($GLOBALS['_lr_next_scheduled'][$hook]), "disabled monitor clears {$hook}");
}
$assert(isset($GLOBALS['_lr_next_scheduled'][\LandingConfig\Monitoring\CLEANUP_HOOK]), 'disabled monitor keeps mandatory contact-retention cleanup scheduled');

// Reservation repair belongs to core delivery too: staged rollout may keep
// Telegram alerts disabled, but a saved lead still needs all delivery rows.
$integration_id = \LandingConfig\Integrations\save_integration(
    'email', 'Core delivery', '', ['to' => 'elapova00@gmail.com'], false, 1, [], true
);
update_option(\LandingConfig\Monitoring\DELIVERY_ROLLOUT_BOUNDARY_OPTION, '2026-07-15 11:30:00');
update_option(\LandingConfig\Monitoring\DELIVERY_ROLLOUT_MIN_LEAD_ID_OPTION, 500);
lr_queue_results([]); // stale sending rows
lr_queue_results([]); // worker queue
lr_queue_results([[
    'id' => 500,
    'delivery_targets' => \LandingConfig\LeadDelivery\encode_delivery_targets([$integration_id => 'email']),
    'delivery_reservations_ready' => 0,
]]); // reservation reconciliation runs after the existing queue
\LandingConfig\Monitoring\run_delivery_cron();
$disabled_delivery_rows = lr_rows(\LandingConfig\DB\get_lead_log_table_name());
$assert(count($disabled_delivery_rows) === 1
    && (int)($disabled_delivery_rows[0]['lead_id'] ?? 0) === 500
    && (int)($disabled_delivery_rows[0]['integration_id'] ?? 0) === $integration_id,
    'disabled alert monitoring still reconciles a saved lead into core delivery');

$delivery_continued = false;
if (function_exists('LandingConfig\\Monitoring\\run_delivery_cron_steps')) {
    \LandingConfig\Monitoring\run_delivery_cron_steps(
        static function (): void { throw new RuntimeException('sensitive reconciliation failure'); },
        static function () use (&$delivery_continued): void { $delivery_continued = true; }
    );
}
$assert($delivery_continued, 'reconciliation exception cannot prevent already queued lead delivery');

lr_reset_state();
\LandingConfig\Monitoring\touch_heartbeat(true, 1784190000);
$assert((int)get_option(\LandingConfig\Monitoring\HEARTBEAT_OPTION, 0) === 1784190000, 'healthy wrapper writes integer heartbeat');
$assert(get_option(\LandingConfig\Monitoring\RUN_STATUS_OPTION, '') === 'ok', 'healthy wrapper writes fixed ok status');
\LandingConfig\Monitoring\touch_heartbeat(false, 1784190060);
$assert(get_option(\LandingConfig\Monitoring\RUN_STATUS_OPTION, '') === 'failed', 'failed wrapper writes fixed failed status');

lr_reset_state();
$alerts_table = \LandingConfig\DB\get_monitor_alerts_table_name();
foreach (['2026-06-16 11:59:59', '2026-06-16 12:00:00', '2026-06-16 12:00:01'] as $last_seen_at) {
    $GLOBALS['wpdb']->insert($alerts_table, [
        'incident_kind' => 'javascript_stall',
        'telegram_status' => 'suppressed',
        'last_seen_at' => $last_seen_at,
        'resolved_at' => null,
        'sent_at' => null,
        'last_response_at' => null,
    ]);
}
$GLOBALS['wpdb']->insert($alerts_table, [
    'incident_kind' => 'javascript_stall',
    'telegram_status' => 'suppressed',
    'last_seen_at' => '2026-07-15 12:00:00',
    'resolved_at' => '2026-05-01 12:00:00',
    'sent_at' => null,
    'last_response_at' => null,
]);
$cleanup = \LandingConfig\Monitoring\cleanup_expired_alerts(strtotime('2026-07-16 12:00:00 UTC'));
$remaining_suppressed = lr_rows($alerts_table);
$assert(($cleanup['deleted_alerts'] ?? -1) === 1,
    'suppressed diagnostics are deleted only after the full 30-day window');
$assert(array_column($remaining_suppressed, 'last_seen_at') === [
    '2026-06-16 12:00:00', '2026-06-16 12:00:01', '2026-07-15 12:00:00',
], 'the 30-day boundary, newer rows, and recently seen resolved diagnostics are retained');
$sql = implode("\n", $GLOBALS['wpdb']->query_log);
$assert(str_contains($sql, "2026-06-16 12:00:00"), 'resolved/sent cutoff is exactly 30 days');
$assert(str_contains($sql, "2026-04-17 12:00:00"), 'terminal unknown/failed cutoff is exactly 90 days');
$assert(str_contains($sql, "telegram_status NOT IN ('pending','retry_wait','sending')"), 'pending, retry and sending are never deleted regardless of age');
$assert(str_contains($sql, "telegram_status<>'suppressed' AND resolved_at IS NOT NULL"),
    'a stale resolution timestamp cannot shorten the 30-day suppressed retention window');
$assert(str_contains($sql, "telegram_status='suppressed'"),
    'non-Telegram diagnostic incidents are cleaned after the 30-day window');
$assert(str_contains($sql,
    "(telegram_status='suppressed' AND last_seen_at<'2026-06-16 12:00:00')"),
    'suppressed retention uses the strict older-than operator at the exact cutoff');
$assert(str_contains($sql, 'LIMIT 1000'), 'cleanup uses batches of 1000');

$source = file_get_contents(__DIR__ . '/../mu-plugin/landing-config/includes/monitoring-alerts.php');
foreach (['getMessage()', 'hash(\'sha256\', $e', 'hash("sha256", $e'] as $unsafe) {
    $assert(!str_contains((string)$source, $unsafe), "cron wrappers never log/hash exception text: {$unsafe}");
}
foreach (['delivery_reconcile_failed','delivery_worker_failed','monitor_scan_failed','monitor_queue_failed','monitor_cleanup_failed'] as $fixed) {
    $assert(str_contains((string)$source, $fixed), "fixed safe failure category {$fixed} exists");
}

echo $failures === 0 ? "PASS: monitoring cron and retention\n" : "FAILURES: {$failures}\n";
exit($failures === 0 ? 0 : 1);
