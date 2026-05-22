<?php
namespace LandingConfig\CookieBanner\Admin;

if (!defined('ABSPATH')) { exit; }

use const LandingConfig\CookieBanner\CPT\POST_TYPE;
use const LandingConfig\CookieBanner\CPT\SEGMENT_META;
use const LandingConfig\CookieBanner\CPT\VALID_LAYOUTS;
use function LandingConfig\CookieBanner\Resolver\get_post_id_for_segment;
use function LandingConfig\CookieBanner\Resolver\read_settings;
use function LandingConfig\SegmentSelector\render;
use function LandingConfig\SegmentSelector\current_from_request;

const MENU_SLUG = 'landing-config-network-cookie-banner';

add_action('network_admin_menu', __NAMESPACE__ . '\\register_menu');
add_action('admin_post_lp_cb_save', __NAMESPACE__ . '\\handle_save');

function register_menu(): void {
    \add_submenu_page(
        'landing-config-network',
        'Cookie-banner',
        'Cookie-banner',
        'manage_network_options',
        MENU_SLUG,
        __NAMESPACE__ . '\\render_page'
    );
}

function _save_field(int $post_id, string $meta_key, $value): void {
    if (is_array($value)) {
        $value = wp_json_encode($value, JSON_UNESCAPED_UNICODE);
    }
    \update_post_meta($post_id, $meta_key, (string) $value);
}

function handle_save(): void {
    if (!\current_user_can('manage_network_options')) wp_die('forbidden');
    \check_admin_referer('lp_cb_save');
    $segment = (int) ($_POST['segment'] ?? 0);

    $post_id = get_post_id_for_segment($segment);
    if (!$post_id) {
        $post_id = \wp_insert_post([
            'post_type'   => POST_TYPE,
            'post_status' => 'publish',
            'post_title'  => 'Cookie banner (segment=' . $segment . ')',
        ]);
        \update_post_meta($post_id, SEGMENT_META, (string) $segment);
    }

    $layout = sanitize_text_field($_POST['layout'] ?? 'bottom-bar');
    if (!in_array($layout, VALID_LAYOUTS, true)) $layout = 'bottom-bar';
    _save_field($post_id, '_lp_cb_layout', $layout);

    foreach ([
        '_lp_cb_title', '_lp_cb_btn_accept_all_text',
        '_lp_cb_btn_save_text', '_lp_cb_btn_reject_text', '_lp_cb_policy_link_text',
        '_lp_cb_policy_link_url', '_lp_cb_reopen_text',
    ] as $meta) {
        $val = isset($_POST[$meta]) ? sanitize_text_field(wp_unslash($_POST[$meta])) : '';
        _save_field($post_id, $meta, $val);
    }

    $desc = isset($_POST['_lp_cb_description']) ? sanitize_textarea_field(wp_unslash($_POST['_lp_cb_description'])) : '';
    _save_field($post_id, '_lp_cb_description', $desc);

    _save_field($post_id, '_lp_cb_show_categories', !empty($_POST['_lp_cb_show_categories']) ? '1' : '0');
    $cats_raw = $_POST['categories'] ?? [];
    $cats = [];
    if (is_array($cats_raw)) {
        foreach ($cats_raw as $c) {
            if (empty($c['slug'])) continue;
            $cats[] = [
                'slug'       => sanitize_key($c['slug']),
                'name'       => sanitize_text_field($c['name'] ?? ''),
                'desc'       => sanitize_text_field($c['desc'] ?? ''),
                'locked'     => !empty($c['locked']),
                'default_on' => !empty($c['default_on']),
            ];
        }
    }
    _save_field($post_id, '_lp_cb_categories', $cats);

    foreach (['color_bg', 'color_text', 'color_accent', 'color_border'] as $f) {
        $hex = sanitize_text_field($_POST['_lp_cb_' . $f] ?? '');
        if ($hex !== '' && !preg_match('/^#([A-Fa-f0-9]{3}|[A-Fa-f0-9]{6})$/', $hex)) $hex = '';
        _save_field($post_id, '_lp_cb_' . $f, $hex);
    }

    _save_field($post_id, '_lp_cb_consent_version', (int) ($_POST['_lp_cb_consent_version'] ?? 1));

    \wp_safe_redirect(\add_query_arg(['page' => MENU_SLUG, 'segment' => $segment, 'saved' => 1], \network_admin_url('admin.php')));
    exit;
}

function render_page(): void {
    if (!\current_user_can('manage_network_options')) wp_die('forbidden');
    $segment = current_from_request();
    $post_id = get_post_id_for_segment($segment);
    $current = $post_id ? read_settings($post_id) : [];
    $get = function(string $field, $default = '') use ($current) {
        $val = $current[$field] ?? null;
        return $val === null ? $default : $val;
    };

    ?>
    <div class="wrap">
        <h1>Cookie-banner</h1>

        <?php if (!empty($_GET['saved'])): ?>
            <div class="notice notice-success is-dismissible"><p>Сохранено.</p></div>
        <?php endif; ?>

        <?php render(MENU_SLUG, $segment); ?>

        <form method="post" action="<?php echo esc_url(\network_admin_url('admin-post.php')); ?>">
            <input type="hidden" name="action" value="lp_cb_save">
            <input type="hidden" name="segment" value="<?php echo esc_attr($segment); ?>">
            <?php \wp_nonce_field('lp_cb_save'); ?>

            <h2>Layout</h2>
            <fieldset>
                <?php foreach (VALID_LAYOUTS as $layout): ?>
                    <label style="display:inline-block; margin-right:24px; text-align:center;">
                        <input type="radio" name="layout" value="<?php echo esc_attr($layout); ?>"
                               <?php checked($get('layout', 'bottom-bar'), $layout); ?>>
                        <br>
                        <img src="<?php echo esc_url(\plugins_url('assets/cookie-banner/previews/' . $layout . '.svg', dirname(dirname(__DIR__)) . '/landing-config.php')); ?>"
                             alt="<?php echo esc_attr($layout); ?>"
                             style="width:160px; height:96px; border:1px solid #ccc; margin-top:4px;">
                        <br><?php echo esc_html($layout); ?>
                    </label>
                <?php endforeach; ?>
            </fieldset>

            <h2>Тексты</h2>
            <table class="form-table">
                <tr><th>Заголовок</th>
                    <td><input type="text" name="_lp_cb_title" value="<?php echo esc_attr($get('title')); ?>" class="regular-text"></td></tr>
                <tr><th>Описание</th>
                    <td><textarea name="_lp_cb_description" rows="3" class="large-text"><?php echo esc_textarea($get('description')); ?></textarea></td></tr>
                <tr><th>Принять все</th>
                    <td><input type="text" name="_lp_cb_btn_accept_all_text" value="<?php echo esc_attr($get('btn_accept_all_text')); ?>" class="regular-text"></td></tr>
                <tr><th>Сохранить</th>
                    <td><input type="text" name="_lp_cb_btn_save_text" value="<?php echo esc_attr($get('btn_save_text')); ?>" class="regular-text"></td></tr>
                <tr><th>Отклонить (пусто = скрыта)</th>
                    <td><input type="text" name="_lp_cb_btn_reject_text" value="<?php echo esc_attr($get('btn_reject_text')); ?>" class="regular-text"></td></tr>
                <tr><th>Текст ссылки на политику</th>
                    <td><input type="text" name="_lp_cb_policy_link_text" value="<?php echo esc_attr($get('policy_link_text')); ?>" class="regular-text"></td></tr>
                <tr><th>URL политики</th>
                    <td><input type="text" name="_lp_cb_policy_link_url" value="<?php echo esc_attr($get('policy_link_url')); ?>" class="regular-text"></td></tr>
                <tr><th>Reopen (footer)</th>
                    <td><input type="text" name="_lp_cb_reopen_text" value="<?php echo esc_attr($get('reopen_text')); ?>" class="regular-text"></td></tr>
            </table>

            <h2>Категории</h2>
            <label>
                <input type="checkbox" name="_lp_cb_show_categories" value="1" <?php checked((bool) $get('show_categories', false)); ?>>
                Показывать категории (detailed mode)
            </label>
            <table class="widefat" style="margin-top:12px;">
                <thead><tr><th>Slug</th><th>Имя</th><th>Описание</th><th>Locked</th><th>Default on</th></tr></thead>
                <tbody id="lp-cb-cats">
                    <?php
                    $cats = $get('categories', []);
                    if (empty($cats)) $cats = \LandingConfig\CookieBanner\Resolver\DEFAULTS['categories'];
                    foreach ($cats as $i => $c): ?>
                        <tr>
                            <td><input type="text" name="categories[<?php echo $i; ?>][slug]" value="<?php echo esc_attr($c['slug'] ?? ''); ?>"></td>
                            <td><input type="text" name="categories[<?php echo $i; ?>][name]" value="<?php echo esc_attr($c['name'] ?? ''); ?>"></td>
                            <td><input type="text" name="categories[<?php echo $i; ?>][desc]" value="<?php echo esc_attr($c['desc'] ?? ''); ?>"></td>
                            <td><input type="checkbox" name="categories[<?php echo $i; ?>][locked]" value="1" <?php checked(!empty($c['locked'])); ?>></td>
                            <td><input type="checkbox" name="categories[<?php echo $i; ?>][default_on]" value="1" <?php checked(!empty($c['default_on'])); ?>></td>
                        </tr>
                    <?php endforeach; ?>
                </tbody>
            </table>
            <p><em>Дополнительная категория (заполни slug чтобы добавить):</em></p>
            <table class="widefat" style="margin-top:4px;">
                <tbody><tr>
                    <td><input type="text" name="categories[99][slug]" placeholder="slug (eg functional)"></td>
                    <td><input type="text" name="categories[99][name]" placeholder="Имя"></td>
                    <td><input type="text" name="categories[99][desc]" placeholder="Описание"></td>
                    <td><input type="checkbox" name="categories[99][locked]" value="1"></td>
                    <td><input type="checkbox" name="categories[99][default_on]" value="1"></td>
                </tr></tbody>
            </table>

            <h2>Цвета (пусто = inherit from theme)</h2>
            <table class="form-table">
                <tr><th>Фон</th>     <td><input type="text" name="_lp_cb_color_bg"     value="<?php echo esc_attr($get('color_bg')); ?>" placeholder="#ffffff" class="small-text"></td></tr>
                <tr><th>Текст</th>   <td><input type="text" name="_lp_cb_color_text"   value="<?php echo esc_attr($get('color_text')); ?>" placeholder="#1d2327" class="small-text"></td></tr>
                <tr><th>Акцент</th>  <td><input type="text" name="_lp_cb_color_accent" value="<?php echo esc_attr($get('color_accent')); ?>" placeholder="#2271b1" class="small-text"></td></tr>
                <tr><th>Граница</th> <td><input type="text" name="_lp_cb_color_border" value="<?php echo esc_attr($get('color_border')); ?>" placeholder="#c3c4c7" class="small-text"></td></tr>
            </table>

            <h2>Версия согласия</h2>
            <input type="number" name="_lp_cb_consent_version" value="<?php echo esc_attr($get('consent_version', 1)); ?>" min="1" class="small-text">
            <p class="description">Bump → пользователи увидят баннер заново.</p>

            <p>
                <button type="submit" class="button button-primary">Сохранить</button>
                <a href="<?php echo esc_url(\home_url('/?lp_cookie_banner_preview=1&segment=' . $segment)); ?>" target="_blank" class="button">Live preview ↗</a>
            </p>
        </form>
    </div>
    <?php
}
