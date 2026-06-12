<?php
namespace LandingConfig\LeadStatuses;

if (!defined('ABSPATH')) { exit; }

use function LandingConfig\Cascade\resolve_for_blog;
use function LandingConfig\Cascade\list_for_blog;
use function LandingConfig\Cascade\has_site_override;
use function LandingConfig\Cascade\_with_blog;

const POST_TYPE  = 'lp_lead_status';
const SLUG_META  = '_lp_status_slug';
const LABEL_META = '_lp_status_label';
const COLOR_META = '_lp_status_color';
const ORDER_META = '_lp_status_order';
const NETWORK_META = '_lp_is_network';

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

function _is_valid_slug(string $slug): bool {
    return $slug !== '' && (bool) preg_match('/^[a-z0-9_-]+$/', $slug);
}

function _is_valid_color(string $color): bool {
    return (bool) preg_match('/^#[0-9a-fA-F]{6}$/', $color);
}

function save_lead_status(array $args, bool $is_network, int $blog_id, int $post_id = 0): int {
    return _with_blog($blog_id, function () use ($args, $is_network, $post_id) {
        $raw = $args['slug'] ?? '';
        $slug = is_string($raw) ? $raw : '';
        if (!_is_valid_slug($slug)) return 0;

        $label = \sanitize_text_field($args['label'] ?? '');
        $color = (string) ($args['color'] ?? '#2271b1');
        if (!_is_valid_color($color)) $color = '#2271b1';
        $order = (int) ($args['order'] ?? 10);

        $post = ['post_type' => POST_TYPE, 'post_status' => 'publish', 'post_title' => $slug];
        if ($post_id > 0) {
            $post['ID'] = $post_id;
            $id = \wp_update_post($post);
        } else {
            $id = \wp_insert_post($post);
        }
        \update_post_meta($id, SLUG_META, $slug);
        \update_post_meta($id, LABEL_META, $label);
        \update_post_meta($id, COLOR_META, $color);
        \update_post_meta($id, ORDER_META, $order);
        \update_post_meta($id, NETWORK_META, $is_network ? '1' : '0');
        return (int) $id;
    });
}

function get_lead_status(int $id): ?array {
    $p = \get_post($id);
    if (!$p || ($p->post_type ?? '') !== POST_TYPE) return null;
    return [
        'id'         => $id,
        'slug'       => (string) \get_post_meta($id, SLUG_META, true),
        'label'      => (string) \get_post_meta($id, LABEL_META, true),
        'color'      => (string) \get_post_meta($id, COLOR_META, true),
        'order'      => (int) \get_post_meta($id, ORDER_META, true),
        'is_network' => (string) \get_post_meta($id, NETWORK_META, true) === '1',
    ];
}

function delete_lead_status(int $id): bool {
    return (bool) \wp_delete_post($id, true);
}

function list_lead_statuses(int $blog_id): array {
    $raw = list_for_blog(POST_TYPE, SLUG_META, NETWORK_META, $blog_id);
    $out = [];
    foreach ($raw as $row) {
        $out[] = [
            'id'         => (int) ($row['__post_id'] ?? 0),
            'slug'       => $row[SLUG_META] ?? '',
            'label'      => $row[LABEL_META] ?? '',
            'color'      => $row[COLOR_META] ?? '#2271b1',
            'order'      => (int) ($row[ORDER_META] ?? 10),
            'is_network' => ($row[NETWORK_META] ?? '0') === '1',
        ];
    }
    usort($out, fn($a, $b) => $a['order'] <=> $b['order']);
    return $out;
}

function resolve_lead_status(string $slug, int $blog_id): ?array {
    $row = resolve_for_blog(POST_TYPE, SLUG_META, NETWORK_META, $slug, $blog_id);
    if (!$row) return null;
    return [
        'slug'       => $row[SLUG_META] ?? $slug,
        'label'      => $row[LABEL_META] ?? '',
        'color'      => $row[COLOR_META] ?? '#2271b1',
        'order'      => (int) ($row[ORDER_META] ?? 10),
        'is_network' => ($row[NETWORK_META] ?? '0') === '1',
    ];
}

function has_override(string $slug, int $blog_id): bool {
    return has_site_override(POST_TYPE, SLUG_META, NETWORK_META, $slug, $blog_id);
}
