<?php
namespace LandingConfig\Admin\Snippets\ReadOnly;

if (!defined('ABSPATH')) { exit; }

use function LandingConfig\Snippets\list_site_snippets;
use function LandingConfig\Snippets\list_network_snippets;

\add_action('admin_menu', function () {
    \add_submenu_page(
        'landing-config',
        'Снипеты (просмотр)',
        'Снипеты',
        'manage_options',
        'landing-config-snippets',
        __NAMESPACE__ . '\\render_page'
    );
});

function render_page(): void {
    if (!\current_user_can('manage_options')) { \wp_die('No.', 403); }
    $blog_id = \get_current_blog_id();
    $net_url = \network_admin_url('admin.php?page=landing-config-network-snippets&segment=' . $blog_id);

    $site_snippets    = list_site_snippets();
    $network_snippets = list_network_snippets();

    // Index site snippets by name to detect overrides.
    $site_names = [];
    foreach ($site_snippets as $s) {
        if (!empty($s['name'])) $site_names[$s['name']] = true;
    }
    ?>
    <div class="wrap">
        <h1>Снипеты <span style="font-size:13px; color:#646970; font-weight:400;">— режим просмотра</span></h1>
        <div class="notice notice-info inline">
            <p>Настройки снипетов управляются super-admin'ом из network admin.
            <a href="<?php echo \esc_url($net_url); ?>" target="_blank">Открыть редактор</a> →</p>
        </div>

        <h2 style="margin-top:24px;">Site snippets (этот сегмент)</h2>
        <?php if (!$site_snippets): ?>
            <p style="color:#646970;"><em>Нет site-specific снипетов.</em></p>
        <?php else: ?>
            <table class="wp-list-table widefat striped">
                <thead><tr><th>Title</th><th>Name</th><th>Position</th><th>Enabled</th></tr></thead>
                <tbody>
                    <?php foreach ($site_snippets as $s): ?>
                        <tr>
                            <td><?php echo \esc_html($s['title'] ?? ''); ?></td>
                            <td><code><?php echo \esc_html($s['name'] ?? ''); ?></code></td>
                            <td><?php echo \esc_html($s['position'] ?? ''); ?></td>
                            <td><?php echo !empty($s['enabled']) ? '✅' : '⛔'; ?></td>
                        </tr>
                    <?php endforeach; ?>
                </tbody>
            </table>
        <?php endif; ?>

        <h2 style="margin-top:24px;">Network snippets (применяются ко всем сегментам)</h2>
        <?php if (!$network_snippets): ?>
            <p style="color:#646970;"><em>Нет network снипетов.</em></p>
        <?php else: ?>
            <table class="wp-list-table widefat striped">
                <thead><tr><th>Title</th><th>Name</th><th>Position</th><th>Enabled</th><th>Источник для этого сегмента</th></tr></thead>
                <tbody>
                    <?php foreach ($network_snippets as $s):
                        $name = $s['name'] ?? '';
                        $is_overridden = $name !== '' && isset($site_names[$name]);
                        $source = $is_overridden ? 'overridden by site' : 'inherited from network';
                        $color  = $is_overridden ? '#dba617' : '#2271b1';
                    ?>
                        <tr>
                            <td><?php echo \esc_html($s['title'] ?? ''); ?></td>
                            <td><code><?php echo \esc_html($name); ?></code></td>
                            <td><?php echo \esc_html($s['position'] ?? ''); ?></td>
                            <td><?php echo !empty($s['enabled']) ? '✅' : '⛔'; ?></td>
                            <td><span style="background:<?php echo \esc_attr($color); ?>; color:#fff; padding:2px 8px; border-radius:3px; font-size:11px;"><?php echo \esc_html($source); ?></span></td>
                        </tr>
                    <?php endforeach; ?>
                </tbody>
            </table>
        <?php endif; ?>
    </div>
    <?php
}
