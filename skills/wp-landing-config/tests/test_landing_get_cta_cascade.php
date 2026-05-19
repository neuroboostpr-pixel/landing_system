<?php
require_once __DIR__ . '/fixtures/wp-bootstrap.php';
require_once __DIR__ . '/../mu-plugin/landing-config/includes/cascade.php';
require_once __DIR__ . '/../mu-plugin/landing-config/includes/cta.php';
require_once __DIR__ . '/../mu-plugin/landing-config/includes/helpers.php';

use function LandingConfig\CTA\save_cta;

$failures = 0; $tests = 0;
function assert_test($cond, $msg) { global $failures, $tests; $tests++; if (!$cond) { echo "FAIL: $msg\n"; $failures++; } }

function reset_lg() {
    $GLOBALS['_mock_posts'] = [];
    $GLOBALS['_mock_post_meta'] = [];
    $GLOBALS['_mock_next_post_id'] = 1;
    $GLOBALS['_mock_current_blog_id'] = 1;
    $GLOBALS['_mock_blog_stack'] = [];
    $GLOBALS['_mock_options'] = [];
    $GLOBALS['_mock_site_options'] = [];
}

// T1: CPT network record on blog_id=1 → helper returns URL built from CPT
reset_lg();
save_cta(['preset_name' => 'primary', 'type' => 'scroll', 'label' => 'X',
    'target' => '#cta-from-cpt', 'phone' => '', 'form_id' => '', 'message_template' => ''], true, 1);
assert_test(landing_get_cta('primary') === '#cta-from-cpt',
    'T1 cascade-read network CTA returns target (got: ' . landing_get_cta('primary') . ')');

// T2: CPT site override on blog_id=2 → helper returns URL from site override
reset_lg();
save_cta(['preset_name' => 'primary', 'type' => 'scroll', 'label' => 'X',
    'target' => '#net', 'phone' => '', 'form_id' => '', 'message_template' => ''], true, 1);
$GLOBALS['_mock_current_blog_id'] = 2;
save_cta(['preset_name' => 'primary', 'type' => 'scroll', 'label' => 'X',
    'target' => '#site-override', 'phone' => '', 'form_id' => '', 'message_template' => ''], false, 2);
assert_test(landing_get_cta('primary') === '#site-override',
    'T2 site override wins on blog_id=2');

// T3: blog_id=1 still gets network value (no override there)
$GLOBALS['_mock_current_blog_id'] = 1;
assert_test(landing_get_cta('primary') === '#net',
    'T3 blog_id=1 still gets network value');

// T4: CPT empty + wp_options legacy populated → legacy fallback works
reset_lg();
$GLOBALS['_mock_options'][1]['landing_cta_presets'] = [
    'primary' => ['type' => 'scroll', 'target' => '#legacy-source', 'label' => 'L',
                  'phone' => '', 'form_id' => '', 'message_template' => ''],
];
assert_test(landing_get_cta('primary') === '#legacy-source',
    'T4 legacy wp_options fallback when CPT is empty (got: ' . landing_get_cta('primary') . ')');

// T5: url_override wins over everything
reset_lg();
save_cta(['preset_name' => 'primary', 'type' => 'scroll', 'label' => 'X',
    'target' => '#cpt', 'phone' => '', 'form_id' => '', 'message_template' => ''], true, 1);
assert_test(landing_get_cta('primary', 'https://override.example/x') === 'https://override.example/x',
    'T5 url_override wins over cascade');

// T6: WhatsApp build still works through cascade
// Note: 'wa' is NOT in PRESET_NAMES, so use 'whatsapp' which IS in PRESET_NAMES
reset_lg();
save_cta(['preset_name' => 'whatsapp', 'type' => 'whatsapp', 'label' => 'WA',
    'target' => '', 'phone' => '+7 911 123 45 67', 'form_id' => '',
    'message_template' => 'Hi, want {model}'], true, 1);
$result = landing_get_cta('whatsapp', null, ['model' => 'L9']);
assert_test(strpos($result, 'wa.me/79111234567') !== false && strpos($result, 'L9') !== false,
    'T6 WhatsApp URL built from cascade CTA with context substitution (got: ' . $result . ')');

echo "$tests tests, $failures failures\n";
exit($failures > 0 ? 1 : 0);
