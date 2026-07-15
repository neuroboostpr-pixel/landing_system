<?php
require_once __DIR__ . '/fixtures/wp-bootstrap.php';
require_once __DIR__ . '/../mu-plugin/landing-config/includes/db.php';

use function LandingConfig\DB\maybe_install_or_migrate;
use function LandingConfig\DB\get_leads_table_name;
use function LandingConfig\DB\get_lead_log_table_name;

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

// Test 4: maybe_install_or_migrate triggers dbDelta when version mismatch
$GLOBALS['_mock_dbdelta_calls'] = [];
$GLOBALS['_mock_site_meta']['landing_config_db_version'] = '';  // not installed yet
maybe_install_or_migrate();
assert_test(
    count($GLOBALS['_mock_dbdelta_calls']) >= 2,  // at least leads + lead_log per blog
    "maybe_install_or_migrate triggers dbDelta calls (got: " . count($GLOBALS['_mock_dbdelta_calls']) . ")"
);

// Test 5: maybe_install_or_migrate is idempotent — second call with same version is no-op
$first_count = count($GLOBALS['_mock_dbdelta_calls']);
maybe_install_or_migrate();
assert_test(
    count($GLOBALS['_mock_dbdelta_calls']) === $first_count,
    "maybe_install_or_migrate is no-op when version matches (call count unchanged)"
);

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
    count($GLOBALS['_mock_dbdelta_calls']) === 4,
    "single-site path calls dbDelta four times (leads + lead_log + status_log + audit), got: " . count($GLOBALS['_mock_dbdelta_calls'])
);
$GLOBALS['_mock_is_multisite'] = true; // reset

// T_PD_DB_1: pd_consent_granted_at column declared in landing_leads CREATE TABLE
$leads_sql = $GLOBALS['_mock_dbdelta_calls'][0] ?? '';
assert_test(strpos($leads_sql, 'pd_consent_granted_at') !== false,
    'T_PD_DB_1 column pd_consent_granted_at declared in landing_leads');
assert_test(strpos($leads_sql, 'DATETIME NULL') !== false,
    'T_PD_DB_2 type is DATETIME NULL');

echo "\n$tests tests, $failures failures\n";
exit($failures > 0 ? 1 : 0);
