<?php
namespace LandingConfig\Admin\GeneralSettings;

if (!defined('ABSPATH')) { exit; }

add_action('admin_menu', function () {
    add_submenu_page(
        \LandingConfig\Admin\MENU_SLUG,
        'Общие настройки',
        'Общие настройки',
        \LandingConfig\Admin\CAP_MANAGE,
        'landing-config-general',
        __NAMESPACE__ . '\\render_page'
    );
});

function render_page(): void {
    if (!current_user_can(\LandingConfig\Admin\CAP_MANAGE)) {
        wp_die('Нет доступа');
    }

    $rc_toggled = false;
    if (isset($_POST['lp_recaptcha_toggle_nonce']) && wp_verify_nonce($_POST['lp_recaptcha_toggle_nonce'], 'lp_recaptcha_toggle')) {
        update_option('lp_recaptcha_enabled', '0');
        $rc_toggled = true;
    }

    $saved = false;
    if (isset($_POST['lp_general_nonce']) && wp_verify_nonce($_POST['lp_general_nonce'], 'lp_general_settings')) {
        $rate_limit = max(1, (int) ($_POST['lp_rate_limit'] ?? 10));
        update_option('lp_rate_limit_per_hour', $rate_limit);

        // reCAPTCHA
        $rc_enabled   = !empty($_POST['lp_recaptcha_enabled']) ? '1' : '0';
        $rc_site_key  = sanitize_text_field($_POST['lp_recaptcha_site_key'] ?? '');
        $rc_threshold = min(1.0, max(0.0, (float) ($_POST['lp_recaptcha_threshold'] ?? 0.5)));
        update_option('lp_recaptcha_enabled',   $rc_enabled);
        update_option('lp_recaptcha_site_key',  $rc_site_key);
        update_option('lp_recaptcha_threshold', (string) $rc_threshold);
        // Secret key: only update if not empty (user typed a new one)
        $rc_secret_raw = $_POST['lp_recaptcha_secret_key'] ?? '';
        if ($rc_secret_raw !== '') {
            update_option('lp_recaptcha_secret_key_enc', \LandingConfig\Encryption\encrypt($rc_secret_raw));
        }

        $saved = true;
    }

    $from_db = get_option('lp_rate_limit_per_hour', false);
    $wp_config_val = defined('LP_RATE_LIMIT_PER_HOUR') ? (int) LP_RATE_LIMIT_PER_HOUR : null;
    // Effective: DB value wins over wp-config constant
    $rate_limit = $from_db !== false ? (int) $from_db : ($wp_config_val ?? 10);

    $rc_enabled    = get_option('lp_recaptcha_enabled',   '0') === '1';
    $rc_site_key   = (string) get_option('lp_recaptcha_site_key', '');
    $rc_threshold  = (float)  get_option('lp_recaptcha_threshold', '0.5');
    $rc_secret_enc = (string) get_option('lp_recaptcha_secret_key_enc', '');
    $rc_secret_set = $rc_secret_enc !== '';
    ?>
    <div class="wrap">
        <h1>Лендинг — Общие настройки</h1>

        <?php if ($saved): ?>
            <div class="notice notice-success is-dismissible"><p>Настройки сохранены.</p></div>
        <?php endif; ?>
        <?php if ($rc_toggled): ?>
            <div class="notice notice-success is-dismissible"><p>reCAPTCHA отключена.</p></div>
        <?php endif; ?>

        <form method="post" action="">
            <?php wp_nonce_field('lp_general_settings', 'lp_general_nonce'); ?>

            <h2>Защита от спама</h2>
            <table class="form-table" role="presentation">
                <tr>
                    <th scope="row">
                        <label for="lp_rate_limit">Лимит заявок с одного IP в час</label>
                    </th>
                    <td>
                        <input
                            type="number"
                            id="lp_rate_limit"
                            name="lp_rate_limit"
                            value="<?php echo esc_attr($rate_limit); ?>"
                            min="1"
                            max="10000"
                            style="width:100px;"
                        >
                        <p class="description">
                            <?php if ($wp_config_val !== null): ?>
                                В wp-config.php задана константа <code>LP_RATE_LIMIT_PER_HOUR = <?php echo $wp_config_val; ?></code>.
                                Значение из этой формы её перекрывает — после сохранения здесь константа больше не учитывается.
                            <?php else: ?>
                                Количество заявок с одного IP-адреса за час. Для тестирования: 100+, для прода: 10–50.
                            <?php endif; ?>
                        </p>
                    </td>
                </tr>
            </table>

            <h2>reCAPTCHA v3</h2>
            <table class="form-table" role="presentation">
                <tr>
                    <th scope="row">Включить reCAPTCHA v3</th>
                    <td>
                        <label>
                            <input type="checkbox" name="lp_recaptcha_enabled" value="1" <?php checked($rc_enabled); ?>>
                            Проверять токен reCAPTCHA при отправке формы
                        </label>
                        <?php if ($rc_enabled): ?>
                        <form method="post" action="" style="display:inline-block;margin-left:16px;">
                            <?php wp_nonce_field('lp_recaptcha_toggle', 'lp_recaptcha_toggle_nonce'); ?>
                            <button type="submit" class="button button-secondary" style="color:#b32d2e;border-color:#b32d2e;"
                                onclick="return confirm('Отключить reCAPTCHA? Ключи сохранятся, можно включить обратно.');">
                                Выключить reCAPTCHA
                            </button>
                        </form>
                        <?php endif; ?>
                    </td>
                </tr>
                <tr>
                    <th scope="row"><label for="lp_recaptcha_site_key">Site Key</label></th>
                    <td>
                        <input type="text" id="lp_recaptcha_site_key" name="lp_recaptcha_site_key"
                            value="<?php echo esc_attr($rc_site_key); ?>"
                            class="regular-text"
                            placeholder="6Lc...">
                        <p class="description">Публичный ключ (v3) из Google reCAPTCHA Admin Console.</p>
                    </td>
                </tr>
                <tr>
                    <th scope="row"><label for="lp_recaptcha_secret_key">Secret Key</label></th>
                    <td>
                        <input type="password" id="lp_recaptcha_secret_key" name="lp_recaptcha_secret_key"
                            value=""
                            class="regular-text"
                            placeholder="<?php echo $rc_secret_set ? '••••••••' : 'Вставьте секретный ключ'; ?>"
                            autocomplete="new-password">
                        <p class="description">
                            <?php if ($rc_secret_set): ?>
                                Ключ сохранён (зашифрован). Оставьте поле пустым чтобы не менять.
                            <?php else: ?>
                                Секретный ключ (v3) из Google reCAPTCHA Admin Console. Хранится зашифрованным.
                            <?php endif; ?>
                        </p>
                    </td>
                </tr>
                <tr>
                    <th scope="row"><label for="lp_recaptcha_threshold">Порог score</label></th>
                    <td>
                        <input type="number" id="lp_recaptcha_threshold" name="lp_recaptcha_threshold"
                            value="<?php echo esc_attr(number_format($rc_threshold, 1)); ?>"
                            min="0.0" max="1.0" step="0.1"
                            style="width:80px;">
                        <p class="description">
                            Score &lt; этого значения = заявка отклоняется. Рекомендуется 0.5.<br>
                            0.0 = принимать всё, 1.0 = принимать только явных людей.
                        </p>
                    </td>
                </tr>
            </table>

            <?php submit_button('Сохранить настройки'); ?>
        </form>
    </div>
    <?php
}
