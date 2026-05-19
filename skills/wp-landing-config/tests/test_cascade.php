<?php
require_once __DIR__ . '/fixtures/wp-bootstrap.php';
require_once __DIR__ . '/../mu-plugin/landing-config/includes/cascade.php';

use function LandingConfig\Cascade\resolve_for_blog;
use function LandingConfig\Cascade\list_for_blog;
use function LandingConfig\Cascade\has_site_override;

$failures = 0; $tests = 0;
function assert_test($cond, $msg) {
    global $failures, $tests;
    $tests++;
    if (!$cond) { echo "FAIL: $msg\n"; $failures++; }
}

function reset_cascade() {
    $GLOBALS['_mock_posts'] = [];
    $GLOBALS['_mock_post_meta'] = [];
    $GLOBALS['_mock_next_post_id'] = 1;
}

function seed_cpt(string $cpt, int $blog_id, string $name, array $meta, bool $is_network): int {
    static $id = 1000;
    $id++;
    $GLOBALS['_mock_posts'][$id] = (object) ['ID' => $id, 'post_type' => $cpt, 'post_status' => 'publish', 'post_title' => $name];
    foreach ($meta as $k => $v) {
        $GLOBALS['_mock_post_meta'][$id][$k] = $v;
    }
    $GLOBALS['_mock_post_meta'][$id]['_lp_test_name'] = $name;
    $GLOBALS['_mock_post_meta'][$id]['_lp_is_network'] = $is_network ? '1' : '0';
    $GLOBALS['_mock_post_meta'][$id]['_lp_blog_id'] = $blog_id;
    return $id;
}

// T1: only network → returns network
reset_cascade();
seed_cpt('lp_test', 1, 'primary', ['_lp_test_value' => 'network_v'], true);
$r = resolve_for_blog('lp_test', '_lp_test_name', '_lp_is_network', 'primary', 2);
assert_test($r !== null && ($r['_lp_test_value'] ?? '') === 'network_v', 'T1 only network returned');

// T2: only site → returns site
reset_cascade();
seed_cpt('lp_test', 2, 'primary', ['_lp_test_value' => 'site_v'], false);
$r = resolve_for_blog('lp_test', '_lp_test_name', '_lp_is_network', 'primary', 2);
assert_test($r !== null && ($r['_lp_test_value'] ?? '') === 'site_v', 'T2 only site returned');

// T3: both → site wins
reset_cascade();
seed_cpt('lp_test', 1, 'primary', ['_lp_test_value' => 'net'], true);
seed_cpt('lp_test', 2, 'primary', ['_lp_test_value' => 'site'], false);
$r = resolve_for_blog('lp_test', '_lp_test_name', '_lp_is_network', 'primary', 2);
assert_test(($r['_lp_test_value'] ?? '') === 'site', 'T3 site wins over network');

// T4: neither → null
reset_cascade();
$r = resolve_for_blog('lp_test', '_lp_test_name', '_lp_is_network', 'primary', 2);
assert_test($r === null, 'T4 null when neither');

// T5: has_site_override returns true/false correctly
reset_cascade();
seed_cpt('lp_test', 2, 'primary', ['_lp_test_value' => 'x'], false);
assert_test(has_site_override('lp_test', '_lp_test_name', '_lp_is_network', 'primary', 2) === true, 'T5a has_site_override true');
assert_test(has_site_override('lp_test', '_lp_test_name', '_lp_is_network', 'other', 2) === false, 'T5b has_site_override false');

// T6: list_for_blog merges network + site, site replaces by name
reset_cascade();
seed_cpt('lp_test', 1, 'a', ['_lp_test_value' => 'net_a'], true);
seed_cpt('lp_test', 1, 'b', ['_lp_test_value' => 'net_b'], true);
seed_cpt('lp_test', 2, 'a', ['_lp_test_value' => 'site_a'], false);
$list = list_for_blog('lp_test', '_lp_test_name', '_lp_is_network', 2);
$by_name = [];
foreach ($list as $row) { $by_name[$row['_lp_test_name']] = $row['_lp_test_value']; }
assert_test($by_name['a'] === 'site_a' && $by_name['b'] === 'net_b', 'T6 list_for_blog merges correctly');

echo "$tests tests, $failures failures\n";
exit($failures > 0 ? 1 : 0);
