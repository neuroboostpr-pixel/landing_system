<?php
namespace LandingConfig\Admin\Leads;

if (!defined('ABSPATH')) { exit; }

use function LandingConfig\DB\get_leads_table_name;
use function LandingConfig\DB\get_lead_status_log_table_name;
use function LandingConfig\LeadStatuses\list_lead_statuses;
use function LandingConfig\LeadStatuses\resolve_lead_status;
use function LandingConfig\LeadStatusLog\log_status_change;

add_action('admin_menu', function () {
    add_submenu_page(
        'landing-config',
        'Заявки',
        'Заявки',
        'manage_options',
        'landing-config-leads',
        __NAMESPACE__ . '\\render_page'
    );
});

add_action('admin_post_landing_leads_bulk_intent',  __NAMESPACE__ . '\\handle_bulk_intent');
add_action('admin_post_landing_leads_bulk_status',  __NAMESPACE__ . '\\handle_bulk_status');
add_action('admin_post_landing_leads_bulk_delete',  __NAMESPACE__ . '\\handle_bulk_delete');
add_action('admin_post_landing_lead_delete',        __NAMESPACE__ . '\\handle_single_delete');

function render_page(): void {
    if (!current_user_can('manage_options')) { wp_die('Insufficient permissions'); }

    if (isset($_GET['action']) && $_GET['action'] === 'export_csv'
        && check_admin_referer('landing_export_leads')) {
        export_csv();
        return;
    }

    global $wpdb;
    $table = get_leads_table_name();
    $per_page = 20;
    $page = max(1, (int)($_GET['paged'] ?? 1));
    $offset = ($page - 1) * $per_page;
    $blog_id = get_current_blog_id();

    // Filter: ?status=<slug> или ?status=all (default)
    $active_status = sanitize_key($_GET['status'] ?? 'all');

    // Counts по статусам — один SQL.
    // $table = $wpdb->prefix . 'landing_leads' (генерируется в DB\get_leads_table_name из доверенного
    // $wpdb->prefix, не из user input). prepare() не используется потому что не нужны placeholders.
    // phpcs:ignore WordPress.DB.PreparedSQL.NotPrepared, WordPress.DB.DirectDatabaseQuery.DirectQuery
    $count_rows = $wpdb->get_results("SELECT processed_status AS s, COUNT(*) AS n FROM `$table` GROUP BY processed_status", ARRAY_A);
    $counts_by_slug = [];
    $total = 0;
    foreach ($count_rows as $cr) {
        $counts_by_slug[(string) $cr['s']] = (int) $cr['n'];
        $total += (int) $cr['n'];
    }

    // WHERE clause для основной выборки
    if ($active_status === 'all') {
        $rows = $wpdb->get_results($wpdb->prepare(
            "SELECT * FROM `$table` ORDER BY created_at DESC LIMIT %d OFFSET %d",
            $per_page, $offset
        ), ARRAY_A);
        $filtered_total = $total;
    } else {
        $rows = $wpdb->get_results($wpdb->prepare(
            "SELECT * FROM `$table` WHERE processed_status = %s ORDER BY created_at DESC LIMIT %d OFFSET %d",
            $active_status, $per_page, $offset
        ), ARRAY_A);
        $filtered_total = $counts_by_slug[$active_status] ?? 0;
    }

    $vocab = list_lead_statuses($blog_id);
    $vocab_by_slug = [];
    foreach ($vocab as $v) $vocab_by_slug[$v['slug']] = $v;

    $export_url = wp_nonce_url(
        admin_url('admin.php?page=landing-config-leads&action=export_csv'),
        'landing_export_leads'
    );
    $base_url = admin_url('admin.php?page=landing-config-leads');
    ?>
    <div class="wrap">
        <?php if (isset($_GET['bulk_updated'])): $bu = (int) $_GET['bulk_updated']; $bf = (int) ($_GET['bulk_failed'] ?? 0); ?>
            <div class="notice notice-success is-dismissible"><p>Обновлено заявок: <strong><?php echo $bu; ?></strong>.<?php if ($bf > 0): ?> Не удалось: <strong><?php echo $bf; ?></strong> (см. debug.log).<?php endif; ?></p></div>
        <?php elseif (isset($_GET['bulk_deleted'])): $bd = (int) $_GET['bulk_deleted']; $bf = (int) ($_GET['bulk_failed'] ?? 0); ?>
            <div class="notice notice-success is-dismissible"><p>Удалено заявок: <strong><?php echo $bd; ?></strong>.<?php if ($bf > 0): ?> Не удалось: <strong><?php echo $bf; ?></strong> (см. debug.log).<?php endif; ?></p></div>
        <?php elseif (isset($_GET['deleted'])): ?>
            <div class="notice notice-success is-dismissible"><p>Заявка удалена.</p></div>
        <?php elseif (isset($_GET['bulk_error'])): ?>
            <div class="notice notice-error is-dismissible"><p>Ошибка: <code><?php echo esc_html((string) $_GET['bulk_error']); ?></code>. Проверь выбор заявок и параметры.</p></div>
        <?php endif; ?>
        <h1>Заявки <a href="<?php echo esc_url($export_url); ?>" class="page-title-action">Экспорт CSV</a></h1>

        <ul class="subsubsub">
            <li>
                <a href="<?php echo esc_url(add_query_arg('status', 'all', $base_url)); ?>" class="<?php echo $active_status === 'all' ? 'current' : ''; ?>">
                    Все <span class="count">(<?php echo (int) $total; ?>)</span>
                </a>
            </li>
            <?php foreach ($vocab as $v):
                $n = (int) ($counts_by_slug[$v['slug']] ?? 0);
                $is_active = $active_status === $v['slug'];
            ?>
                | <li>
                    <a href="<?php echo esc_url(add_query_arg('status', $v['slug'], $base_url)); ?>" class="<?php echo $is_active ? 'current' : ''; ?>">
                        <?php echo esc_html($v['label']); ?> <span class="count">(<?php echo $n; ?>)</span>
                    </a>
                </li>
            <?php endforeach; ?>
        </ul>
        <div style="clear:both;"></div>

        <form method="post" action="<?php echo esc_url(admin_url('admin-post.php')); ?>">
            <?php wp_nonce_field('landing_leads_bulk_intent'); ?>
            <input type="hidden" name="action" value="landing_leads_bulk_intent">
            <input type="hidden" name="status" value="<?php echo esc_attr($active_status); ?>">

            <div class="tablenav top">
                <div class="alignleft actions bulkactions">
                    <select name="bulk_action">
                        <option value="">— Действие —</option>
                        <option value="change_status">Изменить статус…</option>
                        <option value="delete">Удалить</option>
                    </select>
                    <button type="submit" class="button action">Применить</button>
                </div>
            </div>

            <table class="wp-list-table widefat striped">
                <thead>
                    <tr>
                        <td class="check-column"><input type="checkbox" id="cb-select-all"></td>
                        <th>ID</th><th>Дата</th><th>Имя</th><th>Телефон</th><th>Email</th>
                        <th>Статус</th>
                        <th>Score</th>
                        <th>Сообщение</th><th>Источник</th><th>UTM</th>
                    </tr>
                </thead>
                <tbody>
                    <?php if (empty($rows)): ?>
                        <tr><td colspan="11"><em>Заявок нет.</em></td></tr>
                    <?php else: foreach ($rows as $r):
                        $status_slug = (string) ($r['processed_status'] ?? '');
                        $v = $vocab_by_slug[$status_slug] ?? null;
                        $badge_label = $v ? $v['label'] : ($status_slug !== '' ? $status_slug : '—');
                        $badge_color = $v ? $v['color'] : '#646970';
                        $badge_warn = $v ? '' : ' title="Статус не найден в vocab"';
                        $detail_url = admin_url('admin.php?page=landing-config-lead-detail&id=' . (int) $r['id']);
                    ?>
                        <?php
                            $delete_url = wp_nonce_url(
                                admin_url('admin-post.php?action=landing_lead_delete&lead_id=' . (int) $r['id']),
                                'landing_lead_delete_' . (int) $r['id']
                            );
                        ?>
                        <tr>
                            <th scope="row" class="check-column"><input type="checkbox" name="lead_ids[]" value="<?php echo (int) $r['id']; ?>"></th>
                            <td><?php echo (int) $r['id']; ?></td>
                            <td><?php echo esc_html($r['created_at']); ?></td>
                            <td>
                                <a href="<?php echo esc_url($detail_url); ?>"><?php echo esc_html($r['name'] ?: '— без имени —'); ?></a>
                                <div class="row-actions">
                                    <span class="trash"><a href="<?php echo esc_url($delete_url); ?>" style="color:#b32d2e;" onclick="return confirm('Удалить заявку #<?php echo (int) $r['id']; ?>? Это необратимо.');">Удалить</a></span>
                                </div>
                            </td>
                            <td><?php echo esc_html($r['phone']); ?></td>
                            <td><?php echo esc_html($r['email']); ?></td>
                            <td><span<?php echo $badge_warn; ?> style="background:<?php echo esc_attr($badge_color); ?>; color:#fff; padding:3px 10px; border-radius:3px; font-size:12px;"><?php echo esc_html($badge_label); ?></span></td>
                            <td><?php
                                $score_val = $r['recaptcha_score'] ?? null;
                                if ($score_val !== null && $score_val !== '') {
                                    $score_f = (float) $score_val;
                                    if ($score_f >= 0.7) {
                                        $sc = '#46b450'; // green
                                    } elseif ($score_f >= 0.4) {
                                        $sc = '#f0ad00'; // yellow
                                    } else {
                                        $sc = '#b32d2e'; // red
                                    }
                                    echo '<span style="background:' . esc_attr($sc) . '; color:#fff; padding:2px 8px; border-radius:3px; font-size:12px; font-family:monospace;">' . esc_html(number_format($score_f, 2)) . '</span>';
                                } else {
                                    echo '<span style="color:#646970;">—</span>';
                                }
                            ?></td>
                            <td><?php echo esc_html(mb_substr($r['message'] ?? '', 0, 60)); ?></td>
                            <td><?php echo esc_html($r['source_block']); ?></td>
                            <td><?php
                                $utm = array_filter([
                                    $r['utm_source'] ? "src={$r['utm_source']}" : '',
                                    $r['utm_medium'] ? "med={$r['utm_medium']}" : '',
                                    $r['utm_campaign'] ? "cmp={$r['utm_campaign']}" : '',
                                ]);
                                echo esc_html(implode(' ', $utm));
                            ?></td>
                        </tr>
                    <?php endforeach; endif; ?>
                </tbody>
            </table>

            <script>
            document.getElementById('cb-select-all')?.addEventListener('change', function() {
                document.querySelectorAll('input[name="lead_ids[]"]').forEach(cb => cb.checked = this.checked);
            });
            </script>
        </form>

        <?php
        $total_pages = (int) ceil($filtered_total / $per_page);
        if ($total_pages > 1) {
            echo '<div class="tablenav"><div class="tablenav-pages">';
            echo paginate_links([
                'base'      => add_query_arg(['status' => $active_status, 'paged' => '%#%'], $base_url),
                'format'    => '',
                'total'     => $total_pages,
                'current'   => $page,
                'prev_text' => '‹',
                'next_text' => '›',
            ]);
            echo '</div></div>';
        }
        ?>
    </div>
    <?php
}

function export_csv(): void {
    if (!current_user_can('manage_options')) { wp_die('Insufficient permissions'); }

    global $wpdb;
    $table = get_leads_table_name();
    $rows = $wpdb->get_results("SELECT * FROM `$table` ORDER BY created_at DESC", ARRAY_A);

    $filename = sprintf('landing-leads-blog-%d-%s.csv', get_current_blog_id(), date('Ymd-His'));
    header('Content-Type: text/csv; charset=utf-8');
    header('Content-Disposition: attachment; filename="' . $filename . '"');

    $out = fopen('php://output', 'w');
    fputs($out, "\xEF\xBB\xBF");

    if (!empty($rows)) {
        fputcsv($out, array_keys($rows[0]));
        foreach ($rows as $r) {
            fputcsv($out, $r);
        }
    } else {
        fputcsv($out, ['id', 'created_at', 'name', 'phone', 'email', 'message']);
    }
    fclose($out);
    exit;
}

/**
 * Bulk action: показывает страницу-форму с выбором целевого статуса + комментария
 * для всех выбранных заявок. lead_ids передаются в hidden inputs до bulk_status handler.
 */
function handle_bulk_intent(): void {
    if (!current_user_can('manage_options')) { wp_die('No.', 403); }
    check_admin_referer('landing_leads_bulk_intent');

    $bulk_action = sanitize_key($_POST['bulk_action'] ?? '');
    $lead_ids = array_map('intval', (array) ($_POST['lead_ids'] ?? []));
    $lead_ids = array_values(array_filter($lead_ids, fn($i) => $i > 0));
    $return_status = sanitize_key($_POST['status'] ?? 'all');

    if (!in_array($bulk_action, ['change_status', 'delete'], true)) {
        wp_safe_redirect(admin_url('admin.php?page=landing-config-leads&status=' . $return_status));
        exit;
    }
    if (empty($lead_ids)) {
        wp_safe_redirect(admin_url('admin.php?page=landing-config-leads&status=' . $return_status . '&bulk_error=no_selection'));
        exit;
    }
    if ($bulk_action === 'delete') {
        // POST to dedicated delete handler (own nonce)
        $blog_id = get_current_blog_id();
        $vocab = list_lead_statuses($blog_id);
        $back_url = admin_url('admin.php?page=landing-config-leads&status=' . $return_status);
        ?>
        <div class="wrap">
            <h1>Удаление заявок</h1>
            <p>Выбрано заявок: <strong><?php echo count($lead_ids); ?></strong>. Это действие <strong>необратимо</strong> — заявки и вся история статусов будут удалены навсегда.</p>
            <form method="post" action="<?php echo esc_url(admin_url('admin-post.php')); ?>">
                <?php wp_nonce_field('landing_leads_bulk_delete'); ?>
                <input type="hidden" name="action" value="landing_leads_bulk_delete">
                <input type="hidden" name="return_status" value="<?php echo esc_attr($return_status); ?>">
                <?php foreach ($lead_ids as $id): ?>
                    <input type="hidden" name="lead_ids[]" value="<?php echo (int) $id; ?>">
                <?php endforeach; ?>
                <p>
                    <button type="submit" class="button button-primary" style="background:#b32d2e; border-color:#b32d2e;">Да, удалить <?php echo count($lead_ids); ?> заявок(у)</button>
                    <a href="<?php echo esc_url($back_url); ?>" class="button" style="margin-left:8px;">Отмена</a>
                </p>
            </form>
        </div>
        <?php
        exit;
    }

    $blog_id = get_current_blog_id();
    $vocab = list_lead_statuses($blog_id);
    $back_url = admin_url('admin.php?page=landing-config-leads&status=' . $return_status);
    ?>
    <div class="wrap">
        <h1>Массовая смена статуса</h1>
        <p>Выбрано заявок: <strong><?php echo count($lead_ids); ?></strong>. Выберите целевой статус и комментарий (опционально). Комментарий будет одинаковым у всех выбранных заявок в истории.</p>

        <form method="post" action="<?php echo esc_url(admin_url('admin-post.php')); ?>" style="background:#fff; padding:20px; border:1px solid #c3c4c7; border-radius:4px; max-width:600px;">
            <?php wp_nonce_field('landing_leads_bulk_status'); ?>
            <input type="hidden" name="action" value="landing_leads_bulk_status">
            <input type="hidden" name="return_status" value="<?php echo esc_attr($return_status); ?>">
            <?php foreach ($lead_ids as $id): ?>
                <input type="hidden" name="lead_ids[]" value="<?php echo (int) $id; ?>">
            <?php endforeach; ?>

            <p>
                <label><strong>Новый статус:</strong></label><br>
                <select name="to_status" required style="width:100%;">
                    <option value="">— Выберите —</option>
                    <?php foreach ($vocab as $v): ?>
                        <option value="<?php echo esc_attr($v['slug']); ?>"><?php echo esc_html($v['label']); ?></option>
                    <?php endforeach; ?>
                </select>
            </p>
            <p>
                <label><strong>Комментарий (опционально):</strong></label><br>
                <textarea name="comment" rows="3" style="width:100%;" placeholder="Массовая обработка ботов / повторных заявок / ..."></textarea>
            </p>
            <p>
                <button type="submit" class="button button-primary">Применить ко всем выбранным</button>
                <a href="<?php echo esc_url($back_url); ?>" class="button" style="margin-left:8px;">Отмена</a>
            </p>
        </form>
    </div>
    <?php
}

/**
 * Bulk apply: цикл по выбранным заявкам с per-lead транзакцией.
 * Ошибка одной заявки не блокирует остальные.
 * Lessons из B19.5: throw RuntimeException внутри try → catch ROLLBACK; wp_die вне try;
 * $wpdb->update проверяется === false.
 */
function handle_bulk_status(): void {
    if (!current_user_can('manage_options')) { wp_die('No.', 403); }
    check_admin_referer('landing_leads_bulk_status');

    $lead_ids = array_map('intval', (array) ($_POST['lead_ids'] ?? []));
    $lead_ids = array_values(array_filter($lead_ids, fn($i) => $i > 0));
    $to_status = sanitize_key($_POST['to_status'] ?? '');
    $comment = sanitize_textarea_field($_POST['comment'] ?? '');
    $return_status = sanitize_key($_POST['return_status'] ?? 'all');
    $blog_id = get_current_blog_id();

    if (empty($lead_ids) || $to_status === '') {
        wp_safe_redirect(admin_url('admin.php?page=landing-config-leads&status=' . $return_status . '&bulk_error=missing_params'));
        exit;
    }
    if (resolve_lead_status($to_status, $blog_id) === null) {
        wp_die('Статус не существует в словаре.', 400);
    }

    global $wpdb;
    $table = get_leads_table_name();
    $user_id = get_current_user_id() ?: null;
    $comment_value = $comment !== '' ? $comment : null;

    $updated = 0;
    $failed = 0;
    foreach ($lead_ids as $lid) {
        $current = $wpdb->get_var($wpdb->prepare("SELECT processed_status FROM `$table` WHERE id = %d", $lid));
        if ($current === null) { $failed++; continue; }
        $from_status = (string) $current;

        // Per-lead транзакция: throw внутри try → catch ROLLBACK + counter++.
        // Никаких wp_die внутри try (lesson B19.5: WP_Die_Exception ловился catch и портил поток).
        $wpdb->query('START TRANSACTION');
        try {
            $log_id = log_status_change($lid, $from_status !== '' ? $from_status : null, $to_status, $user_id, $comment_value);
            if ($log_id === 0) {
                throw new \RuntimeException('log_status_change returned 0 (whitelist?)');
            }
            $upd = $wpdb->update($table, ['processed_status' => $to_status], ['id' => $lid], ['%s'], ['%d']);
            if ($upd === false) {
                throw new \RuntimeException('wpdb->update failed: ' . $wpdb->last_error);
            }
            $wpdb->query('COMMIT');
            $updated++;
        } catch (\Throwable $e) {
            $wpdb->query('ROLLBACK');
            error_log('[landing-config] bulk_status lead_id=' . $lid . ' failed: ' . $e->getMessage());
            $failed++;
        }
    }

    $redirect = admin_url('admin.php?page=landing-config-leads&status=' . $return_status . '&bulk_updated=' . $updated . ($failed > 0 ? '&bulk_failed=' . $failed : ''));
    wp_safe_redirect($redirect);
    exit;
}

/**
 * Bulk delete: удаляет выбранные заявки и их лог статусов.
 * Каждая заявка в отдельной транзакции — ошибка одной не блокирует остальные.
 */
function handle_bulk_delete(): void {
    if (!current_user_can('manage_options')) { wp_die('No.', 403); }
    check_admin_referer('landing_leads_bulk_delete');

    $lead_ids = array_map('intval', (array) ($_POST['lead_ids'] ?? []));
    $lead_ids = array_values(array_filter($lead_ids, fn($i) => $i > 0));
    $return_status = sanitize_key($_POST['return_status'] ?? 'all');

    if (empty($lead_ids)) {
        wp_safe_redirect(admin_url('admin.php?page=landing-config-leads&status=' . $return_status . '&bulk_error=no_selection'));
        exit;
    }

    global $wpdb;
    $table     = get_leads_table_name();
    $log_table = get_lead_status_log_table_name();

    $deleted = 0;
    $failed  = 0;
    foreach ($lead_ids as $lid) {
        $wpdb->query('START TRANSACTION');
        try {
            $del_log = $wpdb->delete($log_table, ['lead_id' => $lid], ['%d']);
            if ($del_log === false) throw new \RuntimeException('log delete failed: ' . $wpdb->last_error);
            $del = $wpdb->delete($table, ['id' => $lid], ['%d']);
            if ($del === false) throw new \RuntimeException('lead delete failed: ' . $wpdb->last_error);
            if ($del === 0) { $wpdb->query('ROLLBACK'); $failed++; continue; }
            $wpdb->query('COMMIT');
            $deleted++;
        } catch (\Throwable $e) {
            $wpdb->query('ROLLBACK');
            error_log('[landing-config] bulk_delete lead_id=' . $lid . ' failed: ' . $e->getMessage());
            $failed++;
        }
    }

    $redirect = admin_url('admin.php?page=landing-config-leads&status=' . $return_status . '&bulk_deleted=' . $deleted . ($failed > 0 ? '&bulk_failed=' . $failed : ''));
    wp_safe_redirect($redirect);
    exit;
}

/**
 * Single-lead delete from detail page.
 */
function handle_single_delete(): void {
    if (!current_user_can('manage_options')) { wp_die('No.', 403); }
    $lead_id = (int) ($_GET['lead_id'] ?? 0);
    if ($lead_id <= 0) { wp_die('Invalid lead_id', 400); }
    check_admin_referer('landing_lead_delete_' . $lead_id);

    global $wpdb;
    $table     = get_leads_table_name();
    $log_table = get_lead_status_log_table_name();

    $wpdb->query('START TRANSACTION');
    try {
        $del_log = $wpdb->delete($log_table, ['lead_id' => $lead_id], ['%d']);
        if ($del_log === false) throw new \RuntimeException($wpdb->last_error);
        $del = $wpdb->delete($table, ['id' => $lead_id], ['%d']);
        if ($del === false) throw new \RuntimeException($wpdb->last_error);
        $wpdb->query('COMMIT');
    } catch (\Throwable $e) {
        $wpdb->query('ROLLBACK');
        wp_die('Ошибка удаления. Подробности в debug.log.', 500);
    }

    wp_safe_redirect(admin_url('admin.php?page=landing-config-leads&deleted=1'));
    exit;
}
