<?php
namespace LandingConfig\Admin\Leads\Network;

if (!defined('ABSPATH')) { exit; }

use function LandingConfig\DB\get_leads_table_name;

add_action('network_admin_menu', function () {
    add_submenu_page(
        'landing-config-network',
        'Заявки (сеть)',
        'Заявки (все сегменты)',
        'manage_network_options',
        'landing-config-network-leads',
        __NAMESPACE__ . '\\render_page'
    );
});

function render_page(): void {
    if (!current_user_can('manage_network_options')) { wp_die('Insufficient permissions'); }

    $filter_blog = (int)($_GET['blog'] ?? 0);
    $sites = get_sites(['number' => 0]);

    $all_rows = [];
    foreach ($sites as $site) {
        if ($filter_blog && (int)$site->blog_id !== $filter_blog) continue;
        switch_to_blog((int)$site->blog_id);
        try {
            global $wpdb;
            $table = get_leads_table_name();
            $rows = $wpdb->get_results(
                "SELECT id, created_at, name, phone, email, source_block FROM `$table` ORDER BY created_at DESC LIMIT 50",
                ARRAY_A
            );
            foreach ($rows as $r) {
                $r['__blog_id'] = (int)$site->blog_id;
                $r['__host'] = $site->domain;
                $all_rows[] = $r;
            }
        } finally {
            restore_current_blog();
        }
    }
    usort($all_rows, function ($a, $b) {
        return strcmp($b['created_at'], $a['created_at']);
    });
    ?>
    <div class="wrap">
        <h1>Заявки — все сегменты</h1>
        <form method="get" style="margin: 1em 0;">
            <input type="hidden" name="page" value="landing-config-network-leads">
            <label>Фильтр по сегменту:
                <select name="blog">
                    <option value="0">Все сегменты</option>
                    <?php foreach ($sites as $s): ?>
                        <option value="<?php echo (int)$s->blog_id; ?>" <?php selected($filter_blog, (int)$s->blog_id); ?>>
                            <?php echo esc_html($s->domain); ?>
                            (blog_id=<?php echo (int)$s->blog_id; ?>)
                        </option>
                    <?php endforeach; ?>
                </select>
            </label>
            <button type="submit" class="button">Применить</button>
        </form>
        <p>Показано: <strong><?php echo count($all_rows); ?></strong> заявок (последние 50 на сегмент).</p>
        <table class="wp-list-table widefat striped">
            <thead>
                <tr>
                    <th>Сегмент</th><th>ID</th><th>Дата</th><th>Имя</th>
                    <th>Телефон</th><th>Email</th><th>Источник</th>
                </tr>
            </thead>
            <tbody>
                <?php if (empty($all_rows)): ?>
                    <tr><td colspan="7"><em>Нет заявок.</em></td></tr>
                <?php else: foreach ($all_rows as $r): ?>
                    <tr>
                        <td><strong><?php echo esc_html($r['__host']); ?></strong></td>
                        <td><?php echo (int)$r['id']; ?></td>
                        <td><?php echo esc_html($r['created_at']); ?></td>
                        <td><?php echo esc_html($r['name']); ?></td>
                        <td><?php echo esc_html($r['phone']); ?></td>
                        <td><?php echo esc_html($r['email']); ?></td>
                        <td><?php echo esc_html($r['source_block']); ?></td>
                    </tr>
                <?php endforeach; endif; ?>
            </tbody>
        </table>
    </div>
    <?php
}
