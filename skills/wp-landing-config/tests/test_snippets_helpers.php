<?php
require_once __DIR__ . '/fixtures/wp-bootstrap.php';
require_once __DIR__ . '/../mu-plugin/landing-config/includes/snippets.php';

use function LandingConfig\Snippets\sanitize_code;
use function LandingConfig\Snippets\save_snippet;
use function LandingConfig\Snippets\get_snippet;
use function LandingConfig\Snippets\delete_snippet;
use function LandingConfig\Snippets\list_snippets;
use function LandingConfig\Snippets\list_site_snippets;
use function LandingConfig\Snippets\list_network_snippets;

$failures = 0; $tests = 0;
function assert_test($cond, $msg) {
    global $failures, $tests;
    $tests++;
    if (!$cond) { echo "FAIL: $msg\n"; $failures++; }
}
function reset_snippets() {
    $GLOBALS['_mock_posts'] = [];
    $GLOBALS['_mock_post_meta'] = [];
    $GLOBALS['_mock_next_post_id'] = 1;
    $GLOBALS['_mock_kses_calls'] = [];
}

// T1: sanitize keeps script/meta/iframe, strips form/onclick
reset_snippets();
$clean = sanitize_code('<script src="https://ya.ru/x.js" async></script><form><input></form>');
assert_test(
    strpos($clean, '<script') !== false && strpos($clean, '<form') === false,
    "sanitize keeps script, strips form (got: $clean)"
);

// T2: save_snippet creates CPT post with all meta (site default)
reset_snippets();
$id = save_snippet([
    'title' => 'Y.Metrika', 'name' => 'metrika',
    'code' => '<script>ym(1,"init");</script>',
    'position' => 'head', 'scope' => 'global',
    'enabled' => true, 'priority' => 5,
]);
assert_test($id > 0, "save_snippet returns post_id (got: $id)");
$s = get_snippet($id);
assert_test(
    $s['title'] === 'Y.Metrika' && $s['name'] === 'metrika'
    && $s['position'] === 'head' && $s['priority'] === 5
    && $s['enabled'] === true && $s['is_network'] === false,
    "round-trip site snippet (got: " . json_encode($s) . ")"
);

// T3: update path
$id2 = save_snippet(['id' => $id, 'title' => 'Y.Metrika v2', 'code' => 'x',
    'position' => 'head', 'scope' => 'global', 'enabled' => false, 'priority' => 10]);
assert_test($id2 === $id, "save_snippet updates existing id");
$s = get_snippet($id);
assert_test(
    $s['title'] === 'Y.Metrika v2' && $s['enabled'] === false && $s['priority'] === 10,
    "updated fields persist"
);

// T4: defaults
reset_snippets();
$id = save_snippet(['title' => 'min', 'code' => 'c']);
$s = get_snippet($id);
assert_test(
    $s['position'] === 'head' && $s['scope'] === 'global'
    && $s['enabled'] === true && $s['priority'] === 10
    && $s['target_post_ids'] === [] && $s['is_network'] === false
    && $s['name'] === '',
    "defaults applied (got: " . json_encode($s) . ")"
);

// T5: invalid position fallback
$id = save_snippet(['title' => 'bad', 'code' => 'c', 'position' => 'evil']);
$s = get_snippet($id);
assert_test($s['position'] === 'head', "invalid position falls back to head");

// T6: local scope + target_post_ids round-trip
reset_snippets();
$id = save_snippet(['title' => 'Local', 'code' => 'c', 'scope' => 'local',
    'target_post_ids' => [42, 99, 100]]);
$s = get_snippet($id);
assert_test(
    $s['scope'] === 'local' && $s['target_post_ids'] === [42, 99, 100],
    "local + targets round-trip"
);

// T7: list_snippets filter by position
reset_snippets();
save_snippet(['title' => 'A', 'code' => 'a', 'position' => 'head']);
save_snippet(['title' => 'B', 'code' => 'b', 'position' => 'body_open']);
$head = list_site_snippets(['position' => 'head']);
assert_test(count($head) === 1 && $head[0]['title'] === 'A', "filter by position");

// T8: list filter by name
reset_snippets();
save_snippet(['title' => 'GA', 'code' => '', 'name' => 'ga4']);
save_snippet(['title' => 'YM', 'code' => '', 'name' => 'metrika']);
$ga = list_site_snippets(['name' => 'ga4']);
assert_test(count($ga) === 1 && $ga[0]['name'] === 'ga4', "filter by name");

// T9: delete removes post + meta
reset_snippets();
$id = save_snippet(['title' => 'X', 'code' => 'x']);
delete_snippet($id);
assert_test(get_post($id) === null, "delete removes post");

// T10: network save sets is_network=true; list_site does NOT return it
reset_snippets();
$nid = save_snippet(['title' => 'Net', 'code' => 'n', 'name' => 'net1'], true);
$sid = save_snippet(['title' => 'Site', 'code' => 's', 'name' => 'site1'], false);
$site = list_site_snippets();
$net = list_network_snippets();
assert_test(
    count($site) === 1 && $site[0]['id'] === $sid && $site[0]['is_network'] === false,
    "list_site_snippets returns only site (got: " . count($site) . ")"
);
assert_test(
    count($net) === 1 && $net[0]['id'] === $nid && $net[0]['is_network'] === true,
    "list_network_snippets returns only network (got: " . count($net) . ")"
);

// T11: get_snippet with is_network=true switches blog and back
reset_snippets();
set_mock_current_blog_id(2);  // pretend we're on subsite 2
$nid = save_snippet(['title' => 'Net2', 'code' => 'x'], true);  // saves "on blog 1"
// After save, we should be back on blog 2
assert_test(
    get_current_blog_id() === 2,
    "save with is_network=true restores blog (got: " . get_current_blog_id() . ")"
);
$s = get_snippet($nid, true);
assert_test(
    $s !== null && $s['is_network'] === true,
    "get_snippet with is_network reads correctly"
);
assert_test(
    get_current_blog_id() === 2,
    "get_snippet with is_network=true restores blog"
);

echo "\n$tests tests, $failures failures\n";
exit($failures > 0 ? 1 : 0);
