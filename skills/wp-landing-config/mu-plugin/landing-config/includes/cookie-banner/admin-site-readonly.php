<?php
namespace LandingConfig\CookieBanner\AdminReadOnly;

if (!defined('ABSPATH')) { exit; }

use function LandingConfig\CookieBanner\Resolver\resolve_for_blog;

const MENU_SLUG = 'landing-config-site-cookie-banner';

add_action('admin_menu', __NAMESPACE__ . '\\register_menu');

function register_menu(): void {
    \add_submenu_page(
        'landing-config',
        'Cookie-banner (read-only)',
        'Cookie-banner',
        'manage_options',
        MENU_SLUG,
        __NAMESPACE__ . '\\render_page'
    );
}

function render_page(): void {
    if (!\current_user_can('manage_options')) wp_die('forbidden');
    $blog_id = \get_current_blog_id();
    $resolved = resolve_for_blog($blog_id);

    $network_url = \network_admin_url('admin.php?page=landing-config-network-cookie-banner&segment=' . $blog_id);

    ?>
    <div class="wrap">
        <h1>Cookie-banner (resolved for this site)</h1>
        <p>Это режим только для чтения. Чтобы изменить настройки — открой
            <a href="<?php echo esc_url($network_url); ?>">Network admin → Cookie-banner для этого сегмента</a>.</p>

        <table class="widefat">
            <thead><tr><th>Поле</th><th>Значение</th></tr></thead>
            <tbody>
                <?php foreach ($resolved as $field => $val): ?>
                    <tr>
                        <td><code><?php echo esc_html($field); ?></code></td>
                        <td>
                            <?php if (is_array($val)): ?>
                                <pre><?php echo esc_html(wp_json_encode($val, JSON_PRETTY_PRINT | JSON_UNESCAPED_UNICODE)); ?></pre>
                            <?php else: ?>
                                <code><?php echo esc_html((string) $val); ?></code>
                            <?php endif; ?>
                        </td>
                    </tr>
                <?php endforeach; ?>
            </tbody>
        </table>
    </div>
    <?php
}
