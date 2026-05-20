<?php
namespace LandingConfig\Admin\Leads;

if (!defined('ABSPATH')) { exit; }

use function LandingConfig\DB\get_leads_table_name;

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

    $vocab = \LandingConfig\LeadStatuses\list_lead_statuses($blog_id);
    $vocab_by_slug = [];
    foreach ($vocab as $v) $vocab_by_slug[$v['slug']] = $v;

    $export_url = wp_nonce_url(
        admin_url('admin.php?page=landing-config-leads&action=export_csv'),
        'landing_export_leads'
    );
    $base_url = admin_url('admin.php?page=landing-config-leads');
    ?>
    <div class="wrap">
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
                        <th>Сообщение</th><th>Источник</th><th>UTM</th>
                    </tr>
                </thead>
                <tbody>
                    <?php if (empty($rows)): ?>
                        <tr><td colspan="10"><em>Заявок нет.</em></td></tr>
                    <?php else: foreach ($rows as $r):
                        $status_slug = (string) ($r['processed_status'] ?? '');
                        $v = $vocab_by_slug[$status_slug] ?? null;
                        $badge_label = $v ? $v['label'] : ($status_slug !== '' ? $status_slug : '—');
                        $badge_color = $v ? $v['color'] : '#646970';
                        $badge_warn = $v ? '' : ' title="Статус не найден в vocab"';
                        $detail_url = admin_url('admin.php?page=landing-config-lead-detail&id=' . (int) $r['id']);
                    ?>
                        <tr>
                            <th scope="row" class="check-column"><input type="checkbox" name="lead_ids[]" value="<?php echo (int) $r['id']; ?>"></th>
                            <td><?php echo (int) $r['id']; ?></td>
                            <td><?php echo esc_html($r['created_at']); ?></td>
                            <td><a href="<?php echo esc_url($detail_url); ?>"><?php echo esc_html($r['name'] ?: '— без имени —'); ?></a></td>
                            <td><?php echo esc_html($r['phone']); ?></td>
                            <td><?php echo esc_html($r['email']); ?></td>
                            <td><span<?php echo $badge_warn; ?> style="background:<?php echo esc_attr($badge_color); ?>; color:#fff; padding:3px 10px; border-radius:3px; font-size:12px;"><?php echo esc_html($badge_label); ?></span></td>
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
