<?php
namespace LandingConfig\HeadSEO;

/**
 * Minimal SEO head injector — meta description + Open Graph + favicon link.
 *
 * Reads from per-blog wp_options:
 *   landing_seo_description (string, ≥70 chars recommended)
 *   landing_seo_og_image    (URL)
 *   landing_seo_og_type     (default: "website")
 *   landing_seo_twitter_card (default: "summary_large_image")
 *
 * Fallbacks:
 *   og:title       → get_bloginfo('name') / wp_title
 *   og:description → landing_seo_description / get_bloginfo('description')
 *   og:url         → home_url(add_query_arg(null, null))
 *   og:image       → landing_seo_og_image / get_site_icon_url(512)
 *   og:type        → landing_seo_og_type / "website"
 *   favicon        → get_site_icon_url(32) (if set in Customizer)
 *
 * Hooked early (priority 2) in wp_head — после consent-init (priority 1)
 * но до большинства theme-вставок.
 *
 * Doesn't override if theme already emits any meta name="description"
 * or og:* tags — checks via $GLOBALS['__lp_head_seo_skip'] sentinel which
 * theme can set in functions.php.
 */
if (!defined('ABSPATH')) { exit; }

const OPTION_DESCRIPTION = 'landing_seo_description';
const OPTION_OG_IMAGE    = 'landing_seo_og_image';
const OPTION_OG_TYPE     = 'landing_seo_og_type';
const OPTION_TW_CARD     = 'landing_seo_twitter_card';
const NETWORK_BLOG_ID    = 1;

/**
 * Cascade-aware read: site override → network default → empty.
 *
 * @param string $option_key e.g. 'landing_seo_description'
 * @param int    $blog_id    Current blog id
 * @return string Always a string (empty if nothing set)
 */
function resolve_setting_cascade(string $option_key, int $blog_id): string {
    // 1. Try site override (non-network blog)
    if ($blog_id !== NETWORK_BLOG_ID && function_exists('switch_to_blog')) {
        \switch_to_blog($blog_id);
        $site_val = (string) \get_option($option_key, '');
        \restore_current_blog();
        if ($site_val !== '') return $site_val;
    } else {
        $site_val = (string) \get_option($option_key, '');
        if ($site_val !== '') return $site_val;
    }

    // 2. Fall back to network default (blog_id = 1)
    if (function_exists('switch_to_blog')) {
        \switch_to_blog(NETWORK_BLOG_ID);
        $network_val = (string) \get_option($option_key, '');
        \restore_current_blog();
        return $network_val;
    }
    return '';
}

add_action('wp_head', __NAMESPACE__ . '\\emit', 2);

function emit(): void {
    if (!empty($GLOBALS['__lp_head_seo_skip'])) {
        return;
    }

    $title = \wp_get_document_title();
    if (!$title) {
        $title = \get_bloginfo('name');
    }

    $description = resolve_setting_cascade(OPTION_DESCRIPTION, \get_current_blog_id());
    if ($description === '') {
        $description = (string) \get_bloginfo('description');
    }

    $url = \home_url(\add_query_arg(null, null));

    $og_image = resolve_setting_cascade(OPTION_OG_IMAGE, \get_current_blog_id());
    if ($og_image === '') {
        $site_icon = \get_site_icon_url(512);
        if ($site_icon) {
            $og_image = $site_icon;
        }
    }

    $og_type = resolve_setting_cascade(OPTION_OG_TYPE, \get_current_blog_id()) ?: 'website';

    $tw_card = resolve_setting_cascade(OPTION_TW_CARD, \get_current_blog_id()) ?: 'summary_large_image';

    $favicon = \get_site_icon_url(32);

    echo "\n<!-- landing-config: head-seo -->\n";

    if ($description) {
        printf('<meta name="description" content="%s">' . "\n",
               \esc_attr($description));
    }

    // Open Graph
    printf('<meta property="og:title" content="%s">' . "\n", \esc_attr($title));
    if ($description) {
        printf('<meta property="og:description" content="%s">' . "\n",
               \esc_attr($description));
    }
    printf('<meta property="og:url" content="%s">' . "\n", \esc_url($url));
    printf('<meta property="og:type" content="%s">' . "\n", \esc_attr($og_type));
    if ($og_image) {
        printf('<meta property="og:image" content="%s">' . "\n", \esc_url($og_image));
    }

    // Twitter Card (соответствует Open Graph image)
    printf('<meta name="twitter:card" content="%s">' . "\n", \esc_attr($tw_card));
    printf('<meta name="twitter:title" content="%s">' . "\n", \esc_attr($title));
    if ($og_image) {
        printf('<meta name="twitter:image" content="%s">' . "\n", \esc_url($og_image));
    }

    // Favicon (если в Customizer установлен Site Icon)
    if ($favicon) {
        printf('<link rel="icon" sizes="32x32" href="%s">' . "\n", \esc_url($favicon));
        $favicon_180 = \get_site_icon_url(180);
        if ($favicon_180) {
            printf('<link rel="apple-touch-icon" sizes="180x180" href="%s">' . "\n",
                   \esc_url($favicon_180));
        }
    }

    echo "<!-- /landing-config: head-seo -->\n";
}
