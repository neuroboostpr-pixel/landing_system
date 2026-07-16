<?php
namespace LandingConfig\LeadDelivery;

if (!defined('ABSPATH')) { exit; }

use function LandingConfig\DB\get_lead_log_table_name;
use function LandingConfig\DB\get_leads_table_name;

const DELIVERY_HOOK = 'landing_config_deliver_lead';
const MAX_ATTEMPTS = 3;
const STALE_SENDING_SECONDS = 300;

function utc_mysql(int $timestamp): string {
    return gmdate('Y-m-d H:i:s', $timestamp);
}

function reserve_integrations(int $lead_id): int {
    if ($lead_id <= 0) { return 0; }
    global $wpdb;
    $count = 0;
    $now = current_time('mysql', true);
    foreach (\LandingConfig\Integrations\list_integrations(get_current_blog_id()) as $integration) {
        $integration_id = (int)($integration['id'] ?? 0);
        $adapter = sanitize_key((string)($integration['adapter_type'] ?? ''));
        if (($integration['enabled'] ?? false) !== true || $integration_id <= 0 || $adapter === '') {
            continue;
        }
        $inserted = $wpdb->insert(get_lead_log_table_name(), [
            'lead_id' => $lead_id,
            'adapter' => $adapter,
            'integration_id' => $integration_id,
            'attempt' => 1,
            'status' => 'queued',
            'response_code' => null,
            'response_body' => null,
            'error_text' => null,
            'next_attempt_at' => $now,
            'locked_at' => null,
            'finished_at' => null,
            'provider_id' => null,
            'created_at' => $now,
        ]);
        if ($inserted !== false && $inserted !== 0) { $count++; }
    }
    return $count;
}

function delivery_lock_name(int $lead_id): string {
    return 'lpd_' . get_current_blog_id() . '_' . $lead_id;
}

function acquire_lead_lock(int $lead_id): bool {
    global $wpdb;
    return (int)$wpdb->get_var($wpdb->prepare('SELECT GET_LOCK(%s, %d)', delivery_lock_name($lead_id), 0)) === 1;
}

function release_lead_lock(int $lead_id): void {
    global $wpdb;
    $wpdb->get_var($wpdb->prepare('SELECT RELEASE_LOCK(%s)', delivery_lock_name($lead_id)));
}

function normalized_retry_after($value): int {
    if (is_array($value)) { $value = reset($value); }
    if (is_int($value) || (is_string($value) && ctype_digit(trim($value)))) {
        return max(1, min(3600, (int)$value));
    }
    return 60;
}

function safe_delivery_error_category(array $result, ?int $code): string {
    $known = ['configuration_missing','unsupported_adapter','adapter_exception','invalid_adapter_result','transport_error'];
    $raw = is_string($result['error'] ?? null) ? $result['error'] : '';
    if (in_array($raw, $known, true)) { return $raw; }
    if ($code === 429) { return 'rate_limited'; }
    if ($code !== null && $code >= 500) { return 'provider_5xx'; }
    if ($code !== null && $code >= 400) { return 'provider_4xx'; }
    if ($code === null) { return 'transport_error'; }
    return 'invalid_response';
}

function send_exact_integration(array $integration, array $lead): array {
    $type = sanitize_key((string)($integration['adapter_type'] ?? ''));
    try {
        if ($type === 'telegram') {
            $result = function_exists('LandingConfig\\REST\\_send_telegram')
                ? \LandingConfig\REST\_send_telegram((array)($integration['settings'] ?? []), $lead)
                : ['ok' => false, 'error' => 'configuration_missing'];
        } else {
            $map = [
                'email' => '\\LandingConfig\\Adapters\\EmailAdapter',
                'whatsapp' => '\\LandingConfig\\Adapters\\WhatsAppAdapter',
                'amocrm' => '\\LandingConfig\\Adapters\\AmoCRMAdapter',
                'bitrix24' => '\\LandingConfig\\Adapters\\Bitrix24Adapter',
                'hubspot' => '\\LandingConfig\\Adapters\\HubSpotAdapter',
                'roistat' => '\\LandingConfig\\Adapters\\RoistatAdapter',
            ];
            if (empty($map[$type]) || !class_exists($map[$type])) {
                $result = ['ok' => false, 'error' => 'unsupported_adapter'];
            } else {
                $adapter = new $map[$type]();
                $result = $adapter->send($lead, (array)($integration['settings'] ?? []));
            }
        }
    } catch (\Throwable $ignored) {
        $result = ['ok' => false, 'error' => 'adapter_exception'];
    }
    if (!is_array($result)) {
        $result = ['ok' => false, 'error' => 'invalid_adapter_result'];
    }
    $code = isset($result['response_code']) && is_numeric($result['response_code'])
        ? (int)$result['response_code'] : null;
    $ok = ($result['ok'] ?? false) === true;
    if ($ok) {
        $status = $type === 'email' ? 'accepted' : 'success';
        $category = '';
    } elseif ($code === 429) {
        $status = 'retry_wait';
        $category = 'rate_limited';
    } elseif ($code === null || $code >= 500 || $code === 408 || $code === 409 || ($code >= 200 && $code < 300)) {
        $status = 'unknown';
        $category = safe_delivery_error_category($result, $code);
    } else {
        $status = 'failed_permanent';
        $category = safe_delivery_error_category($result, $code);
    }
    return [
        'status' => $status,
        'safe_category' => $category,
        'response_code' => $code,
        'retry_after' => normalized_retry_after($result['retry_after'] ?? null),
    ];
}

function load_lead(int $lead_id): ?array {
    global $wpdb;
    $row = $wpdb->get_row($wpdb->prepare(
        'SELECT * FROM `' . get_leads_table_name() . '` WHERE id=%d LIMIT 1', $lead_id
    ), ARRAY_A);
    return is_array($row) ? $row : null;
}

function observe_worker_result(int $lead_id, int $integration_id, string $adapter,
    string $status, string $safe_category, ?int $response_code): void {
    if (!function_exists('LandingConfig\\Monitoring\\observe_delivery_result')) { return; }
    try {
        \LandingConfig\Monitoring\observe_delivery_result(
            $lead_id, $integration_id, sanitize_key($adapter), $status, $safe_category, $response_code
        );
    } catch (\Throwable $ignored) {
        error_log('[landing-config] monitor_observe_failed');
    }
}

function process_reservation(array $row, int $now): bool {
    global $wpdb;
    $row_id = (int)($row['id'] ?? 0);
    $lead_id = (int)($row['lead_id'] ?? 0);
    $integration_id = (int)($row['integration_id'] ?? 0);
    $adapter = sanitize_key((string)($row['adapter'] ?? ''));
    $attempt = max(1, (int)($row['attempt'] ?? 1));
    if ($row_id <= 0 || $lead_id <= 0 || $integration_id <= 0 || $adapter === '' || !acquire_lead_lock($lead_id)) {
        return false;
    }
    try {
        $claimed = $wpdb->update(get_lead_log_table_name(), [
            'status' => 'sending', 'locked_at' => utc_mysql($now),
        ], ['id' => $row_id, 'status' => 'queued']);
        if ((int)$claimed !== 1) { return false; }

        $lead = load_lead($lead_id);
        $integration = \LandingConfig\Integrations\get_integration($integration_id);
        if (!is_array($lead) || !is_array($integration) || ($integration['enabled'] ?? false) !== true
            || sanitize_key((string)($integration['adapter_type'] ?? '')) !== $adapter) {
            $result = ['status' => 'failed_permanent', 'safe_category' => 'configuration_missing', 'response_code' => null, 'retry_after' => 60];
        } else {
            $result = send_exact_integration($integration, $lead);
        }

        $status = (string)$result['status'];
        if ($status === 'retry_wait' && $attempt >= MAX_ATTEMPTS) {
            $status = 'failed_permanent';
        }
        $wpdb->update(get_lead_log_table_name(), [
            'status' => $status,
            'response_code' => $result['response_code'],
            'response_body' => null,
            'error_text' => $result['safe_category'] !== '' ? $result['safe_category'] : null,
            'finished_at' => utc_mysql($now),
        ], ['id' => $row_id, 'status' => 'sending']);

        if ($status === 'retry_wait') {
            $due = $now + (int)$result['retry_after'];
            $wpdb->insert(get_lead_log_table_name(), [
                'lead_id' => $lead_id,
                'adapter' => $adapter,
                'integration_id' => $integration_id,
                'attempt' => $attempt + 1,
                'status' => 'queued',
                'response_code' => null,
                'response_body' => null,
                'error_text' => null,
                'next_attempt_at' => utc_mysql($due),
                'locked_at' => null,
                'finished_at' => null,
                'provider_id' => null,
                'created_at' => utc_mysql($now),
            ]);
            if (function_exists('wp_schedule_single_event')) {
                wp_schedule_single_event($due, DELIVERY_HOOK, [$lead_id]);
            }
        }
        observe_worker_result($lead_id, $integration_id, $adapter, $status,
            (string)$result['safe_category'], $result['response_code']);
        return true;
    } finally {
        release_lead_lock($lead_id);
    }
}

function run_delivery_worker(int $limit = 20, ?int $now = null): array {
    global $wpdb;
    $now = $now ?? time();
    $limit = max(1, min(100, $limit));
    $rows = $wpdb->get_results($wpdb->prepare(
        "SELECT id,lead_id,integration_id,adapter,attempt,status,next_attempt_at FROM `" . get_lead_log_table_name()
        . "` WHERE status='queued' AND (next_attempt_at IS NULL OR next_attempt_at<=%s) ORDER BY id ASC LIMIT %d",
        utc_mysql($now), $limit
    ), ARRAY_A);
    $processed = 0;
    foreach (is_array($rows) ? $rows : [] as $row) {
        if (process_reservation((array)$row, $now)) { $processed++; }
    }
    return ['processed' => $processed];
}

function mark_stale_sending_unknown(?int $now = null): int {
    global $wpdb;
    $now = $now ?? time();
    $cutoff = utc_mysql($now - STALE_SENDING_SECONDS);
    $rows = $wpdb->get_results($wpdb->prepare(
        "SELECT id,lead_id,integration_id,adapter FROM `" . get_lead_log_table_name()
        . "` WHERE status='sending' AND locked_at<%s LIMIT 100", $cutoff
    ), ARRAY_A);
    $changed = 0;
    foreach (is_array($rows) ? $rows : [] as $row) {
        $updated = $wpdb->update(get_lead_log_table_name(), [
            'status' => 'unknown', 'error_text' => 'delivery_sending_stale',
            'finished_at' => utc_mysql($now),
        ], ['id' => (int)($row['id'] ?? 0), 'status' => 'sending']);
        if ((int)$updated === 1) {
            $changed++;
            observe_worker_result((int)($row['lead_id'] ?? 0), (int)($row['integration_id'] ?? 0),
                sanitize_key((string)($row['adapter'] ?? '')), 'unknown', 'delivery_sending_stale', null);
        }
    }
    return $changed;
}
