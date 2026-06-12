<?php
namespace LandingConfig\CookieBanner\CPT;

if (!defined('ABSPATH')) { exit; }

const POST_TYPE      = 'lp_cookie_banner';
const SEGMENT_META   = '_lp_cb_segment';
const LAYOUT_META    = '_lp_cb_layout';
const TITLE_META     = '_lp_cb_title';
const DESCRIPTION_META = '_lp_cb_description';
const BTN_ACCEPT_META = '_lp_cb_btn_accept_all_text';
const BTN_SAVE_META   = '_lp_cb_btn_save_text';
const BTN_REJECT_META = '_lp_cb_btn_reject_text';
const POLICY_TEXT_META = '_lp_cb_policy_link_text';
const POLICY_URL_META  = '_lp_cb_policy_link_url';
const REOPEN_META      = '_lp_cb_reopen_text';
const SHOW_CATEGORIES_META = '_lp_cb_show_categories';
const CATEGORIES_META  = '_lp_cb_categories';
const COLOR_BG_META    = '_lp_cb_color_bg';
const COLOR_TEXT_META  = '_lp_cb_color_text';
const COLOR_ACCENT_META = '_lp_cb_color_accent';
const COLOR_BORDER_META = '_lp_cb_color_border';
const CONSENT_VERSION_META = '_lp_cb_consent_version';

const VALID_LAYOUTS = ['top-bar', 'bottom-bar', 'floating-card-left', 'floating-card-right', 'center-modal'];

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
            'edit_posts'        => 'manage_network_options',
            'edit_others_posts' => 'manage_network_options',
            'publish_posts'     => 'manage_network_options',
            'delete_posts'      => 'manage_network_options',
            'read'              => 'read',
        ],
    ]);
}
