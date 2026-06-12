<?php
namespace LandingConfig\LlmsTxt;

if (!defined('ABSPATH')) { exit; }

add_action('parse_request', __NAMESPACE__ . '\\intercept', 0);

function intercept($wp): void {
    $uri = isset($_SERVER['REQUEST_URI']) ? (string) $_SERVER['REQUEST_URI'] : '';
    $path = parse_url($uri, PHP_URL_PATH) ?: '';
    // Match /llms.txt with optional trailing slash, regardless of subsite path prefix
    if (!preg_match('#/llms\.txt/?$#', $path)) return;
    serve();
}

function serve(): void {
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
