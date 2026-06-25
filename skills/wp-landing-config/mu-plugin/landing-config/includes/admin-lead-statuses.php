<?php
namespace LandingConfig\Admin\LeadStatuses;

if (!defined('ABSPATH')) { exit; }

use function LandingConfig\LeadStatuses\list_lead_statuses;
use function LandingConfig\LeadStatuses\save_lead_status;
use function LandingConfig\LeadStatuses\delete_lead_status;
use function LandingConfig\LeadStatuses\has_override;
use function LandingConfig\SegmentSelector\render as render_selector;
use function LandingConfig\SegmentSelector\current_from_request;
use function LandingConfig\AdminMode\cap;
use function LandingConfig\AdminMode\admin_url_for;
use function LandingConfig\AdminMode\menu_hook;
use function LandingConfig\AdminMode\parent_slug;
use function LandingConfig\AdminMode\page_slug;

\add_action(menu_hook(), function () {
    \add_submenu_page(
        parent_slug(),
        'Статусы заявок',
        'Статусы заявок',
        cap(),
        page_slug('lead-statuses'),
        __NAMESPACE__ . '\\dispatch'
    );
});

\add_action('admin_post_landing_lead_status_save', __NAMESPACE__ . '\\handle_save');
\add_action('admin_post_landing_lead_status_delete', __NAMESPACE__ . '\\handle_delete');
\add_action('admin_post_landing_lead_status_delete_override', __NAMESPACE__ . '\\handle_delete_override');

function dispatch(): void {
    if (!\current_user_can(cap())) { \wp_die('Insufficient permissions', 403); }
    $segment = current_from_request();
    render_page($segment);
}

function render_page(int $segment): void {
    $main_id = \function_exists('get_main_site_id') ? \get_main_site_id() : 1;
    $blog_id = $segment === 0 ? $main_id : $segment;
    $list = list_lead_statuses($blog_id);
    ?>
    <div class="wrap">
        <?php if (isset($_GET['saved'])): ?>
            <div class="notice notice-success is-dismissible"><p>Статус сохранён.</p></div>
        <?php elseif (isset($_GET['deleted'])): ?>
            <div class="notice notice-success is-dismissible"><p>Статус удалён.</p></div>
        <?php endif; ?>
        <h1>Статусы заявок</h1>
        <p>Словарь статусов для админки «Заявки». Сетевые статусы видны на всех сегментах;
        сегмент может переопределить статус по slug или добавить свой.</p>
        <?php render_selector('landing-config-network-lead-statuses', $segment); ?>

        <h2>Текущие статусы (отсортированы по order)</h2>
        <table class="wp-list-table widefat striped">
            <thead>
                <tr>
                    <th style="width:60px;">Цвет</th>
                    <th>Slug</th>
                    <th>Label</th>
                    <th style="width:80px;">Order</th>
                    <th style="width:120px;">Источник</th>
                    <th style="width:180px;">Действия</th>
                </tr>
            </thead>
            <tbody>
                <?php if (empty($list)): ?>
                    <tr><td colspan="6"><em>Нет статусов. Добавьте первый ниже.</em></td></tr>
                <?php else: foreach ($list as $s):
                    $is_site_row = !$s['is_network'];
                    $can_override = ($segment !== 0) && $s['is_network'] && !has_override($s['slug'], $segment);
                ?>
                    <tr>
                        <td><span style="display:inline-block; width:24px; height:24px; background:<?php echo \esc_attr($s['color']); ?>; border-radius:3px; border:1px solid #c3c4c7;"></span></td>
                        <td><code><?php echo \esc_html($s['slug']); ?></code></td>
                        <td><?php echo \esc_html($s['label']); ?></td>
                        <td><?php echo (int) $s['order']; ?></td>
                        <td>
                            <?php if ($s['is_network'] && $segment === 0): ?>
                                <span style="background:#2271b1; color:#fff; padding:2px 8px; border-radius:3px; font-size:11px;">NETWORK</span>
                            <?php elseif ($s['is_network'] && $segment !== 0): ?>
                                <span style="background:#2271b1; color:#fff; padding:2px 8px; border-radius:3px; font-size:11px;">INHERITED</span>
                            <?php else: ?>
                                <span style="background:#dba617; color:#fff; padding:2px 8px; border-radius:3px; font-size:11px;">SITE OVERRIDE</span>
                            <?php endif; ?>
                        </td>
                        <td>
                            <?php if (($segment === 0 && $s['is_network']) || ($segment !== 0 && $is_site_row)): ?>
                                <a href="#edit-<?php echo (int) $s['id']; ?>" class="button button-small" onclick="document.getElementById('edit-form-<?php echo (int) $s['id']; ?>').style.display='block'; return false;">Изменить</a>
                                <a href="<?php echo \esc_url(\wp_nonce_url(
                                    admin_url_for('admin-post.php?action=landing_lead_status_delete&id=' . $s['id'] . '&segment=' . $segment),
                                    'landing_lead_status_delete_' . $s['id']
                                )); ?>" class="button button-small" onclick="return confirm('Удалить статус? Существующие заявки сохранят значение slug, но потеряют label/color.');">Удалить</a>
                            <?php elseif ($can_override): ?>
                                <a href="#override-<?php echo \esc_attr($s['slug']); ?>" class="button button-small" onclick="document.getElementById('override-form-<?php echo \esc_attr($s['slug']); ?>').style.display='block'; return false;">Override</a>
                            <?php endif; ?>
                        </td>
                    </tr>
                    <?php if (($segment === 0 && $s['is_network']) || ($segment !== 0 && $is_site_row)): ?>
                        <tr id="edit-form-<?php echo (int) $s['id']; ?>" style="display:none; background:#f6f7f7;">
                            <td colspan="6">
                                <?php render_edit_form($s, $segment); ?>
                            </td>
                        </tr>
                    <?php elseif ($can_override): ?>
                        <tr id="override-form-<?php echo \esc_attr($s['slug']); ?>" style="display:none; background:#fff8e5;">
                            <td colspan="6">
                                <p><strong>Создать site override для slug «<?php echo \esc_html($s['slug']); ?>».</strong> Изменения применятся только к этому сегменту.</p>
                                <?php render_edit_form(['id' => 0, 'slug' => $s['slug'], 'label' => $s['label'], 'color' => $s['color'], 'order' => $s['order']], $segment); ?>
                            </td>
                        </tr>
                    <?php endif; ?>
                <?php endforeach; endif; ?>
            </tbody>
        </table>

        <h2 style="margin-top:32px;">Добавить новый статус</h2>
        <?php render_edit_form(['id' => 0, 'slug' => '', 'label' => '', 'color' => '#2271b1', 'order' => 10], $segment); ?>
    </div>
    <?php
}

function render_edit_form(array $s, int $segment): void {
    ?>
    <form method="post" action="<?php echo \esc_url(admin_url_for('admin-post.php')); ?>" style="background:#fff; padding:12px; border-radius:4px; border:1px solid #c3c4c7;">
        <?php \wp_nonce_field('landing_lead_status_save'); ?>
        <input type="hidden" name="action" value="landing_lead_status_save">
        <input type="hidden" name="id" value="<?php echo (int) $s['id']; ?>">
        <input type="hidden" name="segment" value="<?php echo (int) $segment; ?>">
        <table class="form-table">
            <tr><th>Slug</th><td><input type="text" name="slug" value="<?php echo \esc_attr($s['slug']); ?>" pattern="[a-z0-9_-]+" required class="regular-text"> <span class="description">a-z, 0-9, _, -. Например: <code>contacted</code>.</span></td></tr>
            <tr><th>Label</th><td><input type="text" name="label" value="<?php echo \esc_attr($s['label']); ?>" required class="regular-text"> <span class="description">Отображаемое название.</span></td></tr>
            <tr><th>Color</th><td><input type="color" name="color" value="<?php echo \esc_attr($s['color']); ?>"></td></tr>
            <tr><th>Order</th><td><input type="number" name="order" value="<?php echo (int) $s['order']; ?>" min="0" step="10" class="small-text"> <span class="description">Меньше = выше в списке.</span></td></tr>
        </table>
        <p><button type="submit" class="button button-primary">Сохранить</button></p>
    </form>
    <?php
}

function handle_save(): void {
    if (!\current_user_can(cap())) { \wp_die('No.', 403); }
    \check_admin_referer('landing_lead_status_save');

    $segment = (int) ($_POST['segment'] ?? 0);
    $is_network = ($segment === 0);
    $main_id = \function_exists('get_main_site_id') ? \get_main_site_id() : 1;
    $blog_id = $is_network ? $main_id : $segment;

    $id = save_lead_status([
        'slug'  => \sanitize_key($_POST['slug'] ?? ''),
        'label' => \sanitize_text_field($_POST['label'] ?? ''),
        'color' => (string) ($_POST['color'] ?? '#2271b1'),
        'order' => (int) ($_POST['order'] ?? 10),
    ], $is_network, $blog_id, (int) ($_POST['id'] ?? 0));

    if ($id === 0) {
        \wp_die('Не удалось сохранить статус. Проверь slug (a-z, 0-9, _, -).', 400);
    }

    \wp_safe_redirect(admin_url_for('admin.php?page=landing-config-network-lead-statuses&segment=' . $segment . '&saved=1'));
    exit;
}

function handle_delete(): void {
    if (!\current_user_can(cap())) { \wp_die('No.', 403); }
    $id = (int) ($_GET['id'] ?? 0);
    if ($id <= 0) \wp_die('Invalid id', 400);
    \check_admin_referer('landing_lead_status_delete_' . $id);

    $segment = (int) ($_GET['segment'] ?? 0);
    delete_lead_status($id);

    \wp_safe_redirect(admin_url_for('admin.php?page=landing-config-network-lead-statuses&segment=' . $segment . '&deleted=1'));
    exit;
}

function handle_delete_override(): void {
    if (!\current_user_can(cap())) { \wp_die('No.', 403); }
    \check_admin_referer('landing_lead_status_delete_override');

    $slug = \sanitize_key($_GET['slug'] ?? '');
    $segment = (int) ($_GET['segment'] ?? 0);
    if ($slug === '' || $segment === 0) \wp_die('Invalid', 400);

    foreach (list_lead_statuses($segment) as $s) {
        if ($s['slug'] === $slug && !$s['is_network']) {
            delete_lead_status($s['id']);
        }
    }
    \wp_safe_redirect(admin_url_for('admin.php?page=landing-config-network-lead-statuses&segment=' . $segment));
    exit;
}
