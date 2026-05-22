<?php
namespace LandingConfig\CookieBanner\Enqueue;

if (!defined('ABSPATH')) { exit; }

use function LandingConfig\CookieBanner\Resolver\resolve_for_blog;

const GTAG_MAP = [
    'necessary' => [],
    'analytics' => ['analytics_storage'],
    'marketing' => ['ad_storage', 'ad_user_data', 'ad_personalization'],
];

const VERSION = '1.0';

function _sanitize_color(string $hex): string {
    $hex = trim($hex);
    if ($hex === '') return '';
    if (preg_match('/^#([A-Fa-f0-9]{3}|[A-Fa-f0-9]{6})$/', $hex)) {
        return $hex;
    }
    return '';
}

function _compose_color_overrides_css(array $settings): string {
    $map = [
        '--cb-bg'     => $settings['color_bg']     ?? '',
        '--cb-text'   => $settings['color_text']   ?? '',
        '--cb-accent' => $settings['color_accent'] ?? '',
        '--cb-border' => $settings['color_border'] ?? '',
    ];
    $parts = [];
    foreach ($map as $var => $val) {
        $hex = _sanitize_color((string) $val);
        if ($hex !== '') {
            $parts[] = $var . ':' . $hex;
        }
    }
    return implode(';', $parts);
}

function on_head(): void {
    $settings = resolve_for_blog(\get_current_blog_id());
    if ($settings === null) return;

    // 1. Google Consent Mode v2 default DENIED
    echo "<script>"
       . "window.dataLayer=window.dataLayer||[];"
       . "function gtag(){dataLayer.push(arguments);}"
       . "gtag('consent','default',{"
       . "'analytics_storage':'denied',"
       . "'ad_storage':'denied',"
       . "'ad_user_data':'denied',"
       . "'ad_personalization':'denied',"
       . "'wait_for_update':500"
       . "});</script>\n";

    // 2. Inline color overrides
    $color_css = _compose_color_overrides_css($settings);
    if ($color_css !== '') {
        echo '<style id="lp-cb-overrides">.lp-cb{' . esc_attr($color_css) . '}</style>' . "\n";
    }

    // 3. Enqueue CSS + JS
    $base_url = \plugins_url('assets/cookie-banner', dirname(dirname(__DIR__)) . '/landing-config.php');
    \wp_enqueue_style('lp-cb-core', $base_url . '/core.css', [], VERSION);
    \wp_enqueue_style('lp-cb-layout', $base_url . '/layouts/' . $settings['layout'] . '.css', ['lp-cb-core'], VERSION);
    \wp_enqueue_script('lp-cb', $base_url . '/banner.js', [], VERSION, true);

    \wp_localize_script('lp-cb', 'LP_CB_CONFIG', [
        'version'         => (int) $settings['consent_version'],
        'storage_key'     => 'lp_cookie_consent',
        'categories'      => $settings['categories'],
        'gtag_map'        => GTAG_MAP,
        'show_categories' => (bool) $settings['show_categories'],
    ]);
}

add_action('wp_head', __NAMESPACE__ . '\\on_head', 1);
