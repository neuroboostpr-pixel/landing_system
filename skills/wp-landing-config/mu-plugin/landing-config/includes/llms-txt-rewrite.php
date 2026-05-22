<?php
namespace LandingConfig\LlmsTxt;

if (!defined('ABSPATH')) { exit; }

add_action('init', __NAMESPACE__ . '\\register_rewrite');
add_filter('query_vars', __NAMESPACE__ . '\\add_query_var');
add_action('template_redirect', __NAMESPACE__ . '\\serve');

function register_rewrite(): void {
    \add_rewrite_rule('^llms\\.txt$', 'index.php?lp_llms_txt=1', 'top');
}

function add_query_var(array $vars): array {
    $vars[] = 'lp_llms_txt';
    return $vars;
}

function serve(): void {
    if (!\get_query_var('lp_llms_txt')) return;
    $content = (string) \get_option('landing_seo_llms_txt', '');
    if ($content === '') {
        \status_header(404);
        exit;
    }
    \status_header(200);
    \header('Content-Type: text/markdown; charset=utf-8');
    echo $content;
    exit;
}
