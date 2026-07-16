<?php
namespace LandingConfig\Monitoring;

if (!defined('ABSPATH')) { exit; }

use function LandingConfig\DB\get_monitor_alerts_table_name;
use function LandingConfig\DB\get_lead_log_table_name;
use function LandingConfig\DB\get_leads_table_name;

const ENABLED_OPTION = 'landing_monitor_enabled';
const HEARTBEAT_OPTION = 'landing_monitor_last_heartbeat';
const RUN_STATUS_OPTION = 'landing_monitor_last_run_status';
const EXTERNAL_HEALTH_OPTION = 'landing_monitor_last_external_health_result';
const SCAN_HOOK = 'landing_config_monitor_scan';
const QUEUE_HOOK = 'landing_config_monitor_queue';
const CLEANUP_HOOK = 'landing_config_monitor_cleanup';
const DELIVERY_HOOK = 'landing_config_deliver_lead';
const GRACE_SECONDS = 300;
const DELIVERY_ROLLOUT_BOUNDARY_OPTION = 'landing_delivery_async_boundary';
const HEARTBEAT_STALE_SECONDS = 180;
const LOCK_TTL_SECONDS = 120;
const MAX_SEND_ATTEMPTS = 3;

function is_enabled(): bool {
    if (defined('LP_MONITOR_ENABLED')) { return LP_MONITOR_ENABLED === true; }
    return (string)get_option(ENABLED_OPTION, '0') === '1';
}

function allowed_incident_kinds(): array {
    return ['missing_lead','javascript_stall','integration_failure','delivery_stuck',
        'fallback_receipt_watch','fallback_delivery_stuck','fallback_delivery_uncertain',
        'external_outage','external_recovery','external_monitor_stale','external_monitor_recovery',
        'monitor_internal_failure','test_alert'];
}
function allowed_severities(): array { return ['info','warning','critical']; }
function allowed_statuses(): array {
    return ['request_started','request_failed','submit_attempt','pending','delivered','unknown','expired',
        'ok','failed','retry_wait','failed_permanent','watching','test'];
}
function allowed_categories(): array {
    return ['missing_wordpress_lead','browser_javascript_stall','external_receipt_confirmed',
        'configuration_missing','unsupported_adapter','adapter_exception','invalid_adapter_result',
        'transport_error','provider_4xx','provider_5xx','rate_limited','invalid_response',
        'delivery_rows_missing','delivery_queued_stuck','delivery_sending_stale',
        'fallback_receipt_watch','fallback_delivery_stuck','fallback_delivery_uncertain',
        'redis_outage','redis_recovery','external_monitor_stale','external_monitor_recovery',
        'monitor_scan_failed','monitor_queue_failed','test'];
}
function allowed_resolutions(): array { return ['','external_recovered','wordpress_lead_saved','delivery_recovered']; }
function utc_mysql(int $timestamp): string { return gmdate('Y-m-d H:i:s', $timestamp); }

function is_valid_submission_id(?string $submission_id): bool {
    return $submission_id === null
        || preg_match('/^[0-9a-f]{8}-[0-9a-f]{4}-4[0-9a-f]{3}-[89ab][0-9a-f]{3}-[0-9a-f]{12}$/', $submission_id) === 1;
}

function incident_fingerprint(string $kind, ?string $submission_id, ?int $lead_id,
    ?int $integration_id, string $adapter, int $scope = 0): string {
    return hash('sha256', implode('|', [get_current_blog_id(), $kind,
        $submission_id ?? '', $lead_id ?? 0, $integration_id ?? 0, $adapter, $scope]));
}

function sql_string(string $value): string {
    global $wpdb;
    return $wpdb->prepare('%s', $value);
}
function sql_nullable_string(?string $value): string { return $value === null ? 'NULL' : sql_string($value); }
function sql_nullable_int(?int $value): string { return $value === null ? 'NULL' : (string)$value; }

function record_incident_scoped(string $kind, string $severity, ?string $submission_id,
    ?int $lead_id, ?int $integration_id, string $adapter, string $safe_status,
    string $safe_category, ?int $provider_response_code, string $resolution,
    int $fingerprint_scope, ?int $now, bool $external): int {
    if (!in_array($kind, allowed_incident_kinds(), true)
        || !in_array($severity, allowed_severities(), true)
        || !in_array($safe_status, allowed_statuses(), true)
        || !in_array($safe_category, allowed_categories(), true)
        || !in_array($resolution, allowed_resolutions(), true)
        || !is_valid_submission_id($submission_id)
        || ($lead_id !== null && $lead_id <= 0)
        || ($integration_id !== null && $integration_id <= 0)
        || preg_match('/^[a-z0-9_-]{0,64}$/', $adapter) !== 1
        || ($provider_response_code !== null && ($provider_response_code < 100 || $provider_response_code > 599))) {
        return 0;
    }
    $external_kinds = ['external_outage','external_recovery','external_monitor_stale','external_monitor_recovery'];
    if ($external) {
        if (!in_array($kind, $external_kinds, true) || $fingerprint_scope <= 0
            || $submission_id !== null || $lead_id !== null || $integration_id !== null || $adapter !== '') {
            return 0;
        }
    } elseif ($fingerprint_scope !== 0 || in_array($kind, $external_kinds, true)) {
        return 0;
    }

    global $wpdb;
    $now = $now ?? time();
    $at = utc_mysql($now);
    $fingerprint = incident_fingerprint($kind, $submission_id, $lead_id, $integration_id, $adapter, $fingerprint_scope);
    $resolved_at = $resolution === '' ? null : $at;
    $table = str_replace('`', '', get_monitor_alerts_table_name());
    $sql = "INSERT INTO `{$table}` (fingerprint,incident_kind,severity,submission_id,lead_id,integration_id,"
        . "fingerprint_scope,adapter,safe_status,safe_category,provider_response_code,occurrence_count,"
        . "first_seen_at,last_seen_at,due_at,locked_at,lock_token,sent_at,resolved_at,resolution,"
        . "telegram_status,send_attempts,last_response_at,telegram_response_code,telegram_message_id) VALUES ("
        . implode(',', [
            sql_string($fingerprint), sql_string($kind), sql_string($severity), sql_nullable_string($submission_id),
            sql_nullable_int($lead_id), sql_nullable_int($integration_id), (string)$fingerprint_scope,
            sql_string($adapter), sql_string($safe_status), sql_string($safe_category),
            sql_nullable_int($provider_response_code), '1', sql_string($at), sql_string($at), sql_string($at),
            'NULL','NULL','NULL',sql_nullable_string($resolved_at),sql_string($resolution),sql_string('pending'),
            '0','NULL','NULL','NULL',
        ]) . ") ON DUPLICATE KEY UPDATE id=LAST_INSERT_ID(id), occurrence_count=occurrence_count+1,"
        . "last_seen_at=VALUES(last_seen_at),safe_status=VALUES(safe_status),safe_category=VALUES(safe_category),"
        . "provider_response_code=VALUES(provider_response_code),"
        . "resolution=IF(VALUES(resolution)<>'',VALUES(resolution),resolution),"
        . "resolved_at=IF(VALUES(resolution)<>'',VALUES(resolved_at),resolved_at)";
    $written = $wpdb->query($sql);
    return $written === false ? 0 : max(0, (int)$wpdb->insert_id);
}

function record_incident(string $kind, string $severity, ?string $submission_id,
    ?int $lead_id, ?int $integration_id, string $adapter, string $safe_status,
    string $safe_category, ?int $provider_response_code = null,
    string $resolution = '', ?int $now = null): int {
    return record_incident_scoped($kind, $severity, $submission_id, $lead_id, $integration_id,
        $adapter, $safe_status, $safe_category, $provider_response_code, $resolution, 0, $now, false);
}

function record_external_incident(string $kind, string $safe_category,
    int $episode_generation, ?int $now = null): int {
    $pairs = [
        'external_outage' => 'redis_outage',
        'external_recovery' => 'redis_recovery',
        'external_monitor_stale' => 'external_monitor_stale',
        'external_monitor_recovery' => 'external_monitor_recovery',
    ];
    if (($pairs[$kind] ?? null) !== $safe_category || $episode_generation <= 0) { return 0; }
    $severity = in_array($kind, ['external_recovery','external_monitor_recovery'], true) ? 'info' : 'critical';
    $status = in_array($kind, ['external_recovery','external_monitor_recovery'], true) ? 'ok' : 'failed';
    return record_incident_scoped($kind, $severity, null, null, null, '', $status,
        $safe_category, null, '', $episode_generation, $now, true);
}

function resolve_integration_incident(int $lead_id, int $integration_id, string $adapter,
    string $resolution, ?int $now = null): void {
    if ($lead_id <= 0 || $integration_id <= 0 || !in_array($resolution, allowed_resolutions(), true)) { return; }
    global $wpdb;
    $fingerprint = incident_fingerprint('integration_failure', null, $lead_id, $integration_id, sanitize_key($adapter), 0);
    $wpdb->update(get_monitor_alerts_table_name(), [
        'resolved_at' => utc_mysql($now ?? time()), 'resolution' => $resolution,
    ], ['fingerprint' => $fingerprint]);
}

function observe_delivery_result(int $lead_id, int $integration_id, string $adapter,
    string $status, string $safe_category, ?int $response_code): void {
    if (!is_enabled() || $lead_id <= 0 || $integration_id <= 0) { return; }
    if (in_array($status, ['success','accepted'], true)) {
        resolve_integration_incident($lead_id, $integration_id, $adapter, 'delivery_recovered');
        return;
    }
    if (!in_array($status, ['unknown','failed_permanent'], true)) { return; }
    record_incident('integration_failure', 'critical', null, $lead_id, $integration_id,
        sanitize_key($adapter), $status, $safe_category, $response_code);
}

function reconcile_delivery_rows(?int $now = null): array {
    global $wpdb;
    $now = $now ?? time();
    $enabled_ids = [];
    foreach (\LandingConfig\Integrations\list_integrations(get_current_blog_id()) as $integration) {
        $integration_id = (int)($integration['id'] ?? 0);
        if (($integration['enabled'] ?? false) === true && $integration_id > 0) {
            $enabled_ids[$integration_id] = $integration_id;
        }
    }
    $missing = [];
    $boundary = (string)get_option(DELIVERY_ROLLOUT_BOUNDARY_OPTION, '');
    $boundary_valid = function_exists('LandingConfig\\DB\\valid_mysql_utc_timestamp')
        && \LandingConfig\DB\valid_mysql_utc_timestamp($boundary);
    if ($enabled_ids !== [] && $boundary_valid) {
        // The IDs come from WordPress integration records and are cast to
        // positive integers above, so the IN list cannot contain SQL input.
        $enabled_id_sql = implode(',', $enabled_ids);
        $missing = $wpdb->get_results($wpdb->prepare(
            "SELECT l.id,l.created_at FROM `" . get_leads_table_name() . "` l LEFT JOIN `" . get_lead_log_table_name()
            . "` d ON d.lead_id=l.id AND d.integration_id IN ({$enabled_id_sql})"
            . " WHERE l.created_at>=%s AND l.created_at<=%s GROUP BY l.id"
            . " HAVING COUNT(DISTINCT d.integration_id)<%d ORDER BY l.id ASC LIMIT 100",
            $boundary, utc_mysql($now - 60), count($enabled_ids)
        ), ARRAY_A);
    }
    $reservations_recreated = 0;
    foreach (is_array($missing) ? $missing : [] as $lead) {
        $lead_id = (int)($lead['id'] ?? 0);
        $created_at = (string)($lead['created_at'] ?? '');
        // SQL owns the normal path; this second boundary check prevents a
        // stale replica/mock/corrupt row from ever replaying a legacy lead.
        if ($lead_id <= 0 || !$boundary_valid
            || !\LandingConfig\DB\valid_mysql_utc_timestamp($created_at)
            || strcmp($created_at, $boundary) < 0) {
            continue;
        }
        $created = \LandingConfig\LeadDelivery\reserve_integrations($lead_id);
        if ($created <= 0) { continue; }
        if (function_exists('wp_schedule_single_event')) {
            wp_schedule_single_event($now, \LandingConfig\LeadDelivery\DELIVERY_HOOK, [$lead_id]);
        }
        $reservations_recreated += $created;
    }

    $queued = $wpdb->get_results($wpdb->prepare(
        "SELECT id,lead_id,integration_id,adapter,attempt FROM `" . get_lead_log_table_name()
        . "` WHERE status='queued' AND COALESCE(next_attempt_at,created_at)<=%s LIMIT 100",
        utc_mysql($now - 300)
    ), ARRAY_A);
    $stuck = 0;
    foreach (is_array($queued) ? $queued : [] as $row) {
        if (record_incident('delivery_stuck', 'critical', null, (int)($row['lead_id'] ?? 0),
            (int)($row['integration_id'] ?? 0), sanitize_key((string)($row['adapter'] ?? '')),
            'failed', 'delivery_queued_stuck', null, '', $now) > 0) { $stuck++; }
    }

    $retry_rows = $wpdb->get_results(
        "SELECT id,lead_id,integration_id,adapter,attempt FROM `" . get_lead_log_table_name()
        . "` WHERE status='retry_wait' ORDER BY id ASC LIMIT 100", ARRAY_A
    );
    foreach (is_array($retry_rows) ? $retry_rows : [] as $row) {
        $successor = $wpdb->get_row($wpdb->prepare(
            "SELECT id,status,next_attempt_at FROM `" . get_lead_log_table_name()
            . "` WHERE lead_id=%d AND integration_id=%d AND attempt=%d LIMIT 1",
            (int)($row['lead_id'] ?? 0), (int)($row['integration_id'] ?? 0), (int)($row['attempt'] ?? 0) + 1
        ), ARRAY_A);
        $healthy = is_array($successor) && ($successor['status'] ?? '') === 'queued'
            && strtotime((string)($successor['next_attempt_at'] ?? '')) > $now - 300;
        if ($healthy) { continue; }
        if (record_incident('delivery_stuck', 'critical', null, (int)($row['lead_id'] ?? 0),
            (int)($row['integration_id'] ?? 0), sanitize_key((string)($row['adapter'] ?? '')),
            'retry_wait', 'delivery_queued_stuck', null, '', $now) > 0) { $stuck++; }
    }
    return ['reservations_recreated' => $reservations_recreated, 'stuck' => $stuck];
}

function classify_timeline(array $events): ?array {
    usort($events, static function (array $left, array $right): int {
        $left_sequence = isset($left['event_sequence']) ? (int)$left['event_sequence'] : PHP_INT_MAX;
        $right_sequence = isset($right['event_sequence']) ? (int)$right['event_sequence'] : PHP_INT_MAX;
        return $left_sequence <=> $right_sequence ?: (int)($left['id'] ?? 0) <=> (int)($right['id'] ?? 0);
    });
    $names = array_values(array_filter(array_map(
        static fn(array $event): string => sanitize_key((string)($event['event_name'] ?? '')),
        $events
    )));
    if (in_array('request_started', $names, true) || in_array('request_failed', $names, true)) {
        return [
            'kind' => 'missing_lead',
            'severity' => 'critical',
            'safe_status' => in_array('request_failed', $names, true) ? 'request_failed' : 'request_started',
            'safe_category' => 'missing_wordpress_lead',
        ];
    }
    if (in_array('submit_attempt', $names, true)) {
        return [
            'kind' => 'javascript_stall',
            'severity' => 'warning',
            'safe_status' => 'submit_attempt',
            'safe_category' => 'browser_javascript_stall',
        ];
    }
    return null;
}

function sign_receipt_status_components(string $secret, string $path, int $timestamp): ?string {
    $key = \LandingConfig\FallbackSecurity\decode_hmac_hex_secret($secret);
    if ($key === null) { return null; }
    return hash_hmac('sha256', "GET\n{$path}\n{$timestamp}\nhybridautos-ae", $key);
}

function receipt_status_signature(string $path, int $timestamp): ?string {
    if (!defined('LP_FALLBACK_STATUS_SECRET') || !defined('LP_FALLBACK_SITE_ID')
        || LP_FALLBACK_SITE_ID !== 'hybridautos-ae') {
        return null;
    }
    return sign_receipt_status_components((string)LP_FALLBACK_STATUS_SECRET, $path, $timestamp);
}

function empty_receipt_result(string $lookup): array {
    return ['lookup' => $lookup, 'exists' => false, 'stored' => false, 'delivery_state' => null];
}

function fetch_external_receipt_status(string $submission_id, ?int $now = null): array {
    if (!is_valid_submission_id($submission_id) || !defined('LP_FALLBACK_STATUS_URL')) {
        return empty_receipt_result('disabled');
    }
    $base = rtrim((string)LP_FALLBACK_STATUS_URL, '/');
    if (filter_var($base, FILTER_VALIDATE_URL) === false || strtolower((string)parse_url($base, PHP_URL_SCHEME)) !== 'https') {
        return empty_receipt_result('disabled');
    }
    $path = '/api/v1/receipts/' . $submission_id;
    $timestamp = $now ?? time();
    $signature = receipt_status_signature($path, $timestamp);
    if ($signature === null) { return empty_receipt_result('disabled'); }
    try {
        $response = wp_remote_get($base . $path, [
            'timeout' => 4,
            'redirection' => 0,
            'headers' => [
                'X-LP-Site-Id' => 'hybridautos-ae',
                'X-LP-Timestamp' => (string)$timestamp,
                'X-LP-Signature' => $signature,
            ],
        ]);
    } catch (\Throwable $ignored) {
        return empty_receipt_result('unknown');
    }
    if (is_wp_error($response)) { return empty_receipt_result('unknown'); }
    $code = (int)wp_remote_retrieve_response_code($response);
    if ($code === 404) { return empty_receipt_result('missing'); }
    if ($code !== 200) { return empty_receipt_result('unknown'); }
    $decoded = json_decode((string)wp_remote_retrieve_body($response), true);
    $expected_keys = ['ok','submission_id','exists','stored','delivery_state'];
    if (!is_array($decoded) || array_keys($decoded) !== $expected_keys
        || ($decoded['ok'] ?? null) !== true
        || ($decoded['submission_id'] ?? '') !== $submission_id
        || !is_bool($decoded['exists'] ?? null)
        || !is_bool($decoded['stored'] ?? null)
        || !in_array($decoded['delivery_state'] ?? null, ['pending','delivered','unknown','expired'], true)) {
        return empty_receipt_result('unknown');
    }
    return [
        'lookup' => 'ok',
        'exists' => $decoded['exists'],
        'stored' => $decoded['stored'],
        'delivery_state' => $decoded['delivery_state'],
    ];
}

function update_incident_by_kind(string $kind, string $submission_id, array $changes): void {
    global $wpdb;
    $fingerprint = incident_fingerprint($kind, $submission_id, null, null, '', 0);
    $wpdb->update(get_monitor_alerts_table_name(), $changes, ['fingerprint' => $fingerprint]);
}

function resolve_submission_incidents(string $submission_id, string $resolution, int $now): void {
    if (!is_valid_submission_id($submission_id) || !in_array($resolution, ['external_recovered','wordpress_lead_saved'], true)) { return; }
    foreach (['missing_lead','javascript_stall','fallback_receipt_watch','fallback_delivery_stuck','fallback_delivery_uncertain'] as $kind) {
        update_incident_by_kind($kind, $submission_id, [
            'resolved_at' => utc_mysql($now), 'resolution' => $resolution,
        ]);
    }
}

function close_receipt_watch(string $submission_id, int $now): void {
    foreach (['fallback_receipt_watch','fallback_delivery_stuck','fallback_delivery_uncertain'] as $kind) {
        update_incident_by_kind($kind, $submission_id, ['resolved_at' => utc_mysql($now)]);
    }
}

function upsert_receipt_watch(string $submission_id, int $now): int {
    $id = record_incident('fallback_receipt_watch', 'info', $submission_id, null, null, '',
        'watching', 'fallback_receipt_watch', null, '', $now);
    if ($id > 0) {
        global $wpdb;
        $wpdb->update(get_monitor_alerts_table_name(), [
            'telegram_status' => 'watching',
            'due_at' => utc_mysql($now + 300),
        ], ['id' => $id]);
    }
    return $id;
}

function apply_receipt_lifecycle(string $submission_id, array $classification, array $receipt,
    bool $wordpress_exists, int $now, ?int $watch_started_at): array {
    if ($wordpress_exists) {
        resolve_submission_incidents($submission_id, 'wordpress_lead_saved', $now);
        return ['terminal' => true, 'result' => 'wordpress_lead_saved'];
    }
    $lookup = (string)($receipt['lookup'] ?? 'unknown');
    $stored = ($receipt['stored'] ?? false) === true;
    $state = $receipt['delivery_state'] ?? null;
    if ($lookup === 'ok' && $stored && $state === 'delivered') {
        resolve_submission_incidents($submission_id, 'external_recovered', $now);
        return ['terminal' => true, 'result' => 'external_recovered'];
    }
    if ($lookup === 'ok' && $stored && in_array($state, ['pending','unknown'], true)) {
        upsert_receipt_watch($submission_id, $now);
        $watch_started_at = $watch_started_at ?? $now;
        if ($state === 'pending' && $now - $watch_started_at >= 600) {
            record_incident('fallback_delivery_stuck', 'critical', $submission_id, null, null, '',
                'pending', 'fallback_delivery_stuck', null, '', $now);
        }
        if ($state === 'unknown') {
            record_incident('fallback_delivery_uncertain', 'critical', $submission_id, null, null, '',
                'unknown', 'fallback_delivery_uncertain', null, '', $now);
        }
        return ['terminal' => false, 'result' => $state];
    }
    if ($lookup === 'ok' && !$stored && $state === 'expired') {
        close_receipt_watch($submission_id, $now);
    }
    $kind = (string)($classification['kind'] ?? '');
    $severity = (string)($classification['severity'] ?? '');
    $safe_status = (string)($classification['safe_status'] ?? '');
    $safe_category = (string)($classification['safe_category'] ?? '');
    $id = record_incident($kind, $severity, $submission_id, null, null, '',
        $safe_status, $safe_category, null, '', $now);
    return ['terminal' => false, 'result' => $id > 0 ? 'incident' : 'ignored'];
}

function mysql_timestamp(string $value): ?int {
    if ($value === '') { return null; }
    $date = \DateTimeImmutable::createFromFormat('!Y-m-d H:i:s', $value, new \DateTimeZone('UTC'));
    return $date instanceof \DateTimeImmutable ? $date->getTimestamp() : null;
}

function run_missing_lead_scan(int $limit = 100, ?int $now = null): array {
    global $wpdb;
    $now = $now ?? time();
    $limit = max(1, min(500, $limit));
    $events = \LandingConfig\DB\get_form_events_table_name();
    $leads = get_leads_table_name();
    $alerts = get_monitor_alerts_table_name();
    $candidates = $wpdb->get_results($wpdb->prepare(
        "SELECT fe.submission_id,MAX(fe.created_at) AS last_event_at,"
        . "MAX(CASE WHEN l.id IS NULL THEN 0 ELSE 1 END) AS wordpress_exists,"
        . "MIN(w.first_seen_at) AS watch_started_at FROM `{$events}` fe LEFT JOIN `{$leads}` l "
        . "ON l.submission_id=fe.submission_id LEFT JOIN `{$alerts}` w ON w.submission_id=fe.submission_id "
        . "AND w.incident_kind='fallback_receipt_watch' AND w.resolved_at IS NULL "
        . "WHERE fe.created_at<=%s AND (w.due_at IS NULL OR w.due_at<=%s) "
        . "GROUP BY fe.submission_id ORDER BY MAX(fe.created_at) ASC LIMIT %d",
        utc_mysql($now - GRACE_SECONDS), utc_mysql($now), $limit
    ), ARRAY_A);
    $classified = 0;
    foreach (is_array($candidates) ? $candidates : [] as $candidate) {
        $submission_id = strtolower((string)($candidate['submission_id'] ?? ''));
        $last_event_at = mysql_timestamp((string)($candidate['last_event_at'] ?? ''));
        if (!is_valid_submission_id($submission_id) || $last_event_at === null || $now - $last_event_at < GRACE_SECONDS) {
            continue;
        }
        $timeline = $wpdb->get_results($wpdb->prepare(
            "SELECT id,event_sequence,event_name,event_detail FROM `{$events}` WHERE submission_id=%s "
            . "ORDER BY CASE WHEN event_sequence IS NULL THEN 1 ELSE 0 END,event_sequence,id",
            $submission_id
        ), ARRAY_A);
        $classification = classify_timeline(is_array($timeline) ? $timeline : []);
        if ($classification === null) { continue; }
        $wordpress_exists = (int)($candidate['wordpress_exists'] ?? 0) === 1;
        $receipt = $wordpress_exists ? empty_receipt_result('disabled')
            : fetch_external_receipt_status($submission_id, $now);
        $watch_started_at = mysql_timestamp((string)($candidate['watch_started_at'] ?? ''));
        apply_receipt_lifecycle($submission_id, $classification, $receipt,
            $wordpress_exists, $now, $watch_started_at);
        $classified++;
    }
    return ['scanned' => is_array($candidates) ? count($candidates) : 0, 'classified' => $classified];
}

function claim_next_alert(?int $now = null): ?array {
    global $wpdb;
    $now = $now ?? time();
    $table = get_monitor_alerts_table_name();
    $row = $wpdb->get_row($wpdb->prepare(
        "SELECT * FROM `{$table}` WHERE telegram_status IN ('pending','retry_wait') "
        . "AND resolved_at IS NULL AND due_at<=%s AND send_attempts<%d ORDER BY due_at,id LIMIT 1",
        utc_mysql($now), MAX_SEND_ATTEMPTS
    ), ARRAY_A);
    if (!is_array($row)) { return null; }
    $id = (int)($row['id'] ?? 0);
    $status = (string)($row['telegram_status'] ?? '');
    $attempts = (int)($row['send_attempts'] ?? 0);
    if ($id <= 0 || !in_array($status, ['pending','retry_wait'], true) || $attempts >= MAX_SEND_ATTEMPTS) {
        return null;
    }
    $lock_token = wp_generate_uuid4();
    $claimed = $wpdb->update($table, [
        'telegram_status' => 'sending',
        'locked_at' => utc_mysql($now),
        'lock_token' => $lock_token,
        'send_attempts' => $attempts + 1,
    ], [
        'id' => $id,
        'telegram_status' => $status,
        'send_attempts' => $attempts,
        'resolved_at' => null,
    ]);
    if ((int)$claimed !== 1) { return null; }
    return array_merge($row, [
        'telegram_status' => 'sending',
        'locked_at' => utc_mysql($now),
        'lock_token' => $lock_token,
        'send_attempts' => $attempts + 1,
    ]);
}

function monitoring_telegram_integration(): ?array {
    $integration = null;
    if (defined('LP_MONITOR_TELEGRAM_INTEGRATION_ID') && (int)LP_MONITOR_TELEGRAM_INTEGRATION_ID > 0) {
        $integration = \LandingConfig\Integrations\get_integration((int)LP_MONITOR_TELEGRAM_INTEGRATION_ID);
        if (!is_array($integration) || ($integration['enabled'] ?? false) !== true
            || ($integration['adapter_type'] ?? '') !== 'telegram') {
            return null;
        }
    } else {
        $matches = \LandingConfig\Integrations\list_integrations_by_type('telegram', get_current_blog_id());
        if (count($matches) !== 1) { return null; }
        $integration = $matches[0];
    }
    $settings = (array)($integration['settings'] ?? []);
    $token = (string)($settings['bot_token'] ?? '');
    if (str_starts_with($token, 'v1:')) { $token = \LandingConfig\Encryption\decrypt($token); }
    $chat_id = (string)($settings['chat_id'] ?? '');
    if ($token === '' || $chat_id === '') { return null; }
    return ['id' => (int)$integration['id'], 'token' => $token, 'chat_id' => $chat_id];
}

function safe_form_context(?string $submission_id): array {
    if ($submission_id === null || !is_valid_submission_id($submission_id)) { return []; }
    global $wpdb;
    $row = $wpdb->get_row($wpdb->prepare(
        "SELECT page_path,form_id,cta_key FROM `" . \LandingConfig\DB\get_form_events_table_name()
        . "` WHERE submission_id=%s ORDER BY id DESC LIMIT 1", $submission_id
    ), ARRAY_A);
    if (!is_array($row)) { return []; }
    return [
        'page_path' => sanitize_text_field((string)($row['page_path'] ?? '')),
        'form_id' => sanitize_key((string)($row['form_id'] ?? '')),
        'cta_key' => sanitize_key((string)($row['cta_key'] ?? '')),
    ];
}

function safe_audit_context(?string $submission_id): array {
    if ($submission_id === null || !is_valid_submission_id($submission_id)) {
        return ['audit_found' => false];
    }
    global $wpdb;
    try {
        $row = $wpdb->get_row($wpdb->prepare(
            "SELECT id FROM `" . \LandingConfig\DB\get_lead_audit_table_name()
            . "` WHERE submission_id=%s ORDER BY id DESC LIMIT 1",
            $submission_id
        ), ARRAY_A);
    } catch (\Throwable $ignored) {
        return ['audit_found' => false];
    }
    $audit_id = is_array($row) ? max(0, (int)($row['id'] ?? 0)) : 0;
    if ($audit_id <= 0) { return ['audit_found' => false]; }
    return [
        'audit_found' => true,
        'audit_id' => $audit_id,
        'audit_url' => admin_url(
            'admin.php?page=landing-config-lead-audit&submission_id=' . rawurlencode($submission_id)
        ),
    ];
}

function build_alert_text(array $alert, array $context): string {
    $kind = (string)($alert['incident_kind'] ?? '');
    $lead_id = max(0, (int)($alert['lead_id'] ?? 0));
    $headings = [
        'missing_lead' => '🚨 Заявка не появилась',
        'javascript_stall' => '⚠️ Форма остановилась до запроса',
        'integration_failure' => '⚠️ Ошибка доставки заявки #' . $lead_id,
        'delivery_stuck' => '⚠️ Ошибка доставки заявки #' . $lead_id,
        'fallback_delivery_stuck' => '⚠️ Резервная заявка ожидает доставку',
        'fallback_delivery_uncertain' => '🚨 Доставка резервной заявки неопределённа',
        'external_outage' => '🚨 Резервное хранилище недоступно',
        'external_recovery' => '✅ Резервное хранилище восстановлено',
        'external_monitor_stale' => '🚨 Внешний мониторинг не отвечает',
        'external_monitor_recovery' => '✅ Внешний мониторинг восстановлен',
        'monitor_internal_failure' => '🚨 Внутренняя проверка заявок завершилась ошибкой',
        'test_alert' => '[TEST — DO NOT CONTACT]',
    ];
    $heading = $headings[$kind] ?? '🚨 Техническое событие заявок';
    $lines = [esc_html($heading), 'Сайт: hybridautos-ae', 'Инцидент: #' . max(0, (int)($alert['id'] ?? 0))];
    if (!empty($context['page_path'])) { $lines[] = 'Страница: ' . esc_html((string)$context['page_path']); }
    if (!empty($context['form_id'])) { $lines[] = 'Форма: ' . esc_html((string)$context['form_id']); }
    if (!empty($context['cta_key'])) { $lines[] = 'CTA: ' . esc_html((string)$context['cta_key']); }
    if ($kind === 'missing_lead') {
        if (($context['audit_found'] ?? false) === true
            && (int)($context['audit_id'] ?? 0) > 0
            && (string)($context['audit_url'] ?? '') !== '') {
            $audit_id = (int)$context['audit_id'];
            $lines[] = 'Аудит WordPress: #' . $audit_id;
            $lines[] = '<a href="' . esc_url((string)$context['audit_url']) . '">Открыть контакт в закрытом журнале</a>';
        } else {
            $lines[] = 'Контакт не дошёл в журнал WordPress — проверить резервное хранилище.';
        }
    }
    return implode("\n", $lines);
}

function normalized_monitor_retry_after($value): int {
    if (is_array($value)) { $value = reset($value); }
    if (is_int($value) || (is_string($value) && ctype_digit(trim($value)))) {
        return max(1, min(3600, (int)$value));
    }
    return 60;
}

function send_monitoring_alert(array $alert, int $now): array {
    $credentials = monitoring_telegram_integration();
    if ($credentials === null) {
        return ['status' => 'failed', 'code' => null, 'message_id' => null, 'retry_after' => 60];
    }
    $submission_id = isset($alert['submission_id']) ? (string)$alert['submission_id'] : null;
    $context = safe_form_context($submission_id);
    if (($alert['incident_kind'] ?? '') === 'missing_lead') {
        $context = array_merge($context, safe_audit_context($submission_id));
    }
    $text = build_alert_text($alert, $context);
    try {
        $response = wp_remote_post('https://api.telegram.org/bot' . $credentials['token'] . '/sendMessage', [
            'timeout' => 8,
            'redirection' => 0,
            'body' => ['chat_id' => $credentials['chat_id'], 'text' => $text, 'parse_mode' => 'HTML'],
        ]);
    } catch (\Throwable $ignored) {
        return ['status' => 'unknown', 'code' => null, 'message_id' => null, 'retry_after' => 60];
    }
    if (is_wp_error($response)) {
        return ['status' => 'unknown', 'code' => null, 'message_id' => null, 'retry_after' => 60];
    }
    $code = (int)wp_remote_retrieve_response_code($response);
    $decoded = json_decode((string)wp_remote_retrieve_body($response), true);
    $message_id = is_array($decoded) ? ($decoded['result']['message_id'] ?? null) : null;
    $confirmed = $code === 200 && is_array($decoded) && ($decoded['ok'] ?? null) === true
        && (is_int($message_id) || (is_string($message_id) && ctype_digit($message_id)))
        && (int)$message_id > 0;
    if ($confirmed) {
        return ['status' => 'sent', 'code' => 200, 'message_id' => (int)$message_id, 'retry_after' => 60];
    }
    if ($code === 429) {
        $retry_after = is_array($decoded) ? ($decoded['parameters']['retry_after'] ?? null) : null;
        return ['status' => 'retry_wait', 'code' => 429, 'message_id' => null,
            'retry_after' => normalized_monitor_retry_after($retry_after)];
    }
    if ($code >= 400 && $code < 500) {
        return ['status' => 'failed', 'code' => $code, 'message_id' => null, 'retry_after' => 60];
    }
    return ['status' => 'unknown', 'code' => $code > 0 ? $code : null, 'message_id' => null, 'retry_after' => 60];
}

function run_alert_queue(int $limit = 10, ?int $now = null): array {
    global $wpdb;
    $now = $now ?? time();
    $limit = max(1, min(100, $limit));
    $summary = ['processed' => 0, 'sent' => 0, 'retry_wait' => 0, 'unknown' => 0, 'failed' => 0];
    for ($i = 0; $i < $limit; $i++) {
        $alert = claim_next_alert($now);
        if ($alert === null) { break; }
        $summary['processed']++;
        $outcome = send_monitoring_alert($alert, $now);
        $status = (string)$outcome['status'];
        if ($status === 'retry_wait' && (int)$alert['send_attempts'] >= MAX_SEND_ATTEMPTS) {
            $status = 'failed';
        }
        $update = [
            'telegram_status' => $status,
            'last_response_at' => utc_mysql($now),
            'telegram_response_code' => $outcome['code'],
            'telegram_message_id' => $outcome['message_id'],
        ];
        if ($status === 'sent') { $update['sent_at'] = utc_mysql($now); }
        if ($status === 'retry_wait') { $update['due_at'] = utc_mysql($now + (int)$outcome['retry_after']); }
        $wpdb->update(get_monitor_alerts_table_name(), $update, [
            'id' => (int)$alert['id'], 'telegram_status' => 'sending', 'lock_token' => (string)$alert['lock_token'],
        ]);
        $summary[$status]++;
    }
    return $summary;
}

function mark_stale_alerts_unknown(?int $now = null): int {
    global $wpdb;
    $now = $now ?? time();
    $rows = $wpdb->get_results($wpdb->prepare(
        "SELECT id FROM `" . get_monitor_alerts_table_name() . "` WHERE telegram_status='sending' AND locked_at<%s LIMIT 100",
        utc_mysql($now - LOCK_TTL_SECONDS)
    ), ARRAY_A);
    $changed = 0;
    foreach (is_array($rows) ? $rows : [] as $row) {
        $updated = $wpdb->update(get_monitor_alerts_table_name(), [
            'telegram_status' => 'unknown', 'last_response_at' => utc_mysql($now),
        ], ['id' => (int)($row['id'] ?? 0), 'telegram_status' => 'sending']);
        if ((int)$updated === 1) { $changed++; }
    }
    return $changed;
}

function configuration_status(): array {
    $integrations = \LandingConfig\Integrations\list_integrations(get_current_blog_id());
    $enabled_emails = [];
    $neuroboost_enabled = false;
    $enabled_telegrams = [];
    $enabled_crm = [];
    foreach ($integrations as $integration) {
        if (($integration['enabled'] ?? false) !== true) { continue; }
        $type = sanitize_key((string)($integration['adapter_type'] ?? ''));
        $label = strtolower((string)($integration['label'] ?? '') . ' ' . (string)($integration['description'] ?? ''));
        if (str_contains($label, 'neuroboost') || str_contains($label, 'нейробуст')) {
            $neuroboost_enabled = true;
        }
        if ($type === 'email') { $enabled_emails[] = $integration; }
        if ($type === 'telegram') { $enabled_telegrams[] = $integration; }
        if (in_array($type, ['roistat','amocrm','bitrix24','hubspot'], true)) { $enabled_crm[] = $integration; }
    }
    $email_binding_ok = count($enabled_emails) === 1
        && strtolower(trim((string)($enabled_emails[0]['settings']['to'] ?? ''))) === 'elapova00@gmail.com';
    $telegram = null;
    if (defined('LP_MONITOR_TELEGRAM_INTEGRATION_ID') && (int)LP_MONITOR_TELEGRAM_INTEGRATION_ID > 0) {
        foreach ($enabled_telegrams as $candidate) {
            if ((int)($candidate['id'] ?? 0) === (int)LP_MONITOR_TELEGRAM_INTEGRATION_ID) { $telegram = $candidate; break; }
        }
    } elseif (count($enabled_telegrams) === 1) {
        $telegram = $enabled_telegrams[0];
    }
    $fallback_url = defined('LP_FALLBACK_URL') ? (string)LP_FALLBACK_URL : '';
    $signing = defined('LP_FALLBACK_SIGNING_SECRET') ? (string)LP_FALLBACK_SIGNING_SECRET : '';
    $status = defined('LP_FALLBACK_STATUS_SECRET') ? (string)LP_FALLBACK_STATUS_SECRET : '';
    $signing_valid = \LandingConfig\FallbackSecurity\decode_hmac_hex_secret($signing) !== null;
    $status_valid = \LandingConfig\FallbackSecurity\decode_hmac_hex_secret($status) !== null;
    return [
        'monitor_enabled' => is_enabled(),
        'fallback_enabled' => defined('LP_FALLBACK_ENABLED') && LP_FALLBACK_ENABLED === true,
        'test_mode_enabled' => defined('LP_FALLBACK_TEST_MODE') && LP_FALLBACK_TEST_MODE === true,
        'fallback_url_configured' => $fallback_url !== '',
        'fallback_url_valid' => filter_var($fallback_url, FILTER_VALIDATE_URL) !== false
            && strtolower((string)parse_url($fallback_url, PHP_URL_SCHEME)) === 'https',
        'signing_secret_configured' => $signing !== '',
        'signing_secret_valid' => $signing_valid,
        'status_secret_configured' => $status !== '',
        'status_secret_valid' => $status_valid,
        'secrets_distinct' => $signing_valid && $status_valid && $signing !== $status,
        'email_binding_ok' => $email_binding_ok,
        'neuroboost_disabled' => !$neuroboost_enabled && ($email_binding_ok || count($enabled_emails) === 0),
        'telegram_enabled' => is_array($telegram),
        'roistat_crm_enabled' => count($enabled_crm) >= 1,
        'email_integration_id' => $email_binding_ok ? (int)$enabled_emails[0]['id'] : 0,
        'telegram_integration_id' => is_array($telegram) ? (int)$telegram['id'] : 0,
        'roistat_crm_integration_id' => count($enabled_crm) >= 1 ? (int)$enabled_crm[0]['id'] : 0,
    ];
}

function add_minute_schedule(array $schedules): array {
    $schedules['landing_every_minute'] = ['interval' => 60, 'display' => 'Landing every minute'];
    return $schedules;
}

function touch_heartbeat(bool $ok, ?int $now = null): void {
    update_option(HEARTBEAT_OPTION, $now ?? time());
    update_option(RUN_STATUS_OPTION, $ok ? 'ok' : 'failed');
}

function external_health_state(): array {
    $stored = get_option(EXTERNAL_HEALTH_OPTION, []);
    $stored = is_array($stored) ? $stored : [];
    return array_merge([
        'last_processed_slot' => 0,
        'accepted_at' => 0,
        'last_status' => 'unknown',
        'failure_count' => 0,
        'episode_generation' => 0,
        'outage_open' => false,
        'monitoring_enabled_at' => 0,
        'monitor_stale_generation' => 0,
        'monitor_stale_open' => false,
    ], array_intersect_key($stored, array_flip([
        'last_processed_slot','accepted_at','last_status','failure_count','episode_generation',
        'outage_open','monitoring_enabled_at','monitor_stale_generation','monitor_stale_open',
    ])));
}

function save_external_health_state(array $state): void {
    update_option(EXTERNAL_HEALTH_OPTION, [
        'last_processed_slot' => max(0, (int)($state['last_processed_slot'] ?? 0)),
        'accepted_at' => max(0, (int)($state['accepted_at'] ?? 0)),
        'last_status' => in_array(($state['last_status'] ?? ''), ['unknown','ok','failed'], true) ? $state['last_status'] : 'unknown',
        'failure_count' => max(0, min(2, (int)($state['failure_count'] ?? 0))),
        'episode_generation' => max(0, (int)($state['episode_generation'] ?? 0)),
        'outage_open' => ($state['outage_open'] ?? false) === true,
        'monitoring_enabled_at' => max(0, (int)($state['monitoring_enabled_at'] ?? 0)),
        'monitor_stale_generation' => max(0, (int)($state['monitor_stale_generation'] ?? 0)),
        'monitor_stale_open' => ($state['monitor_stale_open'] ?? false) === true,
    ]);
}

function note_monitoring_enabled(?int $now = null): void {
    if (!is_enabled()) { return; }
    $state = external_health_state();
    if ((int)$state['monitoring_enabled_at'] <= 0) {
        $state['monitoring_enabled_at'] = $now ?? time();
        save_external_health_state($state);
    }
}

function apply_external_health_observation(string $status, int $slot, ?int $accepted_at = null): array {
    if (!in_array($status, ['ok','failed'], true) || $slot <= 0) {
        return ['accepted' => false, 'duplicate' => false, 'outage' => false, 'recovery' => false];
    }
    global $wpdb;
    $lock = 'lph_' . get_current_blog_id() . '_external_health';
    if ((int)$wpdb->get_var($wpdb->prepare('SELECT GET_LOCK(%s, 1)', $lock)) !== 1) {
        return ['accepted' => false, 'duplicate' => false, 'outage' => false, 'recovery' => false];
    }
    try {
        $state = external_health_state();
        if ($slot <= (int)$state['last_processed_slot']) {
            return ['accepted' => true, 'duplicate' => true, 'outage' => false, 'recovery' => false];
        }
        $accepted_at = $accepted_at ?? time();
        $outage = false;
        $recovery = false;
        if (($state['monitor_stale_open'] ?? false) === true && (int)$state['monitor_stale_generation'] > 0) {
            record_external_incident('external_monitor_recovery', 'external_monitor_recovery',
                (int)$state['monitor_stale_generation'], $accepted_at);
            $state['monitor_stale_open'] = false;
        }
        if ($status === 'failed') {
            if (($state['outage_open'] ?? false) === true) {
                $state['failure_count'] = 2;
            } elseif (($state['last_status'] ?? '') === 'failed'
                && $slot === (int)$state['last_processed_slot'] + 1
                && (int)$state['episode_generation'] > 0) {
                $state['failure_count'] = min(2, (int)$state['failure_count'] + 1);
            } else {
                $state['failure_count'] = 1;
                $state['episode_generation'] = $slot;
            }
            if ((int)$state['failure_count'] >= 2 && ($state['outage_open'] ?? false) !== true) {
                record_external_incident('external_outage', 'redis_outage',
                    (int)$state['episode_generation'], $accepted_at);
                $state['outage_open'] = true;
                $outage = true;
            }
        } else {
            if (($state['outage_open'] ?? false) === true && (int)$state['episode_generation'] > 0) {
                record_external_incident('external_recovery', 'redis_recovery',
                    (int)$state['episode_generation'], $accepted_at);
                $recovery = true;
            }
            $state['failure_count'] = 0;
            $state['outage_open'] = false;
        }
        $state['last_status'] = $status;
        $state['last_processed_slot'] = $slot;
        $state['accepted_at'] = $accepted_at;
        save_external_health_state($state);
        return ['accepted' => true, 'duplicate' => false, 'outage' => $outage, 'recovery' => $recovery];
    } finally {
        $wpdb->get_var($wpdb->prepare('SELECT RELEASE_LOCK(%s)', $lock));
    }
}

function check_external_monitor_stale(?int $now = null): array {
    if (!is_enabled()) { return ['stale' => false, 'created' => false]; }
    $now = $now ?? time();
    $state = external_health_state();
    $enabled_at = (int)$state['monitoring_enabled_at'];
    if ($enabled_at <= 0) {
        note_monitoring_enabled($now);
        return ['stale' => false, 'created' => false];
    }
    $reference = (int)$state['accepted_at'] > 0 ? (int)$state['accepted_at'] : $enabled_at;
    if ($now - $reference <= 900) { return ['stale' => false, 'created' => false]; }
    if (($state['monitor_stale_open'] ?? false) === true) {
        return ['stale' => true, 'created' => false];
    }
    $generation = max(1, intdiv($now, 300));
    record_external_incident('external_monitor_stale', 'external_monitor_stale', $generation, $now);
    $state['monitor_stale_generation'] = $generation;
    $state['monitor_stale_open'] = true;
    save_external_health_state($state);
    return ['stale' => true, 'created' => true];
}

function sync_monitoring_schedule(?int $now = null): void {
    $now = $now ?? time();
    // Lead delivery is a sales-critical service, not an optional monitoring
    // feature. Keep its worker scheduled during a staged monitoring rollout.
    if (!wp_next_scheduled(DELIVERY_HOOK)) {
        wp_schedule_event($now + 5, 'landing_every_minute', DELIVERY_HOOK);
    }
    if (!is_enabled()) {
        foreach ([SCAN_HOOK, QUEUE_HOOK, CLEANUP_HOOK] as $hook) {
            wp_clear_scheduled_hook($hook);
        }
        return;
    }
    note_monitoring_enabled($now);
    if (!wp_next_scheduled(SCAN_HOOK)) {
        wp_schedule_event($now + 10, 'landing_every_minute', SCAN_HOOK);
    }
    if (!wp_next_scheduled(QUEUE_HOOK)) {
        wp_schedule_event($now + 40, 'landing_every_minute', QUEUE_HOOK);
    }
    if (!wp_next_scheduled(CLEANUP_HOOK)) {
        wp_schedule_event($now + 300, 'daily', CLEANUP_HOOK);
    }
}

function run_delivery_cron_steps(callable $reconcile, callable $deliver): void {
    try {
        $reconcile();
    } catch (\Throwable $ignored) {
        error_log('[landing-config] delivery_reconcile_failed');
    }
    try {
        $deliver();
    } catch (\Throwable $ignored) {
        error_log('[landing-config] delivery_worker_failed');
    }
}

function run_delivery_cron(): void {
    run_delivery_cron_steps(
        // Reservation repair is part of delivery correctness and therefore
        // runs even when optional incident alerts are staged off.
        static function (): void { reconcile_delivery_rows(); },
        static function (): void {
            \LandingConfig\LeadDelivery\mark_stale_sending_unknown();
            \LandingConfig\LeadDelivery\run_delivery_worker(20);
        }
    );
}

function run_scan_cron(): void {
    if (!is_enabled()) { return; }
    try {
        reconcile_delivery_rows();
        run_missing_lead_scan();
        if (function_exists(__NAMESPACE__ . '\\check_external_monitor_stale')) {
            check_external_monitor_stale();
        }
        touch_heartbeat(true);
    } catch (\Throwable $ignored) {
        touch_heartbeat(false);
        error_log('[landing-config] monitor_scan_failed');
        record_incident('monitor_internal_failure', 'critical', null, null, null, '',
            'failed', 'monitor_scan_failed');
    }
}

function run_queue_cron(): void {
    if (!is_enabled()) { return; }
    try {
        mark_stale_alerts_unknown();
        run_alert_queue();
    } catch (\Throwable $ignored) {
        update_option(RUN_STATUS_OPTION, 'failed');
        error_log('[landing-config] monitor_queue_failed');
    }
}

function cleanup_expired_alerts(?int $now = null): array {
    global $wpdb;
    $now = $now ?? time();
    $cutoff_30 = utc_mysql($now - 30 * DAY_IN_SECONDS);
    $cutoff_90 = utc_mysql($now - 90 * DAY_IN_SECONDS);
    $table = get_monitor_alerts_table_name();
    $total = 0;
    do {
        $deleted = $wpdb->query($wpdb->prepare(
            "DELETE FROM `{$table}` WHERE telegram_status NOT IN ('pending','retry_wait','sending') AND ("
            . "(resolved_at IS NOT NULL AND resolved_at<%s) OR "
            . "(telegram_status='sent' AND sent_at IS NOT NULL AND sent_at<%s) OR "
            . "(telegram_status IN ('unknown','failed') AND COALESCE(last_response_at,last_seen_at)<%s)"
            . ") LIMIT 1000",
            $cutoff_30, $cutoff_30, $cutoff_90
        ));
        $deleted = is_int($deleted) && $deleted > 0 ? $deleted : 0;
        $total += $deleted;
    } while ($deleted === 1000);
    return ['deleted' => $total];
}

function run_cleanup_cron(): void {
    if (!is_enabled()) { return; }
    try {
        cleanup_expired_alerts();
    } catch (\Throwable $ignored) {
        error_log('[landing-config] monitor_cleanup_failed');
    }
}

add_filter('cron_schedules', __NAMESPACE__ . '\\add_minute_schedule');
add_action('init', __NAMESPACE__ . '\\sync_monitoring_schedule', 3);
add_action(DELIVERY_HOOK, __NAMESPACE__ . '\\run_delivery_cron');
add_action(SCAN_HOOK, __NAMESPACE__ . '\\run_scan_cron');
add_action(QUEUE_HOOK, __NAMESPACE__ . '\\run_queue_cron');
add_action(CLEANUP_HOOK, __NAMESPACE__ . '\\run_cleanup_cron');
