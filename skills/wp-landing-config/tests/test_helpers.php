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


// CTA helper tests

// Test 7: url_override takes precedence
$GLOBALS['_mock_options'][1]['landing_cta_presets'] = [
    'primary' => ['type' => 'scroll', 'target' => '#default'],
];
assert_test(
    landing_get_cta('primary', 'https://custom.example/url') === 'https://custom.example/url',
    "landing_get_cta override URL wins"
);

// Test 8: scroll preset returns target
assert_test(
    landing_get_cta('primary') === '#default',
    "scroll preset returns target (got: " . landing_get_cta('primary') . ")"
);

// Test 9: tel preset returns tel: URL
$GLOBALS['_mock_options'][1]['landing_cta_presets']['phone'] = ['type' => 'tel', 'phone' => '+7 (911) 123-45-67'];
assert_test(
    landing_get_cta('phone') === 'tel:+79111234567',
    "tel preset returns cleaned tel: URL (got: " . landing_get_cta('phone') . ")"
);

// Test 10: whatsapp preset substitutes template
$GLOBALS['_mock_options'][1]['landing_cta_presets']['wa'] = [
    'type' => 'whatsapp',
    'phone' => '+79001234567',
    'message_template' => 'Hello {model}',
];
$result = landing_get_cta('wa', null, ['model' => 'L9']);
assert_test(
    strpos($result, 'wa.me/79001234567') !== false && strpos($result, 'Hello%20L9') !== false,
    "whatsapp preset substitutes {model} (got: $result)"
);

// Test 11: missing preset returns #
assert_test(
    landing_get_cta('nonexistent') === '#',
    "missing preset returns #"
);

// Test 12: whatsapp with empty phone falls back
$GLOBALS['_mock_options'][1]['landing_cta_presets']['wa2'] = ['type' => 'whatsapp', 'phone' => ''];
assert_test(
    landing_get_cta('wa2') === '#contact-form',
    "whatsapp with empty phone falls back to #contact-form"
);

echo "\n$tests tests, $failures failures\n";
exit($failures > 0 ? 1 : 0);
