<?php
require_once __DIR__ . '/fixtures/wp-bootstrap.php';
require_once __DIR__ . '/../mu-plugin/landing-config/includes/helpers.php';

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

// Test 1: landing_config_get reads per-site first
update_option('landing_crm_amocrm_key', 'site-specific-key');
update_site_option('landing_defaults_crm_amocrm_key', 'network-default-key');
assert_test(
    landing_config_get('crm_amocrm_key') === 'site-specific-key',
    "per-site value wins over network default (got: " . landing_config_get('crm_amocrm_key') . ")"
);

// Test 2: landing_config_get falls back to network default when per-site missing
$GLOBALS['_mock_options'] = [];  // clear per-site
assert_test(
    landing_config_get('crm_amocrm_key') === 'network-default-key',
    "fallback to network default when per-site empty (got: " . landing_config_get('crm_amocrm_key') . ")"
);

// Test 3: landing_config_get returns default param when both empty
$GLOBALS['_mock_site_meta'] = [];
assert_test(
    landing_config_get('nonexistent_key', 'my-default') === 'my-default',
    "default param returned when both per-site and network empty"
);

// Test 4: landing_config_get returns empty string by default
assert_test(
    landing_config_get('nonexistent_key') === '',
    "default of landing_config_get is empty string (got: " . landing_config_get('nonexistent_key') . ")"
);

// Test 5: landing_config_set writes per-site
landing_config_set('test_key', 'test-value');
assert_test(
    get_option('landing_test_key') === 'test-value',
    "landing_config_set writes to per-site wp_options with landing_ prefix"
);

// Test 6: landing_config_set_network_default writes to sitemeta
landing_config_set_network_default('test_key', 'network-value');
assert_test(
    get_site_option('landing_defaults_test_key') === 'network-value',
    "landing_config_set_network_default writes to wp_sitemeta with landing_defaults_ prefix"
);

echo "\n$tests tests, $failures failures\n";
exit($failures > 0 ? 1 : 0);
