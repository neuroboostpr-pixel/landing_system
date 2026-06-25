<?php
namespace LandingConfig\CookieBanner\Resolver;

if (!defined('ABSPATH')) { exit; }

use const LandingConfig\CookieBanner\CPT\POST_TYPE;
use const LandingConfig\CookieBanner\CPT\SEGMENT_META;
use const LandingConfig\CookieBanner\CPT\VALID_LAYOUTS;

// Network records are stored in the root blog (matches cascade.php pattern).
const NETWORK_BLOG_ID = 1;

const DEFAULTS = [
    'enabled'              => true,
    'layout'               => 'bottom-bar',
    'title'                => 'Мы используем cookies',
    'description'          => 'Cookies помогают нам обеспечить работу сайта и понять, как вы им пользуетесь.',
    'btn_accept_all_text'  => 'Принять все',
    'btn_save_text'        => 'Сохранить настройки',
    'btn_reject_text'      => '',
    'policy_link_text'     => 'Политика обработки персональных данных',
    'policy_link_url'      => '/policy',
    'reopen_text'          => 'Настройки cookies',
    'show_categories'      => false,
    'categories'           => [
        ['slug' => 'necessary', 'name' => 'Необходимые',
         'desc' => 'Обеспечивают базовую работу сайта. Не могут быть отключены.',
         'locked' => true, 'default_on' => true],
        ['slug' => 'analytics', 'name' => 'Аналитика',
         'desc' => 'Помогают понять, как посетители используют сайт.',
         'locked' => false, 'default_on' => false],
        ['slug' => 'marketing', 'name' => 'Маркетинг',
         'desc' => 'Для показа релевантной рекламы и ретаргетинга.',
         'locked' => false, 'default_on' => false],
    ],
    'color_bg'             => '',
    'color_text'           => '',
    'color_accent'         => '',
    'color_border'         => '',
    'consent_version'      => 1,
];

const META_KEY_MAP = [
    'enabled'              => '_lp_cb_enabled',
    'layout'               => '_lp_cb_layout',
    'title'                => '_lp_cb_title',
    'description'          => '_lp_cb_description',
    'btn_accept_all_text'  => '_lp_cb_btn_accept_all_text',
    'btn_save_text'        => '_lp_cb_btn_save_text',
    'btn_reject_text'      => '_lp_cb_btn_reject_text',
    'policy_link_text'     => '_lp_cb_policy_link_text',
    'policy_link_url'      => '_lp_cb_policy_link_url',
    'reopen_text'          => '_lp_cb_reopen_text',
    'show_categories'      => '_lp_cb_show_categories',
    'categories'           => '_lp_cb_categories',
    'color_bg'             => '_lp_cb_color_bg',
    'color_text'           => '_lp_cb_color_text',
    'color_accent'         => '_lp_cb_color_accent',
    'color_border'         => '_lp_cb_color_border',
    'consent_version'      => '_lp_cb_consent_version',
];

/**
 * Find the post ID for a given segment.
 *
 * - segment=0 (network default) → reads from NETWORK_BLOG_ID (root)
 * - segment=N (site override)  → reads from blog N (via switch_to_blog)
 *
 * Both record types live in a per-site posts table — the segment number
 * tells us WHICH blog stores the record. This mirrors the pattern in
 * includes/cascade.php (CTA/Integrations CPTs).
 */
function get_post_id_for_segment(int $segment): ?int {
    $target_blog = ($segment === 0) ? NETWORK_BLOG_ID : $segment;
    $current_blog = \get_current_blog_id();

    if ($target_blog !== $current_blog && function_exists('switch_to_blog')) {
        \switch_to_blog($target_blog);
        $id = _query_post_id($segment);
        \restore_current_blog();
        return $id;
    }
    return _query_post_id($segment);
}

function _query_post_id(int $segment): ?int {
    $q = \get_posts([
        'post_type'   => POST_TYPE,
        'post_status' => 'publish',
        'meta_key'    => SEGMENT_META,
        'meta_value'  => (string) $segment,
        'numberposts' => 1,
        'fields'      => 'ids',
    ]);
    return !empty($q) ? (int) $q[0] : null;
}

/**
 * Read all known settings from a post.
 *
 * $source_segment: 0 = network record (lives in NETWORK_BLOG_ID),
 *                  N = site override (lives in blog N).
 * Used to pick the right blog context for get_post_meta — meta lives in
 * the same per-blog table as the post.
 */
function read_settings(int $post_id, int $source_segment = 0): array {
    $target_blog = ($source_segment === 0) ? NETWORK_BLOG_ID : $source_segment;
    $current_blog = \get_current_blog_id();
    $switched = false;
    if ($target_blog !== $current_blog && function_exists('switch_to_blog')) {
        \switch_to_blog($target_blog);
        $switched = true;
    }

    $out = [];
    foreach (META_KEY_MAP as $field => $meta_key) {
        $val = \get_post_meta($post_id, $meta_key, true);
        if ($val === '' || $val === false || $val === null) {
            $out[$field] = null;
            continue;
        }
        if ($field === 'categories') {
            $decoded = json_decode((string) $val, true);
            $out[$field] = is_array($decoded) ? $decoded : null;
        } elseif ($field === 'enabled' || $field === 'show_categories') {
            $out[$field] = ($val === '1' || $val === 1 || $val === true);
        } elseif ($field === 'consent_version') {
            $out[$field] = (int) $val;
        } else {
            $out[$field] = (string) $val;
        }
    }

    if ($switched) {
        \restore_current_blog();
    }
    return $out;
}

/**
 * Resolve cookie-banner settings for a given blog_id using cascade:
 * network (segment=0, stored in NETWORK_BLOG_ID) → site (segment=blog_id, stored in blog_id) → DEFAULTS.
 */
function resolve_for_blog(int $blog_id): array {
    $network_id = get_post_id_for_segment(0);
    $site_id    = ($blog_id !== 0) ? get_post_id_for_segment($blog_id) : null;

    $network = $network_id ? read_settings($network_id, 0) : [];
    $site    = $site_id    ? read_settings($site_id, $blog_id) : [];

    $out = DEFAULTS;
    foreach (META_KEY_MAP as $field => $_) {
        if (isset($site[$field]) && $site[$field] !== null) {
            $out[$field] = $site[$field];
        } elseif (isset($network[$field]) && $network[$field] !== null) {
            $out[$field] = $network[$field];
        }
        // else: DEFAULTS value stays
    }

    // Validate layout — reject unknown values
    if (!in_array($out['layout'], VALID_LAYOUTS, true)) {
        $out['layout'] = 'bottom-bar';
    }

    return $out;
}
