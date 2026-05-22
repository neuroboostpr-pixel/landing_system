<?php
namespace LandingConfig\HeadSEOAdmin;

if (!defined('ABSPATH')) { exit; }

const MENU_SLUG = 'landing-config-head-seo';
const NETWORK_BLOG_ID = 1;

const VALID_OG_TYPES      = ['website', 'article', 'product'];
const VALID_TWITTER_CARDS = ['summary', 'summary_large_image'];

add_action('network_admin_menu', __NAMESPACE__ . '\\register_menu');
add_action('admin_post_lp_head_seo_save', __NAMESPACE__ . '\\handle_save');
add_action('admin_enqueue_scripts', __NAMESPACE__ . '\\enqueue_assets');

function register_menu(): void {
    \add_submenu_page(
        'landing-config-network',
        'Head & SEO',
        'Head & SEO',
        'manage_network_options',
        MENU_SLUG,
        __NAMESPACE__ . '\\render_page'
    );
}

function enqueue_assets($hook): void {
    if (strpos((string) $hook, MENU_SLUG) === false) return;
    $base = \plugins_url('assets/seo-audit', dirname(__DIR__) . '/landing-config.php');
    \wp_enqueue_style('lp-head-seo-preview', $base . '/preview.css', [], '1.0');
    \wp_enqueue_script('lp-head-seo-preview', $base . '/preview.js', [], '1.0', true);
    \wp_enqueue_media();
}

/**
 * Pure save logic. Sanitizes input. Writes to wp_options in given segment's blog.
 *
 * @return bool always true on success
 */
function save_settings_for_segment(int $segment, array $input): bool {
    $target_blog = ($segment === 0) ? NETWORK_BLOG_ID : $segment;
    $current_blog = \get_current_blog_id();
    $switched = false;
    if (function_exists('switch_to_blog') && $target_blog !== $current_blog) {
        \switch_to_blog($target_blog);
        $switched = true;
    }

    if (isset($input['description'])) {
        \update_option('landing_seo_description', \sanitize_textarea_field((string) $input['description']));
    }
    if (isset($input['og_image'])) {
        \update_option('landing_seo_og_image', \esc_url_raw((string) $input['og_image']));
    }
    if (isset($input['og_type'])) {
        $og_type = (string) $input['og_type'];
        if (!in_array($og_type, VALID_OG_TYPES, true)) $og_type = 'website';
        \update_option('landing_seo_og_type', $og_type);
    }
    if (isset($input['twitter_card'])) {
        $tw = (string) $input['twitter_card'];
        if (!in_array($tw, VALID_TWITTER_CARDS, true)) $tw = 'summary_large_image';
        \update_option('landing_seo_twitter_card', $tw);
    }
    if (isset($input['llms_txt'])) {
        \update_option('landing_seo_llms_txt', (string) $input['llms_txt']);
    }

    if ($switched) \restore_current_blog();
    return true;
}

function load_settings_for_segment(int $segment): array {
    $target_blog = ($segment === 0) ? NETWORK_BLOG_ID : $segment;
    $current_blog = \get_current_blog_id();
    $switched = false;
    if (function_exists('switch_to_blog') && $target_blog !== $current_blog) {
        \switch_to_blog($target_blog);
        $switched = true;
    }
    $out = [
        'description'  => (string) \get_option('landing_seo_description', ''),
        'og_image'     => (string) \get_option('landing_seo_og_image', ''),
        'og_type'      => (string) \get_option('landing_seo_og_type', 'website'),
        'twitter_card' => (string) \get_option('landing_seo_twitter_card', 'summary_large_image'),
        'llms_txt'     => (string) \get_option('landing_seo_llms_txt', ''),
    ];
    if ($switched) \restore_current_blog();
    return $out;
}

function handle_save(): void {
    if (!\current_user_can('manage_network_options')) wp_die('forbidden');
    \check_admin_referer('lp_head_seo_save');
    $segment = (int) ($_POST['segment'] ?? 0);

    save_settings_for_segment($segment, [
        'description'  => $_POST['description']  ?? '',
        'og_image'     => $_POST['og_image']     ?? '',
        'og_type'      => $_POST['og_type']      ?? '',
        'twitter_card' => $_POST['twitter_card'] ?? '',
        'llms_txt'     => $_POST['llms_txt']     ?? '',
    ]);

    \wp_safe_redirect(\add_query_arg([
        'page' => MENU_SLUG, 'segment' => $segment, 'saved' => 1,
    ], \network_admin_url('admin.php')));
    exit;
}

function render_segment_selector(int $current): void {
    ?>
    <select name="segment_selector" onchange="window.location.href='<?php echo esc_js(\network_admin_url('admin.php?page=' . MENU_SLUG)); ?>&segment=' + this.value">
        <option value="0" <?php selected($current, 0); ?>>Network default</option>
        <?php foreach (\get_sites(['fields' => 'ids']) as $bid):
            $url = \get_site_url((int) $bid); ?>
            <option value="<?php echo (int) $bid; ?>" <?php selected($current, (int) $bid); ?>>
                blog #<?php echo (int) $bid; ?> — <?php echo esc_html((string) $url); ?>
            </option>
        <?php endforeach; ?>
    </select>
    <?php
}

function render_page(): void {
    if (!\current_user_can('manage_network_options')) wp_die('forbidden');
    $segment = isset($_GET['segment']) ? (int) $_GET['segment'] : 0;
    $settings = load_settings_for_segment($segment);
    $site_name = \get_bloginfo('name');
    ?>
    <div class="wrap">
        <h1>Head & SEO</h1>

        <?php if (!empty($_GET['saved'])): ?>
            <div class="notice notice-success is-dismissible"><p>Сохранено.</p></div>
        <?php endif; ?>

        <div style="margin-bottom: 16px;">
            <label>Сегмент: </label>
            <?php render_segment_selector($segment); ?>
        </div>

        <div style="display:flex; gap:24px; align-items:flex-start;">
          <div style="flex: 1 1 60%; min-width:0;">
            <form method="post" action="<?php echo esc_url(\admin_url('admin-post.php')); ?>">
                <?php \wp_nonce_field('lp_head_seo_save'); ?>
                <input type="hidden" name="action" value="lp_head_seo_save">
                <input type="hidden" name="segment" value="<?php echo (int) $segment; ?>">

                <h2>Description</h2>
                <textarea name="description" rows="3" class="large-text" id="lp-input-description"
                          placeholder="≥70 символов"><?php echo esc_textarea($settings['description']); ?></textarea>
                <p class="description"><span id="lp-char-count">0</span> символов (рекомендация: 70-320)</p>

                <h2>Open Graph Image</h2>
                <input type="text" name="og_image" id="lp-input-og-image" class="regular-text"
                       value="<?php echo esc_attr($settings['og_image']); ?>"
                       placeholder="https://example.com/og.png">
                <button type="button" class="button" id="lp-pick-og-image">Выбрать из медиа</button>

                <h2>Open Graph Type</h2>
                <select name="og_type" id="lp-input-og-type">
                    <?php foreach (VALID_OG_TYPES as $t): ?>
                        <option value="<?php echo esc_attr($t); ?>" <?php selected($settings['og_type'], $t); ?>>
                            <?php echo esc_html($t); ?>
                        </option>
                    <?php endforeach; ?>
                </select>

                <h2>Twitter Card</h2>
                <select name="twitter_card">
                    <?php foreach (VALID_TWITTER_CARDS as $t): ?>
                        <option value="<?php echo esc_attr($t); ?>" <?php selected($settings['twitter_card'], $t); ?>>
                            <?php echo esc_html($t); ?>
                        </option>
                    <?php endforeach; ?>
                </select>

                <h2 id="llms-txt">llms.txt content</h2>
                <p class="description">Markdown по <a href="https://llmstxt.org" target="_blank">llmstxt.org spec</a>.
                   Пусто → /llms.txt не отдаётся.</p>
                <textarea name="llms_txt" rows="10" class="large-text"
                          placeholder="# Site name&#10;&#10;> Description&#10;&#10;## Resources&#10;- [Title](URL): Note"><?php echo esc_textarea($settings['llms_txt']); ?></textarea>

                <p style="margin-top: 20px;">
                    <button type="submit" class="button button-primary">Сохранить</button>
                </p>
            </form>
          </div>

          <aside style="flex: 0 0 380px;">
            <h2>Preview</h2>

            <h3>OG-карточка</h3>
            <div class="lp-preview-og-card">
                <div class="lp-preview-og-image" id="lp-preview-og-image-area"
                     <?php if ($settings['og_image']): ?>
                       style="background-image:url('<?php echo esc_url($settings['og_image']); ?>')"
                     <?php endif; ?>>
                </div>
                <div class="lp-preview-og-meta">
                    <div class="lp-preview-og-domain"><?php echo esc_html(parse_url(\home_url(), PHP_URL_HOST) ?? ''); ?></div>
                    <div class="lp-preview-og-title" id="lp-preview-og-title"><?php echo esc_html($site_name); ?></div>
                    <div class="lp-preview-og-desc" id="lp-preview-og-desc"><?php echo esc_html($settings['description']); ?></div>
                </div>
            </div>

            <h3 style="margin-top: 24px;">SERP-сниппет</h3>
            <div class="lp-preview-serp">
                <div class="lp-preview-serp-breadcrumb"><?php echo esc_html(parse_url(\home_url(), PHP_URL_HOST) ?? ''); ?></div>
                <div class="lp-preview-serp-title" id="lp-preview-serp-title"><?php echo esc_html($site_name); ?></div>
                <div class="lp-preview-serp-desc" id="lp-preview-serp-desc"><?php echo esc_html($settings['description']); ?></div>
            </div>
          </aside>
        </div>
    </div>
    <?php
}
