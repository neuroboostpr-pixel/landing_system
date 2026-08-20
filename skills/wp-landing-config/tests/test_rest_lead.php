<?php
require_once __DIR__ . '/fixtures/wp-bootstrap.php';
require_once __DIR__ . '/../mu-plugin/landing-config/includes/db.php';
require_once __DIR__ . '/../mu-plugin/landing-config/includes/encryption.php';
require_once __DIR__ . '/../mu-plugin/landing-config/includes/helpers.php';
require_once __DIR__ . '/../mu-plugin/landing-config/includes/cascade.php';
require_once __DIR__ . '/../mu-plugin/landing-config/includes/integrations.php';
require_once __DIR__ . '/../mu-plugin/landing-config/includes/lead-delivery-worker.php';
require_once __DIR__ . '/../mu-plugin/landing-config/includes/rest-lead.php';

use function LandingConfig\REST\handle_lead;

$failures = 0;
$tests = 0;

function assert_test($condition, $message) {
    global $failures, $tests;
    $tests++;
    if (!$condition) {
        echo "FAIL: $message\n";
        $failures++;
    }
}

function inserted_lead_rows(): array {
    return array_values(array_filter(
        $GLOBALS['_mock_inserted_leads'],
        static fn($row) => str_ends_with((string)($row['table'] ?? ''), 'landing_leads')
    ));
}

// Reset rate-limit before each batch
function reset_state() {
    $GLOBALS['_mock_inserted_leads'] = [];
    $GLOBALS['_mock_mail_sent'] = [];
    $GLOBALS['_mock_transients'] = [];
    $GLOBALS['_mock_actions_fired'] = [];
    $GLOBALS['_mock_options'] = [];
    $_SERVER['REMOTE_ADDR'] = '203.0.113.1';
    $_SERVER['HTTP_USER_AGENT'] = 'test-agent';
}

// Test 1: missing phone+email → 400
reset_state();
$req = new WP_REST_Request(['name' => 'Bob', 'phone' => '', 'email' => '']);
$resp = handle_lead($req);
assert_test(
    $resp->get_status() === 400,
    "missing phone+email returns 400 (got: " . $resp->get_status() . ")"
);
assert_test(
    count(inserted_lead_rows()) === 0,
    "no lead insert when validation fails"
);

// Test 2: honeypot field filled → 400 (silently rejects bots)
reset_state();
$req = new WP_REST_Request(['name' => 'Bob', 'phone' => '+71111111111', 'website' => 'spam-bot-trap']);
$resp = handle_lead($req);
assert_test(
    $resp->get_status() === 400,
    "honeypot 'website' field filled returns 400"
);

// Test 3: valid request inserts lead
reset_state();
set_mock_current_blog_id(1);
$req = new WP_REST_Request([
    'name' => 'Alice',
    'phone' => '+79991234567',
    'email' => 'alice@example.com',
    'message' => 'Test message',
    'source_block' => 'hero',
    'utm_source' => 'google',
    'pd_consent' => '1',
]);
$resp = handle_lead($req);
assert_test(
    $resp->get_status() === 200,
    "valid request returns 200 (got: " . $resp->get_status() . ")"
);
assert_test(
    count(inserted_lead_rows()) === 1,
    "exactly 1 lead insert"
);
$inserted = inserted_lead_rows()[0];
assert_test(
    $inserted['data']['name'] === 'Alice' &&
    $inserted['data']['phone'] === '+79991234567' &&
    $inserted['data']['email'] === 'alice@example.com',
    "inserted data has name/phone/email"
);
assert_test(
    $inserted['data']['source_block'] === 'hero' &&
    $inserted['data']['utm_source'] === 'google',
    "inserted data has source_block + utm_source"
);
assert_test(
    $resp->get_data()['ok'] === true && isset($resp->get_data()['lead_id']),
    "response includes ok=true + lead_id"
);

// Test 4: the endpoint never sends a second, hard-coded fallback email.
// Delivery belongs only to configured integrations.
assert_test(
    count($GLOBALS['_mock_mail_sent']) === 0,
    "no hard-coded admin fallback email is sent"
);

// Test 4b: landing_config_lead_received action fired
$fired_hooks = array_column($GLOBALS['_mock_actions_fired'], 'hook');
assert_test(
    in_array('landing_config_lead_received', $fired_hooks, true),
    "action 'landing_config_lead_received' fired on success"
);

// A database write is not confirmed unless MySQL returns a positive row id.
class MockWpdbZeroLeadId extends MockWpdbInsert {
    public function insert($table, $data, $formats = null) {
        $result = parent::insert($table, $data, $formats);
        if (str_ends_with((string) $table, 'landing_leads')) {
            $this->insert_id = 0;
        }
        return $result;
    }
}
$normal_wpdb = $GLOBALS['wpdb'];
$GLOBALS['wpdb'] = new MockWpdbZeroLeadId();
reset_state();
$resp = handle_lead(new WP_REST_Request([
    'name' => 'NoId',
    'phone' => '+971501234567',
    'pd_consent' => '1',
]));
assert_test($resp->get_status() === 500, 'lead insert without a positive id returns 500');
assert_test(($resp->get_data()['ok'] ?? true) === false, 'lead insert without a positive id never returns ok=true');
assert_test(!isset($resp->get_data()['lead_id']), 'failed response never exposes a false positive lead id');
$GLOBALS['wpdb'] = $normal_wpdb;

// Test 5: writes to per-blog table
reset_state();
set_mock_current_blog_id(2);
$req = new WP_REST_Request([
    'name' => 'BlogTwo', 'phone' => '+79993334444', 'email' => 'b2@x.com', 'pd_consent' => '1',
]);
handle_lead($req);
$blog_two_rows = inserted_lead_rows();
assert_test(
    count($blog_two_rows) === 1 && $blog_two_rows[0]['table'] === 'wp_2_landing_leads',
    "insert goes to wp_<bid>_landing_leads (got: " . ($blog_two_rows[0]['table'] ?? 'none') . ")"
);

// Test 6: rate limit — 11th request from same IP within window returns 429
reset_state();
set_mock_current_blog_id(1);
for ($i = 0; $i < 10; $i++) {
    $req = new WP_REST_Request(['name' => "User$i", 'phone' => '+71000000' . sprintf('%03d', $i), 'pd_consent' => '1']);
    $resp = handle_lead($req);
    assert_test($resp->get_status() === 200, "request $i stays below the ten-per-hour limit");
}
$req = new WP_REST_Request(['name' => 'Eleventh', 'phone' => '+71000000011', 'pd_consent' => '1']);
$resp = handle_lead($req);
assert_test(
    $resp->get_status() === 429,
    "11th request from same IP within hour returns 429 (got: " . $resp->get_status() . ")"
);

// Test 7: rate limit is per-IP (different IP not blocked)
$_SERVER['REMOTE_ADDR'] = '198.51.100.2';
$req = new WP_REST_Request(['name' => 'OtherIP', 'phone' => '+79995556677', 'pd_consent' => '1']);
$resp = handle_lead($req);
assert_test(
    $resp->get_status() === 200,
    "different IP not affected by first IP's rate limit (got: " . $resp->get_status() . ")"
);

// T_PD_1..5: explicit consent is mandatory. The browser must never fabricate it.

function reset_pd() {
    $GLOBALS['_mock_inserted_leads'] = [];
    $GLOBALS['_mock_transients'] = [];  // сброс rate limit
    $GLOBALS['_mock_options'] = [];
    $_SERVER['REMOTE_ADDR'] = '10.0.0.1';
}

function pd_request($overrides = []) {
    $defaults = [
        'name'        => 'Test',
        'phone'       => '+71234567890',
        'email'       => 'test@example.com',
        'pd_consent'  => '1',
        'website'     => '',  // honeypot empty
    ];
    return new WP_REST_Request(array_merge($defaults, $overrides));
}

// T_PD_1: с pd_consent=1 → 200, pd_consent_granted_at не NULL
reset_pd();
set_mock_current_blog_id(1);
$req = pd_request();
$resp = \LandingConfig\REST\handle_lead($req);
$data = $resp->get_data();
assert_test($data['ok'] === true, 'T_PD_1a returns ok=true');
$rows = inserted_lead_rows();
assert_test(count($rows) === 1, 'T_PD_1b 1 lead inserted');
assert_test(!empty($rows[0]['data']['pd_consent_granted_at']), 'T_PD_1c pd_consent_granted_at populated');

// T_PD_2: missing consent is rejected after the early audit, before lead creation.
reset_pd();
$req = pd_request();
$params = $req->get_params();
unset($params['pd_consent']);
$req2 = new WP_REST_Request($params);
$resp = \LandingConfig\REST\handle_lead($req2);
$data = $resp->get_data();
assert_test($resp->get_status() === 400, 'T_PD_2a missing pd_consent is rejected');
assert_test($data['ok'] === false, 'T_PD_2b missing pd_consent returns ok=false');
assert_test(($data['error'] ?? '') === 'pd_consent', 'T_PD_2c missing pd_consent has stable error code');
assert_test(count(inserted_lead_rows()) === 0, 'T_PD_2d missing pd_consent creates no lead');

// T_PD_3: empty consent is rejected.
reset_pd();
$resp = \LandingConfig\REST\handle_lead(pd_request(['pd_consent' => '']));
assert_test($resp->get_status() === 400, 'T_PD_3 empty pd_consent is rejected');

// T_PD_4: false consent is rejected.
reset_pd();
$resp = \LandingConfig\REST\handle_lead(pd_request(['pd_consent' => '0']));
assert_test($resp->get_status() === 400, 'T_PD_4 pd_consent=0 is rejected');

// T_PD_5: timestamp в пределах текущей минуты
reset_pd();
set_mock_current_blog_id(1);
$ts_before = time();
\LandingConfig\REST\handle_lead(pd_request());
$rows = inserted_lead_rows();
$ts_granted = strtotime($rows[0]['data']['pd_consent_granted_at']);
$ts_after = time();
assert_test($ts_granted >= $ts_before && $ts_granted <= $ts_after + 1,
    "T_PD_5 timestamp within range (ts_before=$ts_before, ts_granted=$ts_granted, ts_after=$ts_after)");

// A browser-generated submission UUID links anonymous pre-submit events to the
// early audit row and final lead without making telemetry required for capture.
reset_pd();
$submission_id = '44444444-4444-4444-8444-444444444444';
$response = \LandingConfig\REST\handle_lead(pd_request(['submission_id' => $submission_id]));
$audit_rows = array_values(array_filter(
    $GLOBALS['_mock_inserted_leads'],
    static fn(array $row): bool => str_ends_with((string) ($row['table'] ?? ''), 'landing_lead_audit')
));
$lead_rows = inserted_lead_rows();
assert_test($response->get_status() === 200, 'submission UUID does not disrupt lead capture');
assert_test(($audit_rows[0]['data']['submission_id'] ?? null) === $submission_id, 'audit row stores submission UUID');
assert_test(($lead_rows[0]['data']['submission_id'] ?? null) === $submission_id, 'lead row stores the same submission UUID');

// Telemetry is optional: a malformed optional UUID is discarded, never used as
// a reason to lose an otherwise valid contact.
reset_pd();
$response = \LandingConfig\REST\handle_lead(pd_request(['submission_id' => 'broken-client-id']));
$lead_rows = inserted_lead_rows();
assert_test($response->get_status() === 200, 'malformed optional UUID never blocks a valid lead');
assert_test(
    array_key_exists('submission_id', $lead_rows[0]['data'] ?? [])
        && $lead_rows[0]['data']['submission_id'] === null,
    'malformed UUID is not stored'
);

// Active reCAPTCHA code is intentionally absent. Historical DB columns may remain
// additive, but no Google verification or score-based rejection may run.
$rest_source = file_get_contents(__DIR__ . '/../mu-plugin/landing-config/includes/rest-lead.php');
assert_test(\LandingConfig\REST\get_global_rate_limit() === 500, 'inherited global technical safeguard remains 500 per hour');
assert_test(!str_contains($rest_source, "expected lead volume"), 'technical safeguard is not presented as validated business traffic');
assert_test(str_contains($rest_source, 'inherited technical safeguard'), 'global ceiling is explicitly documented as a technical safeguard');
assert_test(!str_contains($rest_source, 'function verify_recaptcha'), 'reCAPTCHA verifier is removed');
assert_test(!str_contains($rest_source, 'google.com/recaptcha'), 'REST endpoint never calls Google reCAPTCHA');
assert_test(!str_contains($rest_source, "'recaptcha_failed'"), 'REST endpoint has no reCAPTCHA rejection path');
assert_test(!str_contains($rest_source, 'send_admin_email('), 'hard-coded duplicate email sender is removed');

echo "\n$tests tests, $failures failures\n";
exit($failures > 0 ? 1 : 0);
