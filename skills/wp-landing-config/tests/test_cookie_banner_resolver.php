<?php
require_once __DIR__ . '/fixtures/wp-bootstrap.php';
require_once dirname(__DIR__) . '/mu-plugin/landing-config/includes/cookie-banner/cpt.php';
require_once dirname(__DIR__) . '/mu-plugin/landing-config/includes/cookie-banner/resolver.php';

$tests = 0; $failures = 0;
function assert_test($cond, $msg) {
    global $tests, $failures;
    $tests++;
    if (!$cond) { $failures++; echo "FAIL: $msg\n"; }
    else { echo "PASS: $msg\n"; }
}

function reset_mock_posts() {
    $GLOBALS['_mock_posts'] = [];
    $GLOBALS['_mock_post_meta'] = [];
    $GLOBALS['_mock_next_post_id'] = 1;
}

function seed_banner(int $segment, array $meta): int {
    global $_mock_next_post_id;
    $id = $GLOBALS['_mock_next_post_id']++;
    $GLOBALS['_mock_posts'][$id] = (object) [
        'ID'          => $id,
        'post_type'   => 'lp_cookie_banner',
        'post_status' => 'publish',
    ];
    $GLOBALS['_mock_post_meta'][$id] = array_merge(
        ['_lp_cb_segment' => (string) $segment],
        $meta
    );
    return $id;
}

// T1: defaults when nothing configured
reset_mock_posts();
$out = \LandingConfig\CookieBanner\Resolver\resolve_for_blog(2);
assert_test($out !== null, 'T1a resolver returns array even without records (DEFAULTS)');
assert_test($out['layout'] === 'bottom-bar', 'T1b default layout is bottom-bar');
assert_test($out['show_categories'] === false, 'T1c default show_categories=false');
assert_test($out['consent_version'] === 1, 'T1d default version=1');

// T2: network-only
reset_mock_posts();
seed_banner(0, ['_lp_cb_layout' => 'top-bar', '_lp_cb_title' => 'Network title']);
$out = \LandingConfig\CookieBanner\Resolver\resolve_for_blog(2);
assert_test($out['layout'] === 'top-bar', 'T2a network layout wins (no site override)');
assert_test($out['title'] === 'Network title', 'T2b network title wins');

// T3: site override
reset_mock_posts();
seed_banner(0, ['_lp_cb_layout' => 'top-bar', '_lp_cb_title' => 'Network title']);
seed_banner(3, ['_lp_cb_layout' => 'center-modal']);
$out = \LandingConfig\CookieBanner\Resolver\resolve_for_blog(3);
assert_test($out['layout'] === 'center-modal', 'T3a site layout wins over network');
assert_test($out['title'] === 'Network title', 'T3b unset site field falls back to network');

// T4: invalid layout from DB -> fallback bottom-bar
reset_mock_posts();
seed_banner(0, ['_lp_cb_layout' => 'invalid-layout-name']);
$out = \LandingConfig\CookieBanner\Resolver\resolve_for_blog(1);
assert_test($out['layout'] === 'bottom-bar', 'T4 invalid layout falls back to bottom-bar');

// T5: categories parsing (stored as JSON string)
reset_mock_posts();
seed_banner(0, ['_lp_cb_categories' => json_encode([
    ['slug' => 'necessary', 'name' => 'Necessary', 'locked' => true],
    ['slug' => 'analytics', 'name' => 'Analytics', 'locked' => false],
])]);
$out = \LandingConfig\CookieBanner\Resolver\resolve_for_blog(1);
assert_test(is_array($out['categories']) && count($out['categories']) === 2,
    'T5 categories parsed from JSON string to array');

echo "$tests tests, $failures failures\n";
exit($failures > 0 ? 1 : 0);
