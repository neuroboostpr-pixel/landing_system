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

    $saved = false;
    if (isset($_POST['lp_general_nonce']) && wp_verify_nonce($_POST['lp_general_nonce'], 'lp_general_settings')) {
        $rate_limit = max(1, (int) ($_POST['lp_rate_limit'] ?? 10));
        update_option('lp_rate_limit_per_hour', $rate_limit);
        $saved = true;
    }

    $rate_limit = (int) get_option('lp_rate_limit_per_hour', defined('LP_RATE_LIMIT_PER_HOUR') ? LP_RATE_LIMIT_PER_HOUR : 10);
    $wp_config_override = defined('LP_RATE_LIMIT_PER_HOUR');
    ?>
    <div class="wrap">
        <h1>Лендинг — Общие настройки</h1>

        <?php if ($saved): ?>
            <div class="notice notice-success is-dismissible"><p>Настройки сохранены.</p></div>
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
                            <?php echo $wp_config_override ? 'disabled' : ''; ?>
                        >
                        <p class="description">
                            <?php if ($wp_config_override): ?>
                                <strong>Значение задано в wp-config.php (<code>LP_RATE_LIMIT_PER_HOUR = <?php echo (int) LP_RATE_LIMIT_PER_HOUR; ?></code>) и переопределяет настройку здесь.</strong>
                                Удалите константу из wp-config.php, чтобы управлять лимитом отсюда.
                            <?php else: ?>
                                Количество заявок с одного IP-адреса за час. Для тестирования: 100+, для прода: 10–50.
                            <?php endif; ?>
                        </p>
                    </td>
                </tr>
            </table>

            <?php if (!$wp_config_override): ?>
                <?php submit_button('Сохранить настройки'); ?>
            <?php endif; ?>
        </form>
    </div>
    <?php
}
