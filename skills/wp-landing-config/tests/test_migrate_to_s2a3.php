<?php
require_once __DIR__ . '/fixtures/wp-bootstrap.php';
require_once __DIR__ . '/../mu-plugin/landing-config/includes/cascade.php';
require_once __DIR__ . '/../mu-plugin/landing-config/includes/cta.php';
require_once __DIR__ . '/../mu-plugin/landing-config/includes/migrate-to-s2a3.php';

use function LandingConfig\Migrate\migrate_cta_from_options;
use function LandingConfig\CTA\list_ctas;

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

echo "$tests tests, $failures failures\n";
exit($failures > 0 ? 1 : 0);
