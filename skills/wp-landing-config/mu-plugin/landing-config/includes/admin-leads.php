<?php
namespace LandingConfig\Admin\Leads;

if (!defined('ABSPATH')) { exit; }

use function LandingConfig\DB\get_leads_table_name;

// Replace the __return_null stub from admin-pages.php
add_action('admin_menu', function () {
    global $submenu;
    if (isset($submenu['landing-config'])) {
        foreach ($submenu['landing-config'] as &$item) {
            if ($item[2] === 'landing-config-leads') {
                $item[3] = __NAMESPACE__ . '\\render_page';
            }
        }
    }
}, 99);

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

    $rows = $wpdb->get_results($wpdb->prepare(
        "SELECT * FROM `$table` ORDER BY created_at DESC LIMIT %d OFFSET %d",
        $per_page, $offset
    ), ARRAY_A);
    $total = (int)$wpdb->get_var("SELECT COUNT(*) FROM `$table`");

    $export_url = wp_nonce_url(
        admin_url('admin.php?page=landing-config-leads&action=export_csv'),
        'landing_export_leads'
    );
    ?>
    <div class="wrap">
        <h1>Заявки <a href="<?php echo esc_url($export_url); ?>" class="page-title-action">Экспорт CSV</a></h1>
        <p>Всего заявок: <strong><?php echo (int)$total; ?></strong></p>
        <table class="wp-list-table widefat striped">
            <thead>
                <tr>
                    <th>ID</th><th>Дата</th><th>Имя</th><th>Телефон</th><th>Email</th>
                    <th>Сообщение</th><th>Источник</th><th>UTM</th>
                </tr>
            </thead>
            <tbody>
                <?php if (empty($rows)): ?>
                    <tr><td colspan="8"><em>Заявок пока нет.</em></td></tr>
                <?php else: foreach ($rows as $r): ?>
                    <tr>
                        <td><?php echo (int)$r['id']; ?></td>
                        <td><?php echo esc_html($r['created_at']); ?></td>
                        <td><?php echo esc_html($r['name']); ?></td>
                        <td><?php echo esc_html($r['phone']); ?></td>
                        <td><?php echo esc_html($r['email']); ?></td>
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
        <?php
        $total_pages = (int)ceil($total / $per_page);
        if ($total_pages > 1) {
            echo '<div class="tablenav"><div class="tablenav-pages">';
            echo paginate_links([
                'base'      => add_query_arg('paged', '%#%'),
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
