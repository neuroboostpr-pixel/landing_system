<?php
namespace LandingConfig\SEOAudit\DeepLinks;

if (!defined('ABSPATH')) { exit; }

/** Path to PHP-consumed fix-actions JSON (auto-gen from Python). */
const CATALOG_PATH = __DIR__ . '/fix-actions.json';

function load_catalog(): array {
    if (!file_exists(CATALOG_PATH)) return [];
    $raw = file_get_contents(CATALOG_PATH);
    $data = json_decode($raw, true);
    return is_array($data) ? $data : [];
}

/**
 * Build deep-link metadata for a given check_id.
 *
 * @param string $check_id  Audit check ID (e.g. H6, N8, S5, AI1)
 * @param int    $blog_id   Blog context (for switch_to_blog if homepage_id needed per-site)
 * @param string $admin_root Base admin URL (e.g. https://x/wp-admin/)
 * @return array{label:string, type:string, url?:string}|null
 */
function build_deep_link(string $check_id, int $blog_id, string $admin_root): ?array {
    $catalog = load_catalog();
    $entry = $catalog[$check_id] ?? null;
    if (!$entry) return null;

    $type = $entry['type'] ?? 'suggestion';
    $label = $entry['label'] ?? $check_id;
    $out = ['label' => $label, 'type' => $type];

    switch ($type) {
        case 'admin_page':
            $page = $entry['page'] ?? '';
            $out['url'] = rtrim($admin_root, '/') . '/admin.php?page=' . urlencode($page);
            break;
        case 'post_edit':
            $homepage_id = (int) (\get_option('page_on_front', 0) ?: 0);
            if (!empty($entry['use_homepage_id']) && $homepage_id > 0) {
                $out['url'] = rtrim($admin_root, '/') . '/post.php?post=' . $homepage_id . '&action=edit';
            } else {
                // Fallback: link to all pages list
                $out['url'] = rtrim($admin_root, '/') . '/edit.php?post_type=page';
            }
            break;
        case 'raw_url':
            $url = (string) ($entry['url'] ?? '');
            $out['url'] = rtrim($admin_root, '/') . '/' . ltrim($url, '/');
            break;
        case 'suggestion':
        default:
            // No URL
            break;
    }
    return $out;
}
