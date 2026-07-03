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
    // CPT управляется только через наш admin-snippets dispatcher
    // (current_user_can('manage_options') там). show_ui=false ⇒ WP не строит
    // edit.php-страницу. При map_meta_cap=true указывать в `capabilities`
    // singular meta-caps (edit_post/read_post/delete_post) — антипаттерн:
    // WP мапит meta→meta рекурсивно и пишет notices в debug.log.
    // Оставляем только plural primitive caps; этого достаточно для
    // wp_insert_post/wp_update_post/wp_delete_post при is_super_admin / admin.
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

        // subpage_scope: 'all' | comma-separated slugs (li-auto,zeekr,...)
        // Controls whether the snippet is injected into self-contained brand subpages.
        $subpage_scope = sanitize_text_field($args['subpage_scope'] ?? 'all');
        if ($subpage_scope === '') $subpage_scope = 'all';

        update_post_meta($id, '_lp_snippet_code', $code);
        update_post_meta($id, '_lp_snippet_name', $name);
        update_post_meta($id, '_lp_snippet_position', $position);
        update_post_meta($id, '_lp_snippet_scope', $scope);
        update_post_meta($id, '_lp_snippet_target_post_ids', $targets);
        update_post_meta($id, '_lp_snippet_enabled', $enabled ? '1' : '0');
        update_post_meta($id, '_lp_snippet_priority', $priority);
        update_post_meta($id, '_lp_snippet_is_network', $is_network ? '1' : '0');
        update_post_meta($id, '_lp_snippet_subpage_scope', $subpage_scope);

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
            'code'            => html_entity_decode((string) get_post_meta($id, '_lp_snippet_code', true), ENT_QUOTES | ENT_HTML5, 'UTF-8'),
            'position'        => (string) get_post_meta($id, '_lp_snippet_position', true) ?: 'head',
            'scope'           => (string) get_post_meta($id, '_lp_snippet_scope', true) ?: 'global',
            'target_post_ids' => array_map('intval', (array) get_post_meta($id, '_lp_snippet_target_post_ids', true)),
            'enabled'         => (string) get_post_meta($id, '_lp_snippet_enabled', true) === '1',
            'priority'        => (int) get_post_meta($id, '_lp_snippet_priority', true),
            'is_network'      => (string) get_post_meta($id, '_lp_snippet_is_network', true) === '1',
            'subpage_scope'   => (string) get_post_meta($id, '_lp_snippet_subpage_scope', true) ?: 'all',
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

/**
 * Return snippets for a given position filtered by subpage slug.
 * Used by lp_render_subpage() to inject only relevant snippets.
 *
 * @param string $position  head | body_open | body_close
 * @param string $slug      subpage slug (e.g. 'li-auto'), or '' for main page
 */
function get_snippets_for_subpage(string $position, string $slug): array {
    $all = render_collect($position);
    return array_values(array_filter($all, function ($s) use ($slug) {
        $scope = $s['subpage_scope'] ?? 'all';
        if ($scope === 'all' || $scope === '') return true;
        $allowed = array_map('trim', explode(',', $scope));
        return in_array($slug, $allowed, true);
    }));
}

/**
 * Collect rendered snippet objects (same logic as render() but returns array).
 */
function render_collect(string $position): array {
    if (!in_array($position, VALID_POSITIONS, true)) return [];

    $current = function_exists('get_queried_object_id') ? get_queried_object_id() : 0;
    $site = list_site_snippets(['position' => $position, 'enabled' => true]);
    $site = array_values(array_filter($site, function ($s) use ($current) {
        if ($s['scope'] === 'global') return true;
        return in_array($current, $s['target_post_ids'], true);
    }));

    $site_names = [];
    foreach ($site as $s) {
        if ($s['name'] !== '') $site_names[] = $s['name'];
    }

    $network = list_network_snippets(['position' => $position, 'enabled' => true]);
    $network = array_values(array_filter($network, function ($s) use ($site_names) {
        return $s['name'] === '' || !in_array($s['name'], $site_names, true);
    }));

    $all = array_merge($network, $site);
    usort($all, fn($a, $b) => $a['priority'] - $b['priority']);
    return $all;
}

add_action('wp_head',      __NAMESPACE__ . '\\render_head',       5);
add_action('wp_body_open', __NAMESPACE__ . '\\render_body_open',  5);
add_action('wp_footer',    __NAMESPACE__ . '\\render_body_close', 99);

function render_head(): void       { render('head'); }
function render_body_open(): void  { render('body_open'); }
function render_body_close(): void { render('body_close'); }

function render(string $position): void {
    if (!in_array($position, VALID_POSITIONS, true)) return;

    // Site snippets — page-scope filter (global or local matching current page)
    $current = function_exists('get_queried_object_id') ? get_queried_object_id() : 0;
    $site = list_site_snippets(['position' => $position, 'enabled' => true]);
    $site = array_values(array_filter($site, function ($s) use ($current) {
        if ($s['scope'] === 'global') return true;
        return in_array($current, $s['target_post_ids'], true);
    }));

    // Names of site snippets → for network override
    $site_names = [];
    foreach ($site as $s) {
        if ($s['name'] !== '') $site_names[] = $s['name'];
    }

    // Network snippets — skip those whose name matches a site snippet name
    $network = list_network_snippets(['position' => $position, 'enabled' => true]);
    $network = array_values(array_filter($network, function ($s) use ($site_names) {
        return $s['name'] === '' || !in_array($s['name'], $site_names, true);
    }));

    $all = array_merge($network, $site);
    usort($all, fn($a, $b) => $a['priority'] - $b['priority']);

    foreach ($all as $s) {
        $tag = $s['is_network'] ? 'network' : 'site';
        printf("\n<!-- lp_snippet:%d \"%s\" [%s] -->\n", $s['id'], $s['title'], $tag);
        echo $s['code'];
        printf("\n<!-- /lp_snippet:%d -->\n", $s['id']);
    }
}
