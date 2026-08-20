<?php
namespace LandingConfig\LeadDelivery;

if (!defined('ABSPATH')) { exit; }

use function LandingConfig\DB\get_lead_log_table_name;
use function LandingConfig\DB\get_leads_table_name;

const DELIVERY_HOOK = 'landing_config_deliver_lead';
const MAX_ATTEMPTS = 5;
const STALE_SENDING_SECONDS = 300;

function utc_mysql(int $timestamp): string {
    return gmdate('Y-m-d H:i:s', $timestamp);
}

/** @return array<int,string> exact integration id => adapter */
function normalize_delivery_targets(array $targets): array {
    $normalized = [];
    foreach ($targets as $integration_id => $adapter) {
        if ((!is_int($integration_id) && !(is_string($integration_id) && ctype_digit($integration_id)))
            || !is_string($adapter)) {
            continue;
        }
        $integration_id = (int)$integration_id;
        $safe_adapter = sanitize_key($adapter);
        if ($integration_id <= 0 || $safe_adapter === '' || $safe_adapter !== $adapter) { continue; }
        $normalized[$integration_id] = $safe_adapter;
    }
    ksort($normalized, SORT_NUMERIC);
    return $normalized;
}

/** @return array<int,string> exact enabled targets at the instant of intake */
function snapshot_enabled_integrations(): array {
    if (!function_exists('LandingConfig\\Integrations\\read_delivery_targets_strict')) {
        throw new \RuntimeException('integration catalog health service missing');
    }
    $targets = normalize_delivery_targets(
        \LandingConfig\Integrations\read_delivery_targets_strict(get_current_blog_id())
    );
    // A dedicated Telegram integration can be reserved for operational
    // failure alerts. It must not receive every sales lead in addition to the
    // normal lead Telegram channel.
    $monitor_id = defined('LP_MONITOR_TELEGRAM_INTEGRATION_ID')
        ? (int)LP_MONITOR_TELEGRAM_INTEGRATION_ID
        : (int)get_option('landing_monitor_telegram_integration_id', 0);
    if ($monitor_id > 0 && ($targets[$monitor_id] ?? '') === 'telegram') {
        unset($targets[$monitor_id]);
    }
    return $targets;
}

function encode_delivery_targets(array $targets): string {
    $encoded = wp_json_encode(normalize_delivery_targets($targets), JSON_UNESCAPED_SLASHES);
    return is_string($encoded) ? $encoded : '';
}

/** @return array<int,string>|null null means absent/corrupt, [] is a valid no-channel plan */
function decode_delivery_targets($encoded): ?array {
    if (!is_string($encoded) || $encoded === '') { return null; }
    $decoded = json_decode($encoded, true);
    if (!is_array($decoded)) { return null; }
    $normalized = normalize_delivery_targets($decoded);
    return count($normalized) === count($decoded) ? $normalized : null;
}

function reserve_integrations(int $lead_id, ?array $targets = null): int {
    if ($lead_id <= 0) { return 0; }
    global $wpdb;
    $count = 0;
    $now = current_time('mysql', true);
    $targets = $targets === null ? snapshot_enabled_integrations() : normalize_delivery_targets($targets);
    foreach ($targets as $integration_id => $adapter) {
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

function delivery_snapshot_is_complete(int $lead_id, array $targets): bool {
    if ($lead_id <= 0) { return false; }
    $targets = normalize_delivery_targets($targets);
    if ($targets === []) { return true; }
    global $wpdb;
    $ids = implode(',', array_map('intval', array_keys($targets)));
    $rows = $wpdb->get_results($wpdb->prepare(
        "SELECT integration_id,adapter FROM `" . get_lead_log_table_name()
        . "` WHERE lead_id=%d AND attempt=1 AND integration_id IN ({$ids})",
        $lead_id
    ), ARRAY_A);
    if (!is_array($rows)) { return false; }
    $present = [];
    foreach ($rows as $row) {
        $id = (int)($row['integration_id'] ?? 0);
        $adapter = sanitize_key((string)($row['adapter'] ?? ''));
        if ($id > 0 && $adapter !== '') { $present[$id] = $adapter; }
    }
    ksort($present, SORT_NUMERIC);
    return $present === $targets;
}

/** @return array{created:int,complete:bool} */
function ensure_delivery_reservations(int $lead_id, array $targets): array {
    $targets = normalize_delivery_targets($targets);
    $created = reserve_integrations($lead_id, $targets);
    $complete = delivery_snapshot_is_complete($lead_id, $targets);
    if ($complete) {
        global $wpdb;
        $updated = $wpdb->update(get_leads_table_name(), [
            'delivery_reservations_ready' => 1,
        ], ['id' => $lead_id]);
        if ($updated === false) { $complete = false; }
    }
    return ['created' => $created, 'complete' => $complete];
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
        $map = [
            'email' => '\\LandingConfig\\Adapters\\EmailAdapter',
            'telegram' => '\\LandingConfig\\Adapters\\TelegramAdapter',
            'whatsapp' => '\\LandingConfig\\Adapters\\WhatsAppAdapter',
            'amocrm' => '\\LandingConfig\\Adapters\\AmoCRMAdapter',
            'bitrix24' => '\\LandingConfig\\Adapters\\Bitrix24Adapter',
            'hubspot' => '\\LandingConfig\\Adapters\\HubSpotAdapter',
            'roistat' => '\\LandingConfig\\Adapters\\RoistatAdapter',
        ];
        if (empty($map[$type]) || !class_exists($map[$type])) {
            $result = ['ok' => false, 'status' => 'failed_permanent', 'error' => 'unsupported_adapter'];
        } else {
            $adapter = new $map[$type]();
            $result = $adapter->send($lead, (array)($integration['settings'] ?? []));
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
    $declared_status = is_string($result['status'] ?? null) ? $result['status'] : '';
    if ($type === 'telegram' && $ok && in_array($declared_status, ['success', 'accepted'], true)) {
        $status = $declared_status;
        $category = '';
    } elseif ($type === 'telegram' && !$ok && in_array($declared_status, ['retry_wait', 'failed_permanent', 'unknown'], true)) {
        $status = $declared_status;
        $category = safe_delivery_error_category($result, $code);
    } elseif ($ok) {
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
    $provider_id = null;
    if (in_array($status, ['success', 'accepted'], true)
        && (is_string($result['provider_id'] ?? null) || is_int($result['provider_id'] ?? null))) {
        $candidate = trim((string)$result['provider_id']);
        $provider_id = $candidate !== '' ? $candidate : null;
    }
    return [
        'status' => $status,
        'safe_category' => $category,
        'response_code' => $code,
        'provider_id' => $provider_id,
        'retry_after' => normalized_retry_after($result['retry_after'] ?? null),
    ];
}

/** @return array{ok:bool,lead:?array} */
function load_lead_checked(int $lead_id): array {
    global $wpdb;
    if (isset($wpdb->last_error)) { $wpdb->last_error = ''; }
    $row = $wpdb->get_row($wpdb->prepare(
        'SELECT * FROM `' . get_leads_table_name() . '` WHERE id=%d LIMIT 1', $lead_id
    ), ARRAY_A);
    if ((string)($wpdb->last_error ?? '') !== '') { return ['ok' => false, 'lead' => null]; }
    return ['ok' => true, 'lead' => is_array($row) ? $row : null];
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

function find_exact_attempt(int $lead_id, int $integration_id, int $attempt): ?array {
    if ($lead_id <= 0 || $integration_id <= 0 || $attempt <= 0) { return null; }
    global $wpdb;
    $row = $wpdb->get_row($wpdb->prepare(
        "SELECT id,status,next_attempt_at FROM `" . get_lead_log_table_name()
        . "` WHERE lead_id=%d AND integration_id=%d AND attempt=%d LIMIT 1",
        $lead_id, $integration_id, $attempt
    ), ARRAY_A);
    return is_array($row) && (int)($row['id'] ?? 0) > 0 ? $row : null;
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

        $lead_read = load_lead_checked($lead_id);
        $integration_read = function_exists('LandingConfig\\Integrations\\get_delivery_integration_checked')
            ? \LandingConfig\Integrations\get_delivery_integration_checked($integration_id)
            : ['ok' => false, 'integration' => null];
        $lead = $lead_read['lead'] ?? null;
        $integration = $integration_read['integration'] ?? null;
        if (!($lead_read['ok'] ?? false) || !($integration_read['ok'] ?? false)) {
            // No provider was contacted. A bounded retry is safe and avoids
            // permanently losing a channel because WordPress briefly could
            // not read the lead or integration configuration.
            $result = ['status' => 'retry_wait', 'safe_category' => 'configuration_read_error',
                'response_code' => null, 'provider_id' => null, 'retry_after' => 60];
        } elseif (!is_array($lead) || !is_array($integration) || ($integration['enabled'] ?? false) !== true
            || sanitize_key((string)($integration['adapter_type'] ?? '')) !== $adapter) {
            $result = ['status' => 'failed_permanent', 'safe_category' => 'configuration_missing', 'response_code' => null, 'retry_after' => 60];
        } else {
            $result = send_exact_integration($integration, $lead);
        }

        $status = (string)$result['status'];
        if ($status === 'retry_wait' && $attempt >= MAX_ATTEMPTS) {
            $status = 'failed_permanent';
        }
        if ($status === 'retry_wait') {
            $due = $now + (int)$result['retry_after'];
            $next_attempt = $attempt + 1;
            $inserted = $wpdb->insert(get_lead_log_table_name(), [
                'lead_id' => $lead_id,
                'adapter' => $adapter,
                'integration_id' => $integration_id,
                'attempt' => $next_attempt,
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
            $successor_exists = $inserted !== false && $inserted !== 0;
            if (!$successor_exists) {
                $successor_exists = find_exact_attempt($lead_id, $integration_id, $next_attempt) !== null;
            }
            if (!$successor_exists) {
                // The provider explicitly asked us to retry, but the new row
                // could not be persisted. Reuse the claimed row as the next
                // bounded attempt so the contact cannot silently fall out of
                // the delivery queue.
                $recycled = $wpdb->update(get_lead_log_table_name(), [
                    'attempt' => $next_attempt,
                    'status' => 'queued',
                    'response_code' => null,
                    'response_body' => null,
                    'error_text' => null,
                    'next_attempt_at' => utc_mysql($due),
                    'locked_at' => null,
                    'finished_at' => null,
                    'provider_id' => null,
                ], ['id' => $row_id, 'status' => 'sending']);
                if ((int)$recycled !== 1) {
                    error_log('[landing-config] delivery_retry_persist_failed');
                    return false;
                }
                if (function_exists('wp_schedule_single_event')) {
                    wp_schedule_single_event($due, DELIVERY_HOOK, [$lead_id]);
                }
                return true;
            }

            $closed = $wpdb->update(get_lead_log_table_name(), [
                'status' => 'retry_wait',
                'response_code' => $result['response_code'],
                'response_body' => null,
                'error_text' => $result['safe_category'] !== '' ? $result['safe_category'] : null,
                'provider_id' => $result['provider_id'] ?? null,
                'finished_at' => utc_mysql($now),
            ], ['id' => $row_id, 'status' => 'sending']);
            if ((int)$closed !== 1) {
                // The successor is already durable, so do not create another
                // attempt. Stale recovery below will close this exact handoff
                // after proving the successor exists.
                error_log('[landing-config] delivery_retry_handoff_close_failed');
            }
            if (function_exists('wp_schedule_single_event')) {
                wp_schedule_single_event($due, DELIVERY_HOOK, [$lead_id]);
            }
        } else {
            $wpdb->update(get_lead_log_table_name(), [
                'status' => $status,
                'response_code' => $result['response_code'],
                'response_body' => null,
                'error_text' => $result['safe_category'] !== '' ? $result['safe_category'] : null,
                'provider_id' => $result['provider_id'] ?? null,
                'finished_at' => utc_mysql($now),
            ], ['id' => $row_id, 'status' => 'sending']);
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
        "SELECT id,lead_id,integration_id,adapter,attempt FROM `" . get_lead_log_table_name()
        . "` WHERE status='sending' AND locked_at<%s LIMIT 100", $cutoff
    ), ARRAY_A);
    $changed = 0;
    foreach (is_array($rows) ? $rows : [] as $row) {
        $attempt = max(1, (int)($row['attempt'] ?? 1));
        $successor = find_exact_attempt(
            (int)($row['lead_id'] ?? 0),
            (int)($row['integration_id'] ?? 0),
            $attempt + 1
        );
        if ($successor !== null) {
            $updated = $wpdb->update(get_lead_log_table_name(), [
                'status' => 'retry_wait',
                'error_text' => 'delivery_retry_handoff_repaired',
                'finished_at' => utc_mysql($now),
            ], ['id' => (int)($row['id'] ?? 0), 'status' => 'sending']);
            if ((int)$updated === 1) { $changed++; }
            continue;
        }
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
