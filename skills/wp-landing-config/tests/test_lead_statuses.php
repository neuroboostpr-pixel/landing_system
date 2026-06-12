<?php
require_once __DIR__ . '/fixtures/wp-bootstrap.php';
require_once __DIR__ . '/../mu-plugin/landing-config/includes/cascade.php';
require_once __DIR__ . '/../mu-plugin/landing-config/includes/lead-statuses.php';

use function LandingConfig\LeadStatuses\save_lead_status;
use function LandingConfig\LeadStatuses\get_lead_status;
use function LandingConfig\LeadStatuses\list_lead_statuses;
use function LandingConfig\LeadStatuses\resolve_lead_status;
use function LandingConfig\LeadStatuses\delete_lead_status;
use function LandingConfig\LeadStatuses\has_override;

$failures = 0; $tests = 0;
function assert_test($c, $m) { global $failures, $tests; $tests++; if (!$c) { echo "FAIL: $m\n"; $failures++; } }

function reset_ls() {
    $GLOBALS['_mock_posts'] = [];
    $GLOBALS['_mock_post_meta'] = [];
    $GLOBALS['_mock_next_post_id'] = 1;
    $GLOBALS['_mock_current_blog_id'] = 1;
    $GLOBALS['_mock_blog_stack'] = [];
}

// T1: save+get round-trip
reset_ls();
$id = save_lead_status([
    'slug'  => 'pending',
    'label' => 'Новая',
    'color' => '#2271b1',
    'order' => 10,
], true, 1);
assert_test($id > 0, 'T1a save_lead_status returned id');
$row = get_lead_status($id);
assert_test($row['slug'] === 'pending', 'T1b slug round-trip');
assert_test($row['label'] === 'Новая', 'T1c label round-trip');
assert_test($row['color'] === '#2271b1', 'T1d color round-trip');
assert_test($row['order'] === 10, 'T1e order round-trip');
assert_test($row['is_network'] === true, 'T1f is_network round-trip');

// T2: cascade site override wins
reset_ls();
save_lead_status(['slug' => 'pending', 'label' => 'Net label', 'color' => '#000000', 'order' => 10], true, 1);
$GLOBALS['_mock_current_blog_id'] = 2;
save_lead_status(['slug' => 'pending', 'label' => 'Site label', 'color' => '#ffffff', 'order' => 10], false, 2);
$r = resolve_lead_status('pending', 2);
assert_test($r['label'] === 'Site label', 'T2 site override wins');

// T3: cascade network fallback
$r = resolve_lead_status('pending', 1);
assert_test($r['label'] === 'Net label', 'T3 network fallback for main blog');

// T4: list sorted by order asc
reset_ls();
save_lead_status(['slug' => 'won', 'label' => 'Won', 'color' => '#00aa00', 'order' => 30], true, 1);
save_lead_status(['slug' => 'pending', 'label' => 'Pending', 'color' => '#0000ff', 'order' => 10], true, 1);
save_lead_status(['slug' => 'in_progress', 'label' => 'In progress', 'color' => '#ffaa00', 'order' => 20], true, 1);
$list = list_lead_statuses(1);
assert_test(count($list) === 3, 'T4a list count == 3');
assert_test($list[0]['slug'] === 'pending', 'T4b first by order is pending');
assert_test($list[1]['slug'] === 'in_progress', 'T4c second is in_progress');
assert_test($list[2]['slug'] === 'won', 'T4d third is won');

// T5: has_override
reset_ls();
save_lead_status(['slug' => 'pending', 'label' => 'Net', 'color' => '#000000', 'order' => 10], true, 1);
assert_test(has_override('pending', 2) === false, 'T5a no override yet');
$GLOBALS['_mock_current_blog_id'] = 2;
save_lead_status(['slug' => 'pending', 'label' => 'Site', 'color' => '#ffffff', 'order' => 10], false, 2);
assert_test(has_override('pending', 2) === true, 'T5b override registered');

// T6: delete removes
reset_ls();
$id = save_lead_status(['slug' => 'spam', 'label' => 'Spam', 'color' => '#999999', 'order' => 50], true, 1);
assert_test(delete_lead_status($id) === true, 'T6a delete returns true');
assert_test(get_lead_status($id) === null, 'T6b row gone after delete');

// T7: invalid slug → 0
reset_ls();
$id = save_lead_status(['slug' => 'BAD SLUG!', 'label' => 'X', 'color' => '#000000', 'order' => 10], true, 1);
assert_test($id === 0, 'T7 invalid slug rejected');

// T8: update path (post_id передан → wp_update_post, не дубль)
reset_ls();
$id1 = save_lead_status(['slug' => 'pending', 'label' => 'Old', 'color' => '#000000', 'order' => 10], true, 1);
$id2 = save_lead_status(['slug' => 'pending', 'label' => 'New', 'color' => '#000000', 'order' => 10], true, 1, $id1);
assert_test($id1 === $id2, 'T8a update reuses post id');
$list = list_lead_statuses(1);
assert_test(count($list) === 1, 'T8b no duplicate row');
assert_test($list[0]['label'] === 'New', 'T8c updated label persists');

// T8d: update path с несуществующим post_id → 0 (real WP behavior)
reset_ls();
$id_bad = save_lead_status(['slug' => 'ghost', 'label' => 'X', 'color' => '#000000', 'order' => 10], true, 1, 9999);
assert_test($id_bad === 0, 'T8d update with nonexistent post_id returns 0');

echo "$tests tests, $failures failures\n";
exit($failures > 0 ? 1 : 0);
