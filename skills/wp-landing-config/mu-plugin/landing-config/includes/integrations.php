<?php
namespace LandingConfig\Integrations;

if (!defined('ABSPATH')) { exit; }

use function LandingConfig\Cascade\list_for_blog;
use function LandingConfig\Cascade\has_site_override;
use function LandingConfig\Encryption\encrypt;
use function LandingConfig\Encryption\decrypt;

const POST_TYPE            = 'lp_integration';
const NAME_META            = '_lp_int_adapter_name';
const ADAPTER_TYPE_META    = '_lp_int_adapter_type';
const LABEL_META           = '_lp_int_label';
const DESCRIPTION_META     = '_lp_int_description';
const NETWORK_META         = '_lp_int_is_network';
const SETTINGS_META        = '_lp_int_settings';
const ENCRYPTED_FIELDS_META = '_lp_int_encrypted_fields';
const ENABLED_META         = '_lp_int_enabled';

const VALID_ADAPTERS = ['email', 'telegram', 'whatsapp', 'amocrm', 'bitrix24', 'hubspot'];

add_action('init', __NAMESPACE__ . '\\register', 5);

function register(): void {
    register_post_type(POST_TYPE, [
        'public'          => false,
        'show_ui'         => false,
        'show_in_menu'    => false,
        'show_in_rest'    => false,
        'supports'        => ['title'],
        'capability_type' => 'post',
        'map_meta_cap'    => true,
        'capabilities'    => [
            'edit_posts'        => 'manage_options',
            'edit_others_posts' => 'manage_options',
            'publish_posts'     => 'manage_options',
            'delete_posts'      => 'manage_options',
            'read'              => 'read',
        ],
    ]);
}

function _with_blog(int $blog_id, callable $fn) {
    $prev = \get_current_blog_id();
    if ($prev === $blog_id) return $fn();
    \switch_to_blog($blog_id);
    try { return $fn(); }
    finally { \restore_current_blog(); }
}

function _encrypt_settings(array $settings, array $encrypted_fields): array {
    foreach ($encrypted_fields as $f) {
        if (isset($settings[$f]) && $settings[$f] !== '') {
            $val = (string) $settings[$f];
            if (!str_starts_with($val, 'v1:')) {
                $settings[$f] = encrypt($val);
            }
        }
    }
    return $settings;
}

function _decrypt_settings(array $settings, array $encrypted_fields): array {
    foreach ($encrypted_fields as $f) {
        if (isset($settings[$f]) && is_string($settings[$f]) && $settings[$f] !== '') {
            if (str_starts_with($settings[$f], 'v1:')) {
                $decrypted = decrypt($settings[$f]);
                if ($decrypted !== '') $settings[$f] = $decrypted;
            }
        }
    }
    return $settings;
}

/**
 * Save (create or update) an integration record.
 *
 * @param string $adapter_type  Adapter slug ('telegram', 'email', …)
 * @param string $label         User-defined display name (required)
 * @param string $description   Optional description
 * @param array  $settings      Field values
 * @param bool   $is_network
 * @param int    $blog_id
 * @param array  $encrypted_fields  Field keys that should be encrypted
 * @param bool   $enabled
 * @param int    $post_id       >0 to update existing record
 * @return int  Post ID, 0 on failure
 */
function save_integration(
    string $adapter_type,
    string $label,
    string $description,
    array  $settings,
    bool   $is_network,
    int    $blog_id,
    array  $encrypted_fields = [],
    bool   $enabled = true,
    int    $post_id = 0
): int {
    if (!in_array($adapter_type, VALID_ADAPTERS, true)) return 0;
    if ($label === '') $label = $adapter_type;

    return _with_blog($blog_id, function () use (
        $adapter_type, $label, $description,
        $settings, $is_network, $encrypted_fields, $enabled, $post_id
    ) {
        $post = [
            'post_type'   => POST_TYPE,
            'post_status' => 'publish',
            'post_title'  => $label,
        ];
        if ($post_id > 0) {
            $post['ID'] = $post_id;
            $id = \wp_update_post($post);
        } else {
            $id = \wp_insert_post($post);
        }
        if (!$id || \is_wp_error($id)) return 0;
        \update_post_meta($id, ADAPTER_TYPE_META,    $adapter_type);
        \update_post_meta($id, NAME_META,             $adapter_type);
        \update_post_meta($id, LABEL_META,            $label);
        \update_post_meta($id, DESCRIPTION_META,      $description);
        \update_post_meta($id, SETTINGS_META,         _encrypt_settings($settings, $encrypted_fields));
        \update_post_meta($id, ENCRYPTED_FIELDS_META, $encrypted_fields);
        \update_post_meta($id, NETWORK_META,          $is_network ? '1' : '0');
        \update_post_meta($id, ENABLED_META,          $enabled ? '1' : '0');
        return (int) $id;
    });
}

function get_integration(int $id): ?array {
    $p = \get_post($id);
    if (!$p || ($p->post_type ?? '') !== POST_TYPE) return null;
    $settings = \get_post_meta($id, SETTINGS_META, true);
    $settings = is_array($settings) ? $settings : [];
    $encrypted_fields = \get_post_meta($id, ENCRYPTED_FIELDS_META, true);
    $encrypted_fields = is_array($encrypted_fields) ? $encrypted_fields : [];

    $adapter_type = (string) \get_post_meta($id, ADAPTER_TYPE_META, true);
    if ($adapter_type === '') {
        $adapter_type = (string) \get_post_meta($id, NAME_META, true);
    }
    $label = (string) \get_post_meta($id, LABEL_META, true);
    if ($label === '') {
        $label = $p->post_title ?: $adapter_type;
    }

    return [
        'id'               => $id,
        'adapter_type'     => $adapter_type,
        'adapter_name'     => $adapter_type,
        'label'            => $label,
        'description'      => (string) \get_post_meta($id, DESCRIPTION_META, true),
        'settings'         => _decrypt_settings($settings, $encrypted_fields),
        'encrypted_fields' => $encrypted_fields,
        'is_network'       => (string) \get_post_meta($id, NETWORK_META, true) === '1',
        'enabled'          => (string) \get_post_meta($id, ENABLED_META, true) === '1',
    ];
}

function delete_integration(int $id): bool {
    return (bool) \wp_delete_post($id, true);
}

/**
 * List ALL integration records visible for a given blog (network + site-level).
 */
function list_integrations(int $blog_id): array {
    return _with_blog($blog_id, function () {
        $posts = \get_posts([
            'post_type'      => POST_TYPE,
            'post_status'    => 'publish',
            'posts_per_page' => -1,
            'orderby'        => 'date',
            'order'          => 'ASC',
        ]);
        $out = [];
        foreach ($posts as $p) {
            $entry = get_integration($p->ID);
            if ($entry) $out[] = $entry;
        }
        return $out;
    });
}

/**
 * List all enabled integrations of a specific adapter type.
 */
function list_integrations_by_type(string $adapter_type, int $blog_id): array {
    $all = list_integrations($blog_id);
    return array_values(array_filter($all, function ($r) use ($adapter_type) {
        return $r['adapter_type'] === $adapter_type && $r['enabled'];
    }));
}

/**
 * Resolve FIRST enabled integration of a given type (BC shim for adapters).
 */
function resolve_integration(string $adapter_name, int $blog_id): ?array {
    $list = list_integrations_by_type($adapter_name, $blog_id);
    return $list[0] ?? null;
}

function has_override(string $adapter_name, int $blog_id): bool {
    return has_site_override(POST_TYPE, NAME_META, NETWORK_META, $adapter_name, $blog_id);
}

/**
 * One-time migration: backfill ADAPTER_TYPE_META and LABEL_META on legacy records
 * that only have NAME_META (post_title = adapter slug).
 * Idempotent — skips records that already have adapter_type set.
 */
function maybe_migrate_legacy_records(): void {
    if (\get_option('landing_config_migration_integrations_labels')) return;

    $posts = \get_posts([
        'post_type'      => POST_TYPE,
        'post_status'    => 'publish',
        'posts_per_page' => -1,
        'meta_query'     => [[
            'key'     => ADAPTER_TYPE_META,
            'compare' => 'NOT EXISTS',
        ]],
    ]);

    foreach ($posts as $p) {
        $adapter = (string) \get_post_meta($p->ID, NAME_META, true);
        if ($adapter === '') $adapter = $p->post_title;
        if (!in_array($adapter, VALID_ADAPTERS, true)) continue;
        \update_post_meta($p->ID, ADAPTER_TYPE_META, $adapter);
        $label = (string) \get_post_meta($p->ID, LABEL_META, true);
        if ($label === '') {
            \update_post_meta($p->ID, LABEL_META, $adapter);
        }
    }
    \update_option('landing_config_migration_integrations_labels', '1');
}

add_action('admin_init', __NAMESPACE__ . '\\maybe_migrate_legacy_records');
