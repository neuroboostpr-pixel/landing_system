<?php
namespace LandingConfig\Health;

if (!defined('ABSPATH')) { exit; }

const SITE_ID = 'hybridautos-ae';
const OBSERVATION_PATH = '/wp-json/landing/v1/external-health-observation';

add_action('rest_api_init', static function (): void {
    register_rest_route('landing/v1', '/health', [
        'methods' => 'GET', 'callback' => __NAMESPACE__ . '\\handle_health',
        'permission_callback' => '__return_true',
    ]);
    register_rest_route('landing/v1', '/submission-status/(?P<submission_id>[0-9a-f-]+)', [
        'methods' => 'GET', 'callback' => __NAMESPACE__ . '\\handle_submission_status',
        'permission_callback' => '__return_true',
    ]);
    register_rest_route('landing/v1', '/external-health-observation', [
        'methods' => 'POST', 'callback' => __NAMESPACE__ . '\\handle_external_health_observation',
        'permission_callback' => '__return_true',
    ]);
});

function no_store(array $data, int $status): \WP_REST_Response {
    $response = new \WP_REST_Response($data, $status);
    $response->header('Cache-Control', 'no-store, private, max-age=0');
    $response->header('Pragma', 'no-cache');
    $response->header('Expires', '0');
    return $response;
}

function build_health_payload(?int $now = null): array {
    global $wpdb;
    $now = $now ?? time();
    try { $database_ok = (int)$wpdb->get_var('SELECT 1') === 1; }
    catch (\Throwable $ignored) { $database_ok = false; }
    $lead_endpoint_ok = function_exists('LandingConfig\\REST\\handle_lead');
    $heartbeat = (int)get_option(\LandingConfig\Monitoring\HEARTBEAT_OPTION, 0);
    $age = $heartbeat > 0 ? max(0, $now - $heartbeat) : -1;
    $heartbeat_ok = \LandingConfig\Monitoring\is_enabled()
        && $heartbeat > 0 && $age <= \LandingConfig\Monitoring\HEARTBEAT_STALE_SECONDS
        && get_option(\LandingConfig\Monitoring\RUN_STATUS_OPTION, '') === 'ok';
    $ok = $database_ok && $lead_endpoint_ok && $heartbeat_ok;
    return [
        'ok' => $ok,
        'site_id' => SITE_ID,
        'site' => $ok ? 'ok' : 'degraded',
        'lead_endpoint' => $lead_endpoint_ok ? 'ok' : 'failed',
        'database' => $database_ok ? 'ok' : 'failed',
        'monitor_heartbeat' => $heartbeat_ok ? 'ok' : 'degraded',
        'heartbeat_age_seconds' => $age,
        'checked_at' => $now,
    ];
}

function handle_health($request) {
    $payload = build_health_payload();
    return no_store($payload, $payload['ok'] ? 200 : 503);
}

function status_key(): ?string {
    if (!defined('LP_FALLBACK_STATUS_SECRET') || !defined('LP_FALLBACK_SITE_ID') || LP_FALLBACK_SITE_ID !== SITE_ID) {
        return null;
    }
    return \LandingConfig\FallbackSecurity\decode_hmac_hex_secret((string)LP_FALLBACK_STATUS_SECRET);
}

function signed_request_signature(string $method, string $path, int $timestamp, string $body_digest): ?string {
    $key = status_key();
    if ($key === null || !in_array($method, ['GET','POST'], true)) { return null; }
    $canonical = $method . "\n" . $path . "\n" . $timestamp . "\n" . SITE_ID;
    if ($method === 'POST') {
        if (preg_match('/^[a-f0-9]{64}$/', $body_digest) !== 1) { return null; }
        $canonical .= "\n" . $body_digest;
    }
    return hash_hmac('sha256', $canonical, $key);
}

function signed_headers_are_valid($request, string $method, string $path, int $now, string $body_digest = ''): bool {
    $site = trim((string)$request->get_header('x-lp-site-id'));
    $timestamp_raw = trim((string)$request->get_header('x-lp-timestamp'));
    $signature = trim((string)$request->get_header('x-lp-signature'));
    if ($site !== SITE_ID || str_contains($site, ',')
        || preg_match('/^(0|[1-9][0-9]*)$/', $timestamp_raw) !== 1
        || preg_match('/^[a-f0-9]{64}$/', $signature) !== 1) {
        return false;
    }
    $timestamp = (int)$timestamp_raw;
    if (abs($now - $timestamp) > 300) { return false; }
    $expected = signed_request_signature($method, $path, $timestamp, $body_digest);
    return is_string($expected) && hash_equals($expected, $signature);
}

function handle_submission_status_at($request, int $now) {
    $submission_id = strtolower(trim((string)$request->get_param('submission_id')));
    if (!\LandingConfig\Monitoring\is_valid_submission_id($submission_id)) {
        return no_store(['ok' => false, 'error' => 'invalid_submission_id'], 400);
    }
    $path = '/wp-json/landing/v1/submission-status/' . $submission_id;
    if (!signed_headers_are_valid($request, 'GET', $path, $now)) {
        return no_store(['ok' => false, 'error' => 'unauthorized'], 401);
    }
    if (function_exists('LandingConfig\\MonitoringAdmin\\consume_status_smoke_failure_at')
        && \LandingConfig\MonitoringAdmin\consume_status_smoke_failure_at($submission_id, $now)) {
        return no_store(['ok' => false, 'error' => 'temporarily_unavailable'], 503);
    }
    global $wpdb;
    try {
        $exists = (int)$wpdb->get_var($wpdb->prepare(
            'SELECT 1 FROM `' . \LandingConfig\DB\get_leads_table_name() . '` WHERE submission_id=%s LIMIT 1',
            $submission_id
        )) === 1;
    } catch (\Throwable $ignored) {
        return no_store(['ok' => false, 'error' => 'temporarily_unavailable'], 503);
    }
    return no_store(['ok' => true, 'site_id' => SITE_ID, 'submission_id' => $submission_id, 'exists' => $exists], 200);
}

function handle_submission_status($request) { return handle_submission_status_at($request, time()); }

function handle_external_health_observation_at($request, int $now) {
    $raw = (string)$request->get_body();
    $digest = hash('sha256', $raw);
    if (!signed_headers_are_valid($request, 'POST', OBSERVATION_PATH, $now, $digest)) {
        return no_store(['ok' => false, 'error' => 'unauthorized'], 401);
    }
    $payload = json_decode($raw, true);
    if (!is_array($payload) || array_keys($payload) !== ['v','site_id','target','status','checked_at_slot']
        || ($payload['v'] ?? null) !== 1 || ($payload['site_id'] ?? '') !== SITE_ID
        || ($payload['target'] ?? '') !== 'redis' || !in_array($payload['status'] ?? '', ['ok','failed'], true)
        || !is_int($payload['checked_at_slot'] ?? null)) {
        return no_store(['ok' => false, 'error' => 'invalid_payload'], 400);
    }
    $timestamp = (int)$request->get_header('x-lp-timestamp');
    if ($payload['checked_at_slot'] !== intdiv($timestamp, 300)) {
        return no_store(['ok' => false, 'error' => 'invalid_payload'], 400);
    }
    $result = \LandingConfig\Monitoring\apply_external_health_observation(
        $payload['status'], $payload['checked_at_slot'], $now
    );
    if (($result['accepted'] ?? false) !== true) {
        return no_store(['ok' => false, 'error' => 'temporarily_unavailable'], 503);
    }
    return no_store(['ok' => true, 'site_id' => SITE_ID, 'accepted' => true,
        'duplicate' => ($result['duplicate'] ?? false) === true], 200);
}

function handle_external_health_observation($request) {
    return handle_external_health_observation_at($request, time());
}
