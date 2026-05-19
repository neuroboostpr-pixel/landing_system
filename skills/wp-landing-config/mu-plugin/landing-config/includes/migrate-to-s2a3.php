<?php
namespace LandingConfig\Migrate;

if (!defined('ABSPATH')) { exit; }

use function LandingConfig\CTA\save_cta;
use function LandingConfig\CTA\list_ctas;
use const LandingConfig\CTA\PRESET_NAMES;

const MARKER_OPTION = 'landing_config_migration_s2a3_cta';

/**
 * Migrate wp_options.landing_cta_presets → lp_cta CPT records on $network_blog_id.
 * Idempotent: returns 0 if CPT already has records, or if wp_options is empty.
 * Marker site_option is set on successful migration to skip future runs.
 *
 * @return int count of records created
 */
function migrate_cta_from_options(int $network_blog_id): int {
    // Idempotency: if CPT already has any network records on blog_id, skip
    $existing = list_ctas($network_blog_id);
    foreach ($existing as $row) {
        if (!empty($row['is_network'])) {
            return 0;
        }
    }

    $opts = \LandingConfig\Cascade\_with_blog($network_blog_id, function () {
        return \get_option('landing_cta_presets', null);
    });
    if (!is_array($opts) || empty($opts)) {
        return 0;
    }
    $count = 0;
    foreach ($opts as $name => $cfg) {
        if (!in_array($name, PRESET_NAMES, true)) continue;
        if (!is_array($cfg)) continue;
        $id = save_cta([
            'preset_name'      => $name,
            'type'             => $cfg['type'] ?? 'scroll',
            'label'            => $cfg['label'] ?? '',
            'target'           => $cfg['target'] ?? '',
            'phone'            => $cfg['phone'] ?? '',
            'form_id'          => $cfg['form_id'] ?? '',
            'message_template' => $cfg['message_template'] ?? '',
        ], true, $network_blog_id);
        if ($id > 0) $count++;
    }
    if ($count > 0) {
        \update_site_option(MARKER_OPTION, '1');
    }
    return $count;
}

/**
 * Entry point: run migration once per network when not already done.
 * Hooked from landing-config.php on admin_init for super-admin context.
 */
function maybe_run(): void {
    if (\get_site_option(MARKER_OPTION) === '1') return;
    $main = \function_exists('get_main_site_id') ? \get_main_site_id() : 1;
    migrate_cta_from_options($main);
}
