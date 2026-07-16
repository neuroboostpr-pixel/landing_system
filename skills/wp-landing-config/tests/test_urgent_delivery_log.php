<?php
require_once __DIR__ . '/fixtures/wp-bootstrap.php';
require_once __DIR__ . '/../mu-plugin/landing-config/includes/db.php';
require_once __DIR__ . '/../mu-plugin/landing-config/includes/encryption.php';
require_once __DIR__ . '/../mu-plugin/landing-config/includes/helpers.php';
require_once __DIR__ . '/../mu-plugin/landing-config/includes/cascade.php';
require_once __DIR__ . '/../mu-plugin/landing-config/includes/integrations.php';
require_once __DIR__ . '/../mu-plugin/landing-config/adapters/AdapterInterface.php';
require_once __DIR__ . '/../mu-plugin/landing-config/adapters/EmailAdapter.php';
require_once __DIR__ . '/../mu-plugin/landing-config/includes/lead-delivery-worker.php';
require_once __DIR__ . '/../mu-plugin/landing-config/includes/rest-lead.php';

$failures = 0;
$assert = static function (bool $condition, string $message) use (&$failures): void {
    if (!$condition) {
        $failures++;
        fwrite(STDERR, "FAIL: {$message}\n");
    }
};

$GLOBALS['_mock_inserted_leads'] = [];
$GLOBALS['_mock_mail_sent'] = [];
$GLOBALS['_mock_transients'] = [];
$GLOBALS['_mock_posts'] = [];
$GLOBALS['_mock_post_meta'] = [];
$GLOBALS['_mock_next_post_id'] = 1;
$_SERVER['REMOTE_ADDR'] = '203.0.113.44';
$_SERVER['HTTP_USER_AGENT'] = 'urgent-hotfix-test';

$integration_id = \LandingConfig\Integrations\save_integration(
    'email',
    'Launch mailbox',
    '',
    ['to' => 'elapova00@gmail.com', 'subject' => 'New HybridAutos lead'],
    false,
    1,
    [],
    true
);
$assert($integration_id > 0, 'email integration fixture is created');

$request = new WP_REST_Request([
    'name' => 'PII-MARKER-NAME',
    'phone' => '+971 50 111 2233',
    'email' => 'pii-marker@example.invalid',
    'message' => 'PII-MARKER-MESSAGE',
    'source_block' => 'https://hybridautos.ae/?utm_source=google',
    'utm_source' => 'google',
    'pd_consent' => '1',
]);
$response = \LandingConfig\REST\handle_lead($request);
$assert($response->get_status() === 200, 'saved lead returns HTTP 200');
$response_data = $response->get_data();
$assert(($response_data['ok'] ?? false) === true, 'saved lead returns ok=true');
$assert(is_int($response_data['lead_id'] ?? null) && $response_data['lead_id'] > 0, 'saved lead returns a positive integer id');

$assert(count($GLOBALS['_mock_mail_sent']) === 0, 'primary response waits for no Email adapter');

$log_rows = array_values(array_filter(
    $GLOBALS['_mock_inserted_leads'],
    static fn(array $row): bool => str_ends_with((string)($row['table'] ?? ''), 'landing_lead_log')
));
$assert(count($log_rows) === 1, 'one exact delivery reservation is stored');
$log = $log_rows[0]['data'] ?? [];
$assert(($log['lead_id'] ?? 0) === ($response_data['lead_id'] ?? -1), 'delivery row belongs to the saved lead');
$assert(($log['adapter'] ?? '') === 'email', 'delivery row identifies Email');
$assert((int)($log['integration_id'] ?? 0) === $integration_id, 'delivery row identifies the exact Email record');
$assert(($log['status'] ?? '') === 'queued', 'primary response stores a queued reservation');
$safe_text = json_encode([$log['response_body'] ?? '', $log['error_text'] ?? '']);
foreach (['PII-MARKER-NAME', '+971 50 111 2233', 'pii-marker@example.invalid', 'PII-MARKER-MESSAGE'] as $pii) {
    $assert(!str_contains((string)$safe_text, $pii), "delivery log excludes PII marker {$pii}");
}

// The worker test exercises the atomic queue claim. Here the legacy helper is
// invoked only to preserve its exact-settings and privacy regression coverage.
\LandingConfig\REST\dispatch_all_integrations(['id' => (int)$response_data['lead_id']] + $request->get_params() + [
    'utm_medium' => '', 'utm_campaign' => '', 'utm_term' => '', 'utm_content' => '',
    'roistat_visit' => '', 'created_at' => current_time('mysql'),
]);
$assert(count($GLOBALS['_mock_mail_sent']) === 1, 'configured Email integration sends once when delivery executes');
$assert(($GLOBALS['_mock_mail_sent'][0]['to'] ?? '') === 'elapova00@gmail.com', 'only launch mailbox receives the email');

// Each enabled record must use its own settings. This prevents two configured
// mailboxes from both resolving to the first recipient.
$second_id = \LandingConfig\Integrations\save_integration(
    'email',
    'Second launch mailbox',
    '',
    ['to' => 'second@example.com', 'subject' => 'Second mailbox'],
    false,
    1,
    [],
    true
);
$assert($second_id > 0, 'second Email integration fixture is created');
update_option('landing_integration_email_to', 'legacy@example.com');
$empty_id = \LandingConfig\Integrations\save_integration(
    'email',
    'Explicit empty mailbox',
    '',
    [],
    false,
    1,
    [],
    true
);
$assert($empty_id > 0, 'explicit-empty Email integration fixture is created');
$GLOBALS['_mock_mail_sent'] = [];
\LandingConfig\REST\dispatch_all_integrations([
    'id' => 501,
    'name' => 'Settings isolation test',
    'phone' => '+971501111111',
    'email' => '',
    'message' => '',
    'source_block' => 'test',
    'utm_source' => '',
    'utm_medium' => '',
    'utm_campaign' => '',
    'created_at' => current_time('mysql'),
]);
$recipients = array_column($GLOBALS['_mock_mail_sent'], 'to');
sort($recipients);
$assert(
    $recipients === ['elapova00@gmail.com', 'second@example.com'],
    'complete Email integrations use their exact recipient and empty settings never use legacy recipient'
);
$assert(!in_array('legacy@example.com', $recipients, true), 'explicit settings never fall back to a legacy recipient');

$summary = \LandingConfig\REST\safe_delivery_summary([
    'ok' => false,
    'response_code' => 503,
    'response_body' => 'RAW-PROVIDER-BODY PII-MARKER-NAME pii-marker@example.invalid',
    'error' => 'RAW-ERROR +971 50 111 2233',
]);
$assert(!str_contains($summary['response_body'], 'RAW-PROVIDER-BODY'), 'raw provider body is never persisted');
$assert(str_contains($summary['response_body'], 'body_sha256='), 'provider body is represented by a fingerprint');
$assert(($summary['error_text'] ?? '') === 'provider_error', 'raw provider error is reduced to a safe category');

echo $failures === 0 ? "PASS: urgent delivery log\n" : "FAILURES: {$failures}\n";
exit($failures === 0 ? 0 : 1);
