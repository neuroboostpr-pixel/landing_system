<?php
/**
 * Unified Network Admin — Snippets page.
 *
 * Single page under network_admin_menu, slug 'landing-config-network-snippets'.
 * A ?segment= query param selects the mode:
 *   segment=0  → network-level snippet editor (was admin-snippets-network.php)
 *   segment=N  → site-level snippet editor for blog_id=N + inherited block (was admin-snippets.php)
 *
 * Nonce names are preserved exactly as they appeared in both original files
 * to keep any existing super-admin bookmarks / email links valid:
 *   Network actions : landing_snippets_network_save, landing_snippets_network_delete
 *   Site actions    : landing_snippets_save, landing_snippets_delete, landing_snippets_override
 */
namespace LandingConfig\Admin\Snippets\Network;

if (!defined('ABSPATH')) { exit; }

use function LandingConfig\Snippets\list_network_snippets;
use function LandingConfig\Snippets\list_site_snippets;
use function LandingConfig\Snippets\get_snippet;
use function LandingConfig\Snippets\save_snippet;
use function LandingConfig\Snippets\delete_snippet;
use function LandingConfig\AdminMode\cap;
use function LandingConfig\AdminMode\admin_url_for;
use function LandingConfig\AdminMode\menu_hook;
use function LandingConfig\AdminMode\parent_slug;
use function LandingConfig\AdminMode\page_slug;

// ---------------------------------------------------------------------------
// Menu registration
// ---------------------------------------------------------------------------

\add_action(menu_hook(), function () {
    \add_submenu_page(
        parent_slug(),
        'Снипеты (сеть)',
        'Снипеты',
        cap(),
        page_slug('snippets'),
        __NAMESPACE__ . '\\dispatch'
    );
});

// ---------------------------------------------------------------------------
// Helpers
// ---------------------------------------------------------------------------

/**
 * Return the current segment from the request (0 = network, N = blog_id).
 */
function current_segment(): int {
    return isset($_REQUEST['segment']) ? (int) $_REQUEST['segment'] : 0;
}

/**
 * Build the base URL for this page, including the segment param.
 */
function page_url(int $segment, array $extra = []): string {
    $args = array_merge(['page' => \LandingConfig\AdminMode\page_slug('snippets'), 'segment' => $segment], $extra);
    return admin_url_for('admin.php?' . \http_build_query($args));
}

// ---------------------------------------------------------------------------
// Dispatcher
// ---------------------------------------------------------------------------

function dispatch(): void {
    if (!\current_user_can(cap())) {
        \wp_die('Insufficient permissions');
    }

    $segment = current_segment();
    $action  = $_REQUEST['action'] ?? 'list';

    if ($segment === 0) {
        // Network-level actions — preserve original nonce names.
        switch ($action) {
            case 'save':
                \check_admin_referer('landing_snippets_network_save');
                handle_save_network();
                return;
            case 'delete':
                \check_admin_referer('landing_snippets_network_delete');
                handle_delete_network();
                return;
            case 'new':
            case 'edit':
                render_page($segment);
                return;
            default:
                render_page($segment);
        }
    } else {
        // Site-level actions — preserve original nonce names from admin-snippets.php.
        switch ($action) {
            case 'save':
                \check_admin_referer('landing_snippets_save');
                handle_save_site($segment);
                return;
            case 'delete':
                \check_admin_referer('landing_snippets_delete');
                handle_delete_site($segment);
                return;
            case 'override':
                \check_admin_referer('landing_snippets_override');
                handle_override_site($segment);
                return;
            case 'new':
            case 'edit':
                render_page($segment);
                return;
            default:
                render_page($segment);
        }
    }
}

// ---------------------------------------------------------------------------
// Top-level render dispatcher
// ---------------------------------------------------------------------------

function render_page(int $segment): void {
    render_segment_selector($segment);

    if ($segment === 0) {
        $action = $_REQUEST['action'] ?? 'list';
        if ($action === 'new' || $action === 'edit') {
            render_edit_form_network();
        } else {
            render_list_network();
        }
    } else {
        $action = $_REQUEST['action'] ?? 'list';
        if ($action === 'new' || $action === 'edit') {
            render_edit_form_site($segment);
        } else {
            render_list_site($segment);
        }
    }
}

// ---------------------------------------------------------------------------
// Segment selector
// ---------------------------------------------------------------------------

function render_segment_selector(int $current_segment): void {
    // Single-site has no audience segments → no selector. Everything is edited
    // at segment=0 (the only / network-default level) on the current blog.
    if (!\is_multisite()) {
        return;
    }
    $sites = \get_sites(['number' => 0]);
    ?>
    <div style="padding:12px 0 8px;">
        <strong>Сегмент:</strong>
        <select onchange="location.href=this.value;" style="margin-left:8px;">
            <option value="<?php echo \esc_url(page_url(0)); ?>" <?php \selected($current_segment, 0); ?>>
                Network (все сегменты)
            </option>
            <?php foreach ($sites as $site): ?>
                <option value="<?php echo \esc_url(page_url((int) $site->blog_id)); ?>"
                        <?php \selected($current_segment, (int) $site->blog_id); ?>>
                    <?php echo \esc_html($site->domain . $site->path); ?> (blog_id=<?php echo (int) $site->blog_id; ?>)
                </option>
            <?php endforeach; ?>
        </select>
    </div>
    <?php
}

// ---------------------------------------------------------------------------
// NETWORK mode — list
// ---------------------------------------------------------------------------

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

    // Single-site has no subsites that could override network snippets.
    if (!\is_multisite()) {
        return $names;
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

function render_list_network(): void {
    $network_snippets = list_network_snippets();
    $overrides        = compute_overrides_by_name($network_snippets);

    $new_url = page_url(0, ['action' => 'new']);
    ?>
    <div class="wrap">
        <h1>
            Снипеты (сеть)
            <a href="<?php echo \esc_url($new_url); ?>" class="page-title-action">Добавить network snippet</a>
        </h1>
        <p>
            Сетевые снипеты применяются ко ВСЕМ сегментам сети. Чтобы конкретный сегмент использовал свою версию —
            выберите его в селекторе выше и создайте site snippet с тем же <code>Name</code>.
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
                $edit_url = page_url(0, ['action' => 'edit', 'id' => (int) $s['id']]);
                $del_url  = \wp_nonce_url(
                    page_url(0, ['action' => 'delete', 'id' => (int) $s['id']]),
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

// ---------------------------------------------------------------------------
// NETWORK mode — edit form
// ---------------------------------------------------------------------------

function render_edit_form_network(): void {
    $id      = isset($_GET['id']) ? (int) $_GET['id'] : 0;
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

    $cancel_url = page_url(0);
    $form_url   = page_url(0);
    ?>
    <div class="wrap">
        <h1><?php echo $snippet ? 'Edit network snippet' : 'New network snippet'; ?></h1>
        <form method="post" action="<?php echo \esc_url($form_url); ?>">
            <input type="hidden" name="page" value="<?php echo \esc_attr(\LandingConfig\AdminMode\page_slug('snippets')); ?>">
            <input type="hidden" name="segment" value="0">
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
                <?php
                $cur_scope = isset($s['subpage_scope']) ? $s['subpage_scope'] : 'all';
                $all_checked = ($cur_scope === 'all');
                $selected_slugs = $all_checked ? [] : array_map('trim', explode(',', $cur_scope));
                $subpages = ['li-auto' => 'Li Auto', 'zeekr' => 'Zeekr', 'xiaomi' => 'Xiaomi', 'lynk-co' => 'Lynk & Co', 'rox' => 'ROX'];
                ?>
                <tr id="lp-snip-subpage-row">
                    <th>Охват подстраниц</th>
                    <td>
                        <label>
                            <input type="checkbox" id="lp-snip-all-subpages" name="subpage_scope_all" value="1" <?php \checked($all_checked, true); ?> onchange="document.getElementById('lp-subpage-list-n').style.display=this.checked?'none':'block'">
                            На всех страницах (включая бренд-подстраницы)
                        </label>
                        <div id="lp-subpage-list-n" style="margin-top:8px;<?php echo $all_checked ? 'display:none;' : ''; ?>">
                            <p class="description" style="margin:0 0 6px;">Выберите бренд-подстраницы:</p>
                            <?php foreach ($subpages as $slug => $label): ?>
                                <label style="display:block; margin-bottom:4px;">
                                    <input type="checkbox" name="subpage_slugs[]" value="<?php echo \esc_attr($slug); ?>" <?php \checked(in_array($slug, $selected_slugs, true), true); ?>>
                                    <?php echo \esc_html($label); ?>
                                </label>
                            <?php endforeach; ?>
                        </div>
                        <p class="description" style="margin-top:6px;">Управляет тем, на каких страницах появляется снипет. При «На всех страницах» — включая и главную, и бренд-подстраницы.</p>
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

// ---------------------------------------------------------------------------
// NETWORK mode — handlers
// ---------------------------------------------------------------------------

function handle_save_network(): void {
    $scope_all = !empty($_POST['subpage_scope_all']);
    if ($scope_all) {
        $subpage_scope = 'all';
    } else {
        $slugs = array_map('sanitize_key', (array) ($_POST['subpage_slugs'] ?? []));
        $subpage_scope = $slugs ? implode(',', $slugs) : 'all';
    }

    \kses_remove_filters();
    $raw_code = \wp_unslash($_POST['code'] ?? '');
    \kses_init_filters();

    $id = save_snippet([
        'id'              => isset($_POST['id']) ? (int) $_POST['id'] : 0,
        'title'           => \sanitize_text_field($_POST['title'] ?? ''),
        'name'            => \sanitize_key($_POST['name'] ?? ''),
        'code'            => $raw_code,
        'position'        => \sanitize_key($_POST['position'] ?? 'head'),
        'scope'           => 'global',
        'target_post_ids' => [],
        'enabled'         => !empty($_POST['enabled']),
        'priority'        => (int) ($_POST['priority'] ?? 10),
        'subpage_scope'   => $subpage_scope,
    ], true);

    \wp_safe_redirect(page_url(0, ['saved' => $id]));
    exit;
}

function handle_delete_network(): void {
    $id = isset($_GET['id']) ? (int) $_GET['id'] : 0;
    if ($id > 0) {
        delete_snippet($id, true);
    }
    \wp_safe_redirect(page_url(0, ['deleted' => 1]));
    exit;
}

// ---------------------------------------------------------------------------
// SITE mode — list
// ---------------------------------------------------------------------------

function render_list_site(int $segment): void {
    \switch_to_blog($segment);
    try {
        $site_snippets    = list_site_snippets();
        $network_snippets = list_network_snippets();
    } finally {
        \restore_current_blog();
    }

    // Build map of site snippet names (non-empty) for override-detection.
    $site_names = [];
    foreach ($site_snippets as $s) {
        if ($s['name'] !== '') {
            $site_names[$s['name']] = $s['title'];
        }
    }

    $new_url = page_url($segment, ['action' => 'new']);
    $site    = \is_multisite() ? \get_blog_details($segment) : null;
    $domain  = $site ? \esc_html($site->domain . $site->path) : "blog_id={$segment}";
    ?>
    <div class="wrap">
        <h1>
            Снипеты — <?php echo $domain; ?>
            <a href="<?php echo \esc_url($new_url); ?>" class="page-title-action">Добавить snippet</a>
        </h1>
        <p>Снипеты вставляются в head/body этого сегмента. Сетевые снипеты применяются ко всем сегментам — их можно перекрыть, добавив site-snippet с тем же <code>Name</code>. Снипеты без <code>Name</code> всегда добавляются, не перекрывают.</p>

        <?php if (isset($_GET['saved'])): ?>
            <div class="notice notice-success is-dismissible"><p>Snippet сохранён (ID <?php echo (int) $_GET['saved']; ?>).</p></div>
        <?php endif; ?>
        <?php if (isset($_GET['deleted'])): ?>
            <div class="notice notice-success is-dismissible"><p>Snippet удалён.</p></div>
        <?php endif; ?>

        <h2>Snippets этого сегмента</h2>
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
                $edit_url = page_url($segment, ['action' => 'edit', 'id' => (int) $s['id']]);
                $del_url  = \wp_nonce_url(
                    page_url($segment, ['action' => 'delete', 'id' => (int) $s['id']]),
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
                    page_url($segment, ['action' => 'override', 'network_id' => (int) $s['id']]),
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

// ---------------------------------------------------------------------------
// SITE mode — edit form
// ---------------------------------------------------------------------------

function render_edit_form_site(int $segment): void {
    $id      = isset($_GET['id']) ? (int) $_GET['id'] : 0;

    \switch_to_blog($segment);
    try {
        $snippet = $id > 0 ? get_snippet($id, false) : null;
        $pages   = \get_posts(['post_type' => 'page', 'posts_per_page' => 200, 'post_status' => 'publish', 'orderby' => 'title', 'order' => 'ASC']);
        $posts   = \get_posts(['post_type' => 'post', 'posts_per_page' => 200, 'post_status' => 'publish', 'orderby' => 'title', 'order' => 'ASC']);
    } finally {
        \restore_current_blog();
    }

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

    $site       = \is_multisite() ? \get_blog_details($segment) : null;
    $domain     = $site ? \esc_html($site->domain . $site->path) : "blog_id={$segment}";
    $cancel_url = page_url($segment);
    $form_url   = page_url($segment);
    ?>
    <div class="wrap">
        <h1><?php echo $snippet ? "Edit snippet — {$domain}" : "New snippet — {$domain}"; ?></h1>
        <form method="post" action="<?php echo \esc_url($form_url); ?>">
            <input type="hidden" name="page" value="<?php echo \esc_attr(\LandingConfig\AdminMode\page_slug('snippets')); ?>">
            <input type="hidden" name="segment" value="<?php echo $segment; ?>">
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
                <?php
                $cur_scope_s = isset($s['subpage_scope']) ? $s['subpage_scope'] : 'all';
                $all_checked_s = ($cur_scope_s === 'all');
                $selected_slugs_s = $all_checked_s ? [] : array_map('trim', explode(',', $cur_scope_s));
                $subpages_s = ['li-auto' => 'Li Auto', 'zeekr' => 'Zeekr', 'xiaomi' => 'Xiaomi', 'lynk-co' => 'Lynk & Co', 'rox' => 'ROX'];
                ?>
                <tr>
                    <th>Охват подстраниц</th>
                    <td>
                        <label>
                            <input type="checkbox" id="lp-snip-all-subpages-s" name="subpage_scope_all" value="1" <?php \checked($all_checked_s, true); ?> onchange="document.getElementById('lp-subpage-list-s').style.display=this.checked?'none':'block'">
                            На всех страницах (включая бренд-подстраницы)
                        </label>
                        <div id="lp-subpage-list-s" style="margin-top:8px;<?php echo $all_checked_s ? 'display:none;' : ''; ?>">
                            <p class="description" style="margin:0 0 6px;">Выберите бренд-подстраницы:</p>
                            <?php foreach ($subpages_s as $slug => $label): ?>
                                <label style="display:block; margin-bottom:4px;">
                                    <input type="checkbox" name="subpage_slugs[]" value="<?php echo \esc_attr($slug); ?>" <?php \checked(in_array($slug, $selected_slugs_s, true), true); ?>>
                                    <?php echo \esc_html($label); ?>
                                </label>
                            <?php endforeach; ?>
                        </div>
                        <p class="description" style="margin-top:6px;">Управляет тем, на каких страницах появляется снипет. При «На всех страницах» — включая и главную, и бренд-подстраницы.</p>
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

// ---------------------------------------------------------------------------
// SITE mode — handlers
// ---------------------------------------------------------------------------

function handle_save_site(int $segment): void {
    $scope_all_s = !empty($_POST['subpage_scope_all']);
    if ($scope_all_s) {
        $subpage_scope_s = 'all';
    } else {
        $slugs_s = array_map('sanitize_key', (array) ($_POST['subpage_slugs'] ?? []));
        $subpage_scope_s = $slugs_s ? implode(',', $slugs_s) : 'all';
    }

    \kses_remove_filters();
    $raw_code_s = \wp_unslash($_POST['code'] ?? '');
    \kses_init_filters();

    \switch_to_blog($segment);
    try {
        $id = save_snippet([
            'id'              => isset($_POST['id']) ? (int) $_POST['id'] : 0,
            'title'           => \sanitize_text_field($_POST['title'] ?? ''),
            'name'            => \sanitize_key($_POST['name'] ?? ''),
            'code'            => $raw_code_s,
            'position'        => \sanitize_key($_POST['position'] ?? 'head'),
            'scope'           => \sanitize_key($_POST['scope'] ?? 'global'),
            'target_post_ids' => array_map('intval', (array) ($_POST['target_post_ids'] ?? [])),
            'enabled'         => !empty($_POST['enabled']),
            'priority'        => (int) ($_POST['priority'] ?? 10),
            'subpage_scope'   => $subpage_scope_s,
        ], false);
    } finally {
        \restore_current_blog();
    }

    \wp_safe_redirect(page_url($segment, ['saved' => $id]));
    exit;
}

function handle_delete_site(int $segment): void {
    $id = isset($_GET['id']) ? (int) $_GET['id'] : 0;
    if ($id > 0) {
        \switch_to_blog($segment);
        try {
            delete_snippet($id, false);
        } finally {
            \restore_current_blog();
        }
    }
    \wp_safe_redirect(page_url($segment, ['deleted' => 1]));
    exit;
}

function handle_override_site(int $segment): void {
    $network_id = isset($_GET['network_id']) ? (int) $_GET['network_id'] : 0;
    $source     = get_snippet($network_id, true);
    if (!$source) {
        \wp_die('Network snippet не найден');
    }

    \switch_to_blog($segment);
    try {
        $new_id = save_snippet([
            'title'           => $source['title'] . ' (site override)',
            'name'            => $source['name'],
            'code'            => $source['code'],
            'position'        => $source['position'],
            'scope'           => 'global',
            'enabled'         => $source['enabled'],
            'priority'        => $source['priority'],
        ], false);
    } finally {
        \restore_current_blog();
    }

    \wp_safe_redirect(page_url($segment, ['action' => 'edit', 'id' => $new_id]));
    exit;
}
