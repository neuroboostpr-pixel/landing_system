<?php
require_once __DIR__ . '/fixtures/wp-bootstrap.php';
require_once dirname(__DIR__) . '/mu-plugin/landing-config/includes/cookie-banner/cpt.php';

$tests = 0; $failures = 0;
function assert_test($cond, $msg) {
    global $tests, $failures;
    $tests++;
    if (!$cond) { $failures++; echo "FAIL: $msg\n"; }
    else { echo "PASS: $msg\n"; }
}

// T1: CPT slug constant defined
assert_test(\LandingConfig\CookieBanner\CPT\POST_TYPE === 'lp_cookie_banner',
    'T1 POST_TYPE constant is lp_cookie_banner');

// T2: register() function exists
assert_test(function_exists('LandingConfig\\CookieBanner\\CPT\\register'),
    'T2 register() function exists');

// T3-T4: meta key constants
assert_test(\LandingConfig\CookieBanner\CPT\SEGMENT_META === '_lp_cb_segment',
    'T3 SEGMENT_META is _lp_cb_segment');
assert_test(\LandingConfig\CookieBanner\CPT\LAYOUT_META === '_lp_cb_layout',
    'T4 LAYOUT_META is _lp_cb_layout');

// T5: VALID_LAYOUTS includes all 5 layouts
$expected = ['top-bar', 'bottom-bar', 'floating-card-left', 'floating-card-right', 'center-modal'];
assert_test(\LandingConfig\CookieBanner\CPT\VALID_LAYOUTS === $expected,
    'T5 VALID_LAYOUTS has all 5 layouts');

echo "$tests tests, $failures failures\n";
exit($failures > 0 ? 1 : 0);
