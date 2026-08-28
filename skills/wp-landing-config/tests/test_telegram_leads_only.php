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
require_once __DIR__ . '/../mu-plugin/landing-config/includes/monitoring-alerts.php';
require_once __DIR__ . '/../mu-plugin/landing-config/includes/lead-delivery-worker.php';

$failures = 0;
$assert = static function (bool $condition, string $message) use (&$failures): void {
    if (!$condition) { $failures++; fwrite(STDERR, "FAIL: {$message}\n"); }
};

lr_reset_state();
update_option('landing_monitor_enabled', '1');
$telegram_id = \LandingConfig\Integrations\save_integration(
    'telegram', 'HybridCars leads', '',
    ['bot_token' => 'lead-bot-token', 'chat_id' => '-100123'],
    false, 1, [], true
);

global $wpdb;
$wpdb->insert(\LandingConfig\DB\get_leads_table_name(), [
    'name' => 'Real Lead Test',
    'phone' => '+971501112233',
    'email' => 'lead@example.test',
    'message' => 'Please call me',
    'source_block' => 'https://hybridautos.test/rox/',
    'utm_source' => 'quality-control',
    'utm_medium' => '',
    'utm_campaign' => '',
    'utm_term' => '',
    'utm_content' => '',
    'roistat_visit' => '',
    'created_at' => current_time('mysql'),
    'processed_status' => 'new',
]);
$lead_id = (int)$wpdb->insert_id;
$reserved = \LandingConfig\LeadDelivery\reserve_integrations($lead_id);
$reservation = lr_rows(\LandingConfig\DB\get_lead_log_table_name())[0] ?? [];
$lead = lr_rows(\LandingConfig\DB\get_leads_table_name())[0] ?? [];
$assert($telegram_id > 0 && $lead_id > 0 && $reserved === 1,
    'real lead has one exact Telegram delivery reservation');

lr_queue_results([$reservation]);
lr_queue_query_count(1);
lr_queue_row($lead);
lr_set_http([
    'response' => ['code' => 200],
    'body' => '{"ok":true,"result":{"message_id":501}}',
    'headers' => [],
]);
$delivery = \LandingConfig\LeadDelivery\run_delivery_worker(20, 1784190000);
$assert(($delivery['processed'] ?? 0) === 1 && count($GLOBALS['_lr_http_requests']) === 1,
    'real lead worker makes exactly one Telegram request');
$request = $GLOBALS['_lr_http_requests'][0] ?? [];
$message = (string)($request['args']['body']['text'] ?? '');
$assert(str_contains((string)($request['url'] ?? ''), 'api.telegram.org/botlead-bot-token/sendMessage'),
    'real lead uses the configured Telegram adapter');
$assert(str_contains($message, 'Новая заявка')
    && str_contains($message, 'Real Lead Test')
    && str_contains($message, '+971501112233'),
    'Telegram receives a real lead card with contact details');
$assert(!str_contains($message, 'Инцидент:')
    && !str_contains($message, 'Форма остановилась')
    && !str_contains($message, 'Техническое событие'),
    'real lead card contains no monitoring alert text');

\LandingConfig\Monitoring\record_incident(
    'integration_failure', 'critical', null, $lead_id, $telegram_id, 'telegram',
    'failed_permanent', 'provider_4xx', 400, '', 1784190000
);
\LandingConfig\Monitoring\run_alert_queue(10, 1784190000);
$assert(count($GLOBALS['_lr_http_requests']) === 1,
    'technical incident adds no Telegram request after the real lead card');
$incidents = lr_rows(\LandingConfig\DB\get_monitor_alerts_table_name());
$assert(count($incidents) === 1 && ($incidents[0]['telegram_status'] ?? '') === 'suppressed',
    'technical incident remains available in the internal log');

echo $failures === 0 ? "PASS: Telegram receives leads only\n" : "FAILURES: {$failures}\n";
exit($failures === 0 ? 0 : 1);
