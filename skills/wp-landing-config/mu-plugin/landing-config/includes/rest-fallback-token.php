<?php
namespace LandingConfig\FallbackSecurity;

if (!defined('ABSPATH')) { exit; }

function decode_hmac_hex_secret(string $secret): ?string {
    if (preg_match('/^[a-f0-9]{64}$/', $secret) !== 1) { return null; }
    $decoded = hex2bin($secret);
    return is_string($decoded) && strlen($decoded) === 32 ? $decoded : null;
}

namespace LandingConfig\FallbackToken;

const TOKEN_TTL_SECONDS = 43200;
const RATE_LIMIT_PER_HOUR = 60;
const SITE_ID = 'hybridautos-ae';
const PROTOCOL_VERSION = '1';
const PRIVACY_POLICY_VERSION = '2026-07-16';

add_action('rest_api_init', static function (): void {
    register_rest_route('landing/v1', '/fallback-token', [
        'methods' => 'GET',
        'callback' => __NAMESPACE__ . '\\handle_token',
        'permission_callback' => '__return_true',
    ]);
});

function flag(string $name): bool {
    return defined($name) && constant($name) === true;
}

function resolve_token_mode_for_flags($request, bool $live_enabled, bool $test_enabled): ?string {
    if ($test_enabled && is_user_logged_in() && current_user_can('manage_options')) {
        $nonce = is_object($request) && method_exists($request, 'get_header')
            ? (string)$request->get_header('x-wp-nonce') : '';
        if ($nonce !== '' && in_array(wp_verify_nonce($nonce, 'wp_rest'), [1, 2], true)) {
            return 'test';
        }
    }
    return $live_enabled ? 'live' : null;
}

function resolve_token_mode($request): ?string {
    return resolve_token_mode_for_flags(
        $request, flag('LP_FALLBACK_ENABLED'), flag('LP_FALLBACK_TEST_MODE')
    );
}

function secrets_are_valid(string $signing, string $status): bool {
    return $signing !== $status
        && \LandingConfig\FallbackSecurity\decode_hmac_hex_secret($signing) !== null
        && \LandingConfig\FallbackSecurity\decode_hmac_hex_secret($status) !== null;
}

function sign_token_components(string $secret, int $issued_at, int $expires_at,
    string $nonce, string $mode): ?string {
    $key = \LandingConfig\FallbackSecurity\decode_hmac_hex_secret($secret);
    if ($key === null || !in_array($mode, ['live','test'], true)
        || preg_match('/^[a-f0-9]{32}$/', $nonce) !== 1) {
        return null;
    }
    $canonical = implode("\n", ['v1', SITE_ID, $issued_at, $expires_at, $nonce, $mode]);
    return hash_hmac('sha256', $canonical, $key);
}

function build_token_bundle(string $mode, ?int $now = null): ?array {
    if (!defined('LP_FALLBACK_SIGNING_SECRET') || !defined('LP_FALLBACK_STATUS_SECRET')) { return null; }
    $signing = (string)LP_FALLBACK_SIGNING_SECRET;
    $status = (string)LP_FALLBACK_STATUS_SECRET;
    if (!secrets_are_valid($signing, $status) || !in_array($mode, ['live','test'], true)) { return null; }
    if (defined('LP_FALLBACK_SITE_ID') && LP_FALLBACK_SITE_ID !== SITE_ID) { return null; }
    $issued_at = $now ?? time();
    $expires_at = $issued_at + TOKEN_TTL_SECONDS;
    try { $nonce = bin2hex(random_bytes(16)); }
    catch (\Throwable $ignored) { return null; }
    $signature = sign_token_components($signing, $issued_at, $expires_at, $nonce, $mode);
    if ($signature === null) { return null; }
    return [
        'ok' => true,
        'site_id' => SITE_ID,
        'protocol_version' => PROTOCOL_VERSION,
        'privacy_policy_version' => PRIVACY_POLICY_VERSION,
        'mode' => $mode,
        'issued_at' => $issued_at,
        'expires_at' => $expires_at,
        'nonce' => $nonce,
        'token' => implode('.', ['v1', $issued_at, $expires_at, $nonce, $mode, $signature]),
    ];
}

function request_is_same_origin($request): bool {
    $origin = is_object($request) && method_exists($request, 'get_header')
        ? trim((string)$request->get_header('origin')) : '';
    $fetch_site = is_object($request) && method_exists($request, 'get_header')
        ? strtolower(trim((string)$request->get_header('sec-fetch-site'))) : '';
    if ($fetch_site !== '' && $fetch_site !== 'same-origin') { return false; }
    if ($origin === '') { return true; }
    $parts = parse_url(home_url('/'));
    if (!is_array($parts) || empty($parts['scheme']) || empty($parts['host'])) { return false; }
    $expected = strtolower($parts['scheme'] . '://' . $parts['host'] . (isset($parts['port']) ? ':' . $parts['port'] : ''));
    return strtolower(rtrim($origin, '/')) === $expected;
}

function consume_rate_slot(): bool {
    global $wpdb;
    $raw_ip = (string)($_SERVER['REMOTE_ADDR'] ?? 'unknown');
    $ip_hmac = hash_hmac('sha256', $raw_ip, wp_salt('auth'));
    $key = 'lp_fallback_token_rate_' . substr($ip_hmac, 0, 48);
    $lock = 'lpt_' . get_current_blog_id() . '_' . substr($ip_hmac, 0, 32);
    if ((int)$wpdb->get_var($wpdb->prepare('SELECT GET_LOCK(%s, 0)', $lock)) !== 1) { return false; }
    try {
        $count = (int)get_transient($key);
        if ($count >= RATE_LIMIT_PER_HOUR) { return false; }
        set_transient($key, $count + 1, HOUR_IN_SECONDS);
        return true;
    } finally {
        $wpdb->get_var($wpdb->prepare('SELECT RELEASE_LOCK(%s)', $lock));
    }
}

function no_store_response(array $data, int $status): \WP_REST_Response {
    $response = new \WP_REST_Response($data, $status);
    $response->header('Cache-Control', 'no-store, private, max-age=0');
    $response->header('Pragma', 'no-cache');
    $response->header('Expires', '0');
    return $response;
}

function handle_token($request) {
    $mode = resolve_token_mode($request);
    if ($mode === null) { return no_store_response(['ok' => false, 'error' => 'not_found'], 404); }
    if (!request_is_same_origin($request)) { return no_store_response(['ok' => false, 'error' => 'forbidden'], 403); }
    if (!consume_rate_slot()) { return no_store_response(['ok' => false, 'error' => 'rate_limited'], 429); }
    $bundle = build_token_bundle($mode);
    if ($bundle === null) { return no_store_response(['ok' => false, 'error' => 'not_found'], 404); }
    return no_store_response($bundle, 200);
}
