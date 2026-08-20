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

// One synthetic application must keep independent terminal evidence for every
// configured channel. A Telegram rejection must not stop the later Roistat job.
lr_reset_state();
$email_id = \LandingConfig\Integrations\save_integration(
    'email', 'Synthetic Email', '', ['to' => 'qa@example.test', 'subject' => 'Synthetic lead'], false, 1, [], true
);
$telegram_id = \LandingConfig\Integrations\save_integration(
    'telegram', 'Synthetic Telegram', '', ['bot_token' => 'synthetic-token', 'chat_id' => 'synthetic-chat'], false, 1, [], true
);
$roistat_id = \LandingConfig\Integrations\save_integration(
    'roistat', 'Synthetic Roistat', '',
    ['webhook_url' => 'https://roistat.invalid/synthetic-hook', 'site_url' => 'https://hybridautos.test/'],
    false, 1, [], true
);
global $wpdb;
$wpdb->insert(\LandingConfig\DB\get_leads_table_name(), [
    'name' => 'Synthetic Lead', 'phone' => '+15550100000', 'email' => 'lead@example.test',
    'message' => 'Synthetic delivery isolation', 'source_block' => 'https://hybridautos.test/test',
    'utm_source' => 'test', 'utm_medium' => 'test', 'utm_campaign' => 'test',
    'utm_term' => '', 'utm_content' => '', 'roistat_visit' => 'synthetic-visit',
    'created_at' => current_time('mysql'), 'processed_status' => 'new',
]);
$isolated_lead_id = (int)$wpdb->insert_id;
$reserved = \LandingConfig\LeadDelivery\reserve_integrations($isolated_lead_id);
$reservations = lr_rows(\LandingConfig\DB\get_lead_log_table_name());
$isolated_lead = lr_rows(\LandingConfig\DB\get_leads_table_name())[0] ?? [];
$assert($reserved === 3 && count($reservations) === 3, 'one lead reserves three exact channel deliveries');
lr_queue_results($reservations);
foreach ($reservations as $_reservation) {
    lr_queue_query_count(1);
    lr_queue_row($isolated_lead);
}
lr_set_mail_result(true);
$GLOBALS['_lr_before_http'] = static function (string $url, array $args): void {
    if (str_contains($url, 'api.telegram.org')) {
        lr_set_http([
            'response' => ['code' => 400],
            'body' => '{"ok":false,"error_code":400,"description":"test_rejected"}',
            'headers' => [],
        ]);
        return;
    }
    lr_set_http(['response' => ['code' => 200], 'body' => '{"status":"ok"}', 'headers' => []]);
};
$isolation_result = \LandingConfig\LeadDelivery\run_delivery_worker(20, strtotime('2026-07-15 12:00:00 UTC'));
$channel_rows = [];
foreach (lr_rows(\LandingConfig\DB\get_lead_log_table_name()) as $delivery_row) {
    $channel_rows[(string)($delivery_row['adapter'] ?? '')] = $delivery_row;
}
$assert(($isolation_result['processed'] ?? 0) === 3, 'worker processes all three reservations for one lead');
$assert(count($channel_rows) === 3, 'one lead keeps three separate channel outcomes');
$assert((int)($channel_rows['email']['lead_id'] ?? 0) === $isolated_lead_id
    && (int)($channel_rows['email']['integration_id'] ?? 0) === $email_id
    && ($channel_rows['email']['status'] ?? '') === 'accepted'
    && (int)($channel_rows['email']['response_code'] ?? 0) === 200
    && !empty($channel_rows['email']['finished_at']), 'Email finishes successfully with exact IDs');
$assert((int)($channel_rows['telegram']['lead_id'] ?? 0) === $isolated_lead_id
    && (int)($channel_rows['telegram']['integration_id'] ?? 0) === $telegram_id
    && ($channel_rows['telegram']['status'] ?? '') === 'failed_permanent'
    && (int)($channel_rows['telegram']['response_code'] ?? 0) === 400
    && ($channel_rows['telegram']['error_text'] ?? '') === 'provider_4xx'
    && !empty($channel_rows['telegram']['finished_at']), 'Telegram rejection is terminal and isolated');
$assert((int)($channel_rows['roistat']['lead_id'] ?? 0) === $isolated_lead_id
    && (int)($channel_rows['roistat']['integration_id'] ?? 0) === $roistat_id
    && ($channel_rows['roistat']['status'] ?? '') === 'success'
    && (int)($channel_rows['roistat']['response_code'] ?? 0) === 200
    && !empty($channel_rows['roistat']['finished_at']), 'Roistat still finishes after Telegram fails');
$assert(count($GLOBALS['_mock_mail_sent']) === 1 && count($GLOBALS['_lr_http_requests']) === 2,
    'one Email and both HTTP adapters are invoked exactly once');
$assert(!in_array('queued', array_column($channel_rows, 'status'), true)
    && !in_array('sending', array_column($channel_rows, 'status'), true), 'all three outcomes are terminal');

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
$wpdb->update(\LandingConfig\DB\get_lead_log_table_name(), ['attempt' => \LandingConfig\LeadDelivery\MAX_ATTEMPTS], ['id' => $row['id']]);
$row['attempt'] = \LandingConfig\LeadDelivery\MAX_ATTEMPTS;
lr_set_http(['response' => ['code' => 429], 'body' => 'limited', 'headers' => []]);
queue_delivery_run($row, [
    'id' => $lead_id, 'name' => 'Worker Test', 'phone' => '+971501111111', 'email' => '',
    'message' => '', 'source_block' => 'test', 'utm_source' => '', 'utm_medium' => '',
    'utm_campaign' => '', 'utm_term' => '', 'utm_content' => '', 'roistat_visit' => '',
    'created_at' => current_time('mysql'), 'processed_status' => 'new',
]);
\LandingConfig\LeadDelivery\run_delivery_worker(20, strtotime('2026-07-15 12:00:00 UTC'));
$rows = lr_rows(\LandingConfig\DB\get_lead_log_table_name());
$assert(count($rows) === 1 && ($rows[0]['status'] ?? '') === 'failed_permanent', 'final allowed 429 is permanent and creates no successor attempt');

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
