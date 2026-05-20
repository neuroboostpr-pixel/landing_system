<?php
namespace LandingConfig\Admin\LeadDetail;

if (!defined('ABSPATH')) { exit; }

use function LandingConfig\DB\get_leads_table_name;
use function LandingConfig\LeadStatuses\list_lead_statuses;
use function LandingConfig\LeadStatuses\resolve_lead_status;
use function LandingConfig\LeadStatusLog\log_status_change;
use function LandingConfig\LeadStatusLog\get_status_history;

\add_action('admin_menu', function () {
    // parent=null + hidden slug — страница доступна по прямой ссылке, в меню не показываем
    \add_submenu_page(
        null,
        'Карточка заявки',
        'Карточка заявки',
        'manage_options',
        'landing-config-lead-detail',
        __NAMESPACE__ . '\\render_page'
    );
});

\add_action('admin_post_landing_lead_change_status', __NAMESPACE__ . '\\handle_change_status');

function render_page(): void {
    if (!\current_user_can('manage_options')) { \wp_die('No.', 403); }
    $lead_id = (int) ($_GET['id'] ?? 0);
    if ($lead_id <= 0) { \wp_die('Не указан id заявки.', 400); }

    global $wpdb;
    $table = get_leads_table_name();
    $lead = $wpdb->get_row($wpdb->prepare("SELECT * FROM `$table` WHERE id = %d", $lead_id), ARRAY_A);
    if (!$lead) { \wp_die('Заявка не найдена.', 404); }

    $blog_id = \get_current_blog_id();
    $current_slug = (string) ($lead['processed_status'] ?? '');
    $current_status = resolve_lead_status($current_slug, $blog_id);
    $vocab = list_lead_statuses($blog_id);
    $history = get_status_history($lead_id);
    $back_url = \admin_url('admin.php?page=landing-config-leads');
    ?>
    <div class="wrap">
        <h1>
            <a href="<?php echo \esc_url($back_url); ?>" class="page-title-action">← Назад к списку</a>
            Заявка #<?php echo (int) $lead_id; ?>
        </h1>

        <p style="margin:16px 0;">
            <strong>Текущий статус:</strong>
            <?php if ($current_status): ?>
                <span style="background:<?php echo \esc_attr($current_status['color']); ?>; color:#fff; padding:4px 14px; border-radius:3px; font-size:14px;">
                    <?php echo \esc_html($current_status['label']); ?>
                </span>
            <?php else: ?>
                <span style="background:#646970; color:#fff; padding:4px 14px; border-radius:3px; font-size:14px;" title="Статус не найден в vocab">
                    <?php echo \esc_html($current_slug ?: '—'); ?>
                </span>
            <?php endif; ?>
            <button type="button" class="button button-primary" style="margin-left:12px;" onclick="document.getElementById('change-status-modal').style.display='block'">
                Сменить статус
            </button>
        </p>

        <?php if (isset($_GET['saved'])): ?>
            <div class="notice notice-success is-dismissible"><p>Статус обновлён.</p></div>
        <?php endif; ?>

        <h2>Данные заявки</h2>
        <table class="form-table">
            <tr><th>Дата</th><td><?php echo \esc_html($lead['created_at']); ?></td></tr>
            <tr><th>Имя</th><td><?php echo \esc_html($lead['name'] ?: '—'); ?></td></tr>
            <tr><th>Телефон</th><td><?php echo \esc_html($lead['phone'] ?: '—'); ?></td></tr>
            <tr><th>Email</th><td><?php echo \esc_html($lead['email'] ?: '—'); ?></td></tr>
            <tr><th>Сообщение</th><td><?php echo nl2br(\esc_html($lead['message'] ?? '')); ?></td></tr>
            <tr><th>Источник</th><td><?php echo \esc_html($lead['source_block'] ?: '—'); ?></td></tr>
            <tr><th>UTM source</th><td><?php echo \esc_html($lead['utm_source'] ?: '—'); ?></td></tr>
            <tr><th>UTM medium</th><td><?php echo \esc_html($lead['utm_medium'] ?: '—'); ?></td></tr>
            <tr><th>UTM campaign</th><td><?php echo \esc_html($lead['utm_campaign'] ?: '—'); ?></td></tr>
            <tr><th>UTM term</th><td><?php echo \esc_html($lead['utm_term'] ?: '—'); ?></td></tr>
            <tr><th>UTM content</th><td><?php echo \esc_html($lead['utm_content'] ?: '—'); ?></td></tr>
            <tr><th>IP</th><td><code><?php echo \esc_html($lead['ip']); ?></code></td></tr>
            <tr><th>User agent</th><td><code style="font-size:11px;"><?php echo \esc_html($lead['user_agent'] ?? ''); ?></code></td></tr>
        </table>

        <h2 style="margin-top:32px;">История изменений</h2>
        <?php if (empty($history)): ?>
            <p style="color:#646970;"><em>Нет записей. Первая запись появится после первой смены статуса.</em></p>
        <?php else: ?>
            <table class="wp-list-table widefat striped">
                <thead>
                    <tr><th style="width:160px;">Когда</th><th style="width:180px;">Кто</th><th>Переход</th><th>Комментарий</th></tr>
                </thead>
                <tbody>
                    <?php foreach ($history as $h):
                        $user_label = $h['user_id'] ? (function() use ($h) {
                            $u = \get_userdata((int) $h['user_id']);
                            return $u ? $u->display_name : 'user#' . (int) $h['user_id'];
                        })() : '— системное —';
                        $from_v = $h['from_status'] ? resolve_lead_status((string) $h['from_status'], $blog_id) : null;
                        $to_v = resolve_lead_status((string) $h['to_status'], $blog_id);
                    ?>
                        <tr>
                            <td><?php echo \esc_html($h['created_at']); ?></td>
                            <td><?php echo \esc_html($user_label); ?></td>
                            <td>
                                <?php if ($from_v): ?>
                                    <span style="background:<?php echo \esc_attr($from_v['color']); ?>; color:#fff; padding:2px 8px; border-radius:3px; font-size:11px;"><?php echo \esc_html($from_v['label']); ?></span>
                                <?php elseif ($h['from_status']): ?>
                                    <code><?php echo \esc_html($h['from_status']); ?></code>
                                <?php else: ?>
                                    <em>— создана —</em>
                                <?php endif; ?>
                                →
                                <?php if ($to_v): ?>
                                    <span style="background:<?php echo \esc_attr($to_v['color']); ?>; color:#fff; padding:2px 8px; border-radius:3px; font-size:11px;"><?php echo \esc_html($to_v['label']); ?></span>
                                <?php else: ?>
                                    <code><?php echo \esc_html($h['to_status']); ?></code>
                                <?php endif; ?>
                            </td>
                            <td><?php echo nl2br(\esc_html($h['comment'] ?? '')); ?></td>
                        </tr>
                    <?php endforeach; ?>
                </tbody>
            </table>
        <?php endif; ?>

        <!-- Modal: смена статуса -->
        <div id="change-status-modal" style="display:none; position:fixed; top:0; left:0; right:0; bottom:0; background:rgba(0,0,0,0.5); z-index:9999;" onclick="if(event.target===this)this.style.display='none'">
            <div style="background:#fff; max-width:520px; margin:80px auto; padding:24px; border-radius:6px;">
                <h2 style="margin-top:0;">Сменить статус</h2>
                <form method="post" action="<?php echo \esc_url(\admin_url('admin-post.php')); ?>">
                    <?php \wp_nonce_field('landing_lead_change_status_' . $lead_id); ?>
                    <input type="hidden" name="action" value="landing_lead_change_status">
                    <input type="hidden" name="lead_id" value="<?php echo (int) $lead_id; ?>">
                    <p>
                        <label><strong>Новый статус:</strong></label><br>
                        <select name="to_status" required style="width:100%;">
                            <?php foreach ($vocab as $v): ?>
                                <option value="<?php echo \esc_attr($v['slug']); ?>" <?php \selected($v['slug'], $current_slug); ?>>
                                    <?php echo \esc_html($v['label']); ?>
                                </option>
                            <?php endforeach; ?>
                        </select>
                    </p>
                    <p>
                        <label><strong>Комментарий (опционально):</strong></label><br>
                        <textarea name="comment" rows="4" style="width:100%;" placeholder="Перезвонил, договорились на встречу в среду."></textarea>
                    </p>
                    <p>
                        <button type="submit" class="button button-primary">Сохранить</button>
                        <button type="button" class="button" onclick="document.getElementById('change-status-modal').style.display='none'">Отмена</button>
                    </p>
                </form>
            </div>
        </div>
    </div>
    <?php
}

function handle_change_status(): void {
    if (!\current_user_can('manage_options')) { \wp_die('No.', 403); }
    $lead_id = (int) ($_POST['lead_id'] ?? 0);
    if ($lead_id <= 0) \wp_die('Invalid lead_id', 400);
    \check_admin_referer('landing_lead_change_status_' . $lead_id);

    $to_status = \sanitize_key($_POST['to_status'] ?? '');
    $comment = \sanitize_textarea_field($_POST['comment'] ?? '');
    $blog_id = \get_current_blog_id();

    // Whitelist
    if (resolve_lead_status($to_status, $blog_id) === null) {
        \wp_die('Статус не существует в словаре.', 400);
    }

    global $wpdb;
    $table = get_leads_table_name();
    $current = $wpdb->get_var($wpdb->prepare("SELECT processed_status FROM `$table` WHERE id = %d", $lead_id));
    if ($current === null) \wp_die('Заявка не найдена.', 404);
    $from_status = (string) $current;

    // Транзакция: log + UPDATE
    $wpdb->query('START TRANSACTION');
    try {
        $log_id = log_status_change($lead_id, $from_status !== '' ? $from_status : null, $to_status, \get_current_user_id() ?: null, $comment !== '' ? $comment : null);
        if ($log_id === 0) {
            $wpdb->query('ROLLBACK');
            \wp_die('Не удалось записать историю.', 500);
        }
        $wpdb->update($table, ['processed_status' => $to_status], ['id' => $lead_id], ['%s'], ['%d']);
        $wpdb->query('COMMIT');
    } catch (\Throwable $e) {
        $wpdb->query('ROLLBACK');
        \error_log('[landing-config] handle_change_status failed: ' . $e->getMessage());
        \wp_die('Ошибка сохранения. Подробности в debug.log.', 500);
    }

    \wp_safe_redirect(\admin_url('admin.php?page=landing-config-lead-detail&id=' . $lead_id . '&saved=1'));
    exit;
}
