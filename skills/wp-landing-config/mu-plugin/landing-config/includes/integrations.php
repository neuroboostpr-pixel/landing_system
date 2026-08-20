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

const VALID_ADAPTERS = ['email', 'telegram', 'whatsapp', 'amocrm', 'bitrix24', 'hubspot', 'roistat'];

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

/** @return array{ok:bool,integration:?array} */
function get_integration_checked(int $id): array {
    global $wpdb;
    if (isset($wpdb->last_error)) { $wpdb->last_error = ''; }
    $p = \get_post($id);
    if ((string)($wpdb->last_error ?? '') !== '') { return ['ok' => false, 'integration' => null]; }
    if (!$p || ($p->post_type ?? '') !== POST_TYPE) { return ['ok' => true, 'integration' => null]; }

    $read_meta = static function (string $key, bool &$ok) use ($id, $wpdb) {
        if (isset($wpdb->last_error)) { $wpdb->last_error = ''; }
        $value = \get_post_meta($id, $key, true);
        if ((string)($wpdb->last_error ?? '') !== '') { $ok = false; }
        return $value;
    };
    $ok = true;
    $settings = $read_meta(SETTINGS_META, $ok);
    $settings = is_array($settings) ? $settings : [];
    $encrypted_fields = $read_meta(ENCRYPTED_FIELDS_META, $ok);
    $encrypted_fields = is_array($encrypted_fields) ? $encrypted_fields : [];

    $adapter_type = (string)$read_meta(ADAPTER_TYPE_META, $ok);
    if ($adapter_type === '') {
        $adapter_type = (string)$read_meta(NAME_META, $ok);
    }
    $label = (string)$read_meta(LABEL_META, $ok);
    if ($label === '') {
        $label = $p->post_title ?: $adapter_type;
    }
    $description = (string)$read_meta(DESCRIPTION_META, $ok);
    $is_network = (string)$read_meta(NETWORK_META, $ok) === '1';
    $enabled = (string)$read_meta(ENABLED_META, $ok) === '1';
    if (!$ok) { return ['ok' => false, 'integration' => null]; }

    return ['ok' => true, 'integration' => [
        'id'               => $id,
        'adapter_type'     => $adapter_type,
        'adapter_name'     => $adapter_type,
        'label'            => $label,
        'description'      => $description,
        'settings'         => _decrypt_settings($settings, $encrypted_fields),
        'encrypted_fields' => $encrypted_fields,
        'is_network'       => $is_network,
        'enabled'          => $enabled,
    ]];
}

function get_integration(int $id): ?array {
    $result = get_integration_checked($id);
    return ($result['ok'] ?? false) && is_array($result['integration'] ?? null)
        ? $result['integration'] : null;
}

/**
 * Read one exact integration for the delivery worker directly from MySQL.
 * WordPress may cache an empty post-meta array after a transient SQL failure;
 * bypassing that cache prevents the next retry from treating a healthy
 * Email/Telegram/CRM channel as permanently disabled.
 *
 * @return array{ok:bool,integration:?array}
 */
function get_delivery_integration_checked(int $id): array {
    if ($id <= 0) { return ['ok' => true, 'integration' => null]; }
    global $wpdb;
    $posts = str_replace('`', '', $wpdb->get_blog_prefix() . 'posts');
    $postmeta = str_replace('`', '', $wpdb->get_blog_prefix() . 'postmeta');
    if (isset($wpdb->last_error)) { $wpdb->last_error = ''; }
    $sql = $wpdb->prepare(
        "/* landing_delivery_integration */ SELECT p.ID,p.post_title,p.post_type,p.post_status,"
        . " MAX(CASE WHEN pm.meta_key=%s THEN pm.meta_value END) AS adapter_type,"
        . " MAX(CASE WHEN pm.meta_key=%s THEN pm.meta_value END) AS legacy_adapter_type,"
        . " MAX(CASE WHEN pm.meta_key=%s THEN pm.meta_value END) AS label,"
        . " MAX(CASE WHEN pm.meta_key=%s THEN pm.meta_value END) AS description,"
        . " MAX(CASE WHEN pm.meta_key=%s THEN pm.meta_value END) AS settings,"
        . " MAX(CASE WHEN pm.meta_key=%s THEN pm.meta_value END) AS encrypted_fields,"
        . " MAX(CASE WHEN pm.meta_key=%s THEN pm.meta_value END) AS is_network,"
        . " MAX(CASE WHEN pm.meta_key=%s THEN pm.meta_value END) AS enabled"
        . " FROM `{$posts}` p LEFT JOIN `{$postmeta}` pm ON pm.post_id=p.ID"
        . " WHERE p.ID=%d GROUP BY p.ID,p.post_title,p.post_type,p.post_status LIMIT 1",
        ADAPTER_TYPE_META, NAME_META, LABEL_META, DESCRIPTION_META,
        SETTINGS_META, ENCRYPTED_FIELDS_META, NETWORK_META, ENABLED_META, $id
    );
    $rows = $wpdb->get_results($sql, ARRAY_A);
    if (!is_array($rows) || (string)($wpdb->last_error ?? '') !== '') {
        return ['ok' => false, 'integration' => null];
    }
    if ($rows === []) { return ['ok' => true, 'integration' => null]; }
    $row = $rows[0] ?? null;
    if (!is_array($row) || (int)($row['ID'] ?? 0) !== $id
        || (string)($row['post_type'] ?? '') !== POST_TYPE
        || (string)($row['post_status'] ?? '') !== 'publish') {
        return ['ok' => true, 'integration' => null];
    }

    $decode = static function ($value) {
        if (!is_string($value)) { return $value; }
        return function_exists('maybe_unserialize') ? \maybe_unserialize($value) : $value;
    };
    $settings = $decode($row['settings'] ?? null);
    $settings = is_array($settings) ? $settings : [];
    $encrypted_fields = $decode($row['encrypted_fields'] ?? null);
    $encrypted_fields = is_array($encrypted_fields) ? $encrypted_fields : [];
    $enabled_raw = is_scalar($row['enabled'] ?? null) ? (string)$row['enabled'] : '';
    if (!in_array($enabled_raw, ['0', '1'], true)) {
        return ['ok' => false, 'integration' => null];
    }
    $adapter_type = trim((string)($row['adapter_type'] ?? ''));
    if ($adapter_type === '') { $adapter_type = trim((string)($row['legacy_adapter_type'] ?? '')); }
    $label = (string)($row['label'] ?? '');
    if ($label === '') { $label = (string)($row['post_title'] ?? '') ?: $adapter_type; }

    return ['ok' => true, 'integration' => [
        'id' => $id,
        'adapter_type' => $adapter_type,
        'adapter_name' => $adapter_type,
        'label' => $label,
        'description' => (string)($row['description'] ?? ''),
        'settings' => _decrypt_settings($settings, $encrypted_fields),
        'encrypted_fields' => $encrypted_fields,
        'is_network' => (string)($row['is_network'] ?? '') === '1',
        'enabled' => $enabled_raw === '1',
    ]];
}

function delete_integration(int $id): bool {
    return (bool) \wp_delete_post($id, true);
}

/**
 * List ALL integration records visible for a given blog (network + site-level).
 */
/** @return array{ok:bool,integrations:array} */
function list_integrations_checked(int $blog_id): array {
    return _with_blog($blog_id, function () {
        global $wpdb;
        if (isset($wpdb->last_error)) { $wpdb->last_error = ''; }
        $posts = \get_posts([
            'post_type'      => POST_TYPE,
            'post_status'    => 'publish',
            'posts_per_page' => -1,
            'orderby'        => 'date',
            'order'          => 'ASC',
            // The intake snapshot must distinguish a genuine empty catalog
            // from a transient SQL failure, not trust a stale query cache.
            'cache_results'  => false,
            'update_post_meta_cache' => false,
            'update_post_term_cache' => false,
        ]);
        if ((string)($wpdb->last_error ?? '') !== '') {
            return ['ok' => false, 'integrations' => []];
        }
        $out = [];
        foreach ($posts as $p) {
            $result = get_integration_checked((int)$p->ID);
            if (!($result['ok'] ?? false)) { return ['ok' => false, 'integrations' => []]; }
            $entry = $result['integration'] ?? null;
            if ($entry) $out[] = $entry;
        }
        return ['ok' => true, 'integrations' => $out];
    });
}

function list_integrations(int $blog_id): array {
    $result = list_integrations_checked($blog_id);
    return ($result['ok'] ?? false) ? (array)($result['integrations'] ?? []) : [];
}

/**
 * Read only the routing fields needed at intake, directly from MySQL. This is
 * deliberately independent of WordPress query/meta caches so a cache or SQL
 * failure cannot masquerade as a healthy empty Email/Telegram/CRM catalog.
 *
 * @return array<int,string> exact enabled integration id => adapter
 * @throws \RuntimeException when catalog health or row integrity is unknown
 */
function read_delivery_targets_strict(int $blog_id): array {
    return _with_blog($blog_id, function (): array {
        global $wpdb;
        $posts = str_replace('`', '', $wpdb->get_blog_prefix() . 'posts');
        $postmeta = str_replace('`', '', $wpdb->get_blog_prefix() . 'postmeta');
        if (isset($wpdb->last_error)) { $wpdb->last_error = ''; }
        $sql = $wpdb->prepare(
            "/* landing_delivery_catalog */ SELECT p.ID,"
            . " MAX(CASE WHEN pm.meta_key=%s THEN pm.meta_value END) AS adapter_type,"
            . " MAX(CASE WHEN pm.meta_key=%s THEN pm.meta_value END) AS legacy_adapter_type,"
            . " MAX(CASE WHEN pm.meta_key=%s THEN pm.meta_value END) AS enabled"
            . " FROM `{$posts}` p LEFT JOIN `{$postmeta}` pm ON pm.post_id=p.ID"
            . " AND pm.meta_key IN (%s,%s,%s)"
            . " WHERE p.post_type=%s AND p.post_status='publish'"
            . " GROUP BY p.ID ORDER BY p.ID ASC",
            ADAPTER_TYPE_META, NAME_META, ENABLED_META,
            ADAPTER_TYPE_META, NAME_META, ENABLED_META, POST_TYPE
        );
        $rows = $wpdb->get_results($sql, ARRAY_A);
        if (!is_array($rows) || (string)($wpdb->last_error ?? '') !== '') {
            throw new \RuntimeException('integration_catalog_unavailable');
        }

        $targets = [];
        $seen = [];
        foreach ($rows as $row) {
            if (!is_array($row) || !isset($row['ID']) || !is_numeric($row['ID'])) {
                throw new \RuntimeException('integration_catalog_invalid');
            }
            $id = (int)$row['ID'];
            $enabled = is_scalar($row['enabled'] ?? null) ? (string)$row['enabled'] : '';
            if ($id <= 0 || isset($seen[$id]) || !in_array($enabled, ['0','1'], true)) {
                throw new \RuntimeException('integration_catalog_invalid');
            }
            $seen[$id] = true;
            if ($enabled !== '1') { continue; }
            $adapter = trim((string)($row['adapter_type'] ?? ''));
            if ($adapter === '') { $adapter = trim((string)($row['legacy_adapter_type'] ?? '')); }
            if ($adapter === '' || sanitize_key($adapter) !== $adapter
                || !in_array($adapter, VALID_ADAPTERS, true)) {
                throw new \RuntimeException('integration_catalog_invalid');
            }
            $targets[$id] = $adapter;
        }
        ksort($targets, SORT_NUMERIC);
        return $targets;
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
