<?php
namespace LandingConfig\MonitoringAdmin;

if (!defined('ABSPATH')) { exit; }

const PAGE_SLUG = 'landing-config-monitoring';
const TEST_ALERT_ACTION = 'lp_monitor_test_alert';
const CONTROLLED_FAILURE_ACTION = 'lp_fallback_arm_controlled_failure';

add_action('admin_menu', static function (): void {
    add_submenu_page('landing-config', 'Мониторинг заявок', 'Мониторинг заявок',
        'manage_options', PAGE_SLUG, __NAMESPACE__ . '\\render_page');
});
add_action('admin_post_' . TEST_ALERT_ACTION, __NAMESPACE__ . '\\handle_test_alert');
add_action('admin_post_' . CONTROLLED_FAILURE_ACTION, __NAMESPACE__ . '\\handle_arm_controlled_failure');

function yes_no(bool $value): string { return $value ? 'yes' : 'no'; }

function render_page(): void {
    if (!current_user_can('manage_options')) { wp_die('Forbidden', 403); }
    global $wpdb;
    $status = \LandingConfig\Monitoring\configuration_status();
    $heartbeat = (int)get_option(\LandingConfig\Monitoring\HEARTBEAT_OPTION, 0);
    $external = \LandingConfig\Monitoring\external_health_state();
    $alerts_table = \LandingConfig\DB\get_monitor_alerts_table_name();
    $delivery_table = \LandingConfig\DB\get_lead_log_table_name();
    try {
        $incident_count = (int)$wpdb->get_var("SELECT COUNT(*) FROM `{$alerts_table}` WHERE resolved_at IS NULL");
        $delivery_queued = (int)$wpdb->get_var("SELECT COUNT(*) FROM `{$delivery_table}` WHERE status='queued'");
        $delivery_sending = (int)$wpdb->get_var("SELECT COUNT(*) FROM `{$delivery_table}` WHERE status='sending'");
        $delivery_unknown = (int)$wpdb->get_var("SELECT COUNT(*) FROM `{$delivery_table}` WHERE status='unknown'");
        $recent = $wpdb->get_results("SELECT id,incident_kind,severity,safe_status,safe_category,occurrence_count,first_seen_at,last_seen_at,telegram_status FROM `{$alerts_table}` ORDER BY id DESC LIMIT 20", ARRAY_A);
    } catch (\Throwable $ignored) {
        $incident_count = $delivery_queued = $delivery_sending = $delivery_unknown = 0;
        $recent = [];
    }
    ?>
    <div class="wrap">
      <h1>Мониторинг заявок</h1>
      <p>Открытые инциденты: <?php echo (int)$incident_count; ?>. Heartbeat: <?php echo (int)$heartbeat; ?>.</p>
      <p>Delivery queued=<?php echo (int)$delivery_queued; ?> sending=<?php echo (int)$delivery_sending; ?> unknown=<?php echo (int)$delivery_unknown; ?>.</p>
      <p>External last slot=<?php echo (int)$external['last_processed_slot']; ?> accepted_at=<?php echo (int)$external['accepted_at']; ?>.</p>
      <table class="widefat striped"><tbody>
      <?php foreach ($status as $key => $value): ?>
        <tr><th><?php echo esc_html((string)$key); ?></th><td><?php echo esc_html(is_bool($value) ? yes_no($value) : (string)(int)$value); ?></td></tr>
      <?php endforeach; ?>
      </tbody></table>

      <h2>Последние безопасные инциденты</h2>
      <table class="widefat striped"><tbody>
      <?php foreach (is_array($recent) ? $recent : [] as $row): ?>
        <tr><?php foreach (['id','incident_kind','severity','safe_status','safe_category','occurrence_count','first_seen_at','last_seen_at','telegram_status'] as $column): ?>
          <td><?php echo esc_html((string)($row[$column] ?? '')); ?></td>
        <?php endforeach; ?></tr>
      <?php endforeach; ?>
      </tbody></table>

      <form method="post" action="<?php echo esc_url(admin_url('admin-post.php')); ?>">
        <?php wp_nonce_field(TEST_ALERT_ACTION); ?>
        <input type="hidden" name="action" value="<?php echo esc_attr(TEST_ALERT_ACTION); ?>">
        <button type="submit" class="button">Отправить [TEST — DO NOT CONTACT]</button>
      </form>

      <?php if (defined('LP_FALLBACK_TEST_MODE') && LP_FALLBACK_TEST_MODE === true): ?>
      <form method="post" action="<?php echo esc_url(admin_url('admin-post.php')); ?>">
        <?php wp_nonce_field(CONTROLLED_FAILURE_ACTION); ?>
        <input type="hidden" name="action" value="<?php echo esc_attr(CONTROLLED_FAILURE_ACTION); ?>">
        <button type="submit" class="button">lp_fallback_arm_controlled_failure</button>
      </form>
      <?php endif; ?>
    </div>
    <?php
}

function require_admin_post(string $action): void {
    if (($_SERVER['REQUEST_METHOD'] ?? '') !== 'POST') { wp_die('Method not allowed', 405); }
    if (!current_user_can('manage_options')) { wp_die('Forbidden', 403); }
    check_admin_referer($action);
}

function safe_admin_redirect(): void {
    nocache_headers();
    header('Cache-Control: no-store, private, max-age=0', true);
    header('Referrer-Policy: no-referrer', true);
}

function handle_test_alert(): void {
    require_admin_post(TEST_ALERT_ACTION);
    \LandingConfig\Monitoring\record_incident('test_alert', 'info', null, null, null, '',
        'test', 'test');
    safe_admin_redirect();
    wp_safe_redirect(admin_url('admin.php?page=' . PAGE_SLUG), 303);
}

function handle_arm_controlled_failure(): void {
    require_admin_post(CONTROLLED_FAILURE_ACTION);
    if (!defined('LP_FALLBACK_TEST_MODE') || LP_FALLBACK_TEST_MODE !== true) { wp_die('Not found', 404); }
    $user_id = get_current_user_id();
    if ($user_id <= 0) { wp_die('Forbidden', 403); }
    set_transient('lp_fallback_controlled_failure_' . $user_id, 'armed', 60);
    safe_admin_redirect();
    wp_safe_redirect(home_url('/'), 303);
}

function consume_controlled_failure_claim(?int $user_id = null): ?array {
    if (!defined('LP_FALLBACK_TEST_MODE') || LP_FALLBACK_TEST_MODE !== true
        || !is_user_logged_in() || !current_user_can('manage_options')) { return null; }
    $user_id = $user_id ?? get_current_user_id();
    if ($user_id <= 0 || $user_id !== get_current_user_id()) { return null; }
    global $wpdb;
    $lock = 'lpcf_' . get_current_blog_id() . '_' . $user_id;
    if ((int)$wpdb->get_var($wpdb->prepare('SELECT GET_LOCK(%s, 0)', $lock)) !== 1) { return null; }
    try {
        $key = 'lp_fallback_controlled_failure_' . $user_id;
        if (get_transient($key) !== 'armed') { return null; }
        delete_transient($key);
        return ['testMode' => true, 'forcePrimaryFailure' => true, 'testRestNonce' => wp_create_nonce('wp_rest')];
    } finally {
        $wpdb->get_var($wpdb->prepare('SELECT RELEASE_LOCK(%s)', $lock));
    }
}
