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

    $from_db = get_option('lp_rate_limit_per_hour', false);
    $wp_config_val = defined('LP_RATE_LIMIT_PER_HOUR') ? (int) LP_RATE_LIMIT_PER_HOUR : null;
    // Effective: DB value wins over wp-config constant
    $rate_limit = $from_db !== false ? (int) $from_db : ($wp_config_val ?? 10);
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

            <?php submit_button('Сохранить настройки'); ?>
        </form>
    </div>
    <?php
}
