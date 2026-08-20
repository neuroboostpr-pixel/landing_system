<?php
namespace LandingConfig\REST;

if (!defined('ABSPATH')) { exit; }

use function LandingConfig\DB\get_leads_table_name;
use function LandingConfig\DB\get_lead_audit_table_name;

const SUBMISSION_LOCK_WAIT_SECONDS = 3;
const MAX_BODY_BYTES = 196608;
const RATE_BUCKET_SECONDS = 3600;

function get_rate_limit(): int {
    $from_db = get_option('lp_rate_limit_per_hour', false);
    if ($from_db !== false) {
        return (int) $from_db;
    }
    if (defined('LP_RATE_LIMIT_PER_HOUR')) {
        return (int) LP_RATE_LIMIT_PER_HOUR;
    }
    return 10;
}

function get_global_rate_limit(): int {
    $from_db = get_option('lp_global_rate_limit_per_hour', false);
    if ($from_db !== false) { return max(0, (int)$from_db); }
    if (defined('LP_GLOBAL_RATE_LIMIT_PER_HOUR')) {
        return max(0, (int)LP_GLOBAL_RATE_LIMIT_PER_HOUR);
    }
    // This inherited technical safeguard is not a validated business-traffic
    // forecast. It bounds database growth and limits how long a public flood
    // can consume intake capacity before the next fixed-hour bucket.
    return 500;
}

function get_honeypot_audit_limit(): int {
    $from_db = get_option('lp_honeypot_audit_limit_per_hour', false);
    if ($from_db !== false) { return max(1, min(500, (int)$from_db)); }
    if (defined('LP_HONEYPOT_AUDIT_LIMIT_PER_HOUR')) {
        return max(1, min(500, (int)LP_HONEYPOT_AUDIT_LIMIT_PER_HOUR));
    }
    return 50;
}

function lead_request_size($request, array $params): int {
    $content_length = isset($_SERVER['CONTENT_LENGTH']) ? max(0, (int)$_SERVER['CONTENT_LENGTH']) : 0;
    $raw = method_exists($request, 'get_body') ? (string)$request->get_body() : '';
    $encoded = function_exists('wp_json_encode')
        ? wp_json_encode($params, JSON_UNESCAPED_UNICODE)
        : json_encode($params, JSON_UNESCAPED_UNICODE);
    $parsed_length = is_string($encoded) ? strlen($encoded) : MAX_BODY_BYTES + 1;
    return max($content_length, strlen($raw), $parsed_length);
}

function rate_bucket_start(?int $now = null): int {
    return intdiv($now ?? time(), RATE_BUCKET_SECONDS) * RATE_BUCKET_SECONDS;
}

function rate_option_name(string $prefix, string $ip, int $bucket, string $kind = ''): string {
    $safe_kind = $kind === '' ? '' : sanitize_key($kind) . '_';
    return $prefix . $safe_kind . $bucket . '_' . substr(hash('sha256', $ip), 0, 24);
}

function rate_limit_lock_name(string $ip, int $bucket): string {
    return 'lpr_' . get_current_blog_id() . '_' . substr(hash('sha256', $bucket . '|' . $ip), 0, 32);
}

function durable_rate_count($stored): ?int {
    if ($stored === false) { return 0; }
    if (is_int($stored) && $stored >= 0) { return $stored; }
    if (is_string($stored) && preg_match('/^(?:0|[1-9][0-9]*)$/D', $stored) === 1) {
        return (int)$stored;
    }
    return null;
}

/**
 * A durable fixed-hour counter serialised by a MySQL named lock. Unlike a
 * transient-only counter, cache eviction cannot reset it and concurrent POSTs
 * from the same IP cannot all pass the limit together.
 */
function consume_lead_rate_limit(string $ip, ?int $now = null): string {
    global $wpdb;
    $bucket = rate_bucket_start($now);
    // One short site-wide lock makes both the global and per-IP counters a
    // single decision, including requests from rotating addresses.
    $lock = rate_limit_lock_name('__site__', $bucket);
    if ((int)$wpdb->get_var($wpdb->prepare(
        'SELECT GET_LOCK(%s, %d)', $lock, SUBMISSION_LOCK_WAIT_SECONDS
    )) !== 1) {
        return 'busy';
    }

    try {
        $key = rate_option_name('landing_lead_rl_bucket_', $ip, $bucket);
        $global_key = rate_option_name('landing_lead_rl_bucket_', '__site__', $bucket, 'global');
        $stored = get_option($key, false);
        $global_stored = get_option($global_key, false);
        $count = durable_rate_count($stored);
        $global_count = durable_rate_count($global_stored);
        if ($count === null || $global_count === null) { return 'busy'; }
        $limit = max(0, get_rate_limit());
        $global_limit = get_global_rate_limit();
        if ($global_count >= $global_limit) { return 'global_limited'; }
        if ($count >= $limit) { return 'limited'; }

        $next = $count + 1;
        $global_next = $global_count + 1;
        $global_written = $global_stored === false
            ? add_option($global_key, (string)$global_next, '', false)
            : update_option($global_key, (string)$global_next);
        if (!$global_written) { return 'busy'; }
        $written = $stored === false
            ? add_option($key, (string)$next, '', false)
            : update_option($key, (string)$next);
        return $written ? 'allowed' : 'busy';
    } finally {
        $wpdb->get_var($wpdb->prepare('SELECT RELEASE_LOCK(%s)', $lock));
    }
}

/**
 * add_option is backed by the unique option_name index, so only one parallel
 * request can claim a recoverable blocked-attempt audit slot. A cache miss or
 * restart cannot recreate the same database key.
 */
function claim_blocked_audit_slot(string $kind, string $ip, ?int $now = null): bool {
    $bucket = rate_bucket_start($now);
    $key = rate_option_name('landing_lead_rl_audit_guard_', $ip, $bucket, $kind);
    return add_option($key, (string)$bucket, '', false);
}

/**
 * Preserve a small number of possible password-manager false positives while
 * keeping bot-filled honeypots on a separate durable budget. They therefore
 * cannot fill the much more important real-lead intake budget.
 */
function claim_honeypot_audit_slot(string $ip, ?int $now = null): bool {
    global $wpdb;
    $bucket = rate_bucket_start($now);
    $lock = rate_limit_lock_name('__honeypot_audit__', $bucket);
    if ((int)$wpdb->get_var($wpdb->prepare(
        'SELECT GET_LOCK(%s, %d)', $lock, SUBMISSION_LOCK_WAIT_SECONDS
    )) !== 1) {
        return false;
    }
    try {
        $budget_key = rate_option_name(
            'landing_lead_rl_audit_budget_', '__site__', $bucket, 'honeypot'
        );
        $stored = get_option($budget_key, false);
        $count = durable_rate_count($stored);
        if ($count === null) { return false; }
        if ($count >= get_honeypot_audit_limit()) { return false; }

        $guard_key = rate_option_name('landing_lead_rl_audit_guard_', $ip, $bucket, 'honeypot');
        if (!add_option($guard_key, (string)$bucket, '', false)) { return false; }
        $written = $stored === false
            ? add_option($budget_key, (string)($count + 1), '', false)
            : update_option($budget_key, (string)($count + 1));
        if (!$written) {
            delete_option($guard_key);
            return false;
        }
        return true;
    } finally {
        $wpdb->get_var($wpdb->prepare('SELECT RELEASE_LOCK(%s)', $lock));
    }
}

add_action('rest_api_init', function () {
    register_rest_route('landing/v1', '/lead', [
        'methods'             => 'POST',
        'callback'            => __NAMESPACE__ . '\\handle_lead',
        'permission_callback' => '__return_true',  // public; protected by honeypot + rate limit
    ]);
});

/**
 * Correlation is optional and must never become another reason to lose a lead.
 * Invalid client identifiers are discarded; valid browser UUIDv4 values are
 * safe to copy into the audit and lead rows.
 */
function normalize_submission_id($value): ?string {
    if (!is_scalar($value)) {
        return null;
    }

    $submission_id = strtolower(trim((string) $value));
    if (preg_match('/^[0-9a-f]{8}-[0-9a-f]{4}-4[0-9a-f]{3}-[89ab][0-9a-f]{3}-[0-9a-f]{12}$/', $submission_id) !== 1) {
        return null;
    }

    return $submission_id;
}

/**
 * Cut a valid UTF-8 value to a database character limit without splitting a
 * multibyte character. Lead input is sanitized before reaching this helper.
 */
function limit_utf8_characters(string $value, int $max_characters): string {
    if ($max_characters <= 0 || $value === '') {
        return '';
    }
    if (preg_match('//u', $value) !== 1) {
        return '';
    }
    if (function_exists('mb_strlen') && function_exists('mb_substr')) {
        return mb_strlen($value, 'UTF-8') <= $max_characters
            ? $value
            : mb_substr($value, 0, $max_characters, 'UTF-8');
    }
    if (function_exists('iconv_strlen') && function_exists('iconv_substr')) {
        $length = iconv_strlen($value, 'UTF-8');
        if ($length !== false && $length <= $max_characters) {
            return $value;
        }
        $cut = iconv_substr($value, 0, $max_characters, 'UTF-8');
        return is_string($cut) ? $cut : '';
    }

    preg_match_all('/./us', $value, $characters);
    return implode('', array_slice($characters[0] ?? [], 0, $max_characters));
}

/**
 * MySQL TEXT is limited by bytes (65,535), not by visible characters.
 */
function limit_utf8_bytes(string $value, int $max_bytes): string {
    if ($max_bytes <= 0 || $value === '') {
        return '';
    }
    if (preg_match('//u', $value) !== 1) {
        return '';
    }
    if (strlen($value) <= $max_bytes) {
        return $value;
    }
    if (function_exists('mb_strcut')) {
        $cut = mb_strcut($value, 0, $max_bytes, 'UTF-8');
        return is_string($cut) ? $cut : '';
    }

    $cut = substr($value, 0, $max_bytes);
    while ($cut !== '' && preg_match('//u', $cut) !== 1) {
        $cut = substr($cut, 0, -1);
    }
    return $cut;
}

/**
 * Sanitize one submitted scalar and make it safe for its actual DB column.
 */
function normalize_lead_text($value, int $limit, string $unit = 'characters', bool $email = false): string {
    if (!is_scalar($value)) {
        return '';
    }

    $unslashed = wp_unslash((string) $value);
    $sanitized = $email ? sanitize_email($unslashed) : sanitize_text_field($unslashed);
    return $unit === 'bytes'
        ? limit_utf8_bytes($sanitized, $limit)
        : limit_utf8_characters($sanitized, $limit);
}

/**
 * Single source of truth for both landing_lead_audit and landing_leads.
 * Optional attribution must never make either complete INSERT fail.
 */
function normalize_lead_payload(array $params, string $ip, string $user_agent): array {
    $recaptcha_token = $params['recaptcha_token'] ?? '';

    return [
        'submission_id' => normalize_submission_id($params['submission_id'] ?? null),
        'ip' => normalize_lead_text($ip, 45),
        'user_agent' => normalize_lead_text($user_agent, 65535, 'bytes'),
        'name' => normalize_lead_text($params['name'] ?? '', 191),
        'phone' => normalize_lead_text($params['phone'] ?? '', 64),
        'email' => normalize_lead_text($params['email'] ?? '', 191, 'characters', true),
        'message' => normalize_lead_text($params['message'] ?? '', 65535, 'bytes'),
        'source_block' => normalize_lead_text($params['source_block'] ?? '', 65535, 'bytes'),
        'utm_source' => normalize_lead_text($params['utm_source'] ?? '', 191),
        'utm_medium' => normalize_lead_text($params['utm_medium'] ?? '', 191),
        'utm_campaign' => normalize_lead_text($params['utm_campaign'] ?? '', 191),
        'utm_term' => normalize_lead_text($params['utm_term'] ?? '', 191),
        'utm_content' => normalize_lead_text($params['utm_content'] ?? '', 191),
        'roistat_visit' => normalize_lead_text($params['roistat_visit'] ?? '', 64),
        'pd_consent' => normalize_lead_text($params['pd_consent'] ?? '', 8),
        'recaptcha_token_present' => is_scalar($recaptcha_token) && (string) $recaptcha_token !== '' ? 1 : 0,
    ];
}

/**
 * Keep the recoverable contact and consent, but remove data that is optional
 * for contacting the person when the first database INSERT fails.
 */
function without_optional_lead_metadata(array $data): array {
    foreach (optional_lead_metadata_fields() as $field) {
        $data[$field] = '';
    }
    return $data;
}

function optional_lead_metadata_fields(): array {
    return [
        'source_block',
        'utm_source',
        'utm_medium',
        'utm_campaign',
        'utm_term',
        'utm_content',
        'roistat_visit',
        'ip',
        'user_agent',
    ];
}

/**
 * Retry only a pre-SQL WordPress validation failure that names an optional
 * metadata column. The surrounding query counter check proves that MySQL was
 * never called, so the retry cannot duplicate a row even when WordPress
 * localizes the human-readable error text.
 */
function is_optional_metadata_storage_error(string $error, bool $query_was_attempted): bool {
    if ($error === '' || $query_was_attempted) {
        return false;
    }
    foreach (optional_lead_metadata_fields() as $field) {
        $quoted_field = preg_quote($field, '/');
        if (preg_match('/(?<![a-z0-9_])' . $quoted_field . '(?![a-z0-9_])/i', $error) === 1) {
            return true;
        }
    }
    return false;
}

/**
 * WPDB may run SHOW FULL COLUMNS before rejecting a value locally. Only an
 * actual INSERT as its final query proves that MySQL could have committed the
 * lead and therefore makes a retry unsafe.
 */
function last_query_is_lead_insert($wpdb, string $table): bool {
    if (!is_object($wpdb) || !property_exists($wpdb, 'last_query')) { return true; }
    $query = ltrim((string)$wpdb->last_query);
    if ($query === '') { return false; }
    $safe_table = preg_quote(str_replace('`', '', $table), '/');
    return preg_match('/^INSERT\s+INTO\s+`?' . $safe_table . '`?(?:\s|\(|$)/i', $query) === 1;
}

/**
 * Insert one row into landing_lead_audit. Called at the very start of handle_lead
 * (before any checks) and updated with lead_id on success.
 * Returns the audit row id so the caller can update it later.
 */
function audit_log_insert(array $normalized): int {
    global $wpdb;
    $table = get_lead_audit_table_name();
    $inserted = $wpdb->insert($table, [
        'submission_id'         => $normalized['submission_id'],
        'ip'                    => $normalized['ip'],
        'user_agent'            => $normalized['user_agent'],
        'name'                  => $normalized['name'],
        'phone'                 => $normalized['phone'],
        'email'                 => $normalized['email'],
        'message'               => $normalized['message'],
        'source_block'          => $normalized['source_block'],
        'utm_source'            => $normalized['utm_source'],
        'utm_medium'            => $normalized['utm_medium'],
        'utm_campaign'          => $normalized['utm_campaign'],
        'utm_term'              => $normalized['utm_term'],
        'utm_content'           => $normalized['utm_content'],
        'roistat_visit'         => $normalized['roistat_visit'],
        'pd_consent'            => $normalized['pd_consent'],
        'recaptcha_token_present' => $normalized['recaptcha_token_present'],
        'blocked_by'            => null,
        'block_detail'          => null,
        'lead_id'               => null,
    ]);
    if ($inserted === false || $inserted === 0 || (int) $wpdb->insert_id <= 0) {
        error_log('[landing-config] audit_insert_failed');
        return 0;
    }
    return (int) $wpdb->insert_id;
}

function audit_log_block(int $audit_id, string $reason, string $detail = ''): void {
    if ($audit_id <= 0) return;
    global $wpdb;
    $safe_reason = normalize_lead_text($reason, 64);
    $safe_detail = normalize_lead_text($detail, 255);
    $wpdb->update(
        get_lead_audit_table_name(),
        ['blocked_by' => $safe_reason, 'block_detail' => $safe_detail !== '' ? $safe_detail : null],
        ['id' => $audit_id],
        ['%s', '%s'],
        ['%d']
    );
}

function audit_log_success(int $audit_id, int $lead_id): void {
    if ($audit_id <= 0) return;
    global $wpdb;
    $wpdb->update(
        get_lead_audit_table_name(),
        ['lead_id' => $lead_id],
        ['id' => $audit_id],
        ['%d'],
        ['%d']
    );
}

/**
 * Reduce an integration result to non-sensitive evidence. Provider response
 * bodies frequently echo the submitted contact, so only a hash and byte count
 * are allowed into WordPress delivery history.
 */
function safe_delivery_summary(array $result): array {
    $ok = ($result['ok'] ?? false) === true;
    $code = isset($result['response_code']) && is_numeric($result['response_code'])
        ? (int) $result['response_code']
        : null;
    $raw_body = is_string($result['response_body'] ?? null)
        ? (string) $result['response_body']
        : '';

    $requested_status = is_string($result['status'] ?? null) ? $result['status'] : '';
    $allowed_statuses = ['success', 'accepted', 'retry_wait', 'failed_permanent', 'unknown'];
    if (in_array($requested_status, $allowed_statuses, true)) {
        $status = $requested_status;
    } elseif ($ok) {
        $status = 'success';
    } elseif ($code === null || $code >= 500 || $code === 408 || $code === 409) {
        $status = 'unknown';
    } elseif ($code === 429) {
        $status = 'retry_wait';
    } else {
        $status = 'failed_permanent';
    }

    $outcome = $ok ? 'accepted' : 'not_confirmed';
    $body_evidence = 'provider_result; outcome=' . $outcome
        . '; body_sha256=' . hash('sha256', $raw_body)
        . '; bytes=' . strlen($raw_body);

    return [
        'status'        => $status,
        'response_code' => $code,
        'response_body' => $body_evidence,
        'error_text'    => $ok ? null : 'provider_error',
    ];
}

function log_delivery_attempt(int $lead_id, int $integration_id, string $adapter, array $result): void {
    if ($lead_id <= 0 || $integration_id <= 0 || $adapter === '') return;

    global $wpdb;
    $safe = safe_delivery_summary($result);
    $wpdb->insert(\LandingConfig\DB\get_lead_log_table_name(), [
        'lead_id'       => $lead_id,
        'integration_id' => $integration_id,
        'adapter'       => sanitize_key($adapter),
        'attempt'       => 1,
        'status'        => $safe['status'],
        'response_code' => $safe['response_code'],
        'response_body' => $safe['response_body'],
        'error_text'    => $safe['error_text'],
        'created_at'    => current_time('mysql'),
    ]);

    // Only internal identifiers are written to debug.log; never contacts,
    // provider bodies, webhook URLs or credentials.
    error_log(sprintf(
        '[landing-config] delivery lead_id=%d integration_id=%d adapter=%s status=%s',
        $lead_id,
        $integration_id,
        sanitize_key($adapter),
        $safe['status']
    ));
}

function submission_lock_name(string $submission_id): string {
    return 'lpl_' . get_current_blog_id() . '_' . substr(hash('sha256', $submission_id), 0, 32);
}

function acquire_submission_lock(string $submission_id): bool {
    global $wpdb;
    return (int)$wpdb->get_var($wpdb->prepare(
        'SELECT GET_LOCK(%s, %d)', submission_lock_name($submission_id), SUBMISSION_LOCK_WAIT_SECONDS
    )) === 1;
}

function release_submission_lock(string $submission_id): void {
    global $wpdb;
    $wpdb->get_var($wpdb->prepare('SELECT RELEASE_LOCK(%s)', submission_lock_name($submission_id)));
}

/** @return array{ok:bool,lead:?array} */
function find_lead_by_submission(string $submission_id): array {
    global $wpdb;
    if (isset($wpdb->last_error)) { $wpdb->last_error = ''; }
    $row = $wpdb->get_row($wpdb->prepare(
        'SELECT id,name,phone,email,message,source_block,utm_source,utm_medium,utm_campaign,utm_term,utm_content,roistat_visit FROM `' . get_leads_table_name()
        . '` WHERE submission_id=%s ORDER BY id ASC LIMIT 1',
        $submission_id
    ), ARRAY_A);
    if ((string)($wpdb->last_error ?? '') !== '') {
        return ['ok' => false, 'lead' => null];
    }
    $lead = is_array($row) && (int)($row['id'] ?? 0) > 0 ? $row : null;
    return ['ok' => true, 'lead' => $lead];
}

function existing_submission_response(array $existing, array $normalized): \WP_REST_Response {
    foreach ([
        'name', 'phone', 'email', 'message', 'source_block',
        'utm_source', 'utm_medium', 'utm_campaign', 'utm_term', 'utm_content',
        'roistat_visit',
    ] as $field) {
        if ((string)($existing[$field] ?? '') !== (string)($normalized[$field] ?? '')) {
            return new \WP_REST_Response(['ok' => false, 'error' => 'idempotency_conflict'], 409);
        }
    }
    return new \WP_REST_Response([
        'ok' => true,
        'lead_id' => (int)$existing['id'],
        'replayed' => true,
    ], 200);
}

function handle_lead($request) {
    $params = $request->get_params();
    $ip = $_SERVER['REMOTE_ADDR'] ?? 'unknown';

    if (lead_request_size($request, (array)$params) > MAX_BODY_BYTES) {
        return new \WP_REST_Response(['ok' => false, 'error' => 'payload_too_large'], 413);
    }

    // A concurrent request may reach REST while another PHP process owns the
    // one-time schema migration. Do not write PII into a partial table: the
    // browser/fallback may retry this explicit temporary response after the
    // short migration completes.
    if (!\LandingConfig\DB\schema_runtime_is_verified()) {
        $response = new \WP_REST_Response(
            ['ok' => false, 'error' => 'temporarily_unavailable'],
            503
        );
        $response->header('Retry-After', '3');
        $response->header('Cache-Control', 'no-store');
        return $response;
    }

    $normalized = normalize_lead_payload(
        $params,
        (string) $ip,
        (string) ($_SERVER['HTTP_USER_AGENT'] ?? '')
    );

    $submission_id = $normalized['submission_id'];
    // A read-only fast path lets a confirmed browser retry receive the same
    // success even after this IP has exhausted its hourly budget. The named
    // lock and a second lookup below still own the concurrent-first-write path.
    if ($submission_id !== null && empty($params['website'])) {
        $lookup = find_lead_by_submission($submission_id);
        // A transient read error is retried once under the submission lock
        // after the recoverable audit is written. It must never be confused
        // with a proven "not found" result and followed by a duplicate INSERT.
        if (($lookup['ok'] ?? false) && is_array($lookup['lead'] ?? null)) {
            return existing_submission_response($lookup['lead'], $normalized);
        }
    }

    // A password manager can accidentally fill the hidden field. Preserve a
    // strictly bounded recovery sample, but keep bot traffic outside the real
    // lead budget so it cannot block campaign contacts for the rest of hour.
    if (!empty($params['website'])) {
        if (claim_honeypot_audit_slot((string)$ip)) {
            $audit_id = audit_log_insert($normalized);
            audit_log_block($audit_id, 'honeypot');
        }
        return new \WP_REST_Response(['ok' => false, 'error' => 'invalid'], 400);
    }

    // Every potentially real attempt consumes an atomic per-IP and site-wide
    // durable budget before any new PII row is written.
    $rate_status = consume_lead_rate_limit((string)$ip);
    if ($rate_status === 'busy') {
        return new \WP_REST_Response(['ok' => false, 'error' => 'temporarily_unavailable'], 503);
    }
    if ($rate_status === 'global_limited') {
        // Fail closed without copying more PII once the site-wide abuse budget
        // is exhausted. The high default is configurable for real campaigns.
        return new \WP_REST_Response(['ok' => false, 'error' => 'rate_limit'], 429);
    }
    if ($rate_status === 'limited') {
        if (claim_blocked_audit_slot('rate_limit', (string)$ip)) {
            $audit_id = audit_log_insert($normalized);
            audit_log_block($audit_id, 'rate_limit', 'limit=' . get_rate_limit());
        }
        return new \WP_REST_Response(['ok' => false, 'error' => 'rate_limit'], 429);
    }

    // Audit legitimate browser attempts before consent/validation checks so a
    // real contact remains recoverable when the request cannot become a lead.
    $audit_id = audit_log_insert($normalized);

    // Consent must be an explicit affirmative value from a real checkbox.
    // The early audit above preserves the attempted contact for diagnosis.
    $raw_consent = $params['pd_consent'] ?? null;
    if (!is_scalar($raw_consent) || (string) $raw_consent !== '1') {
        audit_log_block($audit_id, 'pd_consent', 'explicit consent missing');
        return new \WP_REST_Response(['ok' => false, 'error' => 'pd_consent'], 400);
    }

    if ($submission_id !== null) {
        if (!acquire_submission_lock($submission_id)) {
            audit_log_block($audit_id, 'idempotency_busy', 'submission lock busy');
            return new \WP_REST_Response(['ok' => false, 'error' => 'temporarily_unavailable'], 503);
        }
        try {
            $lookup = find_lead_by_submission($submission_id);
            if (!($lookup['ok'] ?? false)) {
                audit_log_block($audit_id, 'db_error', 'idempotency_lookup_failed');
                error_log('[landing-config] idempotency_lookup_failed');
                return new \WP_REST_Response(['ok' => false, 'error' => 'temporarily_unavailable'], 503);
            }
            if (is_array($lookup['lead'] ?? null)) {
                $response = existing_submission_response($lookup['lead'], $normalized);
                if ($response->get_status() === 200) {
                    audit_log_success($audit_id, (int)$lookup['lead']['id']);
                } else {
                    audit_log_block($audit_id, 'idempotency_conflict', 'contact mismatch');
                }
                return $response;
            }
            return store_new_lead($params, $normalized, $audit_id, (string)$ip);
        } finally {
            release_submission_lock($submission_id);
        }
    }
    return store_new_lead($params, $normalized, $audit_id, (string)$ip);
}

function store_new_lead(array $params, array $normalized, int $audit_id, string $ip) {
    // Required: at least one of phone or email
    $name = $normalized['name'];
    $phone = $normalized['phone'];
    $email = $normalized['email'];
    if ($phone === '' && $email === '') {
        audit_log_block($audit_id, 'validation', 'phone and email both empty');
        return new \WP_REST_Response(
            ['ok' => false, 'error' => 'phone or email required'],
            400
        );
    }

    try {
        if (!function_exists('LandingConfig\\LeadDelivery\\snapshot_enabled_integrations')
            || !function_exists('LandingConfig\\LeadDelivery\\encode_delivery_targets')) {
            throw new \RuntimeException('delivery snapshot service missing');
        }
        $delivery_targets = \LandingConfig\LeadDelivery\snapshot_enabled_integrations();
        $encoded_delivery_targets = \LandingConfig\LeadDelivery\encode_delivery_targets($delivery_targets);
        if ($encoded_delivery_targets === '') { throw new \RuntimeException('delivery snapshot encoding failed'); }
    } catch (\Throwable $ignored) {
        audit_log_block($audit_id, 'db_error', 'delivery_snapshot_failed');
        error_log('[landing-config] delivery_snapshot_failed');
        return new \WP_REST_Response(['ok' => false, 'error' => 'temporarily_unavailable'], 503);
    }

    $data = [
        'submission_id'    => $normalized['submission_id'],
        'name'             => $name,
        'phone'            => $phone,
        'email'            => $email,
        'message'          => $normalized['message'],
        'source_block'     => $normalized['source_block'],
        'utm_source'       => $normalized['utm_source'],
        'utm_medium'       => $normalized['utm_medium'],
        'utm_campaign'     => $normalized['utm_campaign'],
        'utm_term'         => $normalized['utm_term'],
        'utm_content'      => $normalized['utm_content'],
        'roistat_visit'    => $normalized['roistat_visit'],
        'ip'               => $normalized['ip'],
        'user_agent'       => $normalized['user_agent'],
        'delivery_targets' => $encoded_delivery_targets,
        'delivery_reservations_ready' => $delivery_targets === [] ? 1 : 0,
        'audit_origin_id'  => $audit_id > 0 ? $audit_id : null,
        'created_at'       => current_time('mysql'),
        'processed_status'      => 'pending',
        'pd_consent_granted_at' => current_time('mysql'),
        'recaptcha_score'       => null,
    ];

    global $wpdb;
    $leads_table = get_leads_table_name();
    if (property_exists($wpdb, 'last_query')) { $wpdb->last_query = ''; }
    $inserted = $wpdb->insert($leads_table, $data);
    if ($inserted === false || $inserted === 0) {
        $first_error = (string) ($wpdb->last_error ?? '');
        $query_was_attempted = last_query_is_lead_insert($wpdb, $leads_table);
        if (!is_optional_metadata_storage_error($first_error, $query_was_attempted)) {
            audit_log_block($audit_id, 'db_error', 'storage_write_failed');
            return new \WP_REST_Response(['ok' => false, 'error' => 'db_error'], 500);
        }
        $data = without_optional_lead_metadata($data);
        $inserted = $wpdb->insert($leads_table, $data);
        if ($inserted === false || $inserted === 0) {
            audit_log_block($audit_id, 'db_error', 'metadata_fallback_failed');
            return new \WP_REST_Response(['ok' => false, 'error' => 'db_error'], 500);
        }
    }
    $lead_id = (int) $wpdb->insert_id;
    if ($lead_id <= 0) {
        audit_log_block($audit_id, 'db_error', 'lead insert did not return a positive id');
        return new \WP_REST_Response(['ok' => false, 'error' => 'db_error'], 500);
    }

    // Audit: пометить как успешно сохранённую заявку
    audit_log_success($audit_id, $lead_id);

    // The durable lead is the success barrier. Delivery reservations and cron
    // are best-effort and are reconciled by monitoring if scheduling fails.
    try {
        if ($delivery_targets !== [] && function_exists('LandingConfig\\LeadDelivery\\ensure_delivery_reservations')) {
            \LandingConfig\LeadDelivery\ensure_delivery_reservations($lead_id, $delivery_targets);
            if (function_exists('wp_schedule_single_event')) {
                wp_schedule_single_event(time(), 'landing_config_deliver_lead', [$lead_id]);
            }
            if (function_exists('spawn_cron')) { spawn_cron(); }
        }
    } catch (\Throwable $ignored) {
        error_log('[landing-config] delivery_schedule_failed');
    }

    do_action('landing_config_lead_received', $lead_id, $data);

    return new \WP_REST_Response([
        'ok'      => true,
        'lead_id' => $lead_id,
    ], 200);
}

function dispatch_all_integrations(array $lead): void {
    $blog_id      = \get_current_blog_id();
    $integrations = \LandingConfig\Integrations\list_integrations($blog_id);

    foreach ($integrations as $integration) {
        if (!$integration['enabled']) continue;

        $type = $integration['adapter_type'];

        try {
            if ($type === 'telegram') {
                $result = _send_telegram($integration['settings'], $lead);
            } else {
                $map = [
                    'email'    => '\\LandingConfig\\Adapters\\EmailAdapter',
                    'whatsapp' => '\\LandingConfig\\Adapters\\WhatsAppAdapter',
                    'amocrm'   => '\\LandingConfig\\Adapters\\AmoCRMAdapter',
                    'bitrix24' => '\\LandingConfig\\Adapters\\Bitrix24Adapter',
                    'hubspot'  => '\\LandingConfig\\Adapters\\HubSpotAdapter',
                    'roistat'  => '\\LandingConfig\\Adapters\\RoistatAdapter',
                ];
                if (empty($map[$type]) || !class_exists($map[$type])) {
                    $result = [
                        'ok' => false,
                        'status' => 'failed_permanent',
                        'response_code' => null,
                        'response_body' => '',
                        'error' => 'unsupported_adapter',
                    ];
                } else {
                    $adapter = new $map[$type]();
                    $result = $adapter->send($lead, (array) ($integration['settings'] ?? []));
                }
            }
        } catch (\Throwable $e) {
            $result = [
                'ok' => false,
                'status' => 'unknown',
                'response_code' => null,
                'response_body' => '',
                'error' => 'adapter_exception',
            ];
        }

        if (!is_array($result)) {
            $result = [
                'ok' => false,
                'status' => 'unknown',
                'response_code' => null,
                'response_body' => '',
                'error' => 'invalid_adapter_result',
            ];
        }
        if ($type === 'email' && ($result['ok'] ?? false) === true) {
            $result['status'] = 'accepted';
        }
        log_delivery_attempt(
            (int) ($lead['id'] ?? 0),
            (int) ($integration['id'] ?? 0),
            (string) $type,
            $result
        );
    }
}

/**
 * Escape characters that have special meaning in Telegram's legacy Markdown
 * parse_mode, so that user-supplied or URL data (e.g. UTM query strings with
 * multiple underscores) can never break message formatting or cause the
 * Telegram API to silently reject the request.
 */
function _tg_escape_markdown(string $text): string {
    return str_replace(
        ['\\', '_', '*', '`', '['],
        ['\\\\', '\\_', '\\*', '\\`', '\\['],
        $text
    );
}

function _send_telegram(array $settings, array $lead): array {
    $token_raw = $settings['bot_token'] ?? '';
    $token     = $token_raw ? (str_starts_with($token_raw, 'v1:') ? \LandingConfig\Encryption\decrypt($token_raw) : $token_raw) : '';
    $chat_id   = $settings['chat_id'] ?? '';
    if ($token === '' || $chat_id === '') {
        return [
            'ok' => false,
            'status' => 'failed_permanent',
            'response_code' => null,
            'response_body' => '',
            'error' => 'configuration_missing',
        ];
    }

    $id      = $lead['id'] ?? '?';
    $name    = _tg_escape_markdown($lead['name'] ?? '');
    $phone   = _tg_escape_markdown($lead['phone'] ?? '');
    $email   = _tg_escape_markdown($lead['email'] ?? '');
    $message = _tg_escape_markdown($lead['message'] ?? '');
    $source  = _tg_escape_markdown($lead['source_block'] ?? '');

    // Show all captured UTM params, not just utm_source, and escape them too
    $utmParts = [];
    foreach (['utm_source', 'utm_medium', 'utm_campaign', 'utm_term', 'utm_content'] as $k) {
        if (!empty($lead[$k])) {
            $utmParts[] = $k . '=' . $lead[$k];
        }
    }
    $utm = _tg_escape_markdown(implode(', ', $utmParts));

    $text = "\xF0\x9F\x94\x94 *Новая заявка #$id*\n\n"
          . "\xF0\x9F\x91\xA4 Имя: " . ($name    ?: '—') . "\n"
          . "\xF0\x9F\x93\xB1 Телефон: " . ($phone   ? "`$phone`" : '—') . "\n"
          . "\xF0\x9F\x93\xA7 Email: " . ($email   ?: '—') . "\n"
          . "\xF0\x9F\x92\xAC Сообщение: " . ($message ?: '—') . "\n"
          . "\xF0\x9F\x93\xA6 Источник: " . ($source  ?: '—') . "\n"
          . "\xF0\x9F\x94\x97 UTM: " . ($utm     ?: '—') . "\n";

    $resp = \wp_remote_post("https://api.telegram.org/bot{$token}/sendMessage", [
        'timeout' => 8,
        'redirection' => 0,
        'body'    => ['chat_id' => $chat_id, 'text' => $text, 'parse_mode' => 'Markdown'],
    ]);

    if (\is_wp_error($resp)) {
        return [
            'ok' => false,
            'status' => 'unknown',
            'response_code' => null,
            'response_body' => '',
            'error' => 'transport_error',
        ];
    }

    $code = \wp_remote_retrieve_response_code($resp);
    $body = (string) \wp_remote_retrieve_body($resp);
    $json = json_decode($body, true);
    $message_id = is_array($json) ? ($json['result']['message_id'] ?? null) : null;
    $confirmed = $code === 200
        && is_array($json)
        && ($json['ok'] ?? null) === true
        && (is_int($message_id) || (is_string($message_id) && ctype_digit($message_id)))
        && (int) $message_id > 0;

    return [
        'ok' => $confirmed,
        'status' => $confirmed ? 'success' : (($code >= 500 || $code === 0) ? 'unknown' : 'failed_permanent'),
        'response_code' => $code ?: null,
        'response_body' => $body,
        'error' => $confirmed ? null : 'telegram_not_confirmed',
    ];
}
