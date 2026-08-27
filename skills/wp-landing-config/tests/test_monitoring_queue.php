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
$assert($exists, 'technical Telegram alert queue exists');
if (!$exists) { echo "FAILURES: {$failures}\n"; exit(1); }

function queue_reset(): int {
    lr_reset_state();
    update_option('landing_monitor_enabled', '1');
    return \LandingConfig\Integrations\save_integration(
        'telegram', 'HybridCars alerts', '',
        ['bot_token' => 'TEST-BOT-TOKEN', 'chat_id' => '-100123'],
        false, 1, [], true
    );
}

function queue_alert_row(): array {
    $rows = lr_rows(\LandingConfig\DB\get_monitor_alerts_table_name());
    return $rows[0] ?? [];
}

$telegram_id = queue_reset();
$assert($telegram_id > 0, 'one exact Telegram integration exists');
$alert_id = \LandingConfig\Monitoring\record_incident(
    'missing_lead', 'critical', '11111111-1111-4111-8111-111111111111',
    null, null, '', 'request_failed', 'missing_wordpress_lead', null, '', 1784190000
);
$row = queue_alert_row();
lr_queue_row($row);
lr_queue_row(null); // no optional form context
lr_queue_row(['id' => 321]); // exact private audit pointer
lr_set_http(['response' => ['code' => 200], 'body' => '{"ok":true,"result":{"message_id":987}}', 'headers' => []]);
$observed_sending = false;
$GLOBALS['_lr_before_http'] = static function () use (&$observed_sending, $alert_id): void {
    $rows = lr_rows(\LandingConfig\DB\get_monitor_alerts_table_name());
    foreach ($rows as $candidate) {
        if ((int)($candidate['id'] ?? 0) === $alert_id) {
            $observed_sending = ($candidate['telegram_status'] ?? '') === 'sending'
                && (int)($candidate['send_attempts'] ?? 0) === 1;
        }
    }
};
$summary = \LandingConfig\Monitoring\run_alert_queue(1, 1784190000);
$sent = queue_alert_row();
$assert($observed_sending, 'row is durably sending with incremented attempts before HTTP');
$assert(count($GLOBALS['_lr_http_requests']) === 1, 'one worker makes one Telegram POST');
$assert(($sent['telegram_status'] ?? '') === 'sent' && (int)($sent['telegram_message_id'] ?? 0) === 987, 'only strict Telegram confirmation becomes sent');
$assert(($summary['sent'] ?? 0) === 1, 'queue summary reports confirmed message');
$first_message = (string)($GLOBALS['_lr_http_requests'][0]['args']['body']['text'] ?? '');
$assert(str_contains($first_message, 'Аудит WordPress: #321'), 'missing-lead alert says the exact private audit row exists');
$assert(str_contains($first_message, 'page=landing-config-lead-audit')
    && str_contains($first_message, 'submission_id=11111111-1111-4111-8111-111111111111'),
    'missing-lead alert links to the exact prepared UUID filter in WordPress admin');

$no_audit_text = \LandingConfig\Monitoring\build_alert_text($row, ['audit_found' => false]);
$assert(str_contains($no_audit_text, 'Контакт не дошёл в журнал WordPress')
    && str_contains($no_audit_text, 'проверить резерв'),
    'missing-lead alert without audit evidence honestly directs staff to fallback storage');
$normal_wpdb = $GLOBALS['wpdb'];
$GLOBALS['wpdb'] = new class extends MockWpdbInsert {
    public function get_row($sql, $output = OBJECT) { throw new RuntimeException('sensitive database failure'); }
};
try { $db_error_context = \LandingConfig\Monitoring\safe_audit_context('11111111-1111-4111-8111-111111111111'); }
catch (Throwable $ignored) { $db_error_context = null; }
$GLOBALS['wpdb'] = $normal_wpdb;
$assert($db_error_context === ['audit_found' => false],
    'audit lookup failure degrades to no-pointer guidance without blocking the technical alert');

// A second worker holding a stale pending snapshot loses the conditional claim.
lr_queue_row($row);
\LandingConfig\Monitoring\run_alert_queue(1, 1784190000);
$assert(count($GLOBALS['_lr_http_requests']) === 1, 'second worker cannot send the same alert');

// Resolution can race between SELECT and conditional claim. The claim must
// include resolved_at IS NULL so a recovered incident is never sent late.
queue_reset();
\LandingConfig\Monitoring\record_incident(
    'missing_lead', 'critical', '99999999-9999-4999-8999-999999999999',
    null, null, '', 'request_failed', 'missing_wordpress_lead', null, '', 1784190000
);
$resolved_snapshot = queue_alert_row();
$GLOBALS['wpdb']->update(\LandingConfig\DB\get_monitor_alerts_table_name(), [
    'resolved_at' => \LandingConfig\Monitoring\utc_mysql(1784190000),
    'resolution' => 'wordpress_lead_saved',
], ['id' => (int)$resolved_snapshot['id']]);
lr_queue_row($resolved_snapshot);
lr_set_http(['response' => ['code' => 200], 'body' => '{"ok":true,"result":{"message_id":988}}', 'headers' => []]);
\LandingConfig\Monitoring\run_alert_queue(1, 1784190000);
$assert($GLOBALS['_lr_http_requests'] === [], 'incident resolved between select and claim is never sent');

queue_reset();
\LandingConfig\Monitoring\record_incident(
    'integration_failure', 'critical', null, 42, 7, 'roistat',
    'failed_permanent', 'provider_4xx', 429, '', 1784190000
);
$row = queue_alert_row();
lr_queue_row($row);
lr_set_http(['response' => ['code' => 429], 'body' => '{"ok":false,"parameters":{"retry_after":7200}}', 'headers' => []]);
\LandingConfig\Monitoring\run_alert_queue(1, 1784190000);
$retry = queue_alert_row();
$assert(($retry['telegram_status'] ?? '') === 'retry_wait', 'only definite 429 becomes retry_wait');
$assert(strtotime((string)($retry['due_at'] ?? '')) === 1784193600, 'Telegram retry_after is clamped to 3600 seconds on existing due_at');
$source = file_get_contents(__DIR__ . '/../mu-plugin/landing-config/includes/monitoring-alerts.php');
$claim_start = (int)strpos((string)$source, 'function claim_next_alert');
$claim_end = (int)strpos((string)$source, 'function configured_monitor_telegram_integration_id', $claim_start);
$queue_source = substr((string)$source, $claim_start, $claim_end - $claim_start);
$assert(!str_contains($queue_source, 'next_attempt_at'), 'alert queue never references nonexistent next_attempt_at');
$assert(str_contains($queue_source, "incident_kind<>'javascript_stall'"),
    'the main Telegram claim skips browser-only stalls so critical alerts cannot wait behind them');

// Third total call is terminal even when Telegram keeps returning 429.
global $wpdb;
$wpdb->update(\LandingConfig\DB\get_monitor_alerts_table_name(), [
    'telegram_status' => 'pending', 'send_attempts' => 2, 'due_at' => \LandingConfig\Monitoring\utc_mysql(1784190000),
], ['id' => (int)$retry['id']]);
$third = queue_alert_row();
lr_queue_row($third);
\LandingConfig\Monitoring\run_alert_queue(1, 1784190000);
$terminal = queue_alert_row();
$assert(($terminal['telegram_status'] ?? '') === 'failed' && (int)($terminal['send_attempts'] ?? 0) === 3, 'third 429 is terminal failed with no fourth call');

// A malformed success response for an alert type that is still enabled must
// remain terminal-unknown rather than being marked sent.
queue_reset();
\LandingConfig\Monitoring\record_incident(
    'integration_failure', 'critical', null, 43, 8, 'roistat',
    'failed_permanent', 'provider_4xx', 400, '', 1784190000
);
$malformed_success = queue_alert_row();
lr_queue_row($malformed_success);
lr_set_http(['response' => ['code' => 200], 'body' => '{"ok":true}', 'headers' => []]);
\LandingConfig\Monitoring\run_alert_queue(1, 1784190000);
$unknown = queue_alert_row();
$assert(($unknown['telegram_status'] ?? '') === 'unknown',
    'malformed empty 2xx is terminal unknown without resend');

queue_reset();
\LandingConfig\Monitoring\record_incident(
    'javascript_stall', 'warning', '22222222-2222-4222-8222-222222222222',
    null, null, '', 'submit_attempt', 'browser_javascript_stall', null, '', 1784190000
);
$row = queue_alert_row();
$assert(($row['telegram_status'] ?? '') === 'suppressed',
    'browser-only stall is recorded for diagnostics but is not queued for Telegram');

// A repeated fingerprint may belong to a historical row that was sent before
// the new policy. The new occurrence must normalize that row to suppressed.
$wpdb->update(\LandingConfig\DB\get_monitor_alerts_table_name(), [
    'telegram_status' => 'sent',
    'sent_at' => \LandingConfig\Monitoring\utc_mysql(1781598000),
], ['id' => (int)$row['id']]);
$GLOBALS['wpdb']->query_log = [];
\LandingConfig\Monitoring\record_incident(
    'javascript_stall', 'warning', '22222222-2222-4222-8222-222222222222',
    null, null, '', 'submit_attempt', 'browser_javascript_stall', null, '', 1784190060
);
$duplicate_sql = implode("\n", $GLOBALS['wpdb']->query_log);
$row = queue_alert_row();
$assert(($row['telegram_status'] ?? '') === 'suppressed'
    && strtotime((string)($row['last_seen_at'] ?? '')) === 1784190060,
    'a repeated historical stall is normalized and retained from its latest occurrence');
$expected_duplicate_suffix =
    "telegram_status=IF(VALUES(telegram_status)='suppressed','suppressed',telegram_status),"
    . "locked_at=IF(VALUES(telegram_status)='suppressed',NULL,locked_at),"
    . "lock_token=IF(VALUES(telegram_status)='suppressed',NULL,lock_token)";
$assert(str_ends_with($duplicate_sql, $expected_duplicate_suffix),
    'duplicate normalization uses the exact safe status and lock expressions');

// A stall that was already pending before this policy was deployed must also
// be suppressed instead of leaking one final noisy Telegram message.
$wpdb->update(\LandingConfig\DB\get_monitor_alerts_table_name(), [
    'telegram_status' => 'pending',
], ['id' => (int)$row['id']]);
$legacy_pending = queue_alert_row();
lr_queue_row($legacy_pending);
lr_queue_row(null);
lr_set_http(['response' => ['code' => 200], 'body' => '{"ok":true,"result":{"message_id":989}}', 'headers' => []]);
$suppressed_summary = \LandingConfig\Monitoring\run_alert_queue(1, 1784190000);
$suppressed = queue_alert_row();
$assert(($suppressed['telegram_status'] ?? '') === 'suppressed',
    'legacy pending browser-only stall is suppressed before Telegram delivery');
$assert($GLOBALS['_lr_http_requests'] === [], 'suppressed browser-only stall makes no Telegram request');
$assert(($suppressed_summary['processed'] ?? -1) === 0,
    'suppressed browser-only stall is not counted as a Telegram delivery attempt');

// Old rows can also be waiting for a future retry, already resolved, or have
// exhausted their attempts. They still need to leave the Telegram queue.
queue_reset();
\LandingConfig\Monitoring\record_incident(
    'javascript_stall', 'warning', '44444444-4444-4444-8444-444444444444',
    null, null, '', 'submit_attempt', 'browser_javascript_stall', null, '', 1784190000
);
$legacy_retry = queue_alert_row();
$wpdb->update(\LandingConfig\DB\get_monitor_alerts_table_name(), [
    'telegram_status' => 'retry_wait',
    'send_attempts' => 3,
    'due_at' => \LandingConfig\Monitoring\utc_mysql(1784197200),
    'resolved_at' => \LandingConfig\Monitoring\utc_mysql(1784190000),
], ['id' => (int)$legacy_retry['id']]);
$legacy_retry = queue_alert_row();
$sweep_exists = function_exists('LandingConfig\\Monitoring\\suppress_queued_non_telegram_alerts');
$assert($sweep_exists, 'a separate legacy suppression sweep exists');
if ($sweep_exists) {
    $GLOBALS['wpdb']->query_log = [];
    $swept = \LandingConfig\Monitoring\suppress_queued_non_telegram_alerts(100);
    $sweep_sql = implode("\n", $GLOBALS['wpdb']->query_log);
    $assert($swept === 1 && (queue_alert_row()['telegram_status'] ?? '') === 'suppressed',
        'legacy retry rows are suppressed even when future, resolved, or attempts are exhausted');
    $assert(str_contains(
        $sweep_sql,
        "WHERE incident_kind='javascript_stall' AND telegram_status IN ('pending','retry_wait') ORDER BY id LIMIT 100"
    ), 'legacy suppression SQL targets both and only pending/retry browser stalls');
    $assert(!str_contains($sweep_sql, 'due_at<=')
        && !str_contains($sweep_sql, 'resolved_at IS NULL')
        && !str_contains($sweep_sql, 'send_attempts<'),
        'legacy suppression does not leave unusual old rows stuck forever');
}

// Last line of defence: even a row that was already claimed before rollout
// must not make a Telegram HTTP request.
$GLOBALS['_lr_http_requests'] = [];
lr_set_http(['response' => ['code' => 200], 'body' => '{"ok":true,"result":{"message_id":990}}', 'headers' => []]);
$blocked_send = \LandingConfig\Monitoring\send_monitoring_alert($legacy_retry, 1784190000);
$assert(($blocked_send['status'] ?? '') === 'suppressed'
    && $GLOBALS['_lr_http_requests'] === [],
    'a browser-only stall is rejected again immediately before Telegram');

// Cleaning old noise and sending a critical alert happen in the same cron run.
if ($sweep_exists) {
    queue_reset();
    \LandingConfig\Monitoring\record_incident(
        'javascript_stall', 'warning', '55555555-5555-4555-8555-555555555555',
        null, null, '', 'submit_attempt', 'browser_javascript_stall', null, '', 1784190000
    );
    $wpdb->update(\LandingConfig\DB\get_monitor_alerts_table_name(), [
        'telegram_status' => 'pending',
    ], ['id' => (int)queue_alert_row()['id']]);
    \LandingConfig\Monitoring\record_incident(
        'missing_lead', 'critical', '66666666-6666-4666-8666-666666666666',
        null, null, '', 'request_failed', 'missing_wordpress_lead', null, '', 1784190000
    );
    $rows = lr_rows(\LandingConfig\DB\get_monitor_alerts_table_name());
    $legacy_stall = array_values(array_filter($rows,
        static fn(array $candidate): bool => ($candidate['incident_kind'] ?? '') === 'javascript_stall'))[0];
    $critical = array_values(array_filter($rows,
        static fn(array $candidate): bool => ($candidate['incident_kind'] ?? '') === 'missing_lead'))[0];
    lr_queue_row($critical);
    lr_queue_row(null); // no optional form context
    lr_queue_row(null); // no private audit pointer
    lr_set_http(['response' => ['code' => 200], 'body' => '{"ok":true,"result":{"message_id":991}}', 'headers' => []]);
    $mixed_summary = \LandingConfig\Monitoring\run_alert_queue(1, 1784190000);
    $rows = lr_rows(\LandingConfig\DB\get_monitor_alerts_table_name());
    $statuses = array_column($rows, 'telegram_status', 'incident_kind');
    $assert(($statuses['javascript_stall'] ?? '') === 'suppressed'
        && ($statuses['missing_lead'] ?? '') === 'sent'
        && ($mixed_summary['sent'] ?? 0) === 1,
        'old browser noise never delays the next critical missing-lead alert');
    $assert(count($GLOBALS['_lr_http_requests']) === 1,
        'mixed queue sends only the critical Telegram message');

    // More old rows than one cleanup batch must still not block a critical
    // alert. The remaining noise is drained on the next run.
    queue_reset();
    for ($index = 1; $index <= 101; $index++) {
        $submission_id = '70000000-0000-4000-8000-' . str_pad((string)$index, 12, '0', STR_PAD_LEFT);
        \LandingConfig\Monitoring\record_incident(
            'javascript_stall', 'warning', $submission_id,
            null, null, '', 'submit_attempt', 'browser_javascript_stall', null, '', 1784190000
        );
    }
    foreach (lr_rows(\LandingConfig\DB\get_monitor_alerts_table_name()) as $candidate) {
        $wpdb->update(\LandingConfig\DB\get_monitor_alerts_table_name(), [
            'telegram_status' => 'pending',
        ], ['id' => (int)$candidate['id']]);
    }
    \LandingConfig\Monitoring\record_incident(
        'missing_lead', 'critical', '77777777-7777-4777-8777-777777777777',
        null, null, '', 'request_failed', 'missing_wordpress_lead', null, '', 1784190000
    );
    $GLOBALS['_lr_execute_monitor_claim_sql'] = true;
    $GLOBALS['wpdb']->query_log = [];
    lr_set_http(['response' => ['code' => 200], 'body' => '{"ok":true,"result":{"message_id":992}}', 'headers' => []]);
    $large_backlog_summary = \LandingConfig\Monitoring\run_alert_queue(1, 1784190000);
    \LandingConfig\Monitoring\run_alert_queue(1, 1784190000);
    $claim_queries = array_values(array_filter(
        $GLOBALS['wpdb']->query_log,
        static fn(string $query): bool => str_starts_with($query, 'SELECT * FROM `')
            && str_contains($query, 'landing_monitor_alerts')
    ));
    $GLOBALS['_lr_execute_monitor_claim_sql'] = false;
    $rows = lr_rows(\LandingConfig\DB\get_monitor_alerts_table_name());
    $remaining_noise = array_filter($rows, static fn(array $candidate): bool =>
        ($candidate['incident_kind'] ?? '') === 'javascript_stall'
        && ($candidate['telegram_status'] ?? '') !== 'suppressed');
    $sent_critical = array_values(array_filter($rows,
        static fn(array $candidate): bool => ($candidate['incident_kind'] ?? '') === 'missing_lead'))[0];
    $assert(($large_backlog_summary['sent'] ?? 0) === 1
        && ($sent_critical['telegram_status'] ?? '') === 'sent'
        && $remaining_noise === [],
        '101 old browser warnings cannot delay one critical alert and are drained safely');
    $assert(count($GLOBALS['_lr_http_requests']) === 1,
        'two queue workers still send the critical alert only once and no browser warning');
    $expected_claim_sql = $wpdb->prepare(
        "SELECT * FROM `" . \LandingConfig\DB\get_monitor_alerts_table_name()
        . "` WHERE telegram_status IN ('pending','retry_wait') "
        . "AND incident_kind<>'javascript_stall' AND resolved_at IS NULL "
        . "AND due_at<=%s AND send_attempts<%d ORDER BY due_at,id LIMIT 1",
        \LandingConfig\Monitoring\utc_mysql(1784190000),
        \LandingConfig\Monitoring\MAX_SEND_ATTEMPTS
    );
    $assert($claim_queries !== []
        && array_values(array_unique($claim_queries)) === [$expected_claim_sql],
        'backlog test executes only the exact canonical critical-claim SQL');
}

queue_reset();
\LandingConfig\Monitoring\record_incident(
    'missing_lead', 'critical', '33333333-3333-4333-8333-333333333333',
    null, null, '', 'request_failed', 'missing_wordpress_lead', null, '', 1784189000
);
$wpdb->update(\LandingConfig\DB\get_monitor_alerts_table_name(), [
    'telegram_status' => 'sending', 'locked_at' => \LandingConfig\Monitoring\utc_mysql(1784189800),
], ['id' => (int)queue_alert_row()['id']]);
lr_queue_results([queue_alert_row()]);
$stale_count = \LandingConfig\Monitoring\mark_stale_alerts_unknown(1784190000);
$stale = queue_alert_row();
$assert($stale_count === 1 && ($stale['telegram_status'] ?? '') === 'unknown', 'stale sending becomes terminal unknown');

$assert(!str_contains((string)$source, 'dispatch_all_integrations'), 'technical queue never dispatches normal lead integrations');
$assert(!str_contains((string)$source, '_send_telegram'), 'technical queue never calls normal lead Telegram function');
$assert(!str_contains((string)$source, 'TelegramAdapter::send'), 'technical queue has an independent client');
$messages = array_map(static fn($request) => (string)($request['args']['body']['text'] ?? ''), $GLOBALS['_lr_http_requests']);
foreach (['+971501111111','contact@example.com','TEST-BOT-TOKEN'] as $secret_or_pii) {
    $assert(!str_contains(implode('|', $messages), $secret_or_pii), "technical message excludes {$secret_or_pii}");
}

echo $failures === 0 ? "PASS: monitoring Telegram queue\n" : "FAILURES: {$failures}\n";
exit($failures === 0 ? 0 : 1);
