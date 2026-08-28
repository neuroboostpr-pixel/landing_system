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

$assert(function_exists('LandingConfig\\Monitoring\\should_deliver_incident_to_telegram'),
    'monitoring Telegram policy exists');

foreach (\LandingConfig\Monitoring\allowed_incident_kinds() as $kind) {
    $assert(
        \LandingConfig\Monitoring\should_deliver_incident_to_telegram($kind) === false,
        "technical incident {$kind} is never eligible for the client Telegram chat"
    );
}

lr_reset_state();
update_option('landing_monitor_enabled', '1');
\LandingConfig\Integrations\save_integration(
    'telegram', 'HybridCars leads', '',
    ['bot_token' => 'TEST-BOT-TOKEN', 'chat_id' => '-100123'],
    false, 1, [], true
);

$incident_id = \LandingConfig\Monitoring\record_incident(
    'missing_lead', 'critical', '11111111-1111-4111-8111-111111111111',
    null, null, '', 'request_failed', 'missing_wordpress_lead', null, '', 1784190000
);
$table = \LandingConfig\DB\get_monitor_alerts_table_name();
$rows = lr_rows($table);
$recorded = $rows[0] ?? [];
$assert($incident_id > 0 && count($rows) === 1,
    'critical incident is still recorded in the internal monitoring log');
$assert(($recorded['telegram_status'] ?? '') === 'suppressed',
    'new critical incident is stored without entering the Telegram queue');

// A critical row left pending by an older release must be drained without a
// Telegram request after this policy is deployed.
$GLOBALS['wpdb']->update($table, [
    'telegram_status' => 'pending',
], ['id' => $incident_id]);
$legacy_pending = lr_rows($table)[0] ?? [];
lr_queue_row($legacy_pending);
lr_set_http([
    'response' => ['code' => 200],
    'body' => '{"ok":true,"result":{"message_id":987}}',
    'headers' => [],
]);
$summary = \LandingConfig\Monitoring\run_alert_queue(1, 1784190000);
$stored = lr_rows($table)[0] ?? [];
$assert(($stored['telegram_status'] ?? '') === 'suppressed',
    'legacy critical monitoring row is removed from the Telegram queue');
$assert(($summary['processed'] ?? -1) === 0 && ($summary['sent'] ?? -1) === 0,
    'monitoring worker sends no technical message');
$assert($GLOBALS['_lr_http_requests'] === [],
    'technical monitoring makes no Telegram HTTP request');
$assert(count(lr_rows($table)) === 1 && ($stored['incident_kind'] ?? '') === 'missing_lead',
    'suppression keeps the incident available in the internal log');

// A row claimed by an older worker before rollout must also leave the
// technical Telegram queue. Its diagnostic record remains intact.
$GLOBALS['wpdb']->update($table, [
    'telegram_status' => 'sending',
    'locked_at' => \LandingConfig\Monitoring\utc_mysql(1784189900),
    'lock_token' => 'legacy-lock',
], ['id' => $incident_id]);
\LandingConfig\Monitoring\run_alert_queue(1, 1784190000);
$stored = lr_rows($table)[0] ?? [];
$assert(($stored['telegram_status'] ?? '') === 'suppressed'
    && empty($stored['locked_at'])
    && empty($stored['lock_token']),
    'legacy in-flight monitoring row is disabled and unlocked');

echo $failures === 0
    ? "PASS: monitoring Telegram policy\n"
    : "FAILURES: {$failures}\n";
exit($failures === 0 ? 0 : 1);
