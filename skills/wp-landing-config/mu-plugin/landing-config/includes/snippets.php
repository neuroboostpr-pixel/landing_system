<?php
namespace LandingConfig\Snippets;

if (!defined('ABSPATH')) { exit; }

const POST_TYPE = 'lp_snippet';
const VALID_POSITIONS = ['head', 'body_open', 'body_close'];
const VALID_SCOPES = ['global', 'local'];
const NETWORK_BLOG_ID = 1;

const ALLOWED_HTML = [
    'script'   => ['src' => true, 'async' => true, 'defer' => true, 'type' => true,
                   'crossorigin' => true, 'integrity' => true, 'nonce' => true,
                   'id' => true, 'class' => true],
    'meta'     => ['name' => true, 'content' => true, 'property' => true,
                   'http-equiv' => true, 'charset' => true, 'itemprop' => true],
    'link'     => ['rel' => true, 'href' => true, 'type' => true, 'crossorigin' => true,
                   'sizes' => true, 'as' => true, 'media' => true, 'integrity' => true],
    'style'    => ['type' => true, 'media' => true, 'id' => true, 'class' => true],
    'noscript' => ['id' => true, 'class' => true],
    'iframe'   => ['src' => true, 'width' => true, 'height' => true, 'frameborder' => true,
                   'allowfullscreen' => true, 'allow' => true, 'loading' => true,
                   'sandbox' => true, 'id' => true, 'class' => true, 'style' => true,
                   'title' => true, 'name' => true],
    'div'      => ['id' => true, 'class' => true, 'style' => true,
                   'role' => true, 'aria-label' => true],
    'span'     => ['id' => true, 'class' => true, 'style' => true],
    'img'      => ['src' => true, 'alt' => true, 'width' => true, 'height' => true,
                   'style' => true, 'class' => true, 'id' => true],
    'a'        => ['href' => true, 'target' => true, 'rel' => true, 'class' => true,
                   'id' => true, 'style' => true],
    'p'        => ['class' => true, 'id' => true],
    'br'       => [],
];

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
            'edit_post'         => 'manage_options',
            'edit_posts'        => 'manage_options',
            'edit_others_posts' => 'manage_options',
            'publish_posts'     => 'manage_options',
            'read_post'         => 'manage_options',
            'delete_post'       => 'manage_options',
        ],
    ]);
}

function sanitize_code(string $code): string {
    return wp_kses($code, ALLOWED_HTML);
}

// Helper to run a callable in NETWORK_BLOG_ID context (no-op if not multisite or already there).
function _with_network_blog(callable $fn) {
    if (function_exists('switch_to_blog') && function_exists('get_current_blog_id')) {
        $prev = (int) get_current_blog_id();
        if ($prev === NETWORK_BLOG_ID) {
            return $fn();
        }
        switch_to_blog(NETWORK_BLOG_ID);
        try {
            return $fn();
        } finally {
            // WP's restore_current_blog pops the switch stack; in our tests the
            // mock just resets to 1, so explicitly switch back to the previous blog.
            if (function_exists('restore_current_blog')) {
                restore_current_blog();
            }
            if (function_exists('get_current_blog_id') && (int) get_current_blog_id() !== $prev) {
                switch_to_blog($prev);
            }
        }
    }
    return $fn();
}

function save_snippet(array $args, bool $is_network = false): int {
    $op = function () use ($args, $is_network) {
        $title    = sanitize_text_field($args['title'] ?? '');
        $name     = sanitize_text_field($args['name'] ?? '');
        $code     = sanitize_code($args['code'] ?? '');
        $position = $args['position'] ?? 'head';
        if (!in_array($position, VALID_POSITIONS, true)) $position = 'head';
        $scope    = $args['scope'] ?? 'global';
        if (!in_array($scope, VALID_SCOPES, true)) $scope = 'global';
        $enabled  = !empty($args['enabled']) || (!isset($args['enabled']) && !isset($args['id']));
        $priority = isset($args['priority']) ? (int) $args['priority'] : 10;
        $targets  = array_values(array_map('intval', (array) ($args['target_post_ids'] ?? [])));

        $post = ['post_type' => POST_TYPE, 'post_status' => 'publish', 'post_title' => $title];
        if (!empty($args['id'])) {
            $post['ID'] = (int) $args['id'];
            $id = wp_update_post($post);
        } else {
            $id = wp_insert_post($post);
        }

        update_post_meta($id, '_lp_snippet_code', $code);
        update_post_meta($id, '_lp_snippet_name', $name);
        update_post_meta($id, '_lp_snippet_position', $position);
        update_post_meta($id, '_lp_snippet_scope', $scope);
        update_post_meta($id, '_lp_snippet_target_post_ids', $targets);
        update_post_meta($id, '_lp_snippet_enabled', $enabled ? '1' : '0');
        update_post_meta($id, '_lp_snippet_priority', $priority);
        update_post_meta($id, '_lp_snippet_is_network', $is_network ? '1' : '0');

        return (int) $id;
    };
    return $is_network ? _with_network_blog($op) : $op();
}

function get_snippet(int $id, bool $is_network = false): ?array {
    $op = function () use ($id) {
        $p = get_post($id);
        if (!$p || ($p->post_type ?? '') !== POST_TYPE) return null;
        return [
            'id'              => $id,
            'title'           => $p->post_title ?? '',
            'name'            => (string) get_post_meta($id, '_lp_snippet_name', true),
            'code'            => (string) get_post_meta($id, '_lp_snippet_code', true),
            'position'        => (string) get_post_meta($id, '_lp_snippet_position', true) ?: 'head',
            'scope'           => (string) get_post_meta($id, '_lp_snippet_scope', true) ?: 'global',
            'target_post_ids' => array_map('intval', (array) get_post_meta($id, '_lp_snippet_target_post_ids', true)),
            'enabled'         => (string) get_post_meta($id, '_lp_snippet_enabled', true) === '1',
            'priority'        => (int) get_post_meta($id, '_lp_snippet_priority', true),
            'is_network'      => (string) get_post_meta($id, '_lp_snippet_is_network', true) === '1',
        ];
    };
    return $is_network ? _with_network_blog($op) : $op();
}

function delete_snippet(int $id, bool $is_network = false): bool {
    $op = fn() => (bool) wp_delete_post($id, true);
    return $is_network ? _with_network_blog($op) : $op();
}

function list_snippets(array $filter = [], bool $is_network = false): array {
    $op = function () use ($filter, $is_network) {
        $posts = get_posts([
            'post_type'      => POST_TYPE,
            'posts_per_page' => -1,
            'post_status'    => 'publish',
            'orderby'        => 'meta_value_num',
            'meta_key'       => '_lp_snippet_priority',
            'order'          => 'ASC',
        ]);
        $out = [];
        foreach ($posts as $p) {
            $s = get_snippet((int) $p->ID, false);  // already in correct blog context
            if (!$s) continue;
            // Filter by is_network flag matching the request
            if ($s['is_network'] !== $is_network) continue;
            if (!empty($filter['position']) && $s['position'] !== $filter['position']) continue;
            if (!empty($filter['scope'])    && $s['scope']    !== $filter['scope'])    continue;
            if (isset($filter['enabled'])   && $s['enabled']  !== (bool) $filter['enabled']) continue;
            if (isset($filter['name'])      && $s['name']     !== $filter['name'])     continue;
            $out[] = $s;
        }
        return $out;
    };
    return $is_network ? _with_network_blog($op) : $op();
}

function list_site_snippets(array $filter = []): array    { return list_snippets($filter, false); }
function list_network_snippets(array $filter = []): array { return list_snippets($filter, true); }
