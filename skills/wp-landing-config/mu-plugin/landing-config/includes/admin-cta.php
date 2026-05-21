<?php
namespace LandingConfig\Admin\CTA;

if (!defined('ABSPATH')) { exit; }

use function LandingConfig\CTA\list_ctas;
use function LandingConfig\CTA\resolve_cta;
use function LandingConfig\CTA\save_cta;
use function LandingConfig\CTA\delete_cta;
use function LandingConfig\CTA\has_cta_override as has_override;
use const LandingConfig\CTA\PRESET_NAMES;
use const LandingConfig\CTA\VALID_TYPES;
use function LandingConfig\SegmentSelector\render as render_selector;
use function LandingConfig\SegmentSelector\current_from_request;

\add_action('network_admin_menu', function () {
    \add_submenu_page(
        'landing-config-network',
        'CTA-кнопки',
        'CTA-кнопки',
        'manage_network_options',
        'landing-config-network-cta',
        __NAMESPACE__ . '\\dispatch'
    );
});

\add_action('admin_post_landing_cta_save', __NAMESPACE__ . '\\handle_save');
\add_action('admin_post_landing_cta_delete_override', __NAMESPACE__ . '\\handle_delete_override');

function dispatch(): void {
    if (!\current_user_can('manage_network_options')) { \wp_die('Insufficient permissions', 403); }
    $segment = current_from_request();
    render_page($segment);
}

function render_page(int $segment): void {
    $main_id = \function_exists('get_main_site_id') ? \get_main_site_id() : 1;
    $blog_id = $segment === 0 ? $main_id : $segment;
    ?>
    <div class="wrap">
        <h1>CTA-кнопки</h1>
        <p>Настройте 5 пресетов кнопок. Темы обращаются к ним через <code>landing_get_cta('preset_name')</code>.
        Сетевые дефолты применяются ко всем сегментам сети. Сегмент может переопределить пресет — кнопка тогда будет специфична для него.</p>
        <?php render_selector('landing-config-network-cta', $segment); ?>

        <?php
        foreach (PRESET_NAMES as $preset_name):
            $effective = resolve_cta($preset_name, $blog_id);
            $is_inherited = ($segment !== 0) && !has_override($preset_name, $segment);
            $is_override = ($segment !== 0) && has_override($preset_name, $segment);
            $effective = $effective ?: ['type' => 'scroll', 'label' => '', 'target' => '', 'phone' => '',
                'form_id' => '', 'message_template' => '', 'is_network' => true];
        ?>
            <div style="background:#fff; border:1px solid #c3c4c7; padding:16px 20px; margin:16px 0; border-radius:4px;">
                <h2 style="margin-top:0;">
                    <code><?php echo \esc_html($preset_name); ?></code>
                    <?php if ($segment === 0): ?>
                        <span class="dashicons dashicons-admin-network" style="color:#2271b1;" title="Network default"></span>
                    <?php elseif ($is_override): ?>
                        <span style="background:#dba617; color:#fff; padding:2px 8px; border-radius:3px; font-size:11px; font-weight:600; vertical-align:middle;">SITE OVERRIDE</span>
                    <?php else: ?>
                        <span style="background:#2271b1; color:#fff; padding:2px 8px; border-radius:3px; font-size:11px; font-weight:600; vertical-align:middle;">INHERITED</span>
                    <?php endif; ?>
                </h2>

                <?php if ($segment !== 0 && $is_inherited): ?>
                    <p style="color:#646970;">Этот пресет наследуется от сетевого дефолта. Чтобы изменить для этого сегмента — нажмите «Override».</p>
                <?php endif; ?>

                <form method="post" action="<?php echo \esc_url(\network_admin_url('admin-post.php')); ?>">
                    <?php \wp_nonce_field('landing_cta_save_' . $preset_name); ?>
                    <input type="hidden" name="action" value="landing_cta_save">
                    <input type="hidden" name="preset_name" value="<?php echo \esc_attr($preset_name); ?>">
                    <input type="hidden" name="segment" value="<?php echo (int) $segment; ?>">

                    <table class="form-table">
                        <tr><th>Type</th><td>
                            <select name="type" <?php \disabled($is_inherited); ?>>
                                <?php foreach (VALID_TYPES as $t): ?>
                                    <option value="<?php echo $t; ?>" <?php \selected($effective['type'], $t); ?>><?php echo $t; ?></option>
                                <?php endforeach; ?>
                            </select>
                        </td></tr>
                        <tr><th>Label</th><td>
                            <input type="text" name="label" value="<?php echo \esc_attr($effective['label']); ?>" class="regular-text" <?php \disabled($is_inherited); ?>>
                        </td></tr>
                        <tr><th>Target / URL</th><td>
                            <input type="text" name="target" value="<?php echo \esc_attr($effective['target']); ?>" class="regular-text" <?php \disabled($is_inherited); ?>>
                        </td></tr>
                        <tr><th>Phone</th><td>
                            <input type="text" name="phone" value="<?php echo \esc_attr($effective['phone']); ?>" placeholder="+71234567890" <?php \disabled($is_inherited); ?>>
                        </td></tr>
                        <tr><th>Form ID</th><td>
                            <input type="text" name="form_id" value="<?php echo \esc_attr($effective['form_id']); ?>" placeholder="main" <?php \disabled($is_inherited); ?>>
                        </td></tr>
                        <tr><th>Message template</th><td>
                            <input type="text" name="message_template" value="<?php echo \esc_attr($effective['message_template']); ?>" class="large-text" <?php \disabled($is_inherited); ?>>
                        </td></tr>
                    </table>

                    <p>
                        <?php if ($segment === 0 || $is_override): ?>
                            <button type="submit" class="button button-primary">Сохранить</button>
                        <?php else: // inherited ?>
                            <button type="submit" class="button button-primary" name="override_action" value="enable">Override для этого сегмента</button>
                        <?php endif; ?>

                        <?php if ($is_override): ?>
                            <a href="<?php echo \esc_url(\wp_nonce_url(
                                \network_admin_url('admin-post.php?action=landing_cta_delete_override&preset_name=' . $preset_name . '&segment=' . $segment),
                                'landing_cta_delete_override_' . $preset_name
                            )); ?>" class="button" style="margin-left:1em;" onclick="return confirm('Удалить override и вернуться к сетевому дефолту?');">Удалить override</a>
                        <?php endif; ?>
                    </p>
                </form>
            </div>
        <?php endforeach; ?>
    </div>
    <?php
}

function handle_save(): void {
    if (!\current_user_can('manage_network_options')) { \wp_die('No.', 403); }
    $preset = \sanitize_text_field($_POST['preset_name'] ?? '');
    if (!in_array($preset, PRESET_NAMES, true)) \wp_die('Invalid preset', 400);
    \check_admin_referer('landing_cta_save_' . $preset);

    $segment = isset($_POST['segment']) ? (int) $_POST['segment'] : 0;
    $is_network = ($segment === 0);
    $main_id = \function_exists('get_main_site_id') ? \get_main_site_id() : 1;
    $blog_id = $is_network ? $main_id : $segment;

    // Delete existing record(s) for this preset on this blog_id+is_network combo,
    // then re-insert (idempotent overwrite — avoids needing a discrete update path).
    foreach (list_ctas($blog_id) as $r) {
        if ($r['preset_name'] === $preset && $r['is_network'] === $is_network) {
            delete_cta($r['id']);
        }
    }

    save_cta([
        'preset_name'      => $preset,
        'type'             => $_POST['type'] ?? 'scroll',
        'label'            => $_POST['label'] ?? '',
        'target'           => $_POST['target'] ?? '',
        'phone'            => $_POST['phone'] ?? '',
        'form_id'          => $_POST['form_id'] ?? '',
        'message_template' => $_POST['message_template'] ?? '',
    ], $is_network, $blog_id);

    \wp_safe_redirect(\network_admin_url('admin.php?page=landing-config-network-cta&segment=' . $segment . '&saved=1'));
    exit;
}

function handle_delete_override(): void {
    if (!\current_user_can('manage_network_options')) { \wp_die('No.', 403); }
    $preset = \sanitize_text_field($_GET['preset_name'] ?? '');
    $segment = (int) ($_GET['segment'] ?? 0);
    if (!in_array($preset, PRESET_NAMES, true) || $segment === 0) \wp_die('Invalid', 400);
    \check_admin_referer('landing_cta_delete_override_' . $preset);

    foreach (list_ctas($segment) as $r) {
        if ($r['preset_name'] === $preset && $r['is_network'] === false) {
            delete_cta($r['id']);
        }
    }
    \wp_safe_redirect(\network_admin_url('admin.php?page=landing-config-network-cta&segment=' . $segment . '&deleted=1'));
    exit;
}
