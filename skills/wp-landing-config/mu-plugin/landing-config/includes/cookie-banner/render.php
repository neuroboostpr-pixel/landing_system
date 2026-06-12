<?php
namespace LandingConfig\CookieBanner\Render;

if (!defined('ABSPATH')) { exit; }

use const LandingConfig\CookieBanner\CPT\VALID_LAYOUTS;
use function LandingConfig\CookieBanner\Resolver\resolve_for_blog;

const LAYOUTS_DIR = __DIR__ . '/layouts';

function render_with_settings(array $settings): void {
    $layout = $settings['layout'] ?? 'bottom-bar';
    if (!in_array($layout, VALID_LAYOUTS, true)) {
        $layout = 'bottom-bar';
    }
    $tpl = LAYOUTS_DIR . '/' . $layout . '.php';
    if (!file_exists($tpl)) {
        $tpl = LAYOUTS_DIR . '/bottom-bar.php';
    }
    include $tpl;
}

function on_footer(): void {
    $settings = resolve_for_blog(\get_current_blog_id());
    if ($settings === null) return;
    render_with_settings($settings);
}

add_action('wp_footer', __NAMESPACE__ . '\\on_footer');
