<?php
require __DIR__ . '/fixtures/lead-reliability-bootstrap.php';
require_once __DIR__ . '/../mu-plugin/landing-config/includes/db.php';
require_once __DIR__ . '/../mu-plugin/landing-config/includes/encryption.php';
require_once __DIR__ . '/../mu-plugin/landing-config/includes/helpers.php';
require_once __DIR__ . '/../mu-plugin/landing-config/includes/cascade.php';
require_once __DIR__ . '/../mu-plugin/landing-config/includes/integrations.php';
require_once __DIR__ . '/../mu-plugin/landing-config/includes/lead-delivery-worker.php';
require_once __DIR__ . '/../mu-plugin/landing-config/includes/rest-lead.php';
require_once __DIR__ . '/../mu-plugin/landing-config/includes/admin-lead-audit.php';

$failures = 0;
$assert = static function (bool $condition, string $message) use (&$failures): void {
    if (!$condition) { $failures++; fwrite(STDERR, "FAIL: {$message}\n"); }
};

$filter_exists = function_exists('LandingConfig\\Admin\\LeadAudit\\build_audit_filter_sql');
$promote_exists = function_exists('LandingConfig\\Admin\\LeadAudit\\promote_audit_rows');
$assert($filter_exists, 'prepared exact submission UUID audit filter exists');
$assert($promote_exists, 'testable safe audit promotion service exists');
if (!$filter_exists || !$promote_exists) {
    echo "FAILURES: {$failures}\n";
    exit(1);
}

$uuid = '44444444-4444-4444-8444-444444444444';
[$where, $args] = \LandingConfig\Admin\LeadAudit\build_audit_filter_sql('blocked', $uuid);
$assert($where === 'WHERE lead_id IS NULL AND submission_id=%s', 'blocked and UUID filters combine with exact equality placeholder');
$assert($args === [$uuid], 'exact normalized UUID is passed separately to wpdb prepare');
[$invalid_where, $invalid_args] = \LandingConfig\Admin\LeadAudit\build_audit_filter_sql('all', 'not-a-uuid');
$assert($invalid_where === '' && $invalid_args === [], 'invalid UUID never enters audit SQL');
$assert(
    \LandingConfig\Admin\LeadAudit\audit_promotion_lock_name(501, $uuid)
        === \LandingConfig\Admin\LeadAudit\audit_promotion_lock_name(999, $uuid),
    'different audit rows for the same submission share one idempotency lock'
);
$assert(
    \LandingConfig\Admin\LeadAudit\audit_promotion_lock_name(501, $uuid)
        === \LandingConfig\REST\submission_lock_name($uuid),
    'manual recovery and primary intake share the same submission idempotency lock'
);

lr_reset_state();
// Use the production IDs requested for the launch configuration.
foreach ([
    [14, 'email', ['to' => 'elapova00@gmail.com']],
    [15, 'telegram', ['bot_token' => 'test', 'chat_id' => '1']],
    [25, 'roistat', ['webhook_url' => 'https://roistat.invalid']],
] as [$id, $adapter, $settings]) {
    $GLOBALS['_mock_next_post_id'] = $id;
    $saved_id = \LandingConfig\Integrations\save_integration(
        $adapter, 'Recovery ' . $adapter, '', $settings, false, 1, [], true
    );
    $assert($saved_id === $id, "fixture creates exact enabled integration {$id}");
}

$consentless = [
    'id' => 501, 'submission_id' => '55555555-5555-4555-8555-555555555555',
    'lead_id' => null, 'pd_consent' => '0', 'phone' => '+971500000001', 'email' => '',
    'name' => 'No consent', 'message' => '', 'source_block' => '',
    'utm_source' => '', 'utm_medium' => '', 'utm_campaign' => '', 'roistat_visit' => '',
    'ip' => '203.0.113.1', 'user_agent' => 'test', 'created_at' => '2026-07-16 08:00:00',
];
$eligible = [
    'id' => 502, 'submission_id' => $uuid,
    'lead_id' => null, 'pd_consent' => '1', 'phone' => '+971500000002', 'email' => '',
    'name' => 'Recover me', 'message' => '', 'source_block' => 'https://hybridautos.test/rox/',
    'utm_source' => 'google', 'utm_medium' => 'cpc', 'utm_campaign' => 'rox', 'roistat_visit' => 'visit',
    'ip' => '203.0.113.2', 'user_agent' => 'test', 'created_at' => '2026-07-16 08:01:00',
];
lr_queue_row($consentless);
lr_queue_row($eligible);
lr_queue_row($eligible); // re-read under the submission-scoped lock
lr_queue_row(null); // no existing lead with this exact submission UUID
$first = \LandingConfig\Admin\LeadAudit\promote_audit_rows([501, 502]);
$assert($first === ['promoted' => 1, 'skipped' => 1], 'consentless audit is skipped and eligible audit is promoted once');
$lead_rows = lr_rows(\LandingConfig\DB\get_leads_table_name());
$assert(count($lead_rows) === 1 && ($lead_rows[0]['submission_id'] ?? '') === $uuid,
    'only eligible exact submission becomes a lead');
$delivery_rows = lr_rows(\LandingConfig\DB\get_lead_log_table_name());
$delivery_ids = array_map(static fn($row) => (int)($row['integration_id'] ?? 0), $delivery_rows);
sort($delivery_ids);
$assert($delivery_ids === [14, 15, 25], 'promoted lead queues exact Email, Telegram and Roistat integration IDs');
$assert(count($GLOBALS['_lr_scheduled_single']) === 1 && count($GLOBALS['_lr_spawn_cron_calls']) === 1,
    'promoted lead schedules and wakes asynchronous delivery once');

$new_lead_id = (int)($lead_rows[0]['id'] ?? 0);
lr_queue_row($eligible); // stale admin snapshot still says lead_id=NULL
lr_queue_row($eligible); // re-read under the submission-scoped lock
lr_queue_row(['id' => $new_lead_id]); // exact submission idempotency lookup wins
$repeat = \LandingConfig\Admin\LeadAudit\promote_audit_rows([502]);
$assert($repeat === ['promoted' => 0, 'skipped' => 1], 'repeat promotion detects existing exact submission and skips');
$assert(count(lr_rows(\LandingConfig\DB\get_leads_table_name())) === 1, 'repeat promotion creates no duplicate lead');
$assert(count(lr_rows(\LandingConfig\DB\get_lead_log_table_name())) === 3,
    'repeat promotion creates no duplicate delivery reservations');
$assert(count($GLOBALS['_lr_scheduled_single']) === 1 && count($GLOBALS['_lr_spawn_cron_calls']) === 1,
    'repeat promotion sends no duplicate delivery job');

$source = file_get_contents(__DIR__ . '/../mu-plugin/landing-config/includes/admin-lead-audit.php');
$handler_source = substr((string)$source, (int)strpos((string)$source, 'function handle_bulk_promote'));
$assert(str_contains($handler_source, "REQUEST_METHOD") && str_contains($handler_source, "'POST'"),
    'bulk recovery mutation rejects GET before reading the action or selected rows');
foreach (['$wpdb->last_error', 'getMessage()', '+971500000002', 'Recover me'] as $unsafe) {
    $assert(!str_contains((string)$source, $unsafe), "audit recovery logs/source exclude {$unsafe}");
}

echo $failures === 0 ? "PASS: admin audit recovery\n" : "FAILURES: {$failures}\n";
exit($failures === 0 ? 0 : 1);
