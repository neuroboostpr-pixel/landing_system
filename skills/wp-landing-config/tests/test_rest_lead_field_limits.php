<?php
require_once __DIR__ . '/fixtures/wp-bootstrap.php';
require_once __DIR__ . '/../mu-plugin/landing-config/includes/db.php';
require_once __DIR__ . '/../mu-plugin/landing-config/includes/encryption.php';
require_once __DIR__ . '/../mu-plugin/landing-config/includes/helpers.php';
require_once __DIR__ . '/../mu-plugin/landing-config/includes/cascade.php';
require_once __DIR__ . '/../mu-plugin/landing-config/includes/integrations.php';
require_once __DIR__ . '/../mu-plugin/landing-config/adapters/AdapterInterface.php';
require_once __DIR__ . '/../mu-plugin/landing-config/adapters/EmailAdapter.php';
require_once __DIR__ . '/../mu-plugin/landing-config/includes/rest-lead.php';

$failures = 0;
$tests = 0;

function assert_field_limit($condition, string $message): void {
    global $failures, $tests;
    $tests++;
    if (!$condition) {
        echo "FAIL: $message\n";
        $failures++;
    }
}

function reset_field_limit_state(MockWpdbInsert $wpdb): void {
    $GLOBALS['wpdb'] = $wpdb;
    $GLOBALS['_mock_inserted_leads'] = [];
    $GLOBALS['_mock_mail_sent'] = [];
    $GLOBALS['_mock_transients'] = [];
    $GLOBALS['_mock_actions_fired'] = [];
    $GLOBALS['_mock_options'] = [];
    $GLOBALS['_mock_posts'] = [];
    $GLOBALS['_mock_post_meta'] = [];
    $GLOBALS['_mock_next_post_id'] = 1;
    $_SERVER['REMOTE_ADDR'] = '203.0.113.1';
    $_SERVER['HTTP_USER_AGENT'] = 'test-agent';
    set_mock_current_blog_id(1);
}

function rows_with_suffix(string $suffix): array {
    return array_values(array_filter(
        $GLOBALS['_mock_inserted_leads'],
        static fn(array $row): bool => str_ends_with((string) ($row['table'] ?? ''), $suffix)
    ));
}

/**
 * Mirrors the field-length rejection performed by WordPress wpdb before SQL is
 * sent to MySQL. VARCHAR/CHAR limits are characters; TEXT limits are bytes.
 */
class LengthAwareLeadWpdb extends MockWpdbInsert {
    public string $last_error = '';
    public array $insert_attempts = [];
    public array $update_attempts = [];

    private function limits_for(string $table): array {
        if (str_ends_with($table, 'landing_lead_audit')) {
            return [
                'submission_id' => ['chars', 36],
                'ip' => ['chars', 45],
                'user_agent' => ['bytes', 65535],
                'name' => ['chars', 191],
                'phone' => ['chars', 64],
                'email' => ['chars', 191],
                'message' => ['bytes', 65535],
                'source_block' => ['bytes', 65535],
                'utm_source' => ['chars', 191],
                'utm_medium' => ['chars', 191],
                'utm_campaign' => ['chars', 191],
                'roistat_visit' => ['chars', 64],
                'pd_consent' => ['chars', 8],
                'blocked_by' => ['chars', 64],
                'block_detail' => ['chars', 255],
            ];
        }

        if (str_ends_with($table, 'landing_leads')) {
            return [
                'submission_id' => ['chars', 36],
                'name' => ['chars', 191],
                'phone' => ['chars', 64],
                'email' => ['chars', 191],
                'message' => ['bytes', 65535],
                'source_block' => ['bytes', 65535],
                'utm_source' => ['chars', 191],
                'utm_medium' => ['chars', 191],
                'utm_campaign' => ['chars', 191],
                'utm_term' => ['chars', 191],
                'utm_content' => ['chars', 191],
                'roistat_visit' => ['chars', 64],
                'ip' => ['chars', 45],
                'user_agent' => ['bytes', 65535],
                'processed_status' => ['chars', 32],
            ];
        }

        return [];
    }

    public function insert($table, $data, $formats = null) {
        $this->insert_attempts[] = ['table' => $table, 'data' => $data];
        $this->last_error = '';

        foreach ($this->limits_for((string) $table) as $field => [$type, $limit]) {
            if (!isset($data[$field])) {
                continue;
            }
            $value = (string) $data[$field];
            $length = $type === 'bytes' ? strlen($value) : mb_strlen($value, 'UTF-8');
            if ($length > $limit) {
                $this->last_error = "Processing the value for field $field failed: value too long";
                $this->insert_id = 0;
                return false;
            }
        }

        return parent::insert($table, $data, $formats);
    }

    public function update($table, $data, $where, $formats = null, $where_formats = null) {
        $this->update_attempts[] = compact('table', 'data', 'where');
        return parent::update($table, $data, $where, $formats, $where_formats);
    }
}

// One oversized field currently makes wpdb reject the whole audit/lead row.
// Every submitted field must be made schema-safe before either INSERT.
$wpdb = new LengthAwareLeadWpdb();
reset_field_limit_state($wpdb);
$_SERVER['REMOTE_ADDR'] = str_repeat('1', 46);
$_SERVER['HTTP_USER_AGENT'] = str_repeat('A', 65536);
$email_192 = str_repeat('e', 184) . '@test.io';
assert_field_limit(strlen($email_192) === 192, 'test email fixture is exactly 192 characters');
$response = \LandingConfig\REST\handle_lead(new WP_REST_Request([
    'name' => str_repeat('N', 192),
    'phone' => str_repeat('7', 65),
    'email' => $email_192,
    'message' => str_repeat('M', 65536),
    'source_block' => str_repeat('S', 65536),
    'utm_source' => str_repeat('a', 192),
    'utm_medium' => str_repeat('b', 192),
    'utm_campaign' => str_repeat('c', 192),
    'utm_term' => str_repeat('d', 192),
    'utm_content' => str_repeat('e', 192),
    'roistat_visit' => str_repeat('r', 65),
    'pd_consent' => '1',
]));
$audit_rows = rows_with_suffix('landing_lead_audit');
$lead_rows = rows_with_suffix('landing_leads');
assert_field_limit($response->get_status() === 200, 'oversized optional data does not lose the contact');
assert_field_limit(count($audit_rows) === 1, 'schema-safe early audit row is stored');
assert_field_limit(count($lead_rows) === 1, 'schema-safe lead row is stored');
if (isset($lead_rows[0]['data'])) {
    $stored = $lead_rows[0]['data'];
    foreach (['name' => 191, 'phone' => 64, 'email' => 191, 'utm_source' => 191,
        'utm_medium' => 191, 'utm_campaign' => 191, 'utm_term' => 191,
        'utm_content' => 191, 'roistat_visit' => 64, 'ip' => 45] as $field => $limit) {
        assert_field_limit(
            mb_strlen((string) ($stored[$field] ?? ''), 'UTF-8') <= $limit,
            "$field is normalized to its $limit-character database limit"
        );
    }
    foreach (['message', 'source_block', 'user_agent'] as $field) {
        assert_field_limit(
            strlen((string) ($stored[$field] ?? '')) <= 65535,
            "$field is normalized to the 65535-byte TEXT limit"
        );
    }
}

// TEXT is byte-limited, while VARCHAR is character-limited. Multibyte input
// must remain valid UTF-8 after truncation.
$wpdb = new LengthAwareLeadWpdb();
reset_field_limit_state($wpdb);
$_SERVER['HTTP_USER_AGENT'] = str_repeat("☃", 21846); // 65,538 bytes
$response = \LandingConfig\REST\handle_lead(new WP_REST_Request([
    'phone' => '+971501234567',
    'message' => str_repeat("🚗", 16384),       // 65,536 bytes
    'source_block' => str_repeat("🚗", 16384),  // 65,536 bytes
    'utm_campaign' => str_repeat("🚗", 192),
    'pd_consent' => '1',
]));
$lead_rows = rows_with_suffix('landing_leads');
assert_field_limit($response->get_status() === 200, 'multibyte metadata cannot lose the contact');
assert_field_limit(count($lead_rows) === 1, 'multibyte lead is stored exactly once');
if (isset($lead_rows[0]['data'])) {
    $stored = $lead_rows[0]['data'];
    assert_field_limit(mb_strlen($stored['utm_campaign'], 'UTF-8') === 191, 'VARCHAR keeps 191 complete emoji');
    foreach (['message', 'source_block', 'user_agent'] as $field) {
        assert_field_limit(strlen($stored[$field]) <= 65535, "$field respects its byte limit");
        assert_field_limit(preg_match('//u', $stored[$field]) === 1, "$field remains valid UTF-8");
    }
}

// Defence in depth: if the first lead INSERT still fails, retry once with
// contact fields intact and all optional request/attribution metadata blank.
class RejectFirstLeadInsertWpdb extends LengthAwareLeadWpdb {
    public int $lead_attempt_count = 0;

    public function insert($table, $data, $formats = null) {
        if (str_ends_with((string) $table, 'landing_leads')) {
            $this->lead_attempt_count++;
            if ($this->lead_attempt_count === 1) {
                $this->insert_attempts[] = ['table' => $table, 'data' => $data];
                $this->last_error = 'WordPress database error: Processing the value for the following field failed: source_block. The supplied value may be too long or contains invalid data.';
                $this->insert_id = 0;
                return false;
            }
        }
        return parent::insert($table, $data, $formats);
    }
}

$wpdb = new RejectFirstLeadInsertWpdb();
reset_field_limit_state($wpdb);
\LandingConfig\Integrations\save_integration(
    'email',
    'Fallback delivery test',
    '',
    ['to' => 'leads@example.test', 'subject' => 'Fallback lead'],
    false,
    1
);
$response = \LandingConfig\REST\handle_lead(new WP_REST_Request([
    'name' => 'Fallback Contact',
    'phone' => '+971501111111',
    'email' => 'fallback@example.com',
    'message' => 'Please call me',
    'source_block' => 'https://example.test/?gclid=ad-click',
    'utm_source' => 'google',
    'utm_medium' => 'cpc',
    'utm_campaign' => 'rox',
    'utm_term' => 'hybrid car',
    'utm_content' => 'hero',
    'roistat_visit' => '12345',
    'pd_consent' => '1',
]));
$lead_rows = rows_with_suffix('landing_leads');
assert_field_limit($response->get_status() === 200, 'one metadata-free retry rescues a valid contact');
assert_field_limit($wpdb->lead_attempt_count === 2, 'lead INSERT is attempted at most twice');
assert_field_limit(count($lead_rows) === 1, 'fallback creates exactly one stored lead');
if (isset($lead_rows[0]['data'])) {
    $stored = $lead_rows[0]['data'];
    assert_field_limit($stored['phone'] === '+971501111111', 'fallback preserves the phone');
    assert_field_limit($stored['email'] === 'fallback@example.com', 'fallback preserves the email');
    assert_field_limit($stored['message'] === 'Please call me', 'fallback preserves the message');
    foreach (['source_block', 'utm_source', 'utm_medium', 'utm_campaign', 'utm_term',
        'utm_content', 'roistat_visit', 'ip', 'user_agent'] as $field) {
        assert_field_limit(($stored[$field] ?? null) === '', "fallback clears optional metadata $field");
    }
}
$received_actions = array_values(array_filter(
    $GLOBALS['_mock_actions_fired'],
    static fn(array $action): bool => ($action['hook'] ?? '') === 'landing_config_lead_received'
));
assert_field_limit(count($received_actions) === 1, 'fallback dispatches the saved lead exactly once');
assert_field_limit(
    (($received_actions[0]['args'][1]['utm_source'] ?? null) === ''),
    'integrations receive the metadata-free row that was actually saved'
);
\LandingConfig\REST\dispatch_all_integrations([
    'id' => (int)($response->get_data()['lead_id'] ?? 0),
] + (array)($received_actions[0]['args'][1] ?? []));
assert_field_limit(count($GLOBALS['_mock_mail_sent']) === 1, 'active email integration receives fallback lead exactly once');
$mail_body = (string) ($GLOBALS['_mock_mail_sent'][0]['body'] ?? '');
assert_field_limit(str_contains($mail_body, '+971501111111'), 'integration receives the saved phone');
assert_field_limit(str_contains($mail_body, 'fallback@example.com'), 'integration receives the saved email');
assert_field_limit(str_contains($mail_body, "Блок:     \n"), 'integration receives the empty source value actually stored');
assert_field_limit(str_contains($mail_body, "UTM:      src= med= cmp=\n"), 'integration receives the empty UTM values actually stored');

// A generic database failure can be ambiguous: the server may have committed
// the first INSERT before the connection failed. Retrying that case without a
// unique submission constraint could duplicate the contact.
class RejectAmbiguousLeadInsertWpdb extends LengthAwareLeadWpdb {
    public int $lead_attempt_count = 0;

    public function insert($table, $data, $formats = null) {
        if (str_ends_with((string) $table, 'landing_leads')) {
            $this->lead_attempt_count++;
            if ($this->lead_attempt_count === 1) {
                $this->insert_attempts[] = ['table' => $table, 'data' => $data];
                $this->last_error = 'Lost connection while writing source_block metadata';
                $this->insert_id = 0;
                return false;
            }
        }
        return parent::insert($table, $data, $formats);
    }
}

$wpdb = new RejectAmbiguousLeadInsertWpdb();
reset_field_limit_state($wpdb);
$response = \LandingConfig\REST\handle_lead(new WP_REST_Request([
    'phone' => '+971504444444',
    'source_block' => 'hero',
    'utm_source' => 'google',
    'pd_consent' => '1',
]));
assert_field_limit($response->get_status() === 500, 'ambiguous DB failure is reported instead of blindly retried');
assert_field_limit($wpdb->lead_attempt_count === 1, 'generic DB failure is never retried');
assert_field_limit(count(rows_with_suffix('landing_leads')) === 0, 'test does not create a duplicate after ambiguous failure');

// A failed diagnostic audit must not reuse a stale wpdb insert_id or interfere
// with the real contact insert.
class RejectAuditInsertWpdb extends LengthAwareLeadWpdb {
    public function insert($table, $data, $formats = null) {
        if (str_ends_with((string) $table, 'landing_lead_audit')) {
            $this->last_error = 'forced audit insert failure';
            return false;
        }
        return parent::insert($table, $data, $formats);
    }
}

$wpdb = new RejectAuditInsertWpdb();
$wpdb->insert_id = 777;
reset_field_limit_state($wpdb);
$response = \LandingConfig\REST\handle_lead(new WP_REST_Request([
    'phone' => '+971502222222',
    'pd_consent' => '1',
]));
$audit_updates = array_values(array_filter(
    $wpdb->update_attempts,
    static fn(array $attempt): bool => str_ends_with((string) ($attempt['table'] ?? ''), 'landing_lead_audit')
));
assert_field_limit($response->get_status() === 200, 'audit failure never blocks contact storage');
assert_field_limit(count(rows_with_suffix('landing_leads')) === 1, 'contact is saved when audit storage is unavailable');
assert_field_limit(count($audit_updates) === 0, 'failed audit never reuses a stale insert id');

// Normalization is for safe storage only. It must not turn decorated or
// malformed consent input into the exact affirmative value required by policy.
$wpdb = new LengthAwareLeadWpdb();
reset_field_limit_state($wpdb);
$response = \LandingConfig\REST\handle_lead(new WP_REST_Request([
    'phone' => '+971503333333',
    'pd_consent' => '<b>1</b>',
]));
assert_field_limit($response->get_status() === 400, 'decorated consent is not normalized into permission');
assert_field_limit(count(rows_with_suffix('landing_leads')) === 0, 'invalid consent never creates a lead');

// Diagnostic text has its own VARCHAR bounds and must not make the audit UPDATE
// fail while recording the reason for a lead-storage error.
$wpdb = new LengthAwareLeadWpdb();
reset_field_limit_state($wpdb);
$normalized = \LandingConfig\REST\normalize_lead_payload(
    ['phone' => '+971505555555', 'pd_consent' => '1'],
    '203.0.113.1',
    'test-agent'
);
$audit_id = \LandingConfig\REST\audit_log_insert($normalized);
\LandingConfig\REST\audit_log_block($audit_id, str_repeat('r', 65), str_repeat('d', 300));
$audit_rows = rows_with_suffix('landing_lead_audit');
assert_field_limit(mb_strlen((string) ($audit_rows[0]['data']['blocked_by'] ?? ''), 'UTF-8') === 64, 'audit reason respects VARCHAR(64)');
assert_field_limit(mb_strlen((string) ($audit_rows[0]['data']['block_detail'] ?? ''), 'UTF-8') === 255, 'audit detail respects VARCHAR(255)');

echo "\n$tests tests, $failures failures\n";
exit($failures > 0 ? 1 : 0);
