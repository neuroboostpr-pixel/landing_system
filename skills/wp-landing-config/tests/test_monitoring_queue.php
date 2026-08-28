<?php
require __DIR__ . '/fixtures/lead-reliability-bootstrap.php';
require_once __DIR__ . '/../mu-plugin/landing-config/includes/db.php';
require_once __DIR__ . '/../mu-plugin/landing-config/includes/encryption.php';
require_once __DIR__ . '/../mu-plugin/landing-config/includes/helpers.php';
require_once __DIR__ . '/../mu-plugin/landing-config/includes/cascade.php';
require_once __DIR__ . '/../mu-plugin/landing-config/includes/integrations.php';
require_once __DIR__ . '/../mu-plugin/landing-config/includes/monitoring-alerts.php';

$failures = 0;
$assert = static function (bool $condition, string $message) use (&$failures): void {
    if (!$condition) { $failures++; fwrite(STDERR, "FAIL: {$message}\n"); }
};

$exists = function_exists('LandingConfig\\Monitoring\\run_alert_queue');
$assert($exists, 'technical monitoring queue exists');
if (!$exists) { echo "FAILURES: {$failures}\n"; exit(1); }

function queue_reset(): int {
    lr_reset_state();
    update_option('landing_monitor_enabled', '1');
    return \LandingConfig\Integrations\save_integration(
        'telegram', 'HybridCars leads', '',
        ['bot_token' => 'TEST-BOT-TOKEN', 'chat_id' => '-100123'],
        false, 1, [], true
    );
}

function queue_rows(): array {
    return lr_rows(\LandingConfig\DB\get_monitor_alerts_table_name());
}

$telegram_id = queue_reset();
$assert($telegram_id > 0, 'normal lead Telegram integration remains configured');

// New technical incidents stay in the private monitoring log and never enter
// the Telegram delivery queue.
$incident_id = \LandingConfig\Monitoring\record_incident(
    'missing_lead', 'critical', '11111111-1111-4111-8111-111111111111',
    null, null, '', 'request_failed', 'missing_wordpress_lead', null, '', 1784190000
);
$row = queue_rows()[0] ?? [];
$assert($incident_id > 0 && ($row['incident_kind'] ?? '') === 'missing_lead',
    'critical incident is retained in the internal monitoring log');
$assert(($row['telegram_status'] ?? '') === 'suppressed',
    'critical incident does not enter Telegram delivery');

// A repeated fingerprint may belong to a historical row that was sent before
// the policy changed. A new occurrence must normalize it to suppressed while
// preserving the updated diagnostic record.
global $wpdb;
$wpdb->update(\LandingConfig\DB\get_monitor_alerts_table_name(), [
    'telegram_status' => 'sent',
    'sent_at' => \LandingConfig\Monitoring\utc_mysql(1781598000),
], ['id' => $incident_id]);
$GLOBALS['wpdb']->query_log = [];
\LandingConfig\Monitoring\record_incident(
    'missing_lead', 'critical', '11111111-1111-4111-8111-111111111111',
    null, null, '', 'request_failed', 'missing_wordpress_lead', null, '', 1784190060
);
$row = queue_rows()[0] ?? [];
$duplicate_sql = implode("\n", $GLOBALS['wpdb']->query_log);
$assert(($row['telegram_status'] ?? '') === 'suppressed'
    && (int)($row['occurrence_count'] ?? 0) === 2
    && strtotime((string)($row['last_seen_at'] ?? '')) === 1784190060,
    'repeat incident stays logged and is normalized away from Telegram');
$expected_duplicate_suffix =
    "telegram_status=IF(VALUES(telegram_status)='suppressed','suppressed',telegram_status),"
    . "locked_at=IF(VALUES(telegram_status)='suppressed',NULL,locked_at),"
    . "lock_token=IF(VALUES(telegram_status)='suppressed',NULL,lock_token)";
$assert(str_ends_with($duplicate_sql, $expected_duplicate_suffix),
    'duplicate normalization clears any obsolete Telegram lock');

// Rows left by an older release in any queue state are all disabled together,
// regardless of incident type, retry time, resolution, or attempt count.
queue_reset();
\LandingConfig\Monitoring\record_incident(
    'missing_lead', 'critical', '22222222-2222-4222-8222-222222222222',
    null, null, '', 'request_failed', 'missing_wordpress_lead', null, '', 1784190000
);
\LandingConfig\Monitoring\record_incident(
    'integration_failure', 'critical', null, 42, 7, 'roistat',
    'failed_permanent', 'provider_4xx', 400, '', 1784190000
);
\LandingConfig\Monitoring\record_incident(
    'javascript_stall', 'warning', '33333333-3333-4333-8333-333333333333',
    null, null, '', 'submit_attempt', 'browser_javascript_stall', null, '', 1784190000
);
foreach (queue_rows() as $candidate) {
    $status = match ((string)($candidate['incident_kind'] ?? '')) {
        'missing_lead' => 'pending',
        'integration_failure' => 'retry_wait',
        default => 'sending',
    };
    $wpdb->update(\LandingConfig\DB\get_monitor_alerts_table_name(), [
        'telegram_status' => $status,
        'send_attempts' => 3,
        'due_at' => \LandingConfig\Monitoring\utc_mysql(1784197200),
        'resolved_at' => \LandingConfig\Monitoring\utc_mysql(1784190000),
        'locked_at' => \LandingConfig\Monitoring\utc_mysql(1784190000),
        'lock_token' => 'legacy-lock',
    ], ['id' => (int)$candidate['id']]);
}
$GLOBALS['wpdb']->query_log = [];
lr_set_http([
    'response' => ['code' => 200],
    'body' => '{"ok":true,"result":{"message_id":987}}',
    'headers' => [],
]);
$summary = \LandingConfig\Monitoring\run_alert_queue(10, 1784190000);
$sweep_sql = implode("\n", $GLOBALS['wpdb']->query_log);
$rows = queue_rows();
$assert(count($rows) === 3
    && count(array_filter($rows, static fn(array $candidate): bool =>
        ($candidate['telegram_status'] ?? '') === 'suppressed'
        && empty($candidate['locked_at'])
        && empty($candidate['lock_token'])
    )) === 3,
    'all legacy technical queue states are suppressed and retained in the log');
$assert(($summary['suppressed'] ?? 0) === 3
    && ($summary['processed'] ?? -1) === 0
    && ($summary['sent'] ?? -1) === 0,
    'queue reports cleanup only and performs no delivery');
$assert($GLOBALS['_lr_http_requests'] === [],
    'legacy technical rows make no Telegram request');
$assert(str_contains(
    $sweep_sql,
    "WHERE telegram_status IN ('pending','retry_wait','sending') ORDER BY id LIMIT 100"
), 'cleanup covers every deliverable legacy status without filtering by incident kind');
$assert(!str_contains($sweep_sql, "incident_kind='")
    && !str_contains($sweep_sql, 'due_at<=')
    && !str_contains($sweep_sql, 'resolved_at IS NULL')
    && !str_contains($sweep_sql, 'send_attempts<'),
    'cleanup cannot leave an unusual technical row queued');

// Defence in depth: a stale database snapshot cannot bypass the broad cleanup.
queue_reset();
\LandingConfig\Monitoring\record_incident(
    'delivery_stuck', 'critical', null, 55, 9, 'telegram',
    'failed', 'delivery_queued_stuck', null, '', 1784190000
);
$row = queue_rows()[0] ?? [];
$wpdb->update(\LandingConfig\DB\get_monitor_alerts_table_name(), [
    'telegram_status' => 'pending',
], ['id' => (int)$row['id']]);
$row['telegram_status'] = 'pending';
lr_queue_row($row);
$claim = \LandingConfig\Monitoring\claim_next_alert(1784190000);
$assert($claim === null && (queue_rows()[0]['telegram_status'] ?? '') === 'suppressed',
    'stale critical snapshot is rejected before it can be claimed');
$blocked_send = \LandingConfig\Monitoring\send_monitoring_alert($row, 1784190000);
$assert(($blocked_send['status'] ?? '') === 'suppressed'
    && $GLOBALS['_lr_http_requests'] === [],
    'last delivery guard rejects every technical incident');

// More rows than one cleanup batch still cannot leak a message: the canonical
// claim sees the remainder and the final policy guard suppresses it.
queue_reset();
for ($index = 1; $index <= 101; $index++) {
    $submission_id = '70000000-0000-4000-8000-' . str_pad((string)$index, 12, '0', STR_PAD_LEFT);
    \LandingConfig\Monitoring\record_incident(
        'missing_lead', 'critical', $submission_id,
        null, null, '', 'request_failed', 'missing_wordpress_lead', null, '', 1784190000
    );
}
foreach (queue_rows() as $candidate) {
    $wpdb->update(\LandingConfig\DB\get_monitor_alerts_table_name(), [
        'telegram_status' => 'pending',
    ], ['id' => (int)$candidate['id']]);
}
$GLOBALS['_lr_execute_monitor_claim_sql'] = true;
$GLOBALS['wpdb']->query_log = [];
$backlog_summary = \LandingConfig\Monitoring\run_alert_queue(1, 1784190000);
$claim_queries = array_values(array_filter(
    $GLOBALS['wpdb']->query_log,
    static fn(string $query): bool => str_starts_with($query, 'SELECT * FROM `')
        && str_contains($query, 'landing_monitor_alerts')
));
$GLOBALS['_lr_execute_monitor_claim_sql'] = false;
$remaining = array_filter(queue_rows(), static fn(array $candidate): bool =>
    ($candidate['telegram_status'] ?? '') !== 'suppressed'
);
$assert(($backlog_summary['suppressed'] ?? 0) === 100
    && ($backlog_summary['processed'] ?? -1) === 0
    && $remaining === [],
    'large legacy backlog is retained but fully disabled without delivery');
$assert($GLOBALS['_lr_http_requests'] === [],
    'large technical backlog produces zero Telegram requests');
$expected_claim_sql = $wpdb->prepare(
    "SELECT * FROM `" . \LandingConfig\DB\get_monitor_alerts_table_name()
    . "` WHERE telegram_status IN ('pending','retry_wait') "
    . "AND resolved_at IS NULL AND due_at<=%s AND send_attempts<%d "
    . "ORDER BY due_at,id LIMIT 1",
    \LandingConfig\Monitoring\utc_mysql(1784190000),
    \LandingConfig\Monitoring\MAX_SEND_ATTEMPTS
);
$assert($claim_queries !== []
    && array_values(array_unique($claim_queries)) === [$expected_claim_sql],
    'backlog fallback uses the canonical claim before the policy guard');

$source = file_get_contents(__DIR__ . '/../mu-plugin/landing-config/includes/monitoring-alerts.php');
$assert(!str_contains((string)$source, 'dispatch_all_integrations'),
    'technical monitoring never dispatches normal lead integrations');
$assert(!str_contains((string)$source, '_send_telegram'),
    'technical monitoring never calls the normal lead Telegram helper');
$assert(!str_contains((string)$source, 'TelegramAdapter::send'),
    'technical monitoring remains isolated from the real lead adapter');

echo $failures === 0 ? "PASS: monitoring Telegram queue\n" : "FAILURES: {$failures}\n";
exit($failures === 0 ? 0 : 1);
