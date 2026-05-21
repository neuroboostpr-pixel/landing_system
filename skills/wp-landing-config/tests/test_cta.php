<?php
require_once __DIR__ . '/fixtures/wp-bootstrap.php';
require_once __DIR__ . '/../mu-plugin/landing-config/includes/cascade.php';
require_once __DIR__ . '/../mu-plugin/landing-config/includes/cta.php';

use function LandingConfig\CTA\save_cta;
use function LandingConfig\CTA\get_cta;
use function LandingConfig\CTA\list_ctas;
use function LandingConfig\CTA\delete_cta;
use function LandingConfig\CTA\resolve_cta;

$failures = 0; $tests = 0;
function assert_test($cond, $msg) { global $failures, $tests; $tests++; if (!$cond) { echo "FAIL: $msg\n"; $failures++; } }

function reset_cta() {
    $GLOBALS['_mock_posts'] = [];
    $GLOBALS['_mock_post_meta'] = [];
    $GLOBALS['_mock_next_post_id'] = 1;
    $GLOBALS['_mock_current_blog_id'] = 1;
    $GLOBALS['_mock_blog_stack'] = [];
}

// T1: save+get round-trip
reset_cta();
$id = save_cta(['preset_name' => 'primary', 'type' => 'scroll', 'label' => 'Заявка',
    'target' => '#form', 'phone' => '', 'form_id' => '', 'message_template' => ''], false, 1);
assert_test($id > 0, 'T1a save_cta returns id');
$row = get_cta($id);
assert_test($row['preset_name'] === 'primary' && $row['label'] === 'Заявка', 'T1b round-trip CTA');
assert_test($row['is_network'] === false, 'T1c is_network=false stored');

// T2: cascade — site override wins
reset_cta();
save_cta(['preset_name' => 'whatsapp', 'type' => 'whatsapp', 'label' => 'NET WA',
    'target' => '', 'phone' => '+1', 'form_id' => '', 'message_template' => ''], true, 1);
$GLOBALS['_mock_current_blog_id'] = 2;
save_cta(['preset_name' => 'whatsapp', 'type' => 'whatsapp', 'label' => 'RUSSIAN WA',
    'target' => '', 'phone' => '+7', 'form_id' => '', 'message_template' => ''], false, 2);
$r = resolve_cta('whatsapp', 2);
assert_test($r['label'] === 'RUSSIAN WA' && $r['phone'] === '+7', 'T2 site override wins on blog_id=2');

// T3: cascade — fallback to network
$r = resolve_cta('whatsapp', 1);  // blog_id=1 has only network record
assert_test($r['label'] === 'NET WA', 'T3 network fallback on blog_id=1');

// T4: list_ctas for blog_id=2 returns merged
reset_cta();
save_cta(['preset_name' => 'primary', 'type' => 'scroll', 'label' => 'Net Primary',
    'target' => '#form', 'phone' => '', 'form_id' => '', 'message_template' => ''], true, 1);
$GLOBALS['_mock_current_blog_id'] = 2;
save_cta(['preset_name' => 'whatsapp', 'type' => 'whatsapp', 'label' => 'Site WA',
    'target' => '', 'phone' => '+7', 'form_id' => '', 'message_template' => ''], false, 2);
$list = list_ctas(2);
$names = array_column($list, 'preset_name');
assert_test(in_array('primary', $names) && in_array('whatsapp', $names), 'T4 list merges network + site');

// T5: delete_cta removes record
reset_cta();
$id = save_cta(['preset_name' => 'phone', 'type' => 'tel', 'label' => 'Call', 'target' => '',
    'phone' => '+1', 'form_id' => '', 'message_template' => ''], false, 1);
assert_test(delete_cta($id) === true, 'T5a delete returns true');
assert_test(get_cta($id) === null, 'T5b deleted CTA returns null');

// T6: invalid preset_name → save_cta returns 0
reset_cta();
$id = save_cta(['preset_name' => 'nonexistent', 'type' => 'scroll', 'label' => 'X',
    'target' => '', 'phone' => '', 'form_id' => '', 'message_template' => ''], false, 1);
assert_test($id === 0, 'T6 invalid preset returns 0');

// T7: get_cta on wrong post_type returns null
reset_cta();
$wrong_id = \wp_insert_post(['post_type' => 'post', 'post_status' => 'publish', 'post_title' => 'not a CTA']);
assert_test(get_cta($wrong_id) === null, 'T7 get_cta returns null on wrong post_type');

echo "$tests tests, $failures failures\n";
exit($failures > 0 ? 1 : 0);
