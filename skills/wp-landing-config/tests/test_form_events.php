<?php
require_once __DIR__ . '/fixtures/lead-reliability-bootstrap.php';
require_once __DIR__ . '/../mu-plugin/landing-config/includes/db.php';

$implementation = __DIR__ . '/../mu-plugin/landing-config/includes/rest-form-events.php';
if (!is_file($implementation)) {
    fwrite(STDERR, "FAIL: rest-form-events.php is missing\n");
    exit(1);
}
require_once $implementation;

$failures = 0;
$tests = 0;
$assert = static function (bool $condition, string $message) use (&$failures, &$tests): void {
    $tests++;
    if (!$condition) {
        $failures++;
        fwrite(STDERR, "FAIL: {$message}\n");
    }
};

function form_event_request(array $overrides = []): WP_REST_Request {
    return new WP_REST_Request(array_merge([
        'submission_id' => '11111111-1111-4111-8111-111111111111',
        'event_name' => 'validation_failed',
        'event_detail' => 'phone',
        'form_id' => 'rox-test-drive',
        'brand' => 'rox',
        'cta_key' => 'request-test-drive',
        'page_path' => '/rox/',
        'utm_source' => 'google',
        'utm_medium' => 'cpc',
        'utm_campaign' => 'rox-search',
    ], $overrides));
}

function reset_form_event_state(): void {
    lr_reset_state();
    $_SERVER['REMOTE_ADDR'] = '203.0.113.55';
    $_SERVER['HTTP_USER_AGENT'] = 'PII-USER-AGENT-MUST-NOT-BE-SAVED';
    unset($_SERVER['CONTENT_LENGTH']);
}

function form_event_rows(): array {
    return lr_rows(\LandingConfig\DB\get_form_events_table_name());
}

// A valid event is stored as anonymous workflow metadata only.
reset_form_event_state();
$response = \LandingConfig\FormEvents\handle_form_event(form_event_request([
    'form_id' => '<b>rox-form</b>',
]));
$assert($response->get_status() === 201, 'valid event returns HTTP 201');
$assert(($response->get_data()['ok'] ?? false) === true, 'valid event returns ok=true');
$rows = form_event_rows();
$assert(count($rows) === 1, 'valid event writes exactly one row');
$row = $rows[0] ?? [];
$assert(($row['submission_id'] ?? '') === '11111111-1111-4111-8111-111111111111', 'UUID is stored for lead correlation');
$assert(($row['event_name'] ?? '') === 'validation_failed' && ($row['event_detail'] ?? '') === 'phone', 'event and allowlisted detail are stored');
$assert(($row['form_id'] ?? '') === 'rox-form', 'metadata is sanitized before storage');
$assert(array_key_exists('event_sequence', $row) && $row['event_sequence'] === null, 'old cached client without event_sequence remains accepted');
foreach (['ip', 'user_agent', 'name', 'phone', 'email', 'message', 'source_block', 'referrer', 'gclid'] as $forbidden) {
    $assert(!array_key_exists($forbidden, $row), "event row excludes {$forbidden}");
}

// Event and detail are both strict allowlists.
foreach ([
    ['event_name' => 'made_up_event'],
    ['event_name' => 'validation_failed', 'event_detail' => 'credit_card'],
    ['event_name' => 'request_failed', 'event_detail' => 'phone'],
    ['event_name' => 'form_started', 'event_detail' => 'phone'],
] as $invalid) {
    reset_form_event_state();
    $response = \LandingConfig\FormEvents\handle_form_event(form_event_request($invalid));
    $assert($response->get_status() === 400, 'unknown event/detail combination is rejected');
    $assert(form_event_rows() === [], 'rejected event/detail writes no row');
}

// Empty detail is required for events which do not have a safe diagnostic code.
reset_form_event_state();
$response = \LandingConfig\FormEvents\handle_form_event(form_event_request([
    'event_name' => 'request_started',
    'event_detail' => '',
]));
$assert($response->get_status() === 201, 'request_started with empty detail is accepted');

// Browser sequence is optional for cached clients, but strict when supplied.
foreach ([1, 65535, '2', '65535'] as $valid_sequence) {
    reset_form_event_state();
    $response = \LandingConfig\FormEvents\handle_form_event(form_event_request([
        'event_sequence' => $valid_sequence,
    ]));
    $rows = form_event_rows();
    $assert($response->get_status() === 201, 'canonical event_sequence is accepted: ' . var_export($valid_sequence, true));
    $assert(($rows[0]['event_sequence'] ?? null) === (int) $valid_sequence, 'event_sequence is stored as an integer');
}

foreach ([null, [], ['1'], true, false, 0, -1, 65536, 1.0, '0', '-1', '65536', '01', '+1', '1.0', ' 1 ', '1e2', 'abc'] as $invalid_sequence) {
    reset_form_event_state();
    $response = \LandingConfig\FormEvents\handle_form_event(form_event_request([
        'event_sequence' => $invalid_sequence,
    ]));
    $assert($response->get_status() === 400, 'non-canonical or out-of-range event_sequence is rejected: ' . var_export($invalid_sequence, true));
    $assert(form_event_rows() === [], 'invalid event_sequence writes no row');
}

// Network arrival can be reversed; browser sequence restores the real order.
reset_form_event_state();
$arrived_first = \LandingConfig\FormEvents\handle_form_event(form_event_request([
    'event_name' => 'request_started',
    'event_detail' => '',
    'event_sequence' => 2,
]));
$arrived_second = \LandingConfig\FormEvents\handle_form_event(form_event_request([
    'event_name' => 'submit_attempt',
    'event_detail' => '',
    'event_sequence' => 1,
]));
$arrival_rows = form_event_rows();
$assert($arrived_first->get_status() === 201 && $arrived_second->get_status() === 201, 'out-of-arrival-order events are both accepted');
$assert(array_column($arrival_rows, 'event_sequence') === [2, 1], 'database arrival order remains visible');
$browser_order = $arrival_rows;
usort($browser_order, static fn(array $a, array $b): int => $a['event_sequence'] <=> $b['event_sequence']);
$assert(array_column($browser_order, 'event_name') === ['submit_attempt', 'request_started'], 'event_sequence recovers browser order independently of arrival');

// Any contact, full URL/referrer, click identifier, or unknown field is rejected.
$forbidden_payloads = [
    ['name' => 'Alice'],
    ['phone' => '+971501234567'],
    ['email' => 'alice@example.com'],
    ['message' => 'Call me'],
    ['source_block' => 'hero'],
    ['full_url' => 'https://hybridautos.ae/rox/'],
    ['url' => 'https://hybridautos.ae/rox/'],
    ['referrer' => 'https://google.com/'],
    ['gclid' => 'secret-click-id'],
    ['gbraid' => 'secret-click-id'],
    ['wbraid' => 'secret-click-id'],
    ['yclid' => 'secret-click-id'],
    ['fbclid' => 'secret-click-id'],
    ['unknown_metadata' => 'not-approved'],
];
foreach ($forbidden_payloads as $extra) {
    reset_form_event_state();
    $response = \LandingConfig\FormEvents\handle_form_event(form_event_request($extra));
    $assert($response->get_status() === 400, 'forbidden or unknown payload field is rejected: ' . array_key_first($extra));
    $assert(form_event_rows() === [], 'forbidden payload never reaches storage');
}

foreach ([
    ['brand' => 'https://hybridautos.ae/rox/'],
    ['utm_campaign' => 'alice@example.com'],
    ['cta_key' => '+971 50 123 4567'],
] as $hidden_sensitive_value) {
    reset_form_event_state();
    $response = \LandingConfig\FormEvents\handle_form_event(form_event_request($hidden_sensitive_value));
    $assert($response->get_status() === 400, 'sensitive value cannot be hidden in an allowed metadata field');
    $assert(form_event_rows() === [], 'sensitive metadata value is not stored');
}

// page_path must be only a path: no host, query string, hash, or protocol-relative URL.
foreach (['https://hybridautos.ae/rox/', '//hybridautos.ae/rox/', '/rox/?gclid=secret', '/rox/#form', 'rox/'] as $bad_path) {
    reset_form_event_state();
    $response = \LandingConfig\FormEvents\handle_form_event(form_event_request(['page_path' => $bad_path]));
    $assert($response->get_status() === 400, "non-path page_path is rejected: {$bad_path}");
}

reset_form_event_state();
$response = \LandingConfig\FormEvents\handle_form_event(form_event_request([
    'submission_id' => 'not-a-uuid',
]));
$assert($response->get_status() === 400, 'invalid submission UUID is rejected');

// Oversized requests and fields cannot turn the endpoint into a log sink.
reset_form_event_state();
$_SERVER['CONTENT_LENGTH'] = '5000';
$response = \LandingConfig\FormEvents\handle_form_event(form_event_request());
$assert($response->get_status() === 413, 'body larger than 4 KiB is rejected');
$assert(form_event_rows() === [], 'oversized body writes no row');

reset_form_event_state();
$response = \LandingConfig\FormEvents\handle_form_event(new WP_REST_Request(
    form_event_request()->get_params(),
    str_repeat('x', 5000)
));
$assert($response->get_status() === 413, 'raw body larger than 4 KiB is rejected without CONTENT_LENGTH');
$assert(form_event_rows() === [], 'oversized raw body writes no row');

reset_form_event_state();
$response = \LandingConfig\FormEvents\handle_form_event(form_event_request([
    'form_id' => str_repeat('a', 101),
]));
$assert($response->get_status() === 400, 'oversized metadata field is rejected instead of truncated');

// Rate limiting uses a one-way IP fingerprint in a transient; raw IP is never persisted.
reset_form_event_state();
update_option('lp_form_event_rate_limit_per_hour', 2);
$first = \LandingConfig\FormEvents\handle_form_event(form_event_request([
    'event_name' => 'form_started', 'event_detail' => '',
]));
$second = \LandingConfig\FormEvents\handle_form_event(form_event_request([
    'submission_id' => '22222222-2222-4222-8222-222222222222',
    'event_name' => 'form_started', 'event_detail' => '',
]));
$third = \LandingConfig\FormEvents\handle_form_event(form_event_request([
    'submission_id' => '33333333-3333-4333-8333-333333333333',
    'event_name' => 'form_started', 'event_detail' => '',
]));
$assert($first->get_status() === 201 && $second->get_status() === 201, 'configured rate-limit allows requests up to its boundary');
$assert($third->get_status() === 429, 'request beyond per-IP hourly limit returns 429');
$transient_keys = array_keys($GLOBALS['_mock_transients']);
$assert(!in_array('203.0.113.55', $transient_keys, true), 'rate-limit key does not contain raw IP as a standalone key');
$assert(!str_contains(implode('|', $transient_keys), '203.0.113.55'), 'rate-limit keys do not expose raw IP');

$lock_sql = array_values(array_filter(
    $GLOBALS['wpdb']->query_log,
    static fn(string $sql): bool => str_contains($sql, 'GET_LOCK(') || str_contains($sql, 'RELEASE_LOCK(')
));
$assert(count($lock_sql) >= 4, 'rate counter changes are guarded by named database locks');
$assert(str_contains($lock_sql[0] ?? '', ', 0)'), 'rate lock acquisition never waits for another request');
$assert(!str_contains(implode('|', $lock_sql), '203.0.113.55'), 'database lock names never expose raw IP');

reset_form_event_state();
$GLOBALS['_lr_force_lock_failure'] = true;
$contended = \LandingConfig\FormEvents\handle_form_event(form_event_request([
    'event_name' => 'form_started', 'event_detail' => '',
]));
$assert($contended->get_status() === 503, 'busy atomic counter lock drops telemetry without waiting');
$assert(form_event_rows() === [], 'lock contention never bypasses the rate counters');
$GLOBALS['_lr_force_lock_failure'] = false;

// A submission cannot generate an unbounded number of events even across IPs.
reset_form_event_state();
update_option('lp_form_event_rate_limit_per_hour', 100);
for ($i = 0; $i < 10; $i++) {
    $_SERVER['REMOTE_ADDR'] = '198.51.100.' . ($i + 1);
    $response = \LandingConfig\FormEvents\handle_form_event(form_event_request([
        'event_name' => 'submit_attempt', 'event_detail' => '',
    ]));
}
$_SERVER['REMOTE_ADDR'] = '198.51.100.99';
$overflow = \LandingConfig\FormEvents\handle_form_event(form_event_request([
    'event_name' => 'submit_attempt', 'event_detail' => '',
]));
$assert($response->get_status() === 201, 'first ten events for one submission are accepted');
$assert($overflow->get_status() === 429, 'eleventh event for one submission is rejected');
$submission_keys = array_values(array_filter(
    array_keys($GLOBALS['_mock_transient_ttls']),
    static fn(string $key): bool => str_starts_with($key, 'landing_form_event_submission_')
));
$assert(
    count($submission_keys) === 1
        && ($GLOBALS['_mock_transient_ttls'][$submission_keys[0]] ?? 0) === 30 * DAY_IN_SECONDS,
    'per-submission event ceiling remains enforced for the full retention window'
);

// Retention removes rows older than 30 days and is scheduled daily.
reset_form_event_state();
lr_queue_query_count(5000);
lr_queue_query_count(5000);
lr_queue_query_count(7);
$deleted = \LandingConfig\FormEvents\cleanup_expired_form_events();
$assert($deleted === 10007, 'retention cleanup drains all expired batches');
$cleanup_sql = implode("\n", $GLOBALS['wpdb']->query_log);
$assert(str_contains($cleanup_sql, 'DELETE FROM `wp_landing_form_events`'), 'retention cleanup targets only form events');
$assert(str_contains($cleanup_sql, 'created_at <'), 'retention cleanup deletes by age');
$delete_queries = array_values(array_filter(
    $GLOBALS['wpdb']->query_log,
    static fn(string $sql): bool => str_contains($sql, 'DELETE FROM `wp_landing_form_events`')
));
$assert(count($delete_queries) === 3, 'retention cleanup continues until the final partial batch');
$assert(str_contains($cleanup_sql, 'landing_form_event_global_%'), 'retention also scans durable anonymous rate-limit buckets');

\LandingConfig\FormEvents\ensure_cleanup_scheduled();
$assert(isset($GLOBALS['_lr_next_scheduled']['landing_config_cleanup_form_events']), '30-day cleanup is scheduled');

$plugin_bootstrap = file_get_contents(__DIR__ . '/../mu-plugin/landing-config/landing-config.php');
$assert(str_contains($plugin_bootstrap, "includes/rest-form-events.php"), 'plugin bootstrap loads the public form-event endpoint');
$assert(str_contains($plugin_bootstrap, "includes/admin-form-events.php"), 'plugin bootstrap loads the administrator event view');

echo $failures === 0 ? "PASS: {$tests} form event assertions\n" : "FAILURES: {$failures}/{$tests}\n";
exit($failures === 0 ? 0 : 1);
