<?php
namespace LandingConfig\Migrate;

if (!defined('ABSPATH')) { exit; }

use function LandingConfig\CTA\save_cta;
use function LandingConfig\CTA\list_ctas;
use function LandingConfig\Integrations\list_integrations;
use function LandingConfig\Integrations\save_integration;
use const LandingConfig\CTA\PRESET_NAMES;
use const LandingConfig\Integrations\VALID_ADAPTERS;

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
    return $count;
}

/**
 * Map adapter machine name to its class name.
 */
function _class_for_adapter(string $name): string {
    return match ($name) {
        'email'    => 'EmailAdapter',
        'telegram' => 'TelegramAdapter',
        'whatsapp' => 'WhatsAppAdapter',
        'amocrm'   => 'AmoCRMAdapter',
        'bitrix24' => 'Bitrix24Adapter',
        'hubspot'  => 'HubSpotAdapter',
        default    => '',
    };
}

/**
 * Collect legacy per-field wp_options for one adapter.
 * Returns ['settings' => [...], 'encrypted_fields' => [...]]
 *
 * Legacy storage (admin-integrations.php): one wp_option per field,
 * keyed landing_integration_{name}_{field}. Password fields were already
 * encrypted by sanitize_secret() before storing — we must NOT re-encrypt.
 */
function _collect_legacy_integration(string $adapter_name): array {
    $cls = '\\LandingConfig\\Adapters\\' . _class_for_adapter($adapter_name);
    if (!class_exists($cls)) return ['settings' => [], 'encrypted_fields' => []];

    $settings = [];
    $encrypted_fields = [];

    // Merge field keys from both field_defs() (legacy) and field_definitions() (new)
    $legacy_keys = method_exists($cls, 'field_defs') ? array_keys($cls::field_defs()) : [];
    $new_keys    = method_exists($cls, 'field_definitions') ? array_keys($cls::field_definitions()) : [];
    $all_keys    = array_unique(array_merge($legacy_keys, $new_keys));

    foreach ($all_keys as $field) {
        $val = \get_option("landing_integration_{$adapter_name}_{$field}", '');
        if ($val !== '' && $val !== false) {
            $settings[$field] = $val;
        }
    }

    // Collect encrypted_fields for metadata — but do NOT re-encrypt (values already encrypted in legacy)
    if (method_exists($cls, 'field_definitions')) {
        foreach ($cls::field_definitions() as $f => $meta) {
            if (!empty($meta['encrypt'])) $encrypted_fields[] = $f;
        }
    }

    return ['settings' => $settings, 'encrypted_fields' => $encrypted_fields];
}

/**
 * Migrate legacy per-field wp_options integration config → lp_integration CPT
 * for the given $network_blog_id (network-level / main site).
 *
 * Idempotent: returns 0 if any CPT rows already exist for this blog (is_network=true rows).
 *
 * Password fields in legacy storage were already encrypted by sanitize_secret().
 * We pass encrypted_fields=[] to save_integration so it does NOT double-encrypt.
 * The ENCRYPTED_FIELDS_META meta is stored empty, which is consistent — the CPT
 * row's decrypt path will skip empty encrypted_fields and return values as-is.
 *
 * @return int count of CPT records created
 */
function migrate_integrations_from_options(int $network_blog_id): int {
    // Idempotency: if any network-level lp_integration rows already exist, skip
    $existing = list_integrations($network_blog_id);
    foreach ($existing as $r) {
        if ($r['is_network']) return 0;
    }

    $count = 0;
    foreach (VALID_ADAPTERS as $adapter_name) {
        $collected = _collect_legacy_integration($adapter_name);
        if (empty($collected['settings'])) continue;

        // encrypted_fields=[] intentionally: legacy values already encrypted;
        // passing them would cause double-encryption in save_integration → _encrypt_settings.
        save_integration(
            $adapter_name,
            $collected['settings'],
            true,            // is_network
            $network_blog_id,
            [],              // encrypted_fields — skip re-encryption
            true             // enabled
        );
        $count++;
    }
    return $count;
}

/**
 * Migrate legacy per-field wp_options integration config for a subsite.
 * Idempotent: skips if any site-level (is_network=false) rows already exist.
 *
 * @return int count of CPT records created
 */
function migrate_subsite_integrations(int $blog_id): int {
    \switch_to_blog($blog_id);
    try {
        // Idempotency: if any site-level lp_integration rows exist, skip
        $existing = list_integrations($blog_id);
        foreach ($existing as $r) {
            if (!$r['is_network']) return 0;
        }

        $count = 0;
        foreach (VALID_ADAPTERS as $adapter_name) {
            $collected = _collect_legacy_integration($adapter_name);
            if (empty($collected['settings'])) continue;

            save_integration(
                $adapter_name,
                $collected['settings'],
                false,   // is_network — site-level for subsite
                $blog_id,
                [],      // encrypted_fields — skip re-encryption
                true     // enabled
            );
            $count++;
        }
        return $count;
    } finally {
        \restore_current_blog();
    }
}

/**
 * Entry point: run migration once per network when not already done.
 * Hooked from landing-config.php on admin_init for super-admin context.
 */
function maybe_run(): void {
    if (\get_site_option(MARKER_OPTION) === '1') return;
    $main = \function_exists('get_main_site_id') ? \get_main_site_id() : 1;
    migrate_cta_from_options($main);
    migrate_integrations_from_options($main);
    seed_default_lead_statuses($main);
    if (\function_exists('get_sites')) {
        foreach (\get_sites(['number' => 0]) as $site) {
            if ((int) $site->blog_id === $main) continue;
            migrate_subsite_integrations((int) $site->blog_id);
        }
    }
    \update_site_option(MARKER_OPTION, '1');
}

/**
 * Создать 5 default-статусов для свежего сайта (B19). Идемпотентно:
 * если хоть один статус уже есть — возвращает 0 без действий.
 * Маркетолог может удалить/переименовать/добавить — seed повторно не сработает.
 */
function seed_default_lead_statuses(int $network_blog_id): int {
    $existing = \LandingConfig\LeadStatuses\list_lead_statuses($network_blog_id);
    if (!empty($existing)) return 0;

    $defaults = [
        ['slug' => 'pending',     'label' => 'Новая',            'color' => '#2271b1', 'order' => 10],
        ['slug' => 'in_progress', 'label' => 'В работе',         'color' => '#dba617', 'order' => 20],
        ['slug' => 'won',         'label' => 'Закрыта успешно',  'color' => '#00a32a', 'order' => 30],
        ['slug' => 'lost',        'label' => 'Отказ',            'color' => '#d63638', 'order' => 40],
        ['slug' => 'spam',        'label' => 'Спам',             'color' => '#646970', 'order' => 50],
    ];

    $count = 0;
    foreach ($defaults as $d) {
        $id = \LandingConfig\LeadStatuses\save_lead_status($d, true, $network_blog_id);
        if ($id > 0) $count++;
    }
    return $count;
}
