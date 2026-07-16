<?php
require_once __DIR__ . '/fixtures/wp-bootstrap.php';
require_once __DIR__ . '/../mu-plugin/landing-config/includes/db.php';

use function LandingConfig\DB\maybe_install_or_migrate;
use function LandingConfig\DB\get_leads_table_name;
use function LandingConfig\DB\get_lead_log_table_name;
use function LandingConfig\DB\get_form_events_table_name;
use function LandingConfig\DB\get_monitor_alerts_table_name;

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

// Test 1: get_leads_table_name returns blog-specific name
set_mock_current_blog_id(2);
assert_test(
    get_leads_table_name() === 'wp_2_landing_leads',
    "get_leads_table_name() returns wp_2_landing_leads for blog_id=2 (got: " . get_leads_table_name() . ")"
);

// Test 2: get_leads_table_name returns base for blog 1
set_mock_current_blog_id(1);
assert_test(
    get_leads_table_name() === 'wp_landing_leads',
    "get_leads_table_name() returns wp_landing_leads for blog_id=1 (got: " . get_leads_table_name() . ")"
);

// Test 3: get_lead_log_table_name returns blog-specific name
set_mock_current_blog_id(3);
assert_test(
    get_lead_log_table_name() === 'wp_3_landing_lead_log',
    "get_lead_log_table_name() returns wp_3_landing_lead_log for blog_id=3 (got: " . get_lead_log_table_name() . ")"
);

// Privacy-safe form events are isolated per site just like leads.
set_mock_current_blog_id(2);
assert_test(
    function_exists('LandingConfig\\DB\\get_form_events_table_name'),
    'get_form_events_table_name() is defined'
);
assert_test(
    function_exists('LandingConfig\\DB\\get_form_events_table_name')
        && get_form_events_table_name() === 'wp_2_landing_form_events',
    "get_form_events_table_name() returns the blog-specific form events table"
);

// Test 4: maybe_install_or_migrate triggers dbDelta when version mismatch
$GLOBALS['_mock_dbdelta_calls'] = [];
$GLOBALS['_mock_site_meta']['landing_config_db_version'] = '';  // not installed yet
maybe_install_or_migrate();
assert_test(
    count($GLOBALS['_mock_dbdelta_calls']) >= 2,  // at least leads + lead_log per blog
    "maybe_install_or_migrate triggers dbDelta calls (got: " . count($GLOBALS['_mock_dbdelta_calls']) . ")"
);
foreach ([1, 2, 3] as $blog_id) {
    assert_test(
        preg_match('/^\d{4}-\d{2}-\d{2} \d{2}:\d{2}:\d{2}$/', (string)($GLOBALS['_mock_options'][$blog_id]['landing_delivery_async_boundary'] ?? '')) === 1,
        "migration records a one-time UTC async-delivery boundary for blog {$blog_id} before reconciliation"
    );
}

// Test 5: maybe_install_or_migrate is idempotent — second call with same version is no-op
$first_count = count($GLOBALS['_mock_dbdelta_calls']);
maybe_install_or_migrate();
assert_test(
    count($GLOBALS['_mock_dbdelta_calls']) === $first_count,
    "maybe_install_or_migrate is no-op when version matches (call count unchanged)"
);

// A site that already has the target schema version but missed the option must
// fail safely by establishing the boundary now, without rerunning dbDelta.
$GLOBALS['_mock_options'] = [];
$before_boundary_backfill = count($GLOBALS['_mock_dbdelta_calls']);
maybe_install_or_migrate();
assert_test(
    !empty($GLOBALS['_mock_options'][1]['landing_delivery_async_boundary'])
        && !empty($GLOBALS['_mock_options'][2]['landing_delivery_async_boundary'])
        && !empty($GLOBALS['_mock_options'][3]['landing_delivery_async_boundary']),
    'boundary is backfilled for every blog even when database version is already current'
);
assert_test(count($GLOBALS['_mock_dbdelta_calls']) === $before_boundary_backfill,
    'boundary backfill does not rerun schema migration');

// Test 6: schema SQL includes required columns
$sql = $GLOBALS['_mock_dbdelta_calls'][0] ?? '';
assert_test(
    strpos($sql, 'id BIGINT') !== false &&
    strpos($sql, 'created_at') !== false &&
    strpos($sql, 'name VARCHAR') !== false &&
    strpos($sql, 'phone VARCHAR') !== false &&
    strpos($sql, 'email VARCHAR') !== false,
    "leads table schema includes id, created_at, name, phone, email"
);

// Test 7: dbDelta calls cover all multisite blogs (not just one)
$GLOBALS['_mock_dbdelta_calls'] = [];
$GLOBALS['_mock_site_meta']['landing_config_db_version'] = '';
maybe_install_or_migrate();
$all_sql = implode("\n", $GLOBALS['_mock_dbdelta_calls']);
assert_test(
    strpos($all_sql, 'wp_2_landing_leads') !== false &&
        strpos($all_sql, 'wp_3_landing_leads') !== false,
    "maybe_install_or_migrate creates tables for blogs 2 and 3, not just blog 1"
);

// Test 8: single-site path (is_multisite=false) still calls dbDelta
$GLOBALS['_mock_dbdelta_calls'] = [];
$GLOBALS['_mock_site_meta']['landing_config_db_version'] = '';
$GLOBALS['_mock_is_multisite'] = false;
set_mock_current_blog_id(1);
maybe_install_or_migrate();
assert_test(
    count($GLOBALS['_mock_dbdelta_calls']) === 6,
    "single-site path calls dbDelta six times (including privacy-safe monitoring), got: " . count($GLOBALS['_mock_dbdelta_calls'])
);
$GLOBALS['_mock_is_multisite'] = true; // reset

// T_PD_DB_1: pd_consent_granted_at column declared in landing_leads CREATE TABLE
$leads_sql = $GLOBALS['_mock_dbdelta_calls'][0] ?? '';
assert_test(strpos($leads_sql, 'pd_consent_granted_at') !== false,
    'T_PD_DB_1 column pd_consent_granted_at declared in landing_leads');
assert_test(strpos($leads_sql, 'DATETIME NULL') !== false,
    'T_PD_DB_2 type is DATETIME NULL');

// Real Google Ads landing URLs regularly exceed 191 characters. Both the
// earliest audit row and the saved lead must accept the full URL so the
// contact is never rejected because of attribution metadata.
$schema_sql = implode("\n", $GLOBALS['_mock_dbdelta_calls']);
assert_test(
    substr_count($schema_sql, 'source_block TEXT NOT NULL') === 2,
    'source_block uses TEXT in both leads and audit tables'
);
assert_test(
    strpos($schema_sql, 'source_block VARCHAR(191)') === false,
    'source_block no longer has the 191-character advertising URL limit'
);

assert_test(
    str_contains($schema_sql, 'CREATE TABLE wp_landing_form_events'),
    'schema creates the standalone form events table'
);
assert_test(
    substr_count($schema_sql, 'submission_id CHAR(36)') === 4,
    'submission_id is present in leads, audit, form events, and monitor incidents for correlation'
);
assert_test(
    !str_contains($schema_sql, 'UNIQUE KEY submission_id'),
    'correlation UUID is not a unique constraint that could reject a retried lead'
);
assert_test(
    !preg_match('/CREATE TABLE wp_landing_form_events[\s\S]*?\b(ip|user_agent|name|phone|email|message|source_block)\b/i', $schema_sql),
    'form events schema stores no contact, raw IP, user-agent, or full source URL'
);
assert_test(
    str_contains($schema_sql, 'event_sequence SMALLINT UNSIGNED NULL'),
    'form events schema stores an optional unsigned browser step'
);
assert_test(
    str_contains($schema_sql, 'KEY submission_sequence (submission_id,event_sequence)'),
    'form events schema indexes browser ordering within a submission'
);
assert_test(
    \LandingConfig\DB\DB_VERSION === '1.1.0',
    'monitoring migration has version 1.1.0'
);

set_mock_current_blog_id(2);
assert_test(get_monitor_alerts_table_name() === 'wp_2_landing_monitor_alerts', 'monitor incidents are isolated per blog');

$schema_sql = implode("\n", $GLOBALS['_mock_dbdelta_calls']);
assert_test(str_contains($schema_sql, 'integration_id BIGINT(20) UNSIGNED NOT NULL DEFAULT 0'), 'delivery rows store exact integration id');
assert_test(str_contains($schema_sql, 'next_attempt_at DATETIME NULL'), 'delivery rows carry queue due time');
assert_test(str_contains(implode("\n", $GLOBALS['wpdb']->query_log ?? []), 'UNIQUE KEY delivery_attempt (lead_id,integration_id,attempt)'), 'migration installs exact reservation key');
assert_test(str_contains($schema_sql, 'UNIQUE KEY fingerprint (fingerprint)'), 'incident fingerprint is unique');
assert_test(str_contains($schema_sql, 'fingerprint_scope BIGINT(20) UNSIGNED NOT NULL DEFAULT 0'), 'incident stores privacy-safe external generation');
preg_match('/CREATE TABLE wp_landing_monitor_alerts \((.*?)\) DEFAULT CHARACTER SET/s', $schema_sql, $monitor_match);
$monitor_sql = $monitor_match[1] ?? '';
foreach (['name','phone','email','message','ip ','user_agent','response_body','error_text','token','webhook'] as $forbidden) {
    assert_test(!preg_match('/\\b' . preg_quote(trim($forbidden), '/') . '\\b/i', $monitor_sql), "monitor schema excludes {$forbidden}");
}

echo "\n$tests tests, $failures failures\n";
exit($failures > 0 ? 1 : 0);
