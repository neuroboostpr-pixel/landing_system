<?php
require_once __DIR__ . '/fixtures/wp-bootstrap.php';
require_once __DIR__ . '/../mu-plugin/landing-config/includes/db.php';
require_once __DIR__ . '/../mu-plugin/landing-config/includes/cascade.php';
require_once __DIR__ . '/../mu-plugin/landing-config/includes/lead-statuses.php';
require_once __DIR__ . '/../mu-plugin/landing-config/includes/lead-status-log.php';

use function LandingConfig\LeadStatuses\save_lead_status;
use function LandingConfig\LeadStatusLog\log_status_change;
use function LandingConfig\LeadStatusLog\get_status_history;

$failures = 0; $tests = 0;
function assert_test($c, $m) { global $failures, $tests; $tests++; if (!$c) { echo "FAIL: $m\n"; $failures++; } }

function reset_lsl() {
    $GLOBALS['_mock_posts'] = [];
    $GLOBALS['_mock_post_meta'] = [];
    $GLOBALS['_mock_next_post_id'] = 1;
    $GLOBALS['_mock_current_blog_id'] = 1;
    $GLOBALS['_mock_status_log'] = [];
    $GLOBALS['_mock_next_status_log_id'] = 1;
}

// Seed vocab — нужно для whitelist валидации
function seed_vocab(int $blog_id = 1): void {
    save_lead_status(['slug' => 'pending', 'label' => 'Pending', 'color' => '#2271b1', 'order' => 10], true, $blog_id);
    save_lead_status(['slug' => 'in_progress', 'label' => 'In progress', 'color' => '#dba617', 'order' => 20], true, $blog_id);
    save_lead_status(['slug' => 'won', 'label' => 'Won', 'color' => '#00a32a', 'order' => 30], true, $blog_id);
}

// T1: log+get round-trip
reset_lsl();
seed_vocab();
$id = log_status_change(42, null, 'pending', 1, 'Заявка создана');
assert_test($id > 0, 'T1a log_status_change returned id');
$h = get_status_history(42);
assert_test(count($h) === 1, 'T1b history count == 1');
assert_test($h[0]['from_status'] === null, 'T1c from is null');
assert_test($h[0]['to_status'] === 'pending', 'T1d to is pending');
assert_test($h[0]['comment'] === 'Заявка создана', 'T1e comment round-trip');
assert_test($h[0]['user_id'] === 1, 'T1f user_id round-trip');

// T2: get_status_history sorted desc
reset_lsl();
seed_vocab();
log_status_change(7, null, 'pending', 1, 'a');
log_status_change(7, 'pending', 'in_progress', 1, 'b');
log_status_change(7, 'in_progress', 'won', 1, 'c');
$h = get_status_history(7);
assert_test(count($h) === 3, 'T2a 3 entries');
assert_test($h[0]['to_status'] === 'won', 'T2b newest first');
assert_test($h[1]['to_status'] === 'in_progress', 'T2c middle');
assert_test($h[2]['to_status'] === 'pending', 'T2d oldest last');

// T3: invalid to_status (not in vocab) → 0
reset_lsl();
seed_vocab();
$id = log_status_change(8, null, 'unknown_status', 1, 'should fail');
assert_test($id === 0, 'T3a invalid to_status rejected');
assert_test(count(get_status_history(8)) === 0, 'T3b nothing written');

// T4: empty comment → NULL
reset_lsl();
seed_vocab();
log_status_change(9, null, 'pending', 1, '');
$h = get_status_history(9);
assert_test($h[0]['comment'] === null, 'T4 empty comment stored as null');

// T5: user_id null (системное изменение)
reset_lsl();
seed_vocab();
log_status_change(10, null, 'pending', null, 'system seed');
$h = get_status_history(10);
assert_test($h[0]['user_id'] === null, 'T5 null user_id stored');

echo "$tests tests, $failures failures\n";
exit($failures > 0 ? 1 : 0);
