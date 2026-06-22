<?php
require_once __DIR__ . '/fixtures/wp-bootstrap.php';
require_once __DIR__ . '/../mu-plugin/landing-config/includes/cascade.php';
require_once __DIR__ . '/../mu-plugin/landing-config/includes/encryption.php';
require_once __DIR__ . '/../mu-plugin/landing-config/includes/helpers.php';
require_once __DIR__ . '/../mu-plugin/landing-config/includes/integrations.php';
require_once __DIR__ . '/../mu-plugin/landing-config/adapters/AdapterInterface.php';
require_once __DIR__ . '/../mu-plugin/landing-config/adapters/EmailAdapter.php';
require_once __DIR__ . '/../mu-plugin/landing-config/includes/lead-dispatcher.php';

use function LandingConfig\Integrations\save_integration;
use function LandingConfig\Integrations\get_integration;
use function LandingConfig\Integrations\resolve_integration;
use function LandingConfig\Integrations\list_integrations;
use function LandingConfig\Integrations\delete_integration;

$failures = 0; $tests = 0;
function assert_test($c, $m) { global $failures, $tests; $tests++; if (!$c) { echo "FAIL: $m\n"; $failures++; } }

function reset_int() {
    $GLOBALS['_mock_posts'] = [];
    $GLOBALS['_mock_post_meta'] = [];
    $GLOBALS['_mock_next_post_id'] = 1;
    $GLOBALS['_mock_current_blog_id'] = 1;
    $GLOBALS['_mock_mail_sent'] = [];
    $GLOBALS['_mock_actions_fired'] = [];
    putenv('WP_LANDING_CONFIG_KEY=' . str_repeat('a', 32));
}

// T1 round-trip with encrypted field
reset_int();
$id = save_integration('telegram', ['bot_token' => 'SECRET123', 'chat_id' => '-1001'], true, 1, ['bot_token']);
assert_test($id > 0, 'T1a save_integration returned id');
$row = get_integration($id);
assert_test($row['settings']['bot_token'] === 'SECRET123', 'T1b token decrypted on get');
assert_test($row['adapter_name'] === 'telegram' && $row['is_network'] === true, 'T1c name+network correct');

// T2 cascade override
reset_int();
save_integration('amocrm', ['domain' => 'net.amocrm.ru', 'token' => 'NET'], true, 1, ['token']);
$GLOBALS['_mock_current_blog_id'] = 2;
save_integration('amocrm', ['domain' => 'site.amocrm.ru', 'token' => 'SITE'], false, 2, ['token']);
$r = resolve_integration('amocrm', 2);
assert_test($r['settings']['domain'] === 'site.amocrm.ru', 'T2a site override domain');
assert_test($r['settings']['token'] === 'SITE', 'T2b site override token decrypted');

// T3 network fallback
$r = resolve_integration('amocrm', 1);
assert_test($r['settings']['domain'] === 'net.amocrm.ru', 'T3 network fallback');

// T4 list merge
reset_int();
save_integration('email', ['to' => 'net@x.ru'], true, 1, []);
$GLOBALS['_mock_current_blog_id'] = 2;
save_integration('telegram', ['bot_token' => 'T', 'chat_id' => '1'], false, 2, ['bot_token']);
$list = list_integrations(2);
$names = array_column($list, 'adapter_name');
assert_test(in_array('email', $names) && in_array('telegram', $names), 'T4 list merge');

// T5 delete
reset_int();
$id = save_integration('email', ['to' => 'x@y.z'], false, 1, []);
assert_test(delete_integration($id) === true && get_integration($id) === null, 'T5 delete works');

// T6 update path — repeated save with $post_id updates instead of duplicating
reset_int();
$id1 = save_integration('telegram', ['bot_token' => 'OLD', 'chat_id' => '1'], false, 1, ['bot_token']);
$id2 = save_integration('telegram', ['bot_token' => 'NEW', 'chat_id' => '2'], false, 1, ['bot_token'], true, $id1);
assert_test($id1 === $id2, 'T6a update reuses same post id');
$row = get_integration($id1);
assert_test($row['settings']['chat_id'] === '2', 'T6b updated value persists');
$list = list_integrations(1);
$tg_count = 0;
foreach ($list as $r) if ($r['adapter_name'] === 'telegram') $tg_count++;
assert_test($tg_count === 1, 'T6c no duplicate row after update');

// T7 decrypt failure preserves ciphertext (does not silently blank)
reset_int();
// Manually inject garbled ciphertext into post_meta — bypass encryption layer
$post_id = \wp_insert_post(['post_type' => 'lp_integration', 'post_status' => 'publish', 'post_title' => 'email']);
\update_post_meta($post_id, '_lp_int_adapter_name', 'email');
\update_post_meta($post_id, '_lp_int_settings', ['api_key' => 'NOT_VALID_CIPHERTEXT_xxxx']);
\update_post_meta($post_id, '_lp_int_encrypted_fields', ['api_key']);
\update_post_meta($post_id, '_lp_int_is_network', '0');
$row = get_integration($post_id);
// On decrypt failure, value must NOT be silently blanked; either ciphertext preserved or null/error sentinel
assert_test($row['settings']['api_key'] !== '', 'T7 decrypt failure does not silently blank field');

// T8 lead dispatcher sends to enabled integration
reset_int();
save_integration('email', ['to' => 'sales@example.com', 'subject' => 'Новая заявка'], false, 1, []);
\LandingConfig\LeadDispatcher\dispatch(501, [
    'name' => 'Анна',
    'phone' => '+79990000000',
    'email' => 'anna@example.com',
    'message' => 'Хочу консультацию',
    'source_block' => 'hero',
    'utm_source' => 'direct',
    'utm_medium' => '',
    'utm_campaign' => '',
    'created_at' => '2026-06-22 10:00:00',
]);
assert_test(count($GLOBALS['_mock_mail_sent']) === 1, 'T8a dispatcher sent one email');
assert_test($GLOBALS['_mock_mail_sent'][0]['to'] === 'sales@example.com', 'T8b dispatcher used integration email');

echo "$tests tests, $failures failures\n";
exit($failures > 0 ? 1 : 0);
