<?php
require_once __DIR__ . '/fixtures/wp-bootstrap.php';
require_once dirname(__DIR__) . '/mu-plugin/landing-config/includes/head-seo.php';

$tests = 0; $failures = 0;
function assert_test($cond, $msg) {
    global $tests, $failures;
    $tests++;
    if (!$cond) { $failures++; echo "FAIL: $msg\n"; }
    else { echo "PASS: $msg\n"; }
}

// T1: resolve_setting_cascade — site-only wins
// wp-bootstrap uses $GLOBALS['_mock_options'][$blog_id][$key]
$GLOBALS['_mock_options'][3]['landing_seo_description'] = 'site-3-desc';
$GLOBALS['_mock_options'][1]['landing_seo_description'] = 'network-desc';
$val = \LandingConfig\HeadSEO\resolve_setting_cascade('landing_seo_description', 3);
assert_test($val === 'site-3-desc', 'T1 site value wins over network');

// T2: empty site → network fallback
unset($GLOBALS['_mock_options'][3]['landing_seo_description']);
$val2 = \LandingConfig\HeadSEO\resolve_setting_cascade('landing_seo_description', 3);
assert_test($val2 === 'network-desc', 'T2 falls back to network when site empty');

// T3: both empty → empty string
unset($GLOBALS['_mock_options'][1]['landing_seo_description']);
$val3 = \LandingConfig\HeadSEO\resolve_setting_cascade('landing_seo_description', 3);
assert_test($val3 === '', 'T3 returns empty when nothing set');

echo "$tests tests, $failures failures\n";
exit($failures > 0 ? 1 : 0);
