<?php
namespace LandingConfig\Admin\CTAReadOnly;

if (!defined('ABSPATH')) { exit; }

use function LandingConfig\CTA\resolve_cta;
use function LandingConfig\CTA\has_cta_override as has_override;
use const LandingConfig\CTA\PRESET_NAMES;

\add_action('admin_menu', function () {
    if (!\is_multisite()) return;
    \add_submenu_page(
        'landing-config',
        'CTA-кнопки (просмотр)',
        'CTA-кнопки',
        'manage_options',
        'landing-config-cta',
        __NAMESPACE__ . '\\render_page'
    );
});

function render_page(): void {
    if (!\current_user_can('manage_options')) { \wp_die('No.', 403); }
    $blog_id = \get_current_blog_id();
    $net_url = \network_admin_url('admin.php?page=landing-config-network-cta&segment=' . $blog_id);
    ?>
    <div class="wrap">
        <h1>CTA-кнопки <span style="font-size:13px; color:#646970; font-weight:400;">— режим просмотра</span></h1>
        <div class="notice notice-info inline">
            <p>Настройки CTA управляются super-admin'ом из network admin.
            <a href="<?php echo \esc_url($net_url); ?>" target="_blank">Открыть редактор</a> →</p>
        </div>

        <table class="wp-list-table widefat striped" style="margin-top:16px;">
            <thead>
                <tr>
                    <th>Preset</th><th>Type</th><th>Label</th><th>Target</th><th>Источник</th>
                </tr>
            </thead>
            <tbody>
                <?php foreach (PRESET_NAMES as $preset_name):
                    $r = resolve_cta($preset_name, $blog_id);
                    $is_override = has_override($preset_name, $blog_id);
                    $source = $is_override ? 'site override' : 'inherited from network';
                    $source_color = $is_override ? '#dba617' : '#2271b1';
                    $target = $r['target'] ?? '';
                    if ($target === '') { $target = $r['phone'] ?? ''; }
                    if ($target === '') { $target = '—'; }
                ?>
                    <tr>
                        <td><code><?php echo \esc_html($preset_name); ?></code></td>
                        <td><?php echo \esc_html($r['type'] ?? '—'); ?></td>
                        <td><?php echo \esc_html($r['label'] ?? '—'); ?></td>
                        <td><?php echo \esc_html($target); ?></td>
                        <td><span style="background:<?php echo \esc_attr($source_color); ?>; color:#fff; padding:2px 8px; border-radius:3px; font-size:11px;"><?php echo \esc_html($source); ?></span></td>
                    </tr>
                <?php endforeach; ?>
            </tbody>
        </table>
    </div>
    <?php
}
