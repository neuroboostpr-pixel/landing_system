<?php
namespace LandingConfig\CookieBanner\Migrate;

if (!defined('ABSPATH')) { exit; }

use const LandingConfig\CookieBanner\CPT\POST_TYPE;
use const LandingConfig\CookieBanner\CPT\SEGMENT_META;

const MARKER = 'landing_config_migration_b2_cookie_banner';

function maybe_run(): void {
    if (\get_site_option(MARKER) === '1') return;

    // Seed network default record in NETWORK_BLOG_ID (root).
    $target = \LandingConfig\CookieBanner\Resolver\NETWORK_BLOG_ID;
    $switched = false;
    if (function_exists('switch_to_blog') && $target !== \get_current_blog_id()) {
        \switch_to_blog($target);
        $switched = true;
    }

    $existing = \LandingConfig\CookieBanner\Resolver\get_post_id_for_segment(0);
    if (!$existing) {
        $defaults = \LandingConfig\CookieBanner\Resolver\DEFAULTS;
        $post_id = \wp_insert_post([
            'post_type'   => POST_TYPE,
            'post_status' => 'publish',
            'post_title'  => 'Cookie banner (network default)',
        ]);
        \update_post_meta($post_id, SEGMENT_META, '0');
        \update_post_meta($post_id, '_lp_cb_layout', $defaults['layout']);
        \update_post_meta($post_id, '_lp_cb_title', $defaults['title']);
        \update_post_meta($post_id, '_lp_cb_description', $defaults['description']);
        \update_post_meta($post_id, '_lp_cb_btn_accept_all_text', $defaults['btn_accept_all_text']);
        \update_post_meta($post_id, '_lp_cb_btn_save_text', $defaults['btn_save_text']);
        \update_post_meta($post_id, '_lp_cb_btn_reject_text', $defaults['btn_reject_text']);
        \update_post_meta($post_id, '_lp_cb_policy_link_text', $defaults['policy_link_text']);
        \update_post_meta($post_id, '_lp_cb_policy_link_url', $defaults['policy_link_url']);
        \update_post_meta($post_id, '_lp_cb_reopen_text', $defaults['reopen_text']);
        \update_post_meta($post_id, '_lp_cb_show_categories', '0');
        \update_post_meta($post_id, '_lp_cb_categories', \wp_json_encode($defaults['categories'], JSON_UNESCAPED_UNICODE));
        \update_post_meta($post_id, '_lp_cb_consent_version', (string) $defaults['consent_version']);
    }

    if ($switched) {
        \restore_current_blog();
    }

    \update_site_option(MARKER, '1');
}
