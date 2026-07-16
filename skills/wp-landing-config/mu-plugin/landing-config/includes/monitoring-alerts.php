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
const GRACE_SECONDS = 300;
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
    $missing = $wpdb->get_results($wpdb->prepare(
        "SELECT l.id FROM `" . get_leads_table_name() . "` l LEFT JOIN `" . get_lead_log_table_name()
        . "` d ON d.lead_id=l.id WHERE l.created_at<=%s GROUP BY l.id HAVING COUNT(d.id)=0 LIMIT 100",
        utc_mysql($now - 60)
    ), ARRAY_A);
    $reservations_recreated = 0;
    foreach (is_array($missing) ? $missing : [] as $lead) {
        $lead_id = (int)($lead['id'] ?? 0);
        if ($lead_id <= 0) { continue; }
        \LandingConfig\LeadDelivery\reserve_integrations($lead_id);
        if (function_exists('wp_schedule_single_event')) {
            wp_schedule_single_event($now, \LandingConfig\LeadDelivery\DELIVERY_HOOK, [$lead_id]);
        }
        $reservations_recreated++;
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

function receipt_status_signature(string $path, int $timestamp): ?string {
    if (!defined('LP_FALLBACK_STATUS_SECRET') || !defined('LP_FALLBACK_SITE_ID')
        || LP_FALLBACK_SITE_ID !== 'hybridautos-ae') {
        return null;
    }
    $key = \LandingConfig\FallbackSecurity\decode_hmac_hex_secret((string)LP_FALLBACK_STATUS_SECRET);
    if ($key === null) { return null; }
    return hash_hmac('sha256', "GET\n{$path}\n{$timestamp}\nhybridautos-ae", $key);
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
