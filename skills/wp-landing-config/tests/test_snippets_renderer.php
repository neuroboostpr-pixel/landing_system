<?php
require_once __DIR__ . '/fixtures/wp-bootstrap.php';
require_once __DIR__ . '/../mu-plugin/landing-config/includes/snippets.php';

use function LandingConfig\Snippets\save_snippet;
use function LandingConfig\Snippets\render;

$failures = 0; $tests = 0;
function assert_test($cond, $msg) {
    global $failures, $tests;
    $tests++;
    if (!$cond) { echo "FAIL: $msg\n"; $failures++; }
}
function reset_state() {
    $GLOBALS['_mock_posts'] = [];
    $GLOBALS['_mock_post_meta'] = [];
    $GLOBALS['_mock_next_post_id'] = 1;
    set_mock_queried_object_id(0);
    set_mock_current_blog_id(1);
}
function capture(callable $fn): string {
    ob_start();
    $fn();
    return (string) ob_get_clean();
}

// T1: render('head') outputs site snippets sorted by priority ASC
reset_state();
save_snippet(['title' => 'B', 'code' => '<meta name="b">', 'position' => 'head', 'priority' => 20]);
save_snippet(['title' => 'A', 'code' => '<meta name="a">', 'position' => 'head', 'priority' => 5]);
$out = capture(fn() => render('head'));
assert_test(
    strpos($out, 'name="a"') !== false
    && strpos($out, 'name="b"') !== false
    && strpos($out, 'name="a"') < strpos($out, 'name="b"'),
    "head snippets sorted by priority ASC (got: $out)"
);

// T2: position isolation
reset_state();
save_snippet(['title' => 'Body', 'code' => '<div>BODYMARK</div>', 'position' => 'body_open']);
save_snippet(['title' => 'Head', 'code' => '<meta name="headmark">', 'position' => 'head']);
$head_out = capture(fn() => render('head'));
$body_out = capture(fn() => render('body_open'));
assert_test(
    strpos($head_out, 'BODYMARK') === false && strpos($head_out, 'headmark') !== false,
    "head output isolated from body_open"
);
assert_test(
    strpos($body_out, 'BODYMARK') !== false && strpos($body_out, 'headmark') === false,
    "body_open output isolated from head"
);

// T3: disabled snippet not rendered
reset_state();
save_snippet(['title' => 'X', 'code' => '<meta name="x">', 'position' => 'head', 'enabled' => false]);
$out = capture(fn() => render('head'));
assert_test(strpos($out, 'name="x"') === false, "disabled snippet not rendered");

// T4: local snippet only on target_post_ids match
reset_state();
save_snippet(['title' => 'Local42', 'code' => '<meta name="for42">', 'position' => 'head',
              'scope' => 'local', 'target_post_ids' => [42]]);
set_mock_queried_object_id(10);
$other = capture(fn() => render('head'));
set_mock_queried_object_id(42);
$target = capture(fn() => render('head'));
assert_test(strpos($other, 'for42') === false,  "local NOT on non-target page");
assert_test(strpos($target, 'for42') !== false, "local ON target page");

// T5: network snippet visible on subsite
reset_state();
set_mock_current_blog_id(2);  // pretend we're on subsite 2
$nid = save_snippet(['title' => 'NetGA', 'code' => '<meta name="ga">', 'position' => 'head'], true);
$out = capture(fn() => render('head'));
assert_test(strpos($out, 'name="ga"') !== false, "network snippet rendered on subsite (got: $out)");
assert_test(strpos($out, '[network]') !== false, "network snippet tagged [network]");

// T6: override by name — site beats network
reset_state();
save_snippet(['title' => 'NetGA', 'code' => '<meta name="net_ga">', 'position' => 'head',
              'name' => 'ga4', 'priority' => 5], true);
save_snippet(['title' => 'SiteGA', 'code' => '<meta name="site_ga">', 'position' => 'head',
              'name' => 'ga4', 'priority' => 10], false);
$out = capture(fn() => render('head'));
assert_test(
    strpos($out, 'site_ga') !== false && strpos($out, 'net_ga') === false,
    "site override skips network (got: $out)"
);

// T7: no name collision = both render (network + site без name)
reset_state();
save_snippet(['title' => 'NetAny', 'code' => '<meta name="netany">', 'position' => 'head', 'priority' => 5], true);
save_snippet(['title' => 'SiteAny', 'code' => '<meta name="siteany">', 'position' => 'head', 'priority' => 10], false);
$out = capture(fn() => render('head'));
assert_test(
    strpos($out, 'netany') !== false && strpos($out, 'siteany') !== false,
    "no-name snippets coexist (got: $out)"
);

// T8: priority sort works cross-source
reset_state();
save_snippet(['title' => 'NetLow', 'code' => '<meta name="netlow">', 'position' => 'head', 'priority' => 5], true);
save_snippet(['title' => 'SiteHigh', 'code' => '<meta name="sitehigh">', 'position' => 'head', 'priority' => 20], false);
$out = capture(fn() => render('head'));
assert_test(
    strpos($out, 'netlow') < strpos($out, 'sitehigh'),
    "cross-source priority sort works (network priority 5 before site priority 20)"
);

// T9: debug comment includes [network] vs [site] tag
reset_state();
save_snippet(['title' => 'Sit', 'code' => '<meta name="s">', 'position' => 'head'], false);
save_snippet(['title' => 'Net', 'code' => '<meta name="n">', 'position' => 'head'], true);
$out = capture(fn() => render('head'));
assert_test(strpos($out, '[network]') !== false && strpos($out, '[site]') !== false,
    "both tags present in debug comments");

// T10: invalid position returns empty (no fatal)
reset_state();
save_snippet(['title' => 'Z', 'code' => 'z', 'position' => 'head']);
$out = capture(fn() => render('invalid-pos'));
assert_test($out === '', "invalid position returns empty");

// T11: only network with no override → renders
reset_state();
save_snippet(['title' => 'OnlyNet', 'code' => '<meta name="only">', 'position' => 'head',
              'name' => 'unique-name'], true);
$out = capture(fn() => render('head'));
assert_test(strpos($out, 'only') !== false, "network without override renders");

echo "\n$tests tests, $failures failures\n";
exit($failures > 0 ? 1 : 0);
