<?php
require_once __DIR__ . '/fixtures/wp-bootstrap.php';
require_once dirname(__DIR__) . '/mu-plugin/landing-config/includes/cookie-banner/cpt.php';
require_once dirname(__DIR__) . '/mu-plugin/landing-config/includes/cookie-banner/resolver.php';
require_once dirname(__DIR__) . '/mu-plugin/landing-config/includes/cookie-banner/migrate.php';

$tests = 0; $failures = 0;
function assert_test($cond, $msg) {
    global $tests, $failures;
    $tests++;
    if (!$cond) { $failures++; echo "FAIL: $msg\n"; }
    else { echo "PASS: $msg\n"; }
}

function reset_state() {
    $GLOBALS['_mock_posts'] = [];
    $GLOBALS['_mock_post_meta'] = [];
    $GLOBALS['_mock_site_meta'] = [];   // bootstrap uses _mock_site_meta for get/update_site_option
    $GLOBALS['_mock_next_post_id'] = 1; // bootstrap uses _mock_next_post_id
}

// T1: maybe_run() seeds network default
reset_state();
\LandingConfig\CookieBanner\Migrate\maybe_run();
$post_id = \LandingConfig\CookieBanner\Resolver\get_post_id_for_segment(0);
assert_test($post_id !== null, 'T1a network record created');
assert_test(($GLOBALS['_mock_site_meta'][\LandingConfig\CookieBanner\Migrate\MARKER] ?? '') === '1',
    'T1b migration marker set');

// T2: idempotent
reset_state();
\LandingConfig\CookieBanner\Migrate\maybe_run();
\LandingConfig\CookieBanner\Migrate\maybe_run();
$count = count(array_filter($GLOBALS['_mock_posts'], function($p) {
    $pt = is_object($p) ? $p->post_type : ($p['post_type'] ?? '');
    return $pt === 'lp_cookie_banner';
}));
assert_test($count === 1, 'T2 idempotent — only 1 record after 2 runs');

// T3: skip if marker already set
reset_state();
$GLOBALS['_mock_site_meta'][\LandingConfig\CookieBanner\Migrate\MARKER] = '1';
\LandingConfig\CookieBanner\Migrate\maybe_run();
$post_id = \LandingConfig\CookieBanner\Resolver\get_post_id_for_segment(0);
assert_test($post_id === null, 'T3 skipped when marker set');

echo "$tests tests, $failures failures\n";
exit($failures > 0 ? 1 : 0);
