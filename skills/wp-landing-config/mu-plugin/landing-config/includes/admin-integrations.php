<?php
namespace LandingConfig\Admin\Integrations;

if (!defined('ABSPATH')) { exit; }

use function LandingConfig\Integrations\list_integrations;
use function LandingConfig\Integrations\resolve_integration;
use function LandingConfig\Integrations\save_integration;
use function LandingConfig\Integrations\delete_integration;
use function LandingConfig\Integrations\has_override;
use const LandingConfig\Integrations\VALID_ADAPTERS;
use function LandingConfig\SegmentSelector\render as render_selector;
use function LandingConfig\SegmentSelector\current_from_request;
use function LandingConfig\AdminMode\cap;
use function LandingConfig\AdminMode\admin_url_for;
use function LandingConfig\AdminMode\menu_hook;
use function LandingConfig\AdminMode\parent_slug;
use function LandingConfig\AdminMode\page_slug;

function adapter_class(string $name): string {
    $map = [
        'email'    => '\\LandingConfig\\Adapters\\EmailAdapter',
        'telegram' => '\\LandingConfig\\Adapters\\TelegramAdapter',
        'whatsapp' => '\\LandingConfig\\Adapters\\WhatsAppAdapter',
        'amocrm'   => '\\LandingConfig\\Adapters\\AmoCRMAdapter',
        'bitrix24' => '\\LandingConfig\\Adapters\\Bitrix24Adapter',
        'hubspot'  => '\\LandingConfig\\Adapters\\HubSpotAdapter',
    ];
    return $map[$name] ?? '';
}

function mask_secret(string $val): string {
    if ($val === '') return '— не задано —';
    if (strlen($val) <= 4) return '••••';
    return str_repeat('•', max(0, strlen($val) - 4)) . substr($val, -4);
}

\add_action(menu_hook(), function () {
    \add_submenu_page(
        parent_slug(),
        'Интеграции',
        'Интеграции',
        cap(),
        page_slug('integrations'),
        __NAMESPACE__ . '\\dispatch'
    );
});

\add_action('admin_post_landing_int_save', __NAMESPACE__ . '\\handle_save');
\add_action('admin_post_landing_int_toggle_override', __NAMESPACE__ . '\\handle_toggle_override');

function dispatch(): void {
    if (!\current_user_can(cap())) { \wp_die('No.', 403); }
    $segment = current_from_request();
    render_page($segment);
}

function render_page(int $segment): void {
    $main_id = \function_exists('get_main_site_id') ? \get_main_site_id() : 1;
    $blog_id = $segment === 0 ? $main_id : $segment;
    ?>
    <div class="wrap">
        <h1>Интеграции</h1>
        <p>Подключите CRM/мессенджеры для отправки заявок. Сетевые настройки применяются ко всем сегментам;
        сегмент может переопределить любой адаптер на свой аккаунт.</p>
        <?php render_selector('landing-config-network-integrations', $segment); ?>

        <?php foreach (VALID_ADAPTERS as $adapter_name):
            $cls = adapter_class($adapter_name);
            $defs = $cls ? $cls::field_definitions() : [];
            $effective = resolve_integration($adapter_name, $blog_id);
            $is_inherited = ($segment !== 0) && !has_override($adapter_name, $segment);
            $is_override  = ($segment !== 0) && has_override($adapter_name, $segment);
            $current_settings = $effective ? $effective['settings'] : array_fill_keys(array_keys($defs), '');
        ?>
            <div style="background:#fff; border:1px solid #c3c4c7; padding:16px 20px; margin:16px 0; border-radius:4px;">
                <h2 style="margin-top:0; display:flex; align-items:center; gap:.6em;">
                    <code><?php echo \esc_html($adapter_name); ?></code>
                    <?php if ($segment === 0): ?>
                        <span class="dashicons dashicons-admin-network" style="color:#2271b1;"></span>
                    <?php elseif ($is_override): ?>
                        <span style="background:#dba617; color:#fff; padding:2px 8px; border-radius:3px; font-size:11px; font-weight:600;">SITE OVERRIDE</span>
                    <?php else: ?>
                        <span style="background:#2271b1; color:#fff; padding:2px 8px; border-radius:3px; font-size:11px; font-weight:600;">INHERITED</span>
                    <?php endif; ?>
                </h2>

                <?php if ($segment !== 0): ?>
                    <form method="post" action="<?php echo \esc_url(admin_url_for('admin-post.php')); ?>" style="margin-bottom:12px;">
                        <?php \wp_nonce_field('landing_int_toggle_override_' . $adapter_name); ?>
                        <input type="hidden" name="action" value="landing_int_toggle_override">
                        <input type="hidden" name="adapter_name" value="<?php echo \esc_attr($adapter_name); ?>">
                        <input type="hidden" name="segment" value="<?php echo (int) $segment; ?>">
                        <label style="font-weight:600;">
                            <input type="checkbox" name="override_enabled" value="1" <?php \checked($is_override); ?>
                                onchange="this.form.submit();">
                            Использовать свой <?php echo \esc_html($adapter_name); ?> для этого сегмента
                        </label>
                    </form>
                <?php endif; ?>

                <?php if ($segment !== 0 && $is_inherited): ?>
                    <div style="background:#f6f7f7; padding:12px; border-radius:4px;">
                        <p style="margin:0 0 8px;"><strong>Унаследовано от сети.</strong> Заявки этого сегмента уходят в:</p>
                        <ul style="margin:0; color:#646970;">
                            <?php foreach ($defs as $field => $meta):
                                $val = $current_settings[$field] ?? '';
                                if (!empty($meta['encrypt'])) $val = mask_secret((string) $val);
                            ?>
                                <li><strong><?php echo \esc_html($meta['label']); ?>:</strong> <code><?php echo \esc_html((string) $val); ?></code></li>
                            <?php endforeach; ?>
                        </ul>
                    </div>
                <?php else: ?>
                    <form method="post" action="<?php echo \esc_url(admin_url_for('admin-post.php')); ?>">
                        <?php \wp_nonce_field('landing_int_save_' . $adapter_name); ?>
                        <input type="hidden" name="action" value="landing_int_save">
                        <input type="hidden" name="adapter_name" value="<?php echo \esc_attr($adapter_name); ?>">
                        <input type="hidden" name="segment" value="<?php echo (int) $segment; ?>">
                        <table class="form-table">
                            <?php foreach ($defs as $field => $meta):
                                $val = $current_settings[$field] ?? '';
                                $input_type = $meta['type'] ?? 'text';
                                if (!empty($meta['encrypt']) && $val !== '') {
                                    $placeholder = '(сохранено: ' . mask_secret((string) $val) . ' — оставьте пустым чтобы не менять)';
                                    $val_for_form = '';
                                } else {
                                    $placeholder = $meta['placeholder'] ?? '';
                                    $val_for_form = $val;
                                }
                            ?>
                                <tr>
                                    <th><?php echo \esc_html($meta['label']); ?></th>
                                    <td>
                                        <input type="<?php echo \esc_attr($input_type); ?>"
                                               name="field[<?php echo \esc_attr($field); ?>]"
                                               value="<?php echo \esc_attr((string) $val_for_form); ?>"
                                               placeholder="<?php echo \esc_attr($placeholder); ?>"
                                               class="regular-text"
                                               <?php if (!empty($meta['required']) && $val === '') echo 'required'; ?>>
                                    </td>
                                </tr>
                            <?php endforeach; ?>
                        </table>
                        <p><button type="submit" class="button button-primary">Сохранить</button></p>
                    </form>
                <?php endif; ?>
            </div>
        <?php endforeach; ?>
    </div>
    <?php
}

function handle_save(): void {
    if (!\current_user_can(cap())) { \wp_die('No.', 403); }
    $adapter_name = \sanitize_text_field($_POST['adapter_name'] ?? '');
    if (!in_array($adapter_name, VALID_ADAPTERS, true)) \wp_die('Invalid', 400);
    \check_admin_referer('landing_int_save_' . $adapter_name);

    $segment = (int) ($_POST['segment'] ?? 0);
    $is_network = ($segment === 0);
    $main_id = \function_exists('get_main_site_id') ? \get_main_site_id() : 1;
    $blog_id = $is_network ? $main_id : $segment;

    $cls = adapter_class($adapter_name);
    $defs = $cls::field_definitions();
    $encrypted_fields = [];
    foreach ($defs as $f => $meta) if (!empty($meta['encrypt'])) $encrypted_fields[] = $f;

    $existing = resolve_integration($adapter_name, $blog_id);
    $existing_settings = $existing ? $existing['settings'] : [];

    $new_settings = [];
    foreach ($defs as $field => $meta) {
        $input = (string) ($_POST['field'][$field] ?? '');
        if (!empty($meta['encrypt']) && $input === '' && isset($existing_settings[$field])) {
            $new_settings[$field] = $existing_settings[$field];
        } else {
            $new_settings[$field] = \sanitize_text_field($input);
        }
    }

    foreach (list_integrations($blog_id) as $r) {
        if ($r['adapter_name'] === $adapter_name && $r['is_network'] === $is_network) {
            delete_integration($r['id']);
        }
    }
    save_integration($adapter_name, $new_settings, $is_network, $blog_id, $encrypted_fields, true);

    \wp_safe_redirect(admin_url_for('admin.php?page=landing-config-network-integrations&segment=' . $segment . '&saved=1'));
    exit;
}

function handle_toggle_override(): void {
    if (!\current_user_can(cap())) { \wp_die('No.', 403); }
    $adapter_name = \sanitize_text_field($_POST['adapter_name'] ?? '');
    if (!in_array($adapter_name, VALID_ADAPTERS, true)) \wp_die('Invalid', 400);
    \check_admin_referer('landing_int_toggle_override_' . $adapter_name);

    $segment = (int) ($_POST['segment'] ?? 0);
    if ($segment === 0) \wp_die('Cannot toggle override on network level', 400);
    $enable = !empty($_POST['override_enabled']);

    if (!$enable) {
        foreach (list_integrations($segment) as $r) {
            if ($r['adapter_name'] === $adapter_name && $r['is_network'] === false) {
                delete_integration($r['id']);
            }
        }
    } else {
        $main_id = \function_exists('get_main_site_id') ? \get_main_site_id() : 1;
        $net = resolve_integration($adapter_name, $main_id);
        $settings = $net ? $net['settings'] : [];
        $cls = adapter_class($adapter_name);
        $encrypted_fields = [];
        foreach ($cls::field_definitions() as $f => $m) if (!empty($m['encrypt'])) $encrypted_fields[] = $f;
        save_integration($adapter_name, $settings, false, $segment, $encrypted_fields, true);
    }
    \wp_safe_redirect(admin_url_for('admin.php?page=landing-config-network-integrations&segment=' . $segment));
    exit;
}
