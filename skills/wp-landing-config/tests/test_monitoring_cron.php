<?php
require __DIR__ . '/fixtures/lead-reliability-bootstrap.php';
require_once __DIR__ . '/../mu-plugin/landing-config/includes/db.php';
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
foreach ([\LandingConfig\LeadDelivery\DELIVERY_HOOK, \LandingConfig\Monitoring\SCAN_HOOK, \LandingConfig\Monitoring\QUEUE_HOOK, \LandingConfig\Monitoring\CLEANUP_HOOK] as $hook) {
    $assert(!isset($GLOBALS['_lr_next_scheduled'][$hook]), "disabled monitor clears {$hook}");
}

lr_reset_state();
\LandingConfig\Monitoring\touch_heartbeat(true, 1784190000);
$assert((int)get_option(\LandingConfig\Monitoring\HEARTBEAT_OPTION, 0) === 1784190000, 'healthy wrapper writes integer heartbeat');
$assert(get_option(\LandingConfig\Monitoring\RUN_STATUS_OPTION, '') === 'ok', 'healthy wrapper writes fixed ok status');
\LandingConfig\Monitoring\touch_heartbeat(false, 1784190060);
$assert(get_option(\LandingConfig\Monitoring\RUN_STATUS_OPTION, '') === 'failed', 'failed wrapper writes fixed failed status');

lr_reset_state();
lr_queue_query_count(3);
lr_queue_query_count(0);
$cleanup = \LandingConfig\Monitoring\cleanup_expired_alerts(strtotime('2026-07-16 12:00:00 UTC'));
$assert(($cleanup['deleted'] ?? -1) === 3, 'retention drains deleted rows in bounded batches');
$sql = implode("\n", $GLOBALS['wpdb']->query_log);
$assert(str_contains($sql, "2026-06-16 12:00:00"), 'resolved/sent cutoff is exactly 30 days');
$assert(str_contains($sql, "2026-04-17 12:00:00"), 'terminal unknown/failed cutoff is exactly 90 days');
$assert(str_contains($sql, "telegram_status NOT IN ('pending','retry_wait','sending')"), 'pending, retry and sending are never deleted regardless of age');
$assert(str_contains($sql, 'LIMIT 1000'), 'cleanup uses batches of 1000');

$source = file_get_contents(__DIR__ . '/../mu-plugin/landing-config/includes/monitoring-alerts.php');
foreach (['getMessage()', 'hash(\'sha256\', $e', 'hash("sha256", $e'] as $unsafe) {
    $assert(!str_contains((string)$source, $unsafe), "cron wrappers never log/hash exception text: {$unsafe}");
}
foreach (['delivery_worker_failed','monitor_scan_failed','monitor_queue_failed','monitor_cleanup_failed'] as $fixed) {
    $assert(str_contains((string)$source, $fixed), "fixed safe failure category {$fixed} exists");
}

echo $failures === 0 ? "PASS: monitoring cron and retention\n" : "FAILURES: {$failures}\n";
exit($failures === 0 ? 0 : 1);
