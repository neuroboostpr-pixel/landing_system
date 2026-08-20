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

/**
 * Build a character-safe UI excerpt even when the optional mbstring PHP
 * extension is unavailable.
 */
function utf8_excerpt(string $value, int $max_characters): string {
    if ($value === '' || $max_characters <= 0 || preg_match('//u', $value) !== 1) {
        return '';
    }
    if (function_exists('mb_substr')) {
        return mb_substr($value, 0, $max_characters, 'UTF-8');
    }
    if (function_exists('iconv_substr')) {
        $excerpt = iconv_substr($value, 0, $max_characters, 'UTF-8');
        if (is_string($excerpt)) {
            return $excerpt;
        }
    }

    $matched = preg_match_all('/./us', $value, $characters);
    return is_int($matched)
        ? implode('', array_slice($characters[0] ?? [], 0, $max_characters))
        : '';
}

function normalize_submission_filter($value): ?string {
    if (!is_scalar($value)) { return null; }
    $submission_id = strtolower(trim((string)$value));
    return wp_is_uuid($submission_id, 4) ? $submission_id : null;
}

/** @return array{0:string,1:array<int,string>} */
function build_audit_filter_sql(string $filter, $submission_value): array {
    $clauses = [];
    $args = [];
    if ($filter === 'ok') { $clauses[] = 'lead_id IS NOT NULL'; }
    elseif ($filter === 'blocked') { $clauses[] = 'lead_id IS NULL'; }
    $submission_id = normalize_submission_filter($submission_value);
    if ($submission_id !== null) {
        $clauses[] = 'submission_id=%s';
        $args[] = $submission_id;
    }
    return [$clauses === [] ? '' : 'WHERE ' . implode(' AND ', $clauses), $args];
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
    $submission_id = normalize_submission_filter($_GET['submission_id'] ?? null);
    [$where, $where_args] = build_audit_filter_sql($filter, $submission_id);

    // phpcs:ignore WordPress.DB.PreparedSQL.InterpolatedNotPrepared, WordPress.DB.DirectDatabaseQuery.DirectQuery
    $total_sql = "SELECT COUNT(*) FROM `$audit_table` $where";
    if ($where_args !== []) { $total_sql = $wpdb->prepare($total_sql, ...$where_args); }
    $total = (int) $wpdb->get_var($total_sql);
    // phpcs:ignore WordPress.DB.PreparedSQL.InterpolatedNotPrepared, WordPress.DB.DirectDatabaseQuery.DirectQuery
    $row_args = array_merge($where_args, [$per_page, $offset]);
    $rows = $wpdb->get_results($wpdb->prepare(
        "SELECT * FROM `$audit_table` $where ORDER BY created_at DESC LIMIT %d OFFSET %d",
        ...$row_args
    ), ARRAY_A);

    // Счётчики для вкладок
    // phpcs:ignore WordPress.DB.DirectDatabaseQuery.DirectQuery
    $count_ok      = (int) $wpdb->get_var("SELECT COUNT(*) FROM `$audit_table` WHERE lead_id IS NOT NULL");
    // phpcs:ignore WordPress.DB.DirectDatabaseQuery.DirectQuery
    $count_blocked = (int) $wpdb->get_var("SELECT COUNT(*) FROM `$audit_table` WHERE lead_id IS NULL");
    $count_all     = $count_ok + $count_blocked;

    $base_url = admin_url('admin.php?page=landing-config-lead-audit');
    if ($submission_id !== null) {
        $base_url = add_query_arg('submission_id', $submission_id, $base_url);
    }

    // Результат bulk-переноса
    $promoted = isset($_GET['promoted']) ? (int) $_GET['promoted'] : null;
    $skipped  = isset($_GET['skipped'])  ? (int) $_GET['skipped']  : null;
    ?>
    <div class="wrap">
        <h1>Лог заявок (аудит)</h1>
        <p style="color:#646970;">Сюда попадают <strong>все</strong> попытки отправки формы — до любых проверок. Колонка <strong>Статус</strong> показывает прошла ли заявка в основную таблицу.</p>

        <?php if ($submission_id !== null): ?>
            <div class="notice notice-info inline"><p>
                Показан точный идентификатор отправки <code><?php echo esc_html($submission_id); ?></code>.
                <a href="<?php echo esc_url(admin_url('admin.php?page=landing-config-lead-audit')); ?>">Сбросить фильтр</a>
            </p></div>
        <?php endif; ?>

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
            <?php if ($submission_id !== null): ?>
                <input type="hidden" name="submission_id" value="<?php echo esc_attr($submission_id); ?>">
            <?php endif; ?>

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
                        <td><?php echo esc_html(utf8_excerpt((string)($r['message'] ?? ''), 60)); ?></td>
                        <td style="font-size:11px;">
                            <?php
                            $parts = array_filter([
                                $r['source_block'] ? esc_html(utf8_excerpt((string)$r['source_block'], 40)) : '',
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

function audit_promotion_lock_name(int $audit_id, ?string $submission_id = null): string {
    $submission_id = normalize_submission_filter($submission_id);
    if ($submission_id !== null) {
        // Use the primary intake lock namespace so a live retry and an admin
        // recovery cannot insert the same submission concurrently.
        if (function_exists('LandingConfig\\REST\\submission_lock_name')) {
            return \LandingConfig\REST\submission_lock_name($submission_id);
        }
        return 'lpl_' . get_current_blog_id() . '_' . substr(hash('sha256', $submission_id), 0, 32);
    }
    $scope = 'audit_' . max(0, $audit_id);
    return 'lpap_' . get_current_blog_id() . '_' . $scope;
}

function acquire_audit_promotion_lock(int $audit_id, ?string $submission_id = null): bool {
    global $wpdb;
    return $audit_id > 0 && (int)$wpdb->get_var($wpdb->prepare(
        'SELECT GET_LOCK(%s, %d)', audit_promotion_lock_name($audit_id, $submission_id), 2
    )) === 1;
}

function release_audit_promotion_lock(int $audit_id, ?string $submission_id = null): void {
    global $wpdb;
    if ($audit_id > 0) {
        $wpdb->get_var($wpdb->prepare(
            'SELECT RELEASE_LOCK(%s)', audit_promotion_lock_name($audit_id, $submission_id)
        ));
    }
}

function audit_row_is_promotable(array $row): bool {
    $lead_id = $row['lead_id'] ?? null;
    return ($lead_id === null || $lead_id === '')
        && (string)($row['pd_consent'] ?? '') === '1'
        && (trim((string)($row['phone'] ?? '')) !== '' || trim((string)($row['email'] ?? '')) !== '');
}

/** @return array{ok:bool,lead_id:int} */
function find_promoted_lead_by_submission(string $submission_id): array {
    if (!wp_is_uuid($submission_id, 4)) { return ['ok' => true, 'lead_id' => 0]; }
    global $wpdb;
    if (isset($wpdb->last_error)) { $wpdb->last_error = ''; }
    $row = $wpdb->get_row($wpdb->prepare(
        'SELECT id FROM `' . get_leads_table_name() . '` WHERE submission_id=%s ORDER BY id ASC LIMIT 1',
        $submission_id
    ), ARRAY_A);
    if ((string)($wpdb->last_error ?? '') !== '') { return ['ok' => false, 'lead_id' => 0]; }
    return ['ok' => true, 'lead_id' => is_array($row) ? max(0, (int)($row['id'] ?? 0)) : 0];
}

/** @return array{ok:bool,lead_id:int} */
function find_promoted_lead_by_audit(int $audit_id): array {
    if ($audit_id <= 0) { return ['ok' => true, 'lead_id' => 0]; }
    global $wpdb;
    if (isset($wpdb->last_error)) { $wpdb->last_error = ''; }
    $row = $wpdb->get_row($wpdb->prepare(
        'SELECT id FROM `' . get_leads_table_name() . '` WHERE audit_origin_id=%d ORDER BY id ASC LIMIT 1',
        $audit_id
    ), ARRAY_A);
    if ((string)($wpdb->last_error ?? '') !== '') { return ['ok' => false, 'lead_id' => 0]; }
    return ['ok' => true, 'lead_id' => is_array($row) ? max(0, (int)($row['id'] ?? 0)) : 0];
}

function link_audit_to_lead(int $audit_id, int $lead_id, string $detail): bool {
    if ($audit_id <= 0 || $lead_id <= 0) { return false; }
    global $wpdb;
    $updated = $wpdb->update(
        get_lead_audit_table_name(),
        ['lead_id' => $lead_id, 'blocked_by' => null, 'block_detail' => $detail],
        ['id' => $audit_id],
        ['%d', '%s', '%s'],
        ['%d']
    );
    if ($updated === false) {
        error_log('[landing-config] audit_promote_link_failed audit_id=' . $audit_id);
        return false;
    }
    return true;
}

function queue_promoted_lead_delivery(int $lead_id, array $delivery_targets): void {
    if ($lead_id <= 0) { return; }
    try {
        if ($delivery_targets !== [] && function_exists('LandingConfig\\LeadDelivery\\ensure_delivery_reservations')) {
            \LandingConfig\LeadDelivery\ensure_delivery_reservations($lead_id, $delivery_targets);
        }
        if ($delivery_targets !== [] && function_exists('wp_schedule_single_event')) {
            wp_schedule_single_event(time(), \LandingConfig\LeadDelivery\DELIVERY_HOOK, [$lead_id]);
        }
        if ($delivery_targets !== [] && function_exists('spawn_cron')) { spawn_cron(); }
    } catch (\Throwable $ignored) {
        error_log('[landing-config] audit_promote_delivery_schedule_failed');
    }
}

function promote_one_audit_row(int $audit_id): string {
    if ($audit_id <= 0) { return 'skipped'; }
    global $wpdb;
    $audit_table = get_lead_audit_table_name();
    $initial = $wpdb->get_row($wpdb->prepare(
        "SELECT * FROM `{$audit_table}` WHERE id=%d LIMIT 1", $audit_id
    ), ARRAY_A);
    if (!is_array($initial) || !audit_row_is_promotable($initial)) { return 'skipped'; }
    $locked_submission_id = normalize_submission_filter($initial['submission_id'] ?? null);
    if (!acquire_audit_promotion_lock($audit_id, $locked_submission_id)) { return 'skipped'; }
    try {
        $row = $wpdb->get_row($wpdb->prepare(
            "SELECT * FROM `{$audit_table}` WHERE id=%d LIMIT 1", $audit_id
        ), ARRAY_A);
        if (!is_array($row) || !audit_row_is_promotable($row)) { return 'skipped'; }
        $phone = trim((string)($row['phone'] ?? ''));
        $email = trim((string)($row['email'] ?? ''));

        $submission_id = normalize_submission_filter($row['submission_id'] ?? null);
        if ($submission_id !== $locked_submission_id) { return 'skipped'; }
        $origin_lookup = find_promoted_lead_by_audit($audit_id);
        if (!($origin_lookup['ok'] ?? false)) {
            error_log('[landing-config] audit_promote_origin_lookup_failed audit_id=' . $audit_id);
            return 'skipped';
        }
        if ((int)($origin_lookup['lead_id'] ?? 0) > 0) {
            link_audit_to_lead($audit_id, (int)$origin_lookup['lead_id'], 'promoted_existing_audit');
            return 'skipped';
        }
        if ($submission_id !== null) {
            $submission_lookup = find_promoted_lead_by_submission($submission_id);
            if (!($submission_lookup['ok'] ?? false)) {
                error_log('[landing-config] audit_promote_submission_lookup_failed audit_id=' . $audit_id);
                return 'skipped';
            }
            $existing_lead_id = (int)($submission_lookup['lead_id'] ?? 0);
            if ($existing_lead_id > 0) {
                link_audit_to_lead($audit_id, $existing_lead_id, 'promoted_existing_submission');
                return 'skipped';
            }
        }

        try {
            $delivery_targets = \LandingConfig\LeadDelivery\snapshot_enabled_integrations();
            $encoded_delivery_targets = \LandingConfig\LeadDelivery\encode_delivery_targets($delivery_targets);
            if ($encoded_delivery_targets === '') { return 'skipped'; }
        } catch (\Throwable $ignored) {
            error_log('[landing-config] audit_promote_snapshot_failed audit_id=' . $audit_id);
            return 'skipped';
        }

        $data = [
            'submission_id'    => $submission_id,
            'name'             => (string)($row['name'] ?? ''),
            'phone'            => $phone,
            'email'            => $email,
            'message'          => (string)($row['message'] ?? ''),
            'source_block'     => (string)($row['source_block'] ?? ''),
            'utm_source'       => (string)($row['utm_source'] ?? ''),
            'utm_medium'       => (string)($row['utm_medium'] ?? ''),
            'utm_campaign'     => (string)($row['utm_campaign'] ?? ''),
            'utm_term'         => (string)($row['utm_term'] ?? ''),
            'utm_content'      => (string)($row['utm_content'] ?? ''),
            'roistat_visit'    => (string)($row['roistat_visit'] ?? ''),
            'ip'               => (string)($row['ip'] ?? ''),
            'user_agent'       => (string)($row['user_agent'] ?? ''),
            'delivery_targets' => $encoded_delivery_targets,
            'delivery_reservations_ready' => $delivery_targets === [] ? 1 : 0,
            'audit_origin_id'  => $audit_id,
            'created_at'       => (string)($row['created_at'] ?? current_time('mysql')),
            'processed_status' => 'pending',
            'pd_consent_granted_at' => (string)($row['created_at'] ?? current_time('mysql')),
            'recaptcha_score'  => null,
        ];
        $inserted = $wpdb->insert(get_leads_table_name(), $data);
        $lead_id = (int)($wpdb->insert_id ?? 0);
        if ($inserted === false || $inserted === 0 || $lead_id <= 0) {
            $origin_lookup = find_promoted_lead_by_audit($audit_id);
            if (($origin_lookup['ok'] ?? false) && (int)($origin_lookup['lead_id'] ?? 0) > 0) {
                link_audit_to_lead($audit_id, (int)$origin_lookup['lead_id'], 'promoted_existing_audit');
                return 'skipped';
            }
            error_log('[landing-config] audit_promote_insert_failed audit_id=' . $audit_id);
            return 'skipped';
        }
        link_audit_to_lead($audit_id, $lead_id, 'promoted_manually');
        queue_promoted_lead_delivery($lead_id, $delivery_targets);
        do_action('landing_config_lead_received', $lead_id, $data);
        return 'promoted';
    } finally {
        release_audit_promotion_lock($audit_id, $locked_submission_id);
    }
}

/** @return array{promoted:int,skipped:int} */
function promote_audit_rows(array $audit_ids): array {
    $summary = ['promoted' => 0, 'skipped' => 0];
    $audit_ids = array_values(array_unique(array_filter(array_map('intval', $audit_ids), static fn(int $id): bool => $id > 0)));
    foreach ($audit_ids as $audit_id) {
        $result = promote_one_audit_row($audit_id);
        $summary[$result === 'promoted' ? 'promoted' : 'skipped']++;
    }
    return $summary;
}

/**
 * Bulk-перенос записей из аудит-лога в основную таблицу заявок.
 * Строки с уже заполненным lead_id пропускаются (не дублируем).
 */
function handle_bulk_promote(): void {
    if (($_SERVER['REQUEST_METHOD'] ?? '') !== 'POST') { wp_die('Method not allowed', 405); }
    if (!current_user_can('manage_options')) { wp_die('No.', 403); }
    check_admin_referer('landing_audit_bulk_promote');

    $bulk_action = sanitize_key($_POST['bulk_action'] ?? '');
    $audit_ids   = array_map('intval', (array)($_POST['audit_ids'] ?? []));
    $audit_ids   = array_values(array_filter($audit_ids, fn($i) => $i > 0));
    $filter      = sanitize_key($_POST['filter'] ?? 'all');
    $submission_id = normalize_submission_filter($_POST['submission_id'] ?? null);

    $back = admin_url('admin.php?page=landing-config-lead-audit&filter=' . $filter);
    if ($submission_id !== null) { $back .= '&submission_id=' . rawurlencode($submission_id); }

    if ($bulk_action !== 'promote') {
        wp_safe_redirect($back);
        exit;
    }
    if (empty($audit_ids)) {
        wp_safe_redirect($back . '&promote_error=no_selection');
        exit;
    }

    $summary = promote_audit_rows($audit_ids);
    wp_safe_redirect($back . '&promoted=' . $summary['promoted'] . '&skipped=' . $summary['skipped']);
    exit;
}
