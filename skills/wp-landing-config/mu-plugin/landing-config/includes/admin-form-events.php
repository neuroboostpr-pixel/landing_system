<?php
namespace LandingConfig\Admin\FormEvents;

if (!defined('ABSPATH')) { exit; }

use function LandingConfig\DB\get_form_events_table_name;
use function LandingConfig\DB\get_leads_table_name;

add_action('admin_menu', function (): void {
    add_submenu_page(
        'landing-config',
        'События форм',
        'События форм',
        'manage_options',
        'landing-config-form-events',
        __NAMESPACE__ . '\\render_page'
    );
});

function render_page(): void {
    if (!current_user_can('manage_options')) {
        wp_die('Insufficient permissions');
    }

    global $wpdb;
    $table = get_form_events_table_name();
    $leads_table = get_leads_table_name();
    $per_page = 50;
    $page = max(1, (int) ($_GET['paged'] ?? 1));
    $offset = ($page - 1) * $per_page;

    // The table name comes from the trusted current WordPress blog prefix.
    $total = (int) $wpdb->get_var("SELECT COUNT(*) FROM `$table`");
    $rows = $wpdb->get_results($wpdb->prepare(
        "SELECT events.*,
            (SELECT MAX(saved.id) FROM `$leads_table` saved
             WHERE saved.submission_id = events.submission_id) AS lead_id
         FROM `$table` events
         ORDER BY events.created_at DESC, events.id DESC LIMIT %d OFFSET %d",
        $per_page,
        $offset
    ), ARRAY_A);

    $base_url = admin_url('admin.php?page=landing-config-form-events');
    ?>
    <div class="wrap">
        <h1>События форм</h1>
        <p style="color:#646970;max-width:900px;">
            Анонимный технический журнал показывает путь формы до основной отправки.
            Он хранит только разрешённые метки и автоматически очищается через 30 дней.
            Дата и ID показывают порядок прихода на сервер, а «Шаг браузера» восстанавливает
            исходный порядок действий, даже если сетевые запросы пришли не по очереди.
        </p>

        <table class="wp-list-table widefat striped" style="font-size:12px;">
            <thead>
                <tr>
                    <th>ID</th>
                    <th>Дата</th>
                    <th>Шаг браузера</th>
                    <th>Submission ID</th>
                    <th>Заявка</th>
                    <th>Событие</th>
                    <th>Деталь</th>
                    <th>Форма</th>
                    <th>Бренд</th>
                    <th>CTA</th>
                    <th>Страница</th>
                    <th>UTM</th>
                </tr>
            </thead>
            <tbody>
            <?php if ($rows === []): ?>
                <tr><td colspan="12"><em>Событий пока нет.</em></td></tr>
            <?php else: foreach ($rows as $row): ?>
                <tr>
                    <td><?php echo (int) $row['id']; ?></td>
                    <td style="white-space:nowrap;"><?php echo esc_html($row['created_at']); ?></td>
                    <td><?php
                        echo $row['event_sequence'] !== null && $row['event_sequence'] !== ''
                            ? (int) $row['event_sequence']
                            : '—';
                    ?></td>
                    <td style="font-family:monospace;"><?php echo esc_html($row['submission_id']); ?></td>
                    <td><?php if (!empty($row['lead_id'])):
                        $lead_url = admin_url('admin.php?page=landing-config-lead-detail&id=' . (int) $row['lead_id']);
                    ?>
                        <a href="<?php echo esc_url($lead_url); ?>">#<?php echo (int) $row['lead_id']; ?></a>
                    <?php else: ?>—<?php endif; ?></td>
                    <td><strong><?php echo esc_html($row['event_name']); ?></strong></td>
                    <td><?php echo esc_html($row['event_detail'] ?: '—'); ?></td>
                    <td><?php echo esc_html($row['form_id'] ?: '—'); ?></td>
                    <td><?php echo esc_html($row['brand'] ?: '—'); ?></td>
                    <td><?php echo esc_html($row['cta_key'] ?: '—'); ?></td>
                    <td><?php echo esc_html($row['page_path']); ?></td>
                    <td><?php
                        $utm = array_filter([
                            $row['utm_source'] ? 'src=' . $row['utm_source'] : '',
                            $row['utm_medium'] ? 'med=' . $row['utm_medium'] : '',
                            $row['utm_campaign'] ? 'cmp=' . $row['utm_campaign'] : '',
                        ]);
                        echo esc_html(implode(' ', $utm) ?: '—');
                    ?></td>
                </tr>
            <?php endforeach; endif; ?>
            </tbody>
        </table>

        <?php
        $total_pages = (int) ceil($total / $per_page);
        if ($total_pages > 1) {
            echo '<div class="tablenav"><div class="tablenav-pages">';
            echo paginate_links([
                'base'      => add_query_arg('paged', '%#%', $base_url),
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
