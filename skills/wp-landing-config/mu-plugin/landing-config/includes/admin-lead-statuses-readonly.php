<?php
namespace LandingConfig\Admin\LeadStatusesReadOnly;

if (!defined('ABSPATH')) { exit; }

use function LandingConfig\LeadStatuses\list_lead_statuses;

\add_action('admin_menu', function () {
    \add_submenu_page(
        'landing-config',
        'Статусы заявок (просмотр)',
        'Статусы заявок',
        'manage_options',
        'landing-config-lead-statuses',
        __NAMESPACE__ . '\\render_page'
    );
});

function render_page(): void {
    if (!\current_user_can('manage_options')) { \wp_die('No.', 403); }
    $blog_id = \get_current_blog_id();
    $net_url = \network_admin_url('admin.php?page=landing-config-network-lead-statuses&segment=' . $blog_id);
    $list = list_lead_statuses($blog_id);
    ?>
    <div class="wrap">
        <h1>Статусы заявок <span style="font-size:13px; color:#646970; font-weight:400;">— режим просмотра</span></h1>
        <div class="notice notice-info inline">
            <p>Словарь управляется super-admin'ом из network admin.
            <a href="<?php echo \esc_url($net_url); ?>" target="_blank">Открыть редактор</a> →</p>
        </div>

        <table class="wp-list-table widefat striped" style="margin-top:16px;">
            <thead>
                <tr><th style="width:60px;">Цвет</th><th>Slug</th><th>Label</th><th style="width:80px;">Order</th><th style="width:180px;">Источник</th></tr>
            </thead>
            <tbody>
                <?php if (empty($list)): ?>
                    <tr><td colspan="5"><em>Нет статусов. Попроси super-admin'а добавить.</em></td></tr>
                <?php else: foreach ($list as $s):
                    $is_override = !$s['is_network'];
                    $source = $is_override ? 'site override' : 'inherited from network';
                    $color = $is_override ? '#dba617' : '#2271b1';
                ?>
                    <tr>
                        <td><span style="display:inline-block; width:24px; height:24px; background:<?php echo \esc_attr($s['color']); ?>; border-radius:3px; border:1px solid #c3c4c7;"></span></td>
                        <td><code><?php echo \esc_html($s['slug']); ?></code></td>
                        <td><?php echo \esc_html($s['label']); ?></td>
                        <td><?php echo (int) $s['order']; ?></td>
                        <td><span style="background:<?php echo \esc_attr($color); ?>; color:#fff; padding:2px 8px; border-radius:3px; font-size:11px;"><?php echo \esc_html($source); ?></span></td>
                    </tr>
                <?php endforeach; endif; ?>
            </tbody>
        </table>
    </div>
    <?php
}
