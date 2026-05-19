<?php
require_once __DIR__ . '/fixtures/wp-bootstrap.php';
require_once __DIR__ . '/../mu-plugin/landing-config/includes/cascade.php';
require_once __DIR__ . '/../mu-plugin/landing-config/includes/encryption.php';
require_once __DIR__ . '/../mu-plugin/landing-config/includes/cta.php';
require_once __DIR__ . '/../mu-plugin/landing-config/includes/integrations.php';
require_once __DIR__ . '/../mu-plugin/landing-config/adapters/AdapterInterface.php';
require_once __DIR__ . '/../mu-plugin/landing-config/adapters/EmailAdapter.php';
require_once __DIR__ . '/../mu-plugin/landing-config/adapters/TelegramAdapter.php';
require_once __DIR__ . '/../mu-plugin/landing-config/adapters/WhatsAppAdapter.php';
require_once __DIR__ . '/../mu-plugin/landing-config/adapters/AmoCRMAdapter.php';
require_once __DIR__ . '/../mu-plugin/landing-config/adapters/Bitrix24Adapter.php';
require_once __DIR__ . '/../mu-plugin/landing-config/adapters/HubSpotAdapter.php';
require_once __DIR__ . '/../mu-plugin/landing-config/includes/migrate-to-s2a3.php';

use function LandingConfig\Migrate\migrate_cta_from_options;
use function LandingConfig\Migrate\migrate_integrations_from_options;
use function LandingConfig\CTA\list_ctas;
use function LandingConfig\Integrations\list_integrations;

$failures = 0; $tests = 0;
function assert_test($c, $m) { global $failures, $tests; $tests++; if (!$c) { echo "FAIL: $m\n"; $failures++; } }

function reset_mig() {
    $GLOBALS['_mock_posts'] = [];
    $GLOBALS['_mock_post_meta'] = [];
    $GLOBALS['_mock_next_post_id'] = 1;
    $GLOBALS['_mock_current_blog_id'] = 1;
    $GLOBALS['_mock_blog_stack'] = [];
    $GLOBALS['_mock_options'] = [];
    $GLOBALS['_mock_site_meta'] = [];   // wp-bootstrap uses _mock_site_meta for get_site_option/update_site_option
}

// T1: миграция 2 пресетов из wp_options.landing_cta_presets → 2 CPT записи is_network=1
reset_mig();
$GLOBALS['_mock_options'][1]['landing_cta_presets'] = [
    'primary' => ['type' => 'scroll', 'target' => '#form', 'label' => 'Primary',
                  'phone' => '', 'form_id' => '', 'message_template' => ''],
    'whatsapp' => ['type' => 'whatsapp', 'target' => '', 'label' => 'WA',
                   'phone' => '+1', 'form_id' => '', 'message_template' => 'Hello'],
];
$migrated = migrate_cta_from_options(1);
assert_test($migrated === 2, "T1a migrated count == 2 (got $migrated)");
$list = list_ctas(1);
assert_test(count($list) === 2, 'T1b 2 CPT records exist on blog_id=1');
$by_name = [];
foreach ($list as $r) { $by_name[$r['preset_name']] = $r; }
assert_test(($by_name['primary']['label'] ?? '') === 'Primary' && ($by_name['primary']['is_network'] ?? null) === true,
    'T1c primary CPT correct (label + is_network=true)');
assert_test(($by_name['whatsapp']['phone'] ?? '') === '+1' && ($by_name['whatsapp']['message_template'] ?? '') === 'Hello',
    'T1d whatsapp CPT correct (phone + message_template)');

// T2: idempotent — повторный прогон no-op
$migrated_again = migrate_cta_from_options(1);
assert_test($migrated_again === 0, "T2 second run is no-op (got $migrated_again)");

// T3: empty wp_options → no migration, no marker
reset_mig();
$migrated = migrate_cta_from_options(1);
assert_test($migrated === 0, 'T3 empty wp_options → no migration');

// T4: unknown preset names skipped (not in PRESET_NAMES)
reset_mig();
$GLOBALS['_mock_options'][1]['landing_cta_presets'] = [
    'primary' => ['type' => 'scroll', 'target' => '#x', 'label' => 'P',
                  'phone' => '', 'form_id' => '', 'message_template' => ''],
    'invalid_name' => ['type' => 'scroll', 'target' => '#y', 'label' => 'X',
                       'phone' => '', 'form_id' => '', 'message_template' => ''],
];
$migrated = migrate_cta_from_options(1);
assert_test($migrated === 1, "T4 only valid preset migrated (got $migrated, expected 1)");

// T_INT_1..4: миграция integrations wp_options → CPT (per-field key layout)
reset_mig();
// Legacy data layout: per-field wp_options written by old admin-integrations.php
\update_option('landing_integration_telegram_bot_token', 'X');
\update_option('landing_integration_telegram_chat_id', '-1');
\update_option('landing_integration_amocrm_subdomain', 'acme');
\update_option('landing_integration_amocrm_access_token', 'Y');

$migrated = migrate_integrations_from_options(1);
assert_test($migrated === 2, "T_INT_1 migrated 2 integrations (got $migrated)");
$list = list_integrations(1);
assert_test(count($list) === 2, 'T_INT_2 2 CPT records exist');
$by_name = [];
foreach ($list as $r) { $by_name[$r['adapter_name']] = $r; }
assert_test(isset($by_name['telegram']) && $by_name['telegram']['settings']['chat_id'] === '-1', 'T_INT_3 telegram migrated');
assert_test(isset($by_name['amocrm']) && $by_name['amocrm']['settings']['subdomain'] === 'acme', 'T_INT_4 amocrm migrated');

// T_INT_5: idempotent — second run is no-op
$again = migrate_integrations_from_options(1);
assert_test($again === 0, "T_INT_5 idempotent (got $again)");

// T_INT_6: migrate_cta_from_options does NOT set MARKER_OPTION on its own.
// Regression for: marker was previously set inside migrate_cta and silently
// skipped integrations migration on next maybe_run() call.
reset_mig();
$GLOBALS['_mock_options'][1]['landing_cta_presets'] = [
    'primary' => ['type' => 'scroll', 'target' => '#x', 'label' => 'X',
                  'phone' => '', 'form_id' => '', 'message_template' => ''],
];
migrate_cta_from_options(1);
assert_test(\get_site_option(\LandingConfig\Migrate\MARKER_OPTION) !== '1',
    'T_INT_6 migrate_cta does not set MARKER_OPTION (maybe_run owns marker)');

echo "$tests tests, $failures failures\n";
exit($failures > 0 ? 1 : 0);
