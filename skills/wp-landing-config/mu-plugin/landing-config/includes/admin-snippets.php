<?php
namespace LandingConfig\Admin\Snippets;

if (!defined('ABSPATH')) { exit; }

use function LandingConfig\Snippets\list_site_snippets;
use function LandingConfig\Snippets\list_network_snippets;
use function LandingConfig\Snippets\get_snippet;
use function LandingConfig\Snippets\save_snippet;
use function LandingConfig\Snippets\delete_snippet;

\add_action('admin_menu', function () {
    \add_submenu_page(
        'landing-config',
        'Снипеты',
        'Снипеты',
        'manage_options',
        'landing-config-snippets',
        __NAMESPACE__ . '\\dispatch'
    );
});

function dispatch(): void {
    if (!\current_user_can('manage_options')) { \wp_die('Insufficient permissions'); }
    $action = $_REQUEST['action'] ?? 'list';

    switch ($action) {
        case 'save':
            \check_admin_referer('landing_snippets_save');
            handle_save();
            return;
        case 'delete':
            \check_admin_referer('landing_snippets_delete');
            handle_delete();
            return;
        case 'override':
            \check_admin_referer('landing_snippets_override');
            handle_override();
            return;
        case 'new':
        case 'edit':
            render_edit_form();
            return;
        default:
            render_list();
    }
}

function render_list(): void {
    $site_snippets    = list_site_snippets();
    $network_snippets = list_network_snippets();

    // Build map of site snippet names (non-empty) for override-detection.
    $site_names = [];
    foreach ($site_snippets as $s) {
        if ($s['name'] !== '') {
            $site_names[$s['name']] = $s['title'];
        }
    }

    $new_url = \admin_url('admin.php?page=landing-config-snippets&action=new');
    ?>
    <div class="wrap">
        <h1>
            Снипеты
            <a href="<?php echo \esc_url($new_url); ?>" class="page-title-action">Добавить snippet</a>
        </h1>
        <p>Снипеты вставляются в head/body вашего сайта. Сетевые снипеты применяются ко всем сегментам сети — их можно перекрыть, добавив site-snippet с тем же <code>Name</code>. Снипеты без <code>Name</code> всегда добавляются, не перекрывают.</p>

        <?php if (isset($_GET['saved'])): ?>
            <div class="notice notice-success is-dismissible"><p>Snippet сохранён (ID <?php echo (int) $_GET['saved']; ?>).</p></div>
        <?php endif; ?>
        <?php if (isset($_GET['deleted'])): ?>
            <div class="notice notice-success is-dismissible"><p>Snippet удалён.</p></div>
        <?php endif; ?>

        <h2>Snippets этого сайта</h2>
        <table class="wp-list-table widefat striped">
            <thead>
                <tr>
                    <th>Name</th><th>Title</th><th>Position</th><th>Scope</th>
                    <th>Enabled</th><th>Priority</th><th>Actions</th>
                </tr>
            </thead>
            <tbody>
            <?php if (empty($site_snippets)): ?>
                <tr><td colspan="7"><em>Site snippets пока нет.</em></td></tr>
            <?php else: foreach ($site_snippets as $s):
                $edit_url = \admin_url('admin.php?page=landing-config-snippets&action=edit&id=' . (int) $s['id']);
                $del_url  = \wp_nonce_url(
                    \admin_url('admin.php?page=landing-config-snippets&action=delete&id=' . (int) $s['id']),
                    'landing_snippets_delete'
                );
            ?>
                <tr>
                    <td><code><?php echo \esc_html($s['name']); ?></code></td>
                    <td><?php echo \esc_html($s['title']); ?></td>
                    <td><?php echo \esc_html($s['position']); ?></td>
                    <td><?php echo \esc_html($s['scope']); ?></td>
                    <td><?php echo $s['enabled'] ? '✓' : '—'; ?></td>
                    <td><?php echo (int) $s['priority']; ?></td>
                    <td>
                        <a href="<?php echo \esc_url($edit_url); ?>">Edit</a> |
                        <a href="<?php echo \esc_url($del_url); ?>" onclick="return confirm('Удалить snippet?');">Delete</a>
                    </td>
                </tr>
            <?php endforeach; endif; ?>
            </tbody>
        </table>

        <h2 style="margin-top:2em;">Inherited from network (read-only)</h2>
        <table class="wp-list-table widefat striped">
            <thead>
                <tr>
                    <th>Name</th><th>Title</th><th>Position</th><th>Status</th><th>Action</th>
                </tr>
            </thead>
            <tbody>
            <?php if (empty($network_snippets)): ?>
                <tr><td colspan="5"><em>Network snippets отсутствуют.</em></td></tr>
            <?php else: foreach ($network_snippets as $s):
                $has_override = $s['name'] !== '' && isset($site_names[$s['name']]);
                $can_override = $s['name'] !== '';
                $override_url = \wp_nonce_url(
                    \admin_url('admin.php?page=landing-config-snippets&action=override&network_id=' . (int) $s['id']),
                    'landing_snippets_override'
                );
            ?>
                <tr>
                    <td><code><?php echo \esc_html($s['name']); ?></code></td>
                    <td><?php echo \esc_html($s['title']); ?></td>
                    <td><?php echo \esc_html($s['position']); ?></td>
                    <td>
                        <?php if ($has_override): ?>
                            <em>Overridden by site "<?php echo \esc_html($site_names[$s['name']]); ?>"</em>
                        <?php elseif ($can_override): ?>
                            <strong>Active (inherited)</strong>
                        <?php else: ?>
                            <strong>Active (inherited, no override possible)</strong>
                        <?php endif; ?>
                    </td>
                    <td>
                        <?php if ($can_override && !$has_override): ?>
                            <a href="<?php echo \esc_url($override_url); ?>" class="button">Override</a>
                        <?php else: ?>
                            —
                        <?php endif; ?>
                    </td>
                </tr>
            <?php endforeach; endif; ?>
            </tbody>
        </table>
    </div>
    <?php
}

function render_edit_form(): void {
    $id = isset($_GET['id']) ? (int) $_GET['id'] : 0;
    $snippet = $id > 0 ? get_snippet($id, false) : null;

    $defaults = [
        'id'              => 0,
        'title'           => '',
        'name'            => '',
        'code'            => '',
        'position'        => 'head',
        'scope'           => 'global',
        'target_post_ids' => [],
        'enabled'         => true,
        'priority'        => 10,
    ];
    $s = $snippet ?: $defaults;

    $cancel_url = \admin_url('admin.php?page=landing-config-snippets');
    $form_url   = \admin_url('admin.php?page=landing-config-snippets');

    // Fetch pages + posts for target multi-select
    $pages = \get_posts(['post_type' => 'page', 'posts_per_page' => 200, 'post_status' => 'publish', 'orderby' => 'title', 'order' => 'ASC']);
    $posts = \get_posts(['post_type' => 'post', 'posts_per_page' => 200, 'post_status' => 'publish', 'orderby' => 'title', 'order' => 'ASC']);

    ?>
    <div class="wrap">
        <h1><?php echo $snippet ? 'Edit snippet' : 'New snippet'; ?></h1>
        <form method="post" action="<?php echo \esc_url($form_url); ?>">
            <input type="hidden" name="page" value="landing-config-snippets">
            <input type="hidden" name="action" value="save">
            <input type="hidden" name="id" value="<?php echo (int) $s['id']; ?>">
            <?php \wp_nonce_field('landing_snippets_save'); ?>

            <table class="form-table">
                <tr>
                    <th><label for="lp-snip-title">Title <span style="color:red">*</span></label></th>
                    <td><input type="text" id="lp-snip-title" name="title" required class="regular-text" value="<?php echo \esc_attr($s['title']); ?>"></td>
                </tr>
                <tr>
                    <th><label for="lp-snip-name">Name</label></th>
                    <td>
                        <input type="text" id="lp-snip-name" name="name" class="regular-text" value="<?php echo \esc_attr($s['name']); ?>" placeholder="ga4, jivosite, custom_widget...">
                        <p class="description">Machine-id для override. Site snippet с тем же name заменяет network snippet. Оставьте пустым чтобы добавлять без перекрытия.</p>
                    </td>
                </tr>
                <tr>
                    <th>Position</th>
                    <td>
                        <?php foreach (['head', 'body_open', 'body_close'] as $pos): ?>
                            <label style="margin-right:1em;">
                                <input type="radio" name="position" value="<?php echo $pos; ?>" <?php \checked($s['position'], $pos); ?>>
                                <?php echo $pos; ?>
                            </label>
                        <?php endforeach; ?>
                    </td>
                </tr>
                <tr>
                    <th>Scope</th>
                    <td>
                        <?php foreach (['global', 'local'] as $sc): ?>
                            <label style="margin-right:1em;">
                                <input type="radio" name="scope" value="<?php echo $sc; ?>" <?php \checked($s['scope'], $sc); ?>>
                                <?php echo $sc; ?>
                            </label>
                        <?php endforeach; ?>
                        <p class="description">global — на всех страницах. local — только на выбранных страницах ниже.</p>
                    </td>
                </tr>
                <tr>
                    <th><label for="lp-snip-targets">Target pages/posts</label></th>
                    <td>
                        <select id="lp-snip-targets" name="target_post_ids[]" multiple size="8" style="min-width:300px;">
                            <?php if (!empty($pages)): ?>
                                <optgroup label="Pages">
                                <?php foreach ($pages as $p): ?>
                                    <option value="<?php echo (int) $p->ID; ?>" <?php echo in_array((int) $p->ID, (array) $s['target_post_ids'], true) ? 'selected' : ''; ?>>
                                        <?php echo \esc_html($p->post_title); ?>
                                    </option>
                                <?php endforeach; ?>
                                </optgroup>
                            <?php endif; ?>
                            <?php if (!empty($posts)): ?>
                                <optgroup label="Posts">
                                <?php foreach ($posts as $p): ?>
                                    <option value="<?php echo (int) $p->ID; ?>" <?php echo in_array((int) $p->ID, (array) $s['target_post_ids'], true) ? 'selected' : ''; ?>>
                                        <?php echo \esc_html($p->post_title); ?>
                                    </option>
                                <?php endforeach; ?>
                                </optgroup>
                            <?php endif; ?>
                        </select>
                        <p class="description">Удерживайте Ctrl/Cmd для выбора нескольких. Используется только при scope=local.</p>
                    </td>
                </tr>
                <tr>
                    <th>Enabled</th>
                    <td>
                        <label>
                            <input type="checkbox" name="enabled" value="1" <?php \checked((bool) $s['enabled'], true); ?>>
                            Активен
                        </label>
                    </td>
                </tr>
                <tr>
                    <th><label for="lp-snip-priority">Priority</label></th>
                    <td>
                        <input type="number" id="lp-snip-priority" name="priority" min="1" max="999" value="<?php echo (int) $s['priority']; ?>" class="small-text">
                        <p class="description">Меньше = раньше в выводе.</p>
                    </td>
                </tr>
                <tr>
                    <th><label for="lp-snip-code">Code</label></th>
                    <td>
                        <textarea id="lp-snip-code" name="code" rows="14" class="large-text code" style="font-family: Consolas, Monaco, monospace;"><?php echo \esc_textarea($s['code']); ?></textarea>
                        <p class="description">Разрешены только безопасные теги: script, meta, link, style, noscript, iframe, div, span, img, a, p, br.</p>
                    </td>
                </tr>
            </table>

            <p class="submit">
                <?php \submit_button('Save', 'primary', 'submit', false); ?>
                <a href="<?php echo \esc_url($cancel_url); ?>" class="button" style="margin-left:1em;">Cancel</a>
            </p>
        </form>
    </div>
    <?php
}

function handle_save(): void {
    $id = save_snippet([
        'id'              => isset($_POST['id']) ? (int) $_POST['id'] : 0,
        'title'           => $_POST['title'] ?? '',
        'name'            => $_POST['name'] ?? '',
        'code'            => \wp_unslash($_POST['code'] ?? ''),
        'position'        => $_POST['position'] ?? 'head',
        'scope'           => $_POST['scope'] ?? 'global',
        'target_post_ids' => (array) ($_POST['target_post_ids'] ?? []),
        'enabled'         => !empty($_POST['enabled']),
        'priority'        => (int) ($_POST['priority'] ?? 10),
    ], false);

    \wp_safe_redirect(\admin_url('admin.php?page=landing-config-snippets&saved=' . $id));
    exit;
}

function handle_delete(): void {
    $id = isset($_GET['id']) ? (int) $_GET['id'] : 0;
    if ($id > 0) {
        delete_snippet($id, false);
    }
    \wp_safe_redirect(\admin_url('admin.php?page=landing-config-snippets&deleted=1'));
    exit;
}

function handle_override(): void {
    $network_id = isset($_GET['network_id']) ? (int) $_GET['network_id'] : 0;
    $source = get_snippet($network_id, true);
    if (!$source) {
        \wp_die('Network snippet не найден');
    }

    $new_id = save_snippet([
        'title'           => $source['title'] . ' (site override)',
        'name'            => $source['name'],
        'code'            => $source['code'],
        'position'        => $source['position'],
        'scope'           => 'global',
        'enabled'         => $source['enabled'],
        'priority'        => $source['priority'],
    ], false);

    \wp_safe_redirect(\admin_url('admin.php?page=landing-config-snippets&action=edit&id=' . $new_id));
    exit;
}
