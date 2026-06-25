<?php
namespace LandingConfig\Admin\IntegrationsReadOnly;

if (!defined('ABSPATH')) { exit; }

use function LandingConfig\Integrations\resolve_integration;
use function LandingConfig\Integrations\has_override;
use const LandingConfig\Integrations\VALID_ADAPTERS;

function adapter_class(string $name): string {
    return \LandingConfig\Admin\Integrations\adapter_class($name);
}
function mask(string $v): string {
    return \LandingConfig\Admin\Integrations\mask_secret($v);
}

\add_action('admin_menu', function () {
    if (!\is_multisite()) return;
    \add_submenu_page(
        'landing-config',
        'Интеграции (просмотр)',
        'Интеграции',
        'manage_options',
        'landing-config-integrations',
        __NAMESPACE__ . '\\render_page'
    );
});

function render_page(): void {
    if (!\current_user_can('manage_options')) { \wp_die('No.', 403); }
    $blog_id = \get_current_blog_id();
    $net_url = \network_admin_url('admin.php?page=landing-config-network-integrations&segment=' . $blog_id);
    ?>
    <div class="wrap">
        <h1>Интеграции <span style="font-size:13px; color:#646970; font-weight:400;">— режим просмотра</span></h1>
        <div class="notice notice-info inline">
            <p>Управляются super-admin'ом. <a href="<?php echo \esc_url($net_url); ?>" target="_blank">Открыть редактор</a> →</p>
        </div>

        <?php foreach (VALID_ADAPTERS as $name):
            $r = resolve_integration($name, $blog_id);
            $is_override = has_override($name, $blog_id);
            $source = $is_override ? 'site override' : 'inherited from network';
            $color = $is_override ? '#dba617' : '#2271b1';
            $cls = adapter_class($name);
            $defs = $cls ? $cls::field_definitions() : [];
        ?>
            <div style="background:#fff; border:1px solid #c3c4c7; padding:12px 16px; margin:10px 0; border-radius:4px;">
                <h3 style="margin:0 0 8px;"><code><?php echo \esc_html($name); ?></code>
                    <span style="background:<?php echo \esc_attr($color); ?>; color:#fff; padding:2px 8px; border-radius:3px; font-size:11px;">
                        <?php echo \esc_html($source); ?>
                    </span>
                </h3>
                <?php if (!$r): ?>
                    <p style="color:#646970;"><em>Не настроено.</em></p>
                <?php else: ?>
                    <ul style="margin:0; color:#646970;">
                        <?php foreach ($defs as $field => $meta):
                            $v = (string) ($r['settings'][$field] ?? '');
                            if (!empty($meta['encrypt'])) $v = mask($v);
                        ?>
                            <li><strong><?php echo \esc_html($meta['label']); ?>:</strong> <code><?php echo \esc_html($v ?: '—'); ?></code></li>
                        <?php endforeach; ?>
                    </ul>
                <?php endif; ?>
            </div>
        <?php endforeach; ?>
    </div>
    <?php
}
