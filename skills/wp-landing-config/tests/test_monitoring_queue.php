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
$queue_source = substr((string)$source, (int)strpos((string)$source, 'function claim_next_alert'));
$assert(!str_contains($queue_source, 'next_attempt_at'), 'alert queue never references nonexistent next_attempt_at');

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

queue_reset();
\LandingConfig\Monitoring\record_incident(
    'javascript_stall', 'warning', '22222222-2222-4222-8222-222222222222',
    null, null, '', 'submit_attempt', 'browser_javascript_stall', null, '', 1784190000
);
$row = queue_alert_row();
lr_queue_row($row);
lr_set_http(['response' => ['code' => 200], 'body' => '{"ok":true}', 'headers' => []]);
\LandingConfig\Monitoring\run_alert_queue(1, 1784190000);
$unknown = queue_alert_row();
$assert(($unknown['telegram_status'] ?? '') === 'unknown', 'malformed empty 2xx is terminal unknown without resend');

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
