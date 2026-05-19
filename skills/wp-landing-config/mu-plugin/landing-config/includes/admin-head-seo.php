<?php
namespace LandingConfig\Admin\HeadSEO;

if (!defined('ABSPATH')) { exit; }

const FIELDS = [
    'ga4_id'                => ['label' => 'Google Analytics 4 ID', 'placeholder' => 'G-XXXXXXXXXX'],
    'yandex_metrika_id'     => ['label' => 'Яндекс.Метрика ID',     'placeholder' => '12345678'],
    'fb_pixel_id'           => ['label' => 'Meta (FB) Pixel ID',     'placeholder' => '123456789012345'],
    'tiktok_pixel_id'       => ['label' => 'TikTok Pixel ID',        'placeholder' => 'CXXXXXXXXXXX'],
    'gsc_verification'      => ['label' => 'Google Search Console (verification content)', 'placeholder' => 'abc...XYZ'],
    'yandex_webmaster_id'   => ['label' => 'Яндекс.Вебмастер (verification content)',     'placeholder' => 'abc...123'],
    'og_default_image'      => ['label' => 'OG image default URL',   'placeholder' => 'https://...'],
    'og_default_title'      => ['label' => 'OG title default',       'placeholder' => 'My Landing'],
    'og_default_description'=> ['label' => 'OG description default', 'placeholder' => 'Краткое описание'],
    'fonts_google_url'      => ['label' => 'Google Fonts URL',       'placeholder' => 'https://fonts.googleapis.com/css2?...'],
    'raw_html_head'         => ['label' => 'Custom HTML в head',     'placeholder' => '<!-- любой код -->', 'type' => 'textarea'],
];

add_action('admin_menu', function () {
    global $submenu;
    if (isset($submenu['landing-config'])) {
        foreach ($submenu['landing-config'] as &$item) {
            if ($item[2] === 'landing-config-head-seo') {
                $item[3] = __NAMESPACE__ . '\\render_page';
            }
        }
    }
}, 99);

add_action('admin_init', function () {
    foreach (FIELDS as $key => $meta) {
        register_setting('landing_head_seo', 'landing_' . $key, [
            'type' => 'string',
            'sanitize_callback' => $key === 'raw_html_head'
                ? __NAMESPACE__ . '\\sanitize_raw_html'
                : 'sanitize_text_field',
        ]);
    }
});

function sanitize_raw_html($input): string {
    $allowed_html = [
        'script'   => ['src' => true, 'async' => true, 'defer' => true, 'type' => true, 'crossorigin' => true],
        'meta'     => ['name' => true, 'content' => true, 'property' => true, 'http-equiv' => true, 'charset' => true],
        'link'     => ['rel' => true, 'href' => true, 'type' => true, 'crossorigin' => true, 'sizes' => true, 'as' => true],
        'style'    => ['type' => true, 'media' => true],
        'noscript' => [],
    ];
    return wp_kses((string)$input, $allowed_html);
}

function render_page(): void {
    if (!current_user_can('manage_options')) { wp_die('Insufficient permissions'); }
    ?>
    <div class="wrap">
        <h1>Head &amp; SEO</h1>
        <p>Все настройки попадают в <code>&lt;head&gt;</code> на каждой странице сайта.
        Поле «Custom HTML» фильтруется через wp_kses (разрешены meta/link/script/style).</p>
        <form method="post" action="options.php">
            <?php settings_fields('landing_head_seo'); ?>
            <table class="form-table">
                <?php foreach (FIELDS as $key => $meta):
                    $value = get_option('landing_' . $key, '');
                    $is_textarea = ($meta['type'] ?? '') === 'textarea';
                ?>
                    <tr>
                        <th><label for="landing_<?php echo $key; ?>"><?php echo esc_html($meta['label']); ?></label></th>
                        <td>
                            <?php if ($is_textarea): ?>
                                <textarea id="landing_<?php echo $key; ?>"
                                    name="landing_<?php echo $key; ?>"
                                    rows="6" class="large-text code"
                                    placeholder="<?php echo esc_attr($meta['placeholder']); ?>"><?php echo esc_textarea($value); ?></textarea>
                            <?php else: ?>
                                <input type="text" id="landing_<?php echo $key; ?>"
                                    name="landing_<?php echo $key; ?>"
                                    value="<?php echo esc_attr($value); ?>"
                                    placeholder="<?php echo esc_attr($meta['placeholder']); ?>"
                                    class="regular-text">
                            <?php endif; ?>
                        </td>
                    </tr>
                <?php endforeach; ?>
            </table>
            <?php submit_button(); ?>
        </form>
    </div>
    <?php
}
