<?php
namespace LandingConfig\Integrations;

if (!defined('ABSPATH')) { exit; }

use function LandingConfig\Cascade\resolve_for_blog;
use function LandingConfig\Cascade\list_for_blog;
use function LandingConfig\Cascade\has_site_override;
use function LandingConfig\Encryption\encrypt;
use function LandingConfig\Encryption\decrypt;

const POST_TYPE = 'lp_integration';
const NAME_META = '_lp_int_adapter_name';
const NETWORK_META = '_lp_int_is_network';
const SETTINGS_META = '_lp_int_settings';
const ENCRYPTED_FIELDS_META = '_lp_int_encrypted_fields';
const ENABLED_META = '_lp_int_enabled';

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
            $settings[$f] = encrypt((string) $settings[$f]);
        }
    }
    return $settings;
}

function _decrypt_settings(array $settings, array $encrypted_fields): array {
    foreach ($encrypted_fields as $f) {
        if (isset($settings[$f]) && is_string($settings[$f]) && $settings[$f] !== '') {
            $decrypted = decrypt($settings[$f]);
            if ($decrypted !== null) $settings[$f] = $decrypted;
        }
    }
    return $settings;
}

function save_integration(string $adapter_name, array $settings, bool $is_network, int $blog_id, array $encrypted_fields = [], bool $enabled = true): int {
    if (!in_array($adapter_name, VALID_ADAPTERS, true)) return 0;

    return _with_blog($blog_id, function () use ($adapter_name, $settings, $is_network, $encrypted_fields, $enabled) {
        $post = ['post_type' => POST_TYPE, 'post_status' => 'publish', 'post_title' => $adapter_name];
        $id = \wp_insert_post($post);
        \update_post_meta($id, NAME_META, $adapter_name);
        \update_post_meta($id, SETTINGS_META, _encrypt_settings($settings, $encrypted_fields));
        \update_post_meta($id, ENCRYPTED_FIELDS_META, $encrypted_fields);
        \update_post_meta($id, NETWORK_META, $is_network ? '1' : '0');
        \update_post_meta($id, ENABLED_META, $enabled ? '1' : '0');
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
    return [
        'id'               => $id,
        'adapter_name'     => (string) \get_post_meta($id, NAME_META, true),
        'settings'         => _decrypt_settings($settings, $encrypted_fields),
        'encrypted_fields' => $encrypted_fields,
        'is_network'       => (string) \get_post_meta($id, NETWORK_META, true) === '1',
        'enabled'          => (string) \get_post_meta($id, ENABLED_META, true) === '1',
    ];
}

function delete_integration(int $id): bool {
    return (bool) \wp_delete_post($id, true);
}

function list_integrations(int $blog_id): array {
    $raw = list_for_blog(POST_TYPE, NAME_META, NETWORK_META, $blog_id);
    $out = [];
    foreach ($raw as $row) {
        $post_id = (int) ($row['__post_id'] ?? 0);
        $entry = get_integration($post_id);
        if ($entry) $out[] = $entry;
    }
    return $out;
}

function resolve_integration(string $adapter_name, int $blog_id): ?array {
    $list = list_integrations($blog_id);
    foreach ($list as $r) {
        if ($r['adapter_name'] === $adapter_name) return $r;
    }
    return null;
}

function has_override(string $adapter_name, int $blog_id): bool {
    return has_site_override(POST_TYPE, NAME_META, NETWORK_META, $adapter_name, $blog_id);
}
