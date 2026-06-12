<?php
namespace LandingConfig\CTA;

if (!defined('ABSPATH')) { exit; }

use function LandingConfig\Cascade\resolve_for_blog;
use function LandingConfig\Cascade\list_for_blog;
use function LandingConfig\Cascade\has_site_override;
use function LandingConfig\Cascade\_with_blog;

const POST_TYPE = 'lp_cta';
const NAME_META = '_lp_cta_preset_name';
const NETWORK_META = '_lp_cta_is_network';
const PRESET_NAMES = ['primary', 'whatsapp', 'phone', 'form_modal', 'learn_more'];
const VALID_TYPES = ['scroll', 'whatsapp', 'tel', 'mailto', 'modal', 'anchor', 'url'];

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

function save_cta(array $args, bool $is_network, int $blog_id): int {
    return _with_blog($blog_id, function () use ($args, $is_network) {
        $preset = \sanitize_text_field($args['preset_name'] ?? '');
        if (!in_array($preset, PRESET_NAMES, true)) {
            return 0;
        }
        $type = \sanitize_text_field($args['type'] ?? 'scroll');
        if (!in_array($type, VALID_TYPES, true)) $type = 'scroll';

        $post = ['post_type' => POST_TYPE, 'post_status' => 'publish', 'post_title' => $preset];
        if (!empty($args['id'])) {
            $post['ID'] = (int) $args['id'];
            $id = \wp_update_post($post);
        } else {
            $id = \wp_insert_post($post);
        }
        \update_post_meta($id, NAME_META, $preset);
        \update_post_meta($id, '_lp_cta_type', $type);
        \update_post_meta($id, '_lp_cta_label', \sanitize_text_field($args['label'] ?? ''));
        \update_post_meta($id, '_lp_cta_target', \sanitize_text_field($args['target'] ?? ''));
        \update_post_meta($id, '_lp_cta_phone', \sanitize_text_field($args['phone'] ?? ''));
        \update_post_meta($id, '_lp_cta_form_id', \sanitize_text_field($args['form_id'] ?? ''));
        \update_post_meta($id, '_lp_cta_message_template', \sanitize_text_field($args['message_template'] ?? ''));
        \update_post_meta($id, NETWORK_META, $is_network ? '1' : '0');
        return (int) $id;
    });
}

function get_cta(int $id): ?array {
    $p = \get_post($id);
    if (!$p || ($p->post_type ?? '') !== POST_TYPE) return null;
    return [
        'id'               => $id,
        'preset_name'      => (string) \get_post_meta($id, NAME_META, true),
        'type'             => (string) \get_post_meta($id, '_lp_cta_type', true),
        'label'            => (string) \get_post_meta($id, '_lp_cta_label', true),
        'target'           => (string) \get_post_meta($id, '_lp_cta_target', true),
        'phone'            => (string) \get_post_meta($id, '_lp_cta_phone', true),
        'form_id'          => (string) \get_post_meta($id, '_lp_cta_form_id', true),
        'message_template' => (string) \get_post_meta($id, '_lp_cta_message_template', true),
        'is_network'       => (string) \get_post_meta($id, NETWORK_META, true) === '1',
    ];
}

function delete_cta(int $id): bool {
    return (bool) \wp_delete_post($id, true);
}

/** Return all CTA records visible to $blog_id (network defaults + site overrides). Each row includes 'id'. */
function list_ctas(int $blog_id): array {
    $raw = list_for_blog(POST_TYPE, NAME_META, NETWORK_META, $blog_id);
    $out = [];
    foreach ($raw as $row) {
        $out[] = [
            'id'               => (int) ($row['__post_id'] ?? 0),
            'preset_name'      => $row[NAME_META] ?? '',
            'type'             => $row['_lp_cta_type'] ?? 'scroll',
            'label'            => $row['_lp_cta_label'] ?? '',
            'target'           => $row['_lp_cta_target'] ?? '',
            'phone'            => $row['_lp_cta_phone'] ?? '',
            'form_id'          => $row['_lp_cta_form_id'] ?? '',
            'message_template' => $row['_lp_cta_message_template'] ?? '',
            'is_network'       => ($row[NETWORK_META] ?? '0') === '1',
        ];
    }
    return $out;
}

/** Return effective CTA for ($preset_name, $blog_id) via cascade. Row does NOT include 'id' (lookup-by-name, not by post). */
function resolve_cta(string $preset_name, int $blog_id): ?array {
    $row = resolve_for_blog(POST_TYPE, NAME_META, NETWORK_META, $preset_name, $blog_id);
    if (!$row) return null;
    return [
        'preset_name'      => $row[NAME_META] ?? $preset_name,
        'type'             => $row['_lp_cta_type'] ?? 'scroll',
        'label'            => $row['_lp_cta_label'] ?? '',
        'target'           => $row['_lp_cta_target'] ?? '',
        'phone'            => $row['_lp_cta_phone'] ?? '',
        'form_id'          => $row['_lp_cta_form_id'] ?? '',
        'message_template' => $row['_lp_cta_message_template'] ?? '',
        'is_network'       => ($row[NETWORK_META] ?? '0') === '1',
    ];
}

function has_cta_override(string $preset_name, int $blog_id): bool {
    return has_site_override(POST_TYPE, NAME_META, NETWORK_META, $preset_name, $blog_id);
}
