<?php
namespace LandingConfig\FormEvents;

if (!defined('ABSPATH')) { exit; }

use function LandingConfig\DB\get_form_events_table_name;

const MAX_BODY_BYTES = 4096;
const MAX_EVENTS_PER_SUBMISSION = 10;
const RETENTION_DAYS = 30;
const CLEANUP_HOOK = 'landing_config_cleanup_form_events';
const RATE_BUCKET_SECONDS = 3600;

function allowed_event_details(): array {
    return [
        'form_started'      => [''],
        'submit_attempt'    => [''],
        'validation_failed' => ['name', 'phone', 'consent'],
        'request_started'   => [''],
        'request_failed'    => ['network', 'http_4xx', 'http_5xx', 'invalid_response', 'unconfirmed'],
    ];
}

function allowed_payload_fields(): array {
    return [
        'submission_id',
        'event_sequence',
        'event_name',
        'event_detail',
        'form_id',
        'brand',
        'cta_key',
        'page_path',
        'utm_source',
        'utm_medium',
        'utm_campaign',
    ];
}

function get_rate_limit(): int {
    $configured = (int) get_option('lp_form_event_rate_limit_per_hour', 120);
    return $configured > 0 ? min($configured, 1000) : 120;
}

function get_global_rate_limit(): int {
    $configured = (int)get_option('lp_form_event_global_rate_limit_per_hour', 2000);
    return $configured > 0 ? min($configured, 10000) : 2000;
}

function rate_bucket_start(?int $now = null): int {
    return intdiv($now ?? time(), RATE_BUCKET_SECONDS) * RATE_BUCKET_SECONDS;
}

function global_rate_option_name(int $bucket): string {
    return 'landing_form_event_global_' . $bucket;
}

function durable_counter_value($stored): ?int {
    if ($stored === false) { return 0; }
    if (is_int($stored) && $stored >= 0) { return $stored; }
    if (is_string($stored) && preg_match('/^(?:0|[1-9][0-9]*)$/D', $stored) === 1) {
        return (int)$stored;
    }
    return null;
}

function is_uuid_v4(string $value): bool {
    if (function_exists('wp_is_uuid')) {
        return wp_is_uuid($value, 4);
    }

    return preg_match(
        '/^[0-9a-f]{8}-[0-9a-f]{4}-4[0-9a-f]{3}-[89ab][0-9a-f]{3}-[0-9a-f]{12}$/i',
        $value
    ) === 1;
}

function request_size($request, array $params): int {
    $content_length = isset($_SERVER['CONTENT_LENGTH']) ? (int) $_SERVER['CONTENT_LENGTH'] : 0;
    $raw_length = 0;
    if (is_object($request) && method_exists($request, 'get_body')) {
        $raw_body = $request->get_body();
        $raw_length = is_string($raw_body) ? strlen($raw_body) : 0;
    }

    $encoded = json_encode($params);
    $parsed_length = is_string($encoded) ? strlen($encoded) : MAX_BODY_BYTES + 1;
    return max($content_length, $raw_length, $parsed_length);
}

/**
 * Count UTF-8 characters for MySQL VARCHAR limits. The byte-count fallback is
 * deliberately conservative if an invalid UTF-8 value reaches this helper.
 */
function utf8_character_length(string $value): int {
    if ($value === '') {
        return 0;
    }
    if (function_exists('mb_strlen')) {
        return (int) mb_strlen($value, 'UTF-8');
    }
    if (function_exists('iconv_strlen')) {
        $length = iconv_strlen($value, 'UTF-8');
        if ($length !== false) {
            return (int) $length;
        }
    }

    $length = preg_match_all('/./us', $value, $characters);
    return is_int($length) ? $length : strlen($value);
}

function contains_sensitive_value(string $value): bool {
    if (preg_match('~(?:https?://|mailto:|tel:)~i', $value) === 1) {
        return true;
    }
    if (preg_match('/[a-z0-9._%+\-]+@[a-z0-9.\-]+\.[a-z]{2,}/i', $value) === 1) {
        return true;
    }

    // A leading plus and at least eight digits is a contact number. Bare
    // numeric UTM campaign IDs remain valid attribution metadata.
    return preg_match('/\+\s*\d(?:[\s().\-]*\d){7,}/', $value) === 1;
}

function normalize_event_sequence(array $params, bool &$valid): ?int {
    if (!array_key_exists('event_sequence', $params)) {
        $valid = true;
        return null;
    }

    $value = $params['event_sequence'];
    if (is_int($value)) {
        $sequence = $value;
    } elseif (is_string($value) && preg_match('/^[1-9][0-9]*$/D', $value) === 1) {
        $sequence = (int) $value;
    } else {
        $valid = false;
        return null;
    }

    if ($sequence < 1 || $sequence > 65535) {
        $valid = false;
        return null;
    }

    $valid = true;
    return $sequence;
}

/**
 * Validate and reduce a browser event to the exact anonymous DB shape.
 * Returning null means the request is unsafe or outside the small contract.
 */
function normalize_payload(array $params): ?array {
    $unknown_fields = array_diff(array_keys($params), allowed_payload_fields());
    if ($unknown_fields !== []) {
        return null;
    }

    foreach (allowed_payload_fields() as $field) {
        if (isset($params[$field]) && !is_scalar($params[$field])) {
            return null;
        }
    }

    $submission_id = strtolower(trim((string) ($params['submission_id'] ?? '')));
    if (!is_uuid_v4($submission_id)) {
        return null;
    }

    $sequence_valid = false;
    $event_sequence = normalize_event_sequence($params, $sequence_valid);
    if (!$sequence_valid) {
        return null;
    }

    $event_name = sanitize_key((string) ($params['event_name'] ?? ''));
    $event_detail = sanitize_key((string) ($params['event_detail'] ?? ''));
    $details = allowed_event_details();
    if (!isset($details[$event_name]) || !in_array($event_detail, $details[$event_name], true)) {
        return null;
    }

    $field_limits = [
        'form_id'      => 100,
        'brand'        => 100,
        'cta_key'      => 100,
        'utm_source'   => 191,
        'utm_medium'   => 191,
        'utm_campaign' => 191,
    ];
    $clean = [];
    foreach ($field_limits as $field => $limit) {
        $value = sanitize_text_field(wp_unslash((string) ($params[$field] ?? '')));
        if (utf8_character_length($value) > $limit) {
            return null;
        }
        if (contains_sensitive_value($value)) {
            return null;
        }
        $clean[$field] = $value;
    }

    $page_path = sanitize_text_field(wp_unslash((string) ($params['page_path'] ?? '')));
    if (
        $page_path === ''
        || utf8_character_length($page_path) > 255
        || !str_starts_with($page_path, '/')
        || str_starts_with($page_path, '//')
        || str_contains($page_path, '?')
        || str_contains($page_path, '#')
        || str_contains($page_path, '://')
        || contains_sensitive_value($page_path)
    ) {
        return null;
    }

    return [
        'submission_id' => $submission_id,
        'event_sequence' => $event_sequence,
        'event_name'     => $event_name,
        'event_detail'   => $event_detail,
        'form_id'        => $clean['form_id'],
        'brand'          => $clean['brand'],
        'cta_key'        => $clean['cta_key'],
        'page_path'      => $page_path,
        'utm_source'     => $clean['utm_source'],
        'utm_medium'     => $clean['utm_medium'],
        'utm_campaign'   => $clean['utm_campaign'],
    ];
}

function acquire_named_lock(string $name): bool {
    global $wpdb;
    return (int) $wpdb->get_var($wpdb->prepare('SELECT GET_LOCK(%s, 0)', $name)) === 1;
}

function release_named_lock(string $name): void {
    global $wpdb;
    $wpdb->get_var($wpdb->prepare('SELECT RELEASE_LOCK(%s)', $name));
}

/**
 * Return allowed, limited, or busy. MySQL named locks serialize the otherwise
 * non-atomic transient read/increment without making a public request wait.
 */
function consume_rate_limit(string $submission_id): string {
    global $wpdb;
    $ip = (string) ($_SERVER['REMOTE_ADDR'] ?? 'unknown');
    $ip_fingerprint = hash_hmac('sha256', $ip, wp_salt('auth'));
    $ip_key = 'landing_form_event_ip_' . substr($ip_fingerprint, 0, 32);
    $submission_key = 'landing_form_event_submission_' . md5($submission_id);
    $blog_id = (int) get_current_blog_id();
    $bucket = rate_bucket_start();
    $site_lock = 'lfe_site_' . $blog_id . '_' . substr(hash('sha256', (string)$bucket), 0, 32);
    $ip_lock = 'lfe_ip_' . $blog_id . '_' . substr(hash('sha256', $ip_fingerprint), 0, 32);
    $submission_lock = 'lfe_sub_' . $blog_id . '_' . substr(hash('sha256', $submission_id), 0, 32);

    // A site-wide lock owns the persistent budget. It is acquired before the
    // narrower locks on every request, so rotating IP/UUID traffic cannot race
    // past the storage ceiling or deadlock counters in a different order.
    if (!acquire_named_lock($site_lock)) {
        return 'busy';
    }

    $ip_lock_acquired = false;
    $submission_lock_acquired = false;
    try {
        if (!acquire_named_lock($ip_lock)) { return 'busy'; }
        $ip_lock_acquired = true;
        if (!acquire_named_lock($submission_lock)) {
            return 'busy';
        }
        $submission_lock_acquired = true;

        $ip_count = (int) get_transient($ip_key);
        if ($ip_count >= get_rate_limit()) {
            return 'limited';
        }

        $submission_count = (int) get_transient($submission_key);
        if ($submission_count >= MAX_EVENTS_PER_SUBMISSION) {
            return 'limited';
        }

        $global_key = global_rate_option_name($bucket);
        $global_stored = get_option($global_key, false);
        $global_count = durable_counter_value($global_stored);
        if ($global_count === null) { return 'busy'; }
        if ($global_count >= get_global_rate_limit()) { return 'limited'; }
        $global_written = $global_stored === false
            ? add_option($global_key, (string)($global_count + 1), '', false)
            : update_option($global_key, (string)($global_count + 1));
        if (!$global_written) { return 'busy'; }

        $ip_written = set_transient($ip_key, $ip_count + 1, HOUR_IN_SECONDS);
        $submission_written = set_transient(
            $submission_key, $submission_count + 1, RETENTION_DAYS * DAY_IN_SECONDS
        );
        if (!$ip_written || !$submission_written) { return 'busy'; }
        return 'allowed';
    } finally {
        if ($submission_lock_acquired) {
            release_named_lock($submission_lock);
        }
        if ($ip_lock_acquired) { release_named_lock($ip_lock); }
        release_named_lock($site_lock);
    }
}

function handle_form_event($request) {
    $params = (array) $request->get_params();
    if (request_size($request, $params) > MAX_BODY_BYTES) {
        return new \WP_REST_Response(['ok' => false, 'error' => 'payload_too_large'], 413);
    }

    $event = normalize_payload($params);
    if ($event === null) {
        return new \WP_REST_Response(['ok' => false, 'error' => 'invalid_payload'], 400);
    }

    $rate_status = consume_rate_limit($event['submission_id']);
    if ($rate_status === 'busy') {
        return new \WP_REST_Response(['ok' => false, 'error' => 'temporarily_unavailable'], 503);
    }
    if ($rate_status !== 'allowed') {
        return new \WP_REST_Response(['ok' => false, 'error' => 'rate_limit'], 429);
    }

    global $wpdb;
    $inserted = $wpdb->insert(get_form_events_table_name(), [
        'created_at' => current_time('mysql'),
    ] + $event);

    if ($inserted === false || $inserted === 0 || (int) $wpdb->insert_id <= 0) {
        return new \WP_REST_Response(['ok' => false, 'error' => 'db_error'], 500);
    }

    return new \WP_REST_Response(['ok' => true], 201);
}

function cleanup_expired_form_events(): int {
    global $wpdb;
    $now = new \DateTimeImmutable((string) current_time('mysql'));
    $cutoff = $now->modify('-' . RETENTION_DAYS . ' days')->format('Y-m-d H:i:s');
    $table = get_form_events_table_name();

    // Small batches avoid one large table lock, while the loop guarantees that
    // a traffic spike cannot leave rows beyond the retention window forever.
    $total_deleted = 0;
    do {
        $deleted = $wpdb->query($wpdb->prepare(
            "DELETE FROM `$table` WHERE created_at < %s LIMIT 5000",
            $cutoff
        ));
        $deleted = is_int($deleted) && $deleted > 0 ? $deleted : 0;
        $total_deleted += $deleted;
    } while ($deleted === 5000);

    // The durable global limiter creates at most one small option per hour.
    // Delete old buckets through the WordPress API so persistent caches are
    // invalidated together with the database row.
    $options_table = str_replace('`', '', (string)($wpdb->options ?? ($wpdb->prefix . 'options')));
    $option_names = $wpdb->get_col(
        "SELECT option_name FROM `{$options_table}` WHERE option_name LIKE 'landing_form_event_global_%' LIMIT 1000"
    );
    $oldest_live_bucket = rate_bucket_start(time() - (2 * RATE_BUCKET_SECONDS));
    foreach (is_array($option_names) ? $option_names : [] as $option_name) {
        if (preg_match('/^landing_form_event_global_(\d{9,12})$/', (string)$option_name, $match) !== 1) { continue; }
        if ((int)$match[1] < $oldest_live_bucket) { delete_option((string)$option_name); }
    }

    return $total_deleted;
}

function ensure_cleanup_scheduled(): void {
    if (!wp_next_scheduled(CLEANUP_HOOK)) {
        wp_schedule_event(time() + HOUR_IN_SECONDS, 'daily', CLEANUP_HOOK);
    }
}

add_action('rest_api_init', function (): void {
    register_rest_route('landing/v1', '/form-event', [
        'methods'             => 'POST',
        'callback'            => __NAMESPACE__ . '\\handle_form_event',
        'permission_callback' => '__return_true',
    ]);
});

add_action('init', __NAMESPACE__ . '\\ensure_cleanup_scheduled', 2);
add_action(CLEANUP_HOOK, __NAMESPACE__ . '\\cleanup_expired_form_events');
