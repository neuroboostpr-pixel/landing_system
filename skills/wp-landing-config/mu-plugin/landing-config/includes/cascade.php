<?php
namespace LandingConfig\Cascade;

if (!defined('ABSPATH')) { exit; }

const NETWORK_BLOG_ID = 1;

function _list_raw(string $cpt, string $is_network_meta_key, bool $is_network): array {
    $posts = \get_posts([
        'post_type'      => $cpt,
        'posts_per_page' => -1,
        'post_status'    => 'publish',
        'meta_query'     => [
            ['key' => $is_network_meta_key, 'value' => $is_network ? '1' : '0'],
        ],
        'orderby'        => 'ID',
        'order'          => 'ASC',
    ]);
    $out = [];
    foreach ($posts as $p) {
        $row = [];
        foreach (\get_post_meta((int)$p->ID) as $key => $values) {
            // get_post_meta($id) returns array<key, array<int, string>> — flatten
            $row[$key] = is_array($values) ? ($values[0] ?? '') : (string) $values;
        }
        $row['__post_id'] = (int) $p->ID;
        $row['__title']   = $p->post_title ?? '';
        $out[] = $row;
    }
    return $out;
}

function _with_blog(int $blog_id, callable $fn) {
    $prev = \function_exists('get_current_blog_id') ? \get_current_blog_id() : 1;
    if ($prev === $blog_id) return $fn();
    \switch_to_blog($blog_id);
    try { return $fn(); }
    finally { \restore_current_blog(); }
}

function list_for_blog(string $cpt, string $name_meta_key, string $is_network_meta_key, int $blog_id): array {
    // 1. Site rows (current blog scope)
    $site = _with_blog($blog_id, fn() => _list_raw($cpt, $is_network_meta_key, false));
    $site_by_name = [];
    foreach ($site as $row) {
        $nm = $row[$name_meta_key] ?? '';
        if ($nm !== '') $site_by_name[$nm] = $row;
    }
    // 2. Network rows
    $network = _with_blog(NETWORK_BLOG_ID, fn() => _list_raw($cpt, $is_network_meta_key, true));
    $network_filtered = [];
    foreach ($network as $row) {
        $nm = $row[$name_meta_key] ?? '';
        if ($nm !== '' && isset($site_by_name[$nm])) continue;  // site override wins
        $network_filtered[] = $row;
    }
    return array_merge($network_filtered, $site);
}

function resolve_for_blog(string $cpt, string $name_meta_key, string $is_network_meta_key, string $name, int $blog_id): ?array {
    $list = list_for_blog($cpt, $name_meta_key, $is_network_meta_key, $blog_id);
    foreach ($list as $row) {
        if (($row[$name_meta_key] ?? '') === $name) return $row;
    }
    return null;
}

function has_site_override(string $cpt, string $name_meta_key, string $is_network_meta_key, string $name, int $blog_id): bool {
    $site = _with_blog($blog_id, fn() => _list_raw($cpt, $is_network_meta_key, false));
    foreach ($site as $row) {
        if (($row[$name_meta_key] ?? '') === $name) return true;
    }
    return false;
}
