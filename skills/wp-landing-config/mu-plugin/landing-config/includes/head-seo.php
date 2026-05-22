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

add_action('wp_head', __NAMESPACE__ . '\\emit', 2);

function emit(): void {
    if (!empty($GLOBALS['__lp_head_seo_skip'])) {
        return;
    }

    $title = \wp_get_document_title();
    if (!$title) {
        $title = \get_bloginfo('name');
    }

    $description = (string) \get_option(OPTION_DESCRIPTION, '');
    if ($description === '') {
        $description = (string) \get_bloginfo('description');
    }

    $url = \home_url(\add_query_arg(null, null));

    $og_image = (string) \get_option(OPTION_OG_IMAGE, '');
    if ($og_image === '') {
        $site_icon = \get_site_icon_url(512);
        if ($site_icon) {
            $og_image = $site_icon;
        }
    }

    $og_type = (string) \get_option(OPTION_OG_TYPE, 'website');
    if ($og_type === '') {
        $og_type = 'website';
    }

    $tw_card = (string) \get_option(OPTION_TW_CARD, 'summary_large_image');
    if ($tw_card === '') {
        $tw_card = 'summary_large_image';
    }

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
