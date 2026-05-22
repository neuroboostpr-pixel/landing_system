<?php
require_once __DIR__ . '/fixtures/wp-bootstrap.php';
require_once dirname(__DIR__) . '/mu-plugin/landing-config/includes/seo-audit/deep-links.php';

$tests = 0; $failures = 0;
function assert_test($cond, $msg) {
    global $tests, $failures;
    $tests++;
    if (!$cond) { $failures++; echo "FAIL: $msg\n"; }
    else { echo "PASS: $msg\n"; }
}

// Mock get_option for show_on_front / page_on_front
// Bootstrap's get_option reads $GLOBALS['_mock_options'][$blog_id][$key]
// Current blog_id is 1 (default in bootstrap).
$GLOBALS['_mock_options'][1]['show_on_front'] = 'page';
$GLOBALS['_mock_options'][1]['page_on_front'] = '96';

$ROOT = 'https://example.com/wp-admin/';

// HTML category: H6 → admin_page
$h6 = \LandingConfig\SEOAudit\DeepLinks\build_deep_link('H6', 1, $ROOT);
assert_test($h6 !== null, 'T1 H6 returns deep link');
assert_test($h6['type'] === 'admin_page', 'T1a H6 type=admin_page');
assert_test(strpos($h6['url'], 'landing-config-head-seo') !== false,
    'T1b H6 url contains target page');

// Network: N8 → raw_url
$n8 = \LandingConfig\SEOAudit\DeepLinks\build_deep_link('N8', 1, $ROOT);
assert_test(strpos($n8['url'], 'options-reading.php') !== false,
    'T2 N8 url is options-reading');

// Schema: S5 → raw_url with anchor
$s5 = \LandingConfig\SEOAudit\DeepLinks\build_deep_link('S5', 1, $ROOT);
assert_test(strpos($s5['url'], 'site_icon') !== false,
    'T3 S5 url contains site_icon');

// AI: AI1 → admin_page
$ai1 = \LandingConfig\SEOAudit\DeepLinks\build_deep_link('AI1', 1, $ROOT);
assert_test($ai1 !== null, 'T4 AI1 returns deep link');
assert_test(strpos($ai1['label'], 'llms.txt') !== false, 'T4a AI1 label mentions llms.txt');

// post_edit with use_homepage_id=true
$h4 = \LandingConfig\SEOAudit\DeepLinks\build_deep_link('H4', 1, $ROOT);
assert_test($h4['type'] === 'post_edit', 'T5 H4 type=post_edit');
assert_test(strpos($h4['url'], 'post.php?post=96') !== false,
    'T5a H4 substitutes homepage id 96');

// suggestion: no URL
$h11 = \LandingConfig\SEOAudit\DeepLinks\build_deep_link('H11', 1, $ROOT);
assert_test($h11['type'] === 'suggestion', 'T6 H11 type=suggestion');
assert_test(!isset($h11['url']) || $h11['url'] === '', 'T6a suggestion has no url');

// Unknown check returns null
$unknown = \LandingConfig\SEOAudit\DeepLinks\build_deep_link('Z99', 1, $ROOT);
assert_test($unknown === null, 'T7 unknown returns null');

echo "$tests tests, $failures failures\n";
exit($failures > 0 ? 1 : 0);
