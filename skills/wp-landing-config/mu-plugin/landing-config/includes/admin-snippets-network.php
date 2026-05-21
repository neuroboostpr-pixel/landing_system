<?php
namespace LandingConfig\Admin\Snippets\Network;

if (!defined('ABSPATH')) { exit; }

use function LandingConfig\Snippets\list_network_snippets;
use function LandingConfig\Snippets\list_site_snippets;
use function LandingConfig\Snippets\get_snippet;
use function LandingConfig\Snippets\save_snippet;
use function LandingConfig\Snippets\delete_snippet;

\add_action('network_admin_menu', function () {
    \add_submenu_page(
        'landing-config-network',
        'Снипеты (сеть)',
        'Снипеты',
        'manage_network_options',
        'landing-config-network-snippets',
        __NAMESPACE__ . '\\dispatch'
    );
});

function dispatch(): void {
    if (!\current_user_can('manage_network_options')) { \wp_die('Insufficient permissions'); }
    $action = $_REQUEST['action'] ?? 'list';

    switch ($action) {
        case 'save':
            \check_admin_referer('landing_snippets_network_save');
            handle_save();
            return;
        case 'delete':
            \check_admin_referer('landing_snippets_network_delete');
            handle_delete();
            return;
        case 'new':
        case 'edit':
            render_edit_form();
            return;
        default:
            render_list();
    }
}

/**
 * Compute "Overridden by" map: network snippet name => list of subsite domains
 * that have a site snippet with the same name.
 *
 * Linear N×M (N = network snippets with non-empty name, M = sites).
 * Acceptable for typical multisite (≤10 subsites). If >50 sites — cache needed.
 *
 * @param array<int,array<string,mixed>> $network_snippets
 * @return array<string,array<int,string>>  name => [domain1, domain2, ...]
 */
function compute_overrides_by_name(array $network_snippets): array {
    $names = [];
    foreach ($network_snippets as $s) {
        if ($s['name'] !== '') {
            $names[$s['name']] = [];
        }
    }
    if (empty($names)) {
        return [];
    }

    $sites = \get_sites(['number' => 0]);
    foreach ($sites as $site) {
        \switch_to_blog((int) $site->blog_id);
        try {
            foreach ($names as $name => $_) {
                $matches = list_site_snippets(['name' => $name]);
                if (!empty($matches)) {
                    $names[$name][] = $site->domain;
                }
            }
        } finally {
            \restore_current_blog();
        }
    }
    return $names;
}

function render_list(): void {
    $network_snippets = list_network_snippets();
    $overrides        = compute_overrides_by_name($network_snippets);

    $new_url = \network_admin_url('admin.php?page=landing-config-network-snippets&action=new');
    ?>
    <div class="wrap">
        <h1>
            Снипеты (сеть)
            <a href="<?php echo \esc_url($new_url); ?>" class="page-title-action">Добавить network snippet</a>
        </h1>
        <p>
            Сетевые снипеты применяются ко ВСЕМ сегментам сети. Чтобы конкретный сегмент использовал свою версию —
            в его админке (<em>Лендинг → Снипеты</em>) создайте site snippet с тем же <code>Name</code>.
            Снипеты без <code>Name</code> всегда добавляются на всех сайтах, не перекрываются.
        </p>

        <?php if (isset($_GET['saved'])): ?>
            <div class="notice notice-success is-dismissible"><p>Network snippet сохранён (ID <?php echo (int) $_GET['saved']; ?>).</p></div>
        <?php endif; ?>
        <?php if (isset($_GET['deleted'])): ?>
            <div class="notice notice-success is-dismissible"><p>Network snippet удалён.</p></div>
        <?php endif; ?>

        <table class="wp-list-table widefat striped">
            <thead>
                <tr>
                    <th>Name</th><th>Title</th><th>Position</th>
                    <th>Enabled</th><th>Priority</th>
                    <th>Overridden by</th><th>Actions</th>
                </tr>
            </thead>
            <tbody>
            <?php if (empty($network_snippets)): ?>
                <tr><td colspan="7"><em>Network snippets пока нет.</em></td></tr>
            <?php else: foreach ($network_snippets as $s):
                $edit_url = \network_admin_url('admin.php?page=landing-config-network-snippets&action=edit&id=' . (int) $s['id']);
                $del_url  = \wp_nonce_url(
                    \network_admin_url('admin.php?page=landing-config-network-snippets&action=delete&id=' . (int) $s['id']),
                    'landing_snippets_network_delete'
                );
                $overridden = ($s['name'] !== '' && !empty($overrides[$s['name']]))
                    ? $overrides[$s['name']]
                    : [];
            ?>
                <tr>
                    <td><code><?php echo \esc_html($s['name']); ?></code></td>
                    <td><?php echo \esc_html($s['title']); ?></td>
                    <td><?php echo \esc_html($s['position']); ?></td>
                    <td><?php echo $s['enabled'] ? '✓' : '—'; ?></td>
                    <td><?php echo (int) $s['priority']; ?></td>
                    <td>
                        <?php if (!empty($overridden)): ?>
                            <?php echo \esc_html(implode(', ', $overridden)); ?>
                        <?php else: ?>
                            —
                        <?php endif; ?>
                    </td>
                    <td>
                        <a href="<?php echo \esc_url($edit_url); ?>">Edit</a> |
                        <a href="<?php echo \esc_url($del_url); ?>" onclick="return confirm('Удалить network snippet?');">Delete</a>
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
    $snippet = $id > 0 ? get_snippet($id, true) : null;

    $defaults = [
        'id'       => 0,
        'title'    => '',
        'name'     => '',
        'code'     => '',
        'position' => 'head',
        'enabled'  => true,
        'priority' => 10,
    ];
    $s = $snippet ?: $defaults;

    $cancel_url = \network_admin_url('admin.php?page=landing-config-network-snippets');
    $form_url   = \network_admin_url('admin.php?page=landing-config-network-snippets');

    ?>
    <div class="wrap">
        <h1><?php echo $snippet ? 'Edit network snippet' : 'New network snippet'; ?></h1>
        <form method="post" action="<?php echo \esc_url($form_url); ?>">
            <input type="hidden" name="page" value="landing-config-network-snippets">
            <input type="hidden" name="action" value="save">
            <input type="hidden" name="id" value="<?php echo (int) $s['id']; ?>">
            <?php \wp_nonce_field('landing_snippets_network_save'); ?>

            <table class="form-table">
                <tr>
                    <th><label for="lp-snip-title">Title <span style="color:red">*</span></label></th>
                    <td><input type="text" id="lp-snip-title" name="title" required class="regular-text" value="<?php echo \esc_attr($s['title']); ?>"></td>
                </tr>
                <tr>
                    <th><label for="lp-snip-name">Name</label></th>
                    <td>
                        <input type="text" id="lp-snip-name" name="name" class="regular-text" value="<?php echo \esc_attr($s['name']); ?>" placeholder="ga4, jivosite, custom_widget...">
                        <p class="description">
                            Machine-id — используется для override. Например <code>ga4</code>, <code>jivosite</code>.
                            Если subsite создаст snippet с тем же name — он перекроет этот network snippet.
                            Оставьте пустым чтобы snippet всегда добавлялся.
                        </p>
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
        'scope'           => 'global',
        'target_post_ids' => [],
        'enabled'         => !empty($_POST['enabled']),
        'priority'        => (int) ($_POST['priority'] ?? 10),
    ], true);

    \wp_safe_redirect(\network_admin_url('admin.php?page=landing-config-network-snippets&saved=' . $id));
    exit;
}

function handle_delete(): void {
    $id = isset($_GET['id']) ? (int) $_GET['id'] : 0;
    if ($id > 0) {
        delete_snippet($id, true);
    }
    \wp_safe_redirect(\network_admin_url('admin.php?page=landing-config-network-snippets&deleted=1'));
    exit;
}
