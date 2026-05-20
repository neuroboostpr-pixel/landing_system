<?php
require_once __DIR__ . '/fixtures/wp-bootstrap.php';
require_once __DIR__ . '/../mu-plugin/landing-config/includes/cascade.php';
require_once __DIR__ . '/../mu-plugin/landing-config/includes/lead-statuses.php';
require_once __DIR__ . '/../mu-plugin/landing-config/includes/db.php';
require_once __DIR__ . '/../mu-plugin/landing-config/includes/lead-status-log.php';

use function LandingConfig\LeadStatuses\save_lead_status;
use function LandingConfig\LeadStatuses\resolve_lead_status;
use function LandingConfig\LeadStatusLog\log_status_change;
use function LandingConfig\LeadStatusLog\get_status_history;

$failures = 0; $tests = 0;
function assert_test($c, $m) { global $failures, $tests; $tests++; if (!$c) { echo "FAIL: $m\n"; $failures++; } }

function reset_ld() {
    $GLOBALS['_mock_posts'] = [];
    $GLOBALS['_mock_post_meta'] = [];
    $GLOBALS['_mock_next_post_id'] = 1;
    $GLOBALS['_mock_current_blog_id'] = 1;
    $GLOBALS['_mock_blog_stack'] = [];
    $GLOBALS['_mock_status_log'] = [];
    $GLOBALS['_mock_next_status_log_id'] = 1;
}

function seed_vocab_ld() {
    save_lead_status(['slug' => 'pending', 'label' => 'Pending', 'color' => '#2271b1', 'order' => 10], true, 1);
    save_lead_status(['slug' => 'in_progress', 'label' => 'In progress', 'color' => '#dba617', 'order' => 20], true, 1);
}

// T1: смена статуса pending → in_progress пишет в log и обновляет state
reset_ld();
seed_vocab_ld();
$lead_id = 42;
$from = 'pending';
$to = 'in_progress';
$comment = 'Перезвонил';
$user_id = 5;

// Whitelist
assert_test(resolve_lead_status($to, 1) !== null, 'T1a whitelist accepts in_progress');

// Запись в log
$log_id = log_status_change($lead_id, $from, $to, $user_id, $comment);
assert_test($log_id > 0, 'T1b log_status_change returned id');

// History содержит запись
$history = get_status_history($lead_id);
assert_test(count($history) === 1, 'T1c history has 1 entry');
assert_test($history[0]['from_status'] === $from, 'T1d from_status preserved');
assert_test($history[0]['to_status'] === $to, 'T1e to_status preserved');
assert_test($history[0]['comment'] === $comment, 'T1f comment preserved');
assert_test((int)$history[0]['user_id'] === $user_id, 'T1g user_id preserved');

// T2: whitelist отвергает invalid status (handler НЕ должен дойти до log)
reset_ld();
seed_vocab_ld();
assert_test(resolve_lead_status('hackerstatus', 1) === null, 'T2a whitelist rejects unknown slug');
// Симуляция: handler бы вернул wp_die ДО log_status_change
// log_status_change всё равно отверг бы из-за второго слоя whitelist:
$log_id = log_status_change(42, 'pending', 'hackerstatus', 5, 'evil');
assert_test($log_id === 0, 'T2b log_status_change rejects invalid slug (defense in depth)');
assert_test(count(get_status_history(42)) === 0, 'T2c nothing written');

// T3: первая смена (from=null) для свеже-созданной заявки
reset_ld();
seed_vocab_ld();
$log_id = log_status_change(99, null, 'pending', 5, 'Заявка создана');
assert_test($log_id > 0, 'T3a first log entry written');
$h = get_status_history(99);
assert_test($h[0]['from_status'] === null, 'T3b first entry has null from');

echo "$tests tests, $failures failures\n";
exit($failures > 0 ? 1 : 0);
