<?php
require __DIR__ . '/fixtures/lead-reliability-bootstrap.php';
require_once __DIR__ . '/../mu-plugin/landing-config/includes/db.php';
require_once __DIR__ . '/../mu-plugin/landing-config/includes/encryption.php';
require_once __DIR__ . '/../mu-plugin/landing-config/includes/helpers.php';
require_once __DIR__ . '/../mu-plugin/landing-config/includes/cascade.php';
require_once __DIR__ . '/../mu-plugin/landing-config/includes/integrations.php';
require_once __DIR__ . '/../mu-plugin/landing-config/adapters/AdapterInterface.php';
require_once __DIR__ . '/../mu-plugin/landing-config/adapters/EmailAdapter.php';
if (is_file(__DIR__ . '/../mu-plugin/landing-config/includes/lead-delivery-worker.php')) {
    require_once __DIR__ . '/../mu-plugin/landing-config/includes/lead-delivery-worker.php';
}
require_once __DIR__ . '/../mu-plugin/landing-config/includes/rest-lead.php';

use function LandingConfig\REST\handle_lead;

$failures = 0;
$assert = static function (bool $condition, string $message) use (&$failures): void {
    if (!$condition) {
        $failures++;
        fwrite(STDERR, "FAIL: {$message}\n");
    }
};

function idempotent_request(array $overrides = []): WP_REST_Request {
    return new WP_REST_Request(array_merge([
        'submission_id' => '11111111-1111-4111-8111-111111111111',
        'name' => 'Reliability test',
        'phone' => '+971501111111',
        'email' => '',
        'message' => '',
        'source_block' => 'hero',
        'utm_source' => 'search',
        'utm_medium' => 'cpc',
        'utm_campaign' => 'synthetic-campaign',
        'utm_term' => 'synthetic-term',
        'utm_content' => 'synthetic-content',
        'roistat_visit' => 'synthetic-visit',
        'pd_consent' => '1',
    ], $overrides));
}

function seed_email_integration(): int {
    return \LandingConfig\Integrations\save_integration(
        'email', 'Launch mailbox', '',
        ['to' => 'elapova00@gmail.com', 'subject' => 'Lead'],
        false, 1, [], true
    );
}

lr_reset_state();
$_SERVER['REMOTE_ADDR'] = '203.0.113.7';
$_SERVER['HTTP_USER_AGENT'] = 'idempotency-test';
$integration_id = seed_email_integration();
update_option('lp_rate_limit_per_hour', 100);
update_option('lp_global_rate_limit_per_hour', 1000);
$assert($integration_id > 0, 'integration fixture exists');
lr_queue_row(null); // first UUID lookup: no existing lead
$first = handle_lead(idempotent_request());
$lead_id = (int)($first->get_data()['lead_id'] ?? 0);
$lead_count = count(lr_rows(\LandingConfig\DB\get_leads_table_name()));
$delivery_count = count(lr_rows(\LandingConfig\DB\get_lead_log_table_name()));
$assert($first->get_status() === 200 && $lead_id > 0, 'first request durably saves a positive lead');
$assert($delivery_count === 1, 'first request reserves one exact integration');
$reservation = lr_rows(\LandingConfig\DB\get_lead_log_table_name())[0] ?? [];
$assert((int)($reservation['integration_id'] ?? 0) === $integration_id, 'reservation stores exact integration id');
$assert(($reservation['status'] ?? '') === 'queued', 'reservation starts queued');
$assert(count($GLOBALS['_lr_http_requests']) === 0 && count($GLOBALS['_mock_mail_sent']) === 0, 'primary response waits for no adapter');

lr_queue_row(lr_rows(\LandingConfig\DB\get_leads_table_name())[0] ?? []);
$replay = handle_lead(idempotent_request());
$assert($replay->get_status() === 200, 'replay succeeds');
$assert($replay->get_data() === ['ok' => true, 'lead_id' => $lead_id, 'replayed' => true], 'replay returns original lead');
$assert(count(lr_rows(\LandingConfig\DB\get_leads_table_name())) === $lead_count, 'replay inserts no lead');
$assert(count(lr_rows(\LandingConfig\DB\get_lead_log_table_name())) === $delivery_count, 'replay redelivers nothing');

$stored_lead = lr_rows(\LandingConfig\DB\get_leads_table_name())[0] ?? [];
$conflicting_changes = [
    'name' => 'Changed name',
    'phone' => '+15550100002',
    'email' => 'changed@example.test',
    'message' => 'Changed message',
    'source_block' => 'footer',
    'utm_source' => 'social',
    'utm_medium' => 'organic',
    'utm_campaign' => 'changed-campaign',
    'utm_term' => 'changed-term',
    'utm_content' => 'changed-content',
    'roistat_visit' => 'changed-visit',
];
foreach ($conflicting_changes as $field => $changed_value) {
    lr_queue_row($stored_lead);
    $conflict = handle_lead(idempotent_request([$field => $changed_value]));
    $assert($conflict->get_status() === 409, "changed {$field} returns a safe conflict");
    $assert(($conflict->get_data()['error'] ?? '') === 'idempotency_conflict', "changed {$field} uses the stable conflict code");
}
$assert(count(lr_rows(\LandingConfig\DB\get_leads_table_name())) === $lead_count, 'conflicts insert no lead');
$assert(count(lr_rows(\LandingConfig\DB\get_lead_log_table_name())) === $delivery_count, 'conflicts reserve no delivery');

lr_reset_state();
$_SERVER['REMOTE_ADDR'] = '203.0.113.7';
$_SERVER['HTTP_USER_AGENT'] = 'idempotency-test';
seed_email_integration();
$GLOBALS['_lr_force_lock_failure'] = true;
$GLOBALS['_lr_force_lock_failure_pattern'] = 'lpl_';
$busy = handle_lead(idempotent_request());
$assert($busy->get_status() === 503, 'contended UUID returns retryable 503');
$assert(lr_rows(\LandingConfig\DB\get_leads_table_name()) === [], 'contended UUID creates no duplicate');
$assert(count(lr_rows(\LandingConfig\DB\get_lead_audit_table_name())) === 1, 'early recoverable audit survives contention');
$lock_sql = implode("\n", $GLOBALS['wpdb']->query_log);
$assert(str_contains($lock_sql, 'GET_LOCK'), 'UUID requests use a named lock');
$assert(!str_contains($lock_sql, '+971501111111'), 'lock SQL contains no contact');

// Even a protected 429 response must leave the submitted contact in the
// private audit table so the sales team can recover it after an alert.
lr_reset_state();
$_SERVER['REMOTE_ADDR'] = '203.0.113.77';
$_SERVER['HTTP_USER_AGENT'] = 'rate-limit-recovery-test';
update_option('lp_rate_limit_per_hour', 1);
$rate_bucket = \LandingConfig\REST\rate_bucket_start();
update_option(\LandingConfig\REST\rate_option_name(
    'landing_lead_rl_bucket_', '203.0.113.77', $rate_bucket
), '1');
update_option(\LandingConfig\REST\rate_option_name(
    'landing_lead_rl_bucket_', '__site__', $rate_bucket, 'global'
), '1');
$limited = handle_lead(idempotent_request([
    'submission_id' => '22222222-2222-4222-8222-222222222222',
    'phone' => '+971509876543',
]));
$limited_audit = lr_rows(\LandingConfig\DB\get_lead_audit_table_name())[0] ?? [];
$assert($limited->get_status() === 429, 'rate-limited primary request returns protected 429');
$assert(($limited_audit['blocked_by'] ?? '') === 'rate_limit', 'rate-limited request records its exact safe reason');
$assert(($limited_audit['phone'] ?? '') === '+971509876543' && empty($limited_audit['lead_id']),
    'rate-limited contact remains recoverable from private audit without pretending a lead was saved');

lr_reset_state();
$_SERVER['REMOTE_ADDR'] = '203.0.113.8';
$_SERVER['HTTP_USER_AGENT'] = 'legacy-test';
$legacy = handle_lead(idempotent_request(['submission_id' => null]));
$assert($legacy->get_status() === 200, 'missing UUID keeps legacy insert path');
lr_reset_state();
$_SERVER['REMOTE_ADDR'] = '203.0.113.9';
$_SERVER['HTTP_USER_AGENT'] = 'legacy-test';
$invalid = handle_lead(idempotent_request(['submission_id' => 'not-a-uuid']));
$assert($invalid->get_status() === 200, 'invalid optional UUID keeps legacy insert path');

echo $failures === 0 ? "PASS: REST lead idempotency\n" : "FAILURES: {$failures}\n";
exit($failures === 0 ? 0 : 1);
