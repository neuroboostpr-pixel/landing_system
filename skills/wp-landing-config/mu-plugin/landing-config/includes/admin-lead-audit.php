<?php
namespace LandingConfig\Admin\LeadAudit;

if (!defined('ABSPATH')) { exit; }

use function LandingConfig\DB\get_lead_audit_table_name;
use function LandingConfig\DB\get_leads_table_name;

add_action('admin_menu', function () {
    add_submenu_page(
        'landing-config',
        'Лог заявок',
        'Лог заявок',
        'manage_options',
        'landing-config-lead-audit',
        __NAMESPACE__ . '\\render_page'
    );
});

add_action('admin_post_landing_audit_bulk_promote', __NAMESPACE__ . '\\handle_bulk_promote');

// Метки причин блокировки
function blocked_label(string $reason): string {
    $labels = [
        'honeypot'        => 'Honeypot',
        'rate_limit'      => 'Rate limit',
        'pd_consent'      => 'Нет согласия',
        'recaptcha_failed' => 'reCAPTCHA',
        'validation'      => 'Валидация',
        'db_error'        => 'Ошибка БД',
    ];
    return $labels[$reason] ?? esc_html($reason);
}

function render_page(): void {
    if (!current_user_can('manage_options')) { wp_die('Insufficient permissions'); }

    global $wpdb;
    $audit_table = get_lead_audit_table_name();
    $per_page = 30;
    $page = max(1, (int)($_GET['paged'] ?? 1));
    $offset = ($page - 1) * $per_page;

    // Фильтр: all / ok / blocked
    $filter = sanitize_key($_GET['filter'] ?? 'all');
    $where = '';
    if ($filter === 'ok') {
        $where = 'WHERE lead_id IS NOT NULL';
    } elseif ($filter === 'blocked') {
        $where = 'WHERE lead_id IS NULL';
    }

    // phpcs:ignore WordPress.DB.PreparedSQL.InterpolatedNotPrepared, WordPress.DB.DirectDatabaseQuery.DirectQuery
    $total = (int) $wpdb->get_var("SELECT COUNT(*) FROM `$audit_table` $where");
    // phpcs:ignore WordPress.DB.PreparedSQL.InterpolatedNotPrepared, WordPress.DB.DirectDatabaseQuery.DirectQuery
    $rows = $wpdb->get_results($wpdb->prepare(
        "SELECT * FROM `$audit_table` $where ORDER BY created_at DESC LIMIT %d OFFSET %d",
        $per_page, $offset
    ), ARRAY_A);

    // Счётчики для вкладок
    // phpcs:ignore WordPress.DB.DirectDatabaseQuery.DirectQuery
    $count_ok      = (int) $wpdb->get_var("SELECT COUNT(*) FROM `$audit_table` WHERE lead_id IS NOT NULL");
    // phpcs:ignore WordPress.DB.DirectDatabaseQuery.DirectQuery
    $count_blocked = (int) $wpdb->get_var("SELECT COUNT(*) FROM `$audit_table` WHERE lead_id IS NULL");
    $count_all     = $count_ok + $count_blocked;

    $base_url = admin_url('admin.php?page=landing-config-lead-audit');

    // Результат bulk-переноса
    $promoted = isset($_GET['promoted']) ? (int) $_GET['promoted'] : null;
    $skipped  = isset($_GET['skipped'])  ? (int) $_GET['skipped']  : null;
    ?>
    <div class="wrap">
        <h1>Лог заявок (аудит)</h1>
        <p style="color:#646970;">Сюда попадают <strong>все</strong> попытки отправки формы — до любых проверок. Колонка <strong>Статус</strong> показывает прошла ли заявка в основную таблицу.</p>

        <?php if ($promoted !== null): ?>
            <div class="notice notice-success is-dismissible">
                <p>Перенесено в заявки: <strong><?php echo $promoted; ?></strong>.
                <?php if ($skipped > 0): ?> Пропущено (уже есть lead_id): <strong><?php echo $skipped; ?></strong>.<?php endif; ?></p>
            </div>
        <?php endif; ?>

        <?php if (isset($_GET['promote_error'])): ?>
            <div class="notice notice-error is-dismissible"><p>Ошибка переноса: <code><?php echo esc_html($_GET['promote_error']); ?></code></p></div>
        <?php endif; ?>

        <ul class="subsubsub">
            <li><a href="<?php echo esc_url(add_query_arg('filter', 'all', $base_url)); ?>" class="<?php echo $filter === 'all' ? 'current' : ''; ?>">Все <span class="count">(<?php echo $count_all; ?>)</span></a></li>
            | <li><a href="<?php echo esc_url(add_query_arg('filter', 'ok', $base_url)); ?>" class="<?php echo $filter === 'ok' ? 'current' : ''; ?>" style="color:#46b450;">Сохранены <span class="count">(<?php echo $count_ok; ?>)</span></a></li>
            | <li><a href="<?php echo esc_url(add_query_arg('filter', 'blocked', $base_url)); ?>" class="<?php echo $filter === 'blocked' ? 'current' : ''; ?>" style="color:#b32d2e;">Заблокированы <span class="count">(<?php echo $count_blocked; ?>)</span></a></li>
        </ul>
        <div style="clear:both;margin-bottom:10px;"></div>

        <form method="post" action="<?php echo esc_url(admin_url('admin-post.php')); ?>">
            <?php wp_nonce_field('landing_audit_bulk_promote'); ?>
            <input type="hidden" name="action" value="landing_audit_bulk_promote">
            <input type="hidden" name="filter" value="<?php echo esc_attr($filter); ?>">

            <div class="tablenav top">
                <div class="alignleft actions bulkactions">
                    <select name="bulk_action">
                        <option value="">— Действие —</option>
                        <option value="promote">Перенести в Заявки</option>
                    </select>
                    <button type="submit" class="button action">Применить</button>
                </div>
                <div class="alignright" style="padding:6px 0;">
                    <em style="color:#646970;">Выбрано только заблокированных — уже сохранённые пропускаются автоматически</em>
                </div>
            </div>

            <table class="wp-list-table widefat striped" style="font-size:13px;">
                <thead>
                    <tr>
                        <td class="check-column"><input type="checkbox" id="cb-select-all-audit"></td>
                        <th style="width:40px;">ID</th>
                        <th style="width:140px;">Дата</th>
                        <th style="width:110px;">Статус</th>
                        <th>Имя</th>
                        <th>Телефон</th>
                        <th>Email</th>
                        <th>Сообщение</th>
                        <th style="width:100px;">Источник / UTM</th>
                        <th style="width:80px;">IP</th>
                        <th>Детали блокировки</th>
                    </tr>
                </thead>
                <tbody>
                <?php if (empty($rows)): ?>
                    <tr><td colspan="11"><em>Записей нет.</em></td></tr>
                <?php else: foreach ($rows as $r):
                    $saved = $r['lead_id'] !== null && $r['lead_id'] !== '';
                    if ($saved) {
                        $status_label = '✓ Сохранена #' . (int)$r['lead_id'];
                        $status_color = '#46b450';
                        $row_style = '';
                    } else {
                        $reason = (string)($r['blocked_by'] ?? '');
                        $status_label = blocked_label($reason);
                        $status_color = '#b32d2e';
                        $row_style = 'background:#fff8f8;';
                    }
                ?>
                    <tr style="<?php echo esc_attr($row_style); ?>">
                        <th scope="row" class="check-column">
                            <input type="checkbox" name="audit_ids[]" value="<?php echo (int)$r['id']; ?>">
                        </th>
                        <td><?php echo (int)$r['id']; ?></td>
                        <td style="white-space:nowrap;"><?php echo esc_html($r['created_at']); ?></td>
                        <td>
                            <span style="background:<?php echo esc_attr($status_color); ?>;color:#fff;padding:2px 8px;border-radius:3px;font-size:11px;white-space:nowrap;">
                                <?php echo esc_html($status_label); ?>
                            </span>
                        </td>
                        <td><?php echo esc_html($r['name'] ?: '—'); ?></td>
                        <td style="white-space:nowrap;"><?php echo esc_html($r['phone'] ?: '—'); ?></td>
                        <td><?php echo esc_html($r['email'] ?: '—'); ?></td>
                        <td><?php echo esc_html(mb_substr((string)($r['message'] ?? ''), 0, 60)); ?></td>
                        <td style="font-size:11px;">
                            <?php
                            $parts = array_filter([
                                $r['source_block'] ? esc_html(mb_substr($r['source_block'], 0, 40)) : '',
                                $r['utm_source']   ? 'src=' . esc_html($r['utm_source']) : '',
                                $r['utm_medium']   ? 'med=' . esc_html($r['utm_medium']) : '',
                            ]);
                            echo implode('<br>', $parts) ?: '—';
                            ?>
                        </td>
                        <td style="font-size:11px;font-family:monospace;"><?php echo esc_html($r['ip']); ?></td>
                        <td style="font-size:11px;color:#646970;">
                            <?php
                            if (!$saved && $r['block_detail']) {
                                echo esc_html($r['block_detail']);
                            } elseif ($saved) {
                                echo '—';
                            } else {
                                echo '<em>нет деталей</em>';
                            }
                            ?>
                        </td>
                    </tr>
                <?php endforeach; endif; ?>
                </tbody>
            </table>

            <script>
            document.getElementById('cb-select-all-audit')?.addEventListener('change', function() {
                document.querySelectorAll('input[name="audit_ids[]"]').forEach(cb => cb.checked = this.checked);
            });
            </script>
        </form>

        <?php
        $total_pages = (int) ceil($total / $per_page);
        if ($total_pages > 1) {
            echo '<div class="tablenav"><div class="tablenav-pages">';
            echo paginate_links([
                'base'      => add_query_arg(['filter' => $filter, 'paged' => '%#%'], $base_url),
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

/**
 * Bulk-перенос записей из аудит-лога в основную таблицу заявок.
 * Строки с уже заполненным lead_id пропускаются (не дублируем).
 */
function handle_bulk_promote(): void {
    if (!current_user_can('manage_options')) { wp_die('No.', 403); }
    check_admin_referer('landing_audit_bulk_promote');

    $bulk_action = sanitize_key($_POST['bulk_action'] ?? '');
    $audit_ids   = array_map('intval', (array)($_POST['audit_ids'] ?? []));
    $audit_ids   = array_values(array_filter($audit_ids, fn($i) => $i > 0));
    $filter      = sanitize_key($_POST['filter'] ?? 'all');

    $back = admin_url('admin.php?page=landing-config-lead-audit&filter=' . $filter);

    if ($bulk_action !== 'promote') {
        wp_safe_redirect($back);
        exit;
    }
    if (empty($audit_ids)) {
        wp_safe_redirect($back . '&promote_error=no_selection');
        exit;
    }

    global $wpdb;
    $audit_table = get_lead_audit_table_name();
    $leads_table = get_leads_table_name();

    $promoted = 0;
    $skipped  = 0;

    foreach ($audit_ids as $audit_id) {
        // phpcs:ignore WordPress.DB.PreparedSQL.NotPrepared, WordPress.DB.DirectDatabaseQuery.DirectQuery
        $row = $wpdb->get_row($wpdb->prepare("SELECT * FROM `$audit_table` WHERE id = %d", $audit_id), ARRAY_A);
        if (!$row) { $skipped++; continue; }

        // Уже есть lead_id — пропускаем
        if ($row['lead_id'] !== null && $row['lead_id'] !== '') {
            $skipped++;
            continue;
        }

        // Вставляем в основную таблицу
        $inserted = $wpdb->insert($leads_table, [
            'submission_id'    => (string)($row['submission_id'] ?? '') ?: null,
            'name'             => (string)($row['name'] ?? ''),
            'phone'            => (string)($row['phone'] ?? ''),
            'email'            => (string)($row['email'] ?? ''),
            'message'          => (string)($row['message'] ?? ''),
            'source_block'     => (string)($row['source_block'] ?? ''),
            'utm_source'       => (string)($row['utm_source'] ?? ''),
            'utm_medium'       => (string)($row['utm_medium'] ?? ''),
            'utm_campaign'     => (string)($row['utm_campaign'] ?? ''),
            'utm_term'         => '',
            'utm_content'      => '',
            'roistat_visit'    => (string)($row['roistat_visit'] ?? ''),
            'ip'               => (string)($row['ip'] ?? ''),
            'user_agent'       => (string)($row['user_agent'] ?? ''),
            'created_at'       => (string)($row['created_at']),
            'processed_status' => 'pending',
            'pd_consent_granted_at' => ($row['pd_consent'] === '1') ? (string)$row['created_at'] : null,
            'recaptcha_score'  => null,
        ]);

        if ($inserted) {
            $new_lead_id = (int)$wpdb->insert_id;
            // Обновляем audit: теперь lead_id заполнен, blocked_by очищаем
            $wpdb->update(
                $audit_table,
                ['lead_id' => $new_lead_id, 'blocked_by' => null, 'block_detail' => 'promoted_manually'],
                ['id' => $audit_id],
                ['%d', '%s', '%s'],
                ['%d']
            );
            $promoted++;
        } else {
            error_log('[landing-config] audit promote: insert failed for audit_id=' . $audit_id . ' err=' . $wpdb->last_error);
        }
    }

    wp_safe_redirect($back . '&promoted=' . $promoted . '&skipped=' . $skipped);
    exit;
}
