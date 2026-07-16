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
if (is_file(__DIR__ . '/../mu-plugin/landing-config/includes/lead-delivery-worker.php')) {
    require_once __DIR__ . '/../mu-plugin/landing-config/includes/lead-delivery-worker.php';
}
require_once __DIR__ . '/../mu-plugin/landing-config/includes/rest-lead.php';

$failures = 0;
$assert = static function (bool $condition, string $message) use (&$failures): void {
    if (!$condition) {
        $failures++;
        fwrite(STDERR, "FAIL: {$message}\n");
    }
};

$worker_exists = function_exists('LandingConfig\\LeadDelivery\\run_delivery_worker');
$assert($worker_exists, 'asynchronous delivery worker exists');
if (!$worker_exists) {
    echo "FAILURES: {$failures}\n";
    exit(1);
}

function delivery_seed(string $type, array $settings): array {
    $integration_id = \LandingConfig\Integrations\save_integration($type, 'Delivery test', '', $settings, false, 1, [], true);
    global $wpdb;
    $wpdb->insert(\LandingConfig\DB\get_leads_table_name(), [
        'name' => 'Worker Test', 'phone' => '+971501111111', 'email' => '', 'message' => '',
        'source_block' => 'test', 'utm_source' => '', 'utm_medium' => '', 'utm_campaign' => '',
        'utm_term' => '', 'utm_content' => '', 'roistat_visit' => '', 'created_at' => current_time('mysql'),
        'processed_status' => 'new',
    ]);
    $lead_id = (int)$wpdb->insert_id;
    \LandingConfig\LeadDelivery\reserve_integrations($lead_id);
    return [$lead_id, $integration_id, lr_rows(\LandingConfig\DB\get_lead_log_table_name())[0] ?? []];
}

function queue_delivery_run(array $reservation, array $lead): void {
    lr_queue_results([$reservation]);
    lr_queue_query_count(1);
    lr_queue_row($lead);
}

lr_reset_state();
[$lead_id, $integration_id, $row] = delivery_seed('email', ['to' => 'elapova00@gmail.com', 'subject' => 'Lead']);
$assert($lead_id > 0 && $integration_id > 0, 'worker fixture has exact IDs');
global $wpdb;
$duplicate = $wpdb->insert(\LandingConfig\DB\get_lead_log_table_name(), [
    'lead_id' => $lead_id, 'integration_id' => $integration_id, 'adapter' => 'email', 'attempt' => 1,
    'status' => 'queued', 'next_attempt_at' => current_time('mysql'),
]);
$assert($duplicate === false, 'unique lead/integration/attempt rejects duplicate reservation');
queue_delivery_run($row, [
    'id' => $lead_id, 'name' => 'Worker Test', 'phone' => '+971501111111', 'email' => '',
    'message' => '', 'source_block' => 'test', 'utm_source' => '', 'utm_medium' => '',
    'utm_campaign' => '', 'utm_term' => '', 'utm_content' => '', 'roistat_visit' => '',
    'created_at' => current_time('mysql'), 'processed_status' => 'new',
]);
$result = \LandingConfig\LeadDelivery\run_delivery_worker(20, strtotime('2026-07-15 12:00:00 UTC'));
$rows = lr_rows(\LandingConfig\DB\get_lead_log_table_name());
$assert(count($GLOBALS['_mock_mail_sent']) === 1, 'first worker sends once');
$assert(($rows[0]['status'] ?? '') === 'accepted', 'confirmed Email becomes accepted');
$lead_rows = lr_rows(\LandingConfig\DB\get_leads_table_name());
$assert(($lead_rows[0]['processed_status'] ?? '') === 'new', 'delivery worker never changes processed_status');

lr_queue_results([$row]);
lr_queue_query_count(0);
\LandingConfig\LeadDelivery\run_delivery_worker(20, strtotime('2026-07-15 12:00:00 UTC'));
$assert(count($GLOBALS['_mock_mail_sent']) === 1, 'second worker loses claim and cannot send twice');

lr_reset_state();
[$lead_id, $integration_id, $row] = delivery_seed('roistat', ['webhook_url' => 'https://roistat.invalid/hook', 'site_url' => 'https://hybridautos.test/']);
lr_set_http(['response' => ['code' => 429], 'body' => '{"error":"limited"}', 'headers' => ['retry-after' => '7200']]);
queue_delivery_run($row, [
    'id' => $lead_id, 'name' => 'Worker Test', 'phone' => '+971501111111', 'email' => '',
    'message' => '', 'source_block' => 'test', 'utm_source' => '', 'utm_medium' => '',
    'utm_campaign' => '', 'utm_term' => '', 'utm_content' => '', 'roistat_visit' => '',
    'created_at' => current_time('mysql'), 'processed_status' => 'new',
]);
\LandingConfig\LeadDelivery\run_delivery_worker(20, strtotime('2026-07-15 12:00:00 UTC'));
$rows = lr_rows(\LandingConfig\DB\get_lead_log_table_name());
$assert(count($rows) === 2, 'definite 429 creates exactly one successor attempt');
$assert(($rows[0]['status'] ?? '') === 'retry_wait', '429 terminally closes current attempt as retry_wait');
$assert((int)($rows[1]['attempt'] ?? 0) === 2 && ($rows[1]['status'] ?? '') === 'queued', '429 successor is queued attempt two');
$assert(strtotime((string)($rows[1]['next_attempt_at'] ?? '')) === strtotime('2026-07-15 13:00:00 UTC'), 'Retry-After is clamped to 3600 seconds');

lr_reset_state();
[$lead_id, $integration_id, $row] = delivery_seed('roistat', ['webhook_url' => 'https://roistat.invalid/hook', 'site_url' => 'https://hybridautos.test/']);
$wpdb->update(\LandingConfig\DB\get_lead_log_table_name(), ['attempt' => 3], ['id' => $row['id']]);
$row['attempt'] = 3;
lr_set_http(['response' => ['code' => 429], 'body' => 'limited', 'headers' => []]);
queue_delivery_run($row, [
    'id' => $lead_id, 'name' => 'Worker Test', 'phone' => '+971501111111', 'email' => '',
    'message' => '', 'source_block' => 'test', 'utm_source' => '', 'utm_medium' => '',
    'utm_campaign' => '', 'utm_term' => '', 'utm_content' => '', 'roistat_visit' => '',
    'created_at' => current_time('mysql'), 'processed_status' => 'new',
]);
\LandingConfig\LeadDelivery\run_delivery_worker(20, strtotime('2026-07-15 12:00:00 UTC'));
$rows = lr_rows(\LandingConfig\DB\get_lead_log_table_name());
$assert(count($rows) === 1 && ($rows[0]['status'] ?? '') === 'failed_permanent', 'third 429 is permanent and creates no attempt four');

lr_reset_state();
[$lead_id, $integration_id, $row] = delivery_seed('roistat', ['webhook_url' => 'https://roistat.invalid/hook', 'site_url' => 'https://hybridautos.test/']);
lr_set_http(['response' => ['code' => 503], 'body' => 'provider unavailable', 'headers' => []]);
queue_delivery_run($row, [
    'id' => $lead_id, 'name' => 'Worker Test', 'phone' => '+971501111111', 'email' => '',
    'message' => '', 'source_block' => 'test', 'utm_source' => '', 'utm_medium' => '',
    'utm_campaign' => '', 'utm_term' => '', 'utm_content' => '', 'roistat_visit' => '',
    'created_at' => current_time('mysql'), 'processed_status' => 'new',
]);
\LandingConfig\LeadDelivery\run_delivery_worker(20, strtotime('2026-07-15 12:00:00 UTC'));
$rows = lr_rows(\LandingConfig\DB\get_lead_log_table_name());
$assert(count($rows) === 1 && ($rows[0]['status'] ?? '') === 'unknown', '5xx is unknown and never blindly retried');

lr_reset_state();
global $wpdb;
$wpdb->insert(\LandingConfig\DB\get_lead_log_table_name(), [
    'lead_id' => 9, 'integration_id' => 7, 'adapter' => 'email', 'attempt' => 1,
    'status' => 'sending', 'locked_at' => '2026-07-15 11:54:59', 'next_attempt_at' => '2026-07-15 11:00:00',
]);
lr_queue_results(lr_rows(\LandingConfig\DB\get_lead_log_table_name()));
$changed = \LandingConfig\LeadDelivery\mark_stale_sending_unknown(strtotime('2026-07-15 12:00:00 UTC'));
$stale = lr_rows(\LandingConfig\DB\get_lead_log_table_name())[0] ?? [];
$assert($changed === 1 && ($stale['status'] ?? '') === 'unknown', 'stale sending becomes unknown and is never made claimable');

$source = file_get_contents(__DIR__ . '/../mu-plugin/landing-config/includes/lead-delivery-worker.php');
$assert(!str_contains((string)$source, 'processed_status'), 'queue implementation never reads or writes business status');

echo $failures === 0 ? "PASS: lead delivery worker\n" : "FAILURES: {$failures}\n";
exit($failures === 0 ? 0 : 1);
