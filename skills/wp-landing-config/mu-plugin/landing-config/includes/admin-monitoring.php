<?php
namespace LandingConfig\MonitoringAdmin;

if (!defined('ABSPATH')) { exit; }

const PAGE_SLUG = 'landing-config-monitoring';
const TEST_ALERT_ACTION = 'lp_monitor_test_alert';
const CONTROLLED_FAILURE_ACTION = 'lp_fallback_arm_controlled_failure';
const STATUS_SMOKE_ACTION = 'lp_fallback_arm_status_smoke';
const STATUS_SMOKE_MAX_TTL = 180;

add_action('admin_menu', static function (): void {
    add_submenu_page('landing-config', 'Мониторинг заявок', 'Мониторинг заявок',
        'manage_options', PAGE_SLUG, __NAMESPACE__ . '\\render_page');
});
add_action('admin_post_' . TEST_ALERT_ACTION, __NAMESPACE__ . '\\handle_test_alert');
add_action('admin_post_' . CONTROLLED_FAILURE_ACTION, __NAMESPACE__ . '\\handle_arm_controlled_failure');
add_action('admin_post_' . STATUS_SMOKE_ACTION, __NAMESPACE__ . '\\handle_arm_status_smoke');

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
        <button type="submit" class="button">Записать тестовый инцидент (без Telegram)</button>
      </form>

      <?php if (defined('LP_FALLBACK_TEST_MODE') && LP_FALLBACK_TEST_MODE === true): ?>
      <form method="post" action="<?php echo esc_url(admin_url('admin-post.php')); ?>">
        <?php wp_nonce_field(CONTROLLED_FAILURE_ACTION); ?>
        <input type="hidden" name="action" value="<?php echo esc_attr(CONTROLLED_FAILURE_ACTION); ?>">
        <button type="submit" class="button">lp_fallback_arm_controlled_failure</button>
      </form>
      <form method="post" action="<?php echo esc_url(admin_url('admin-post.php')); ?>">
        <?php wp_nonce_field(STATUS_SMOKE_ACTION); ?>
        <input type="hidden" name="action" value="<?php echo esc_attr(STATUS_SMOKE_ACTION); ?>">
        <label>Тестовый UUID для одноразового status 503
          <input type="text" name="smoke_submission_id" required autocomplete="off"
            pattern="[0-9a-fA-F-]{36}" maxlength="36">
        </label>
        <button type="submit" class="button">Вооружить status smoke на 180 секунд</button>
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

function status_smoke_test_mode_enabled(): bool {
    return defined('LP_FALLBACK_TEST_MODE') && LP_FALLBACK_TEST_MODE === true;
}

function normalized_status_smoke_uuid($value): ?string {
    if (!is_scalar($value)) { return null; }
    $uuid = strtolower(trim((string)$value));
    return \LandingConfig\Monitoring\is_valid_submission_id($uuid) ? $uuid : null;
}

function status_smoke_scope(string $submission_id): ?array {
    $uuid = normalized_status_smoke_uuid($submission_id);
    if ($uuid === null) { return null; }
    $scope = hash_hmac('sha256', $uuid, wp_salt('auth'));
    return [
        'key' => 'lp_status_smoke_' . substr($scope, 0, 48),
        'lock' => 'lpss_' . get_current_blog_id() . '_' . substr($scope, 0, 32),
    ];
}

function with_status_smoke_lock(string $submission_id, callable $callback) {
    $scope = status_smoke_scope($submission_id);
    if ($scope === null) { return false; }
    global $wpdb;
    if ((int)$wpdb->get_var($wpdb->prepare('SELECT GET_LOCK(%s, 0)', $scope['lock'])) !== 1) {
        return false;
    }
    try { return $callback($scope['key']); }
    finally { $wpdb->get_var($wpdb->prepare('SELECT RELEASE_LOCK(%s)', $scope['lock'])); }
}

function arm_status_smoke_at(string $submission_id, int $ttl, int $now): bool {
    if (!status_smoke_test_mode_enabled() || normalized_status_smoke_uuid($submission_id) === null || $now <= 0) {
        return false;
    }
    $ttl = max(1, min(STATUS_SMOKE_MAX_TTL, $ttl));
    return with_status_smoke_lock($submission_id, static function (string $key) use ($ttl, $now): bool {
        return set_transient($key, ['state' => 'armed', 'expires_at' => $now + $ttl], $ttl) === true;
    }) === true;
}

function consume_status_smoke_failure_at(string $submission_id, int $now): bool {
    if (!status_smoke_test_mode_enabled() || normalized_status_smoke_uuid($submission_id) === null || $now <= 0) {
        return false;
    }
    return with_status_smoke_lock($submission_id, static function (string $key) use ($now): bool {
        $state = get_transient($key);
        if (!is_array($state) || ($state['state'] ?? '') !== 'armed'
            || !is_int($state['expires_at'] ?? null) || (int)$state['expires_at'] <= $now) {
            if ($state !== false) { delete_transient($key); }
            return false;
        }
        $remaining = max(1, min(STATUS_SMOKE_MAX_TTL, (int)$state['expires_at'] - $now));
        set_transient($key, ['state' => 'consumed', 'expires_at' => (int)$state['expires_at']], $remaining);
        return true;
    }) === true;
}

function handle_arm_status_smoke(): void {
    require_admin_post(STATUS_SMOKE_ACTION);
    if (!status_smoke_test_mode_enabled()) { wp_die('Not found', 404); }
    $submission_id = normalized_status_smoke_uuid($_POST['smoke_submission_id'] ?? null);
    if ($submission_id === null) { wp_die('Invalid submission id', 400); }
    if (!arm_status_smoke_at($submission_id, STATUS_SMOKE_MAX_TTL, time())) {
        wp_die('Temporarily unavailable', 503);
    }
    safe_admin_redirect();
    wp_safe_redirect(admin_url('admin.php?page=' . PAGE_SLUG), 303);
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
