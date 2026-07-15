<?php
namespace LandingConfig\REST;

if (!defined('ABSPATH')) { exit; }

use function LandingConfig\DB\get_leads_table_name;
use function LandingConfig\DB\get_lead_audit_table_name;

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

add_action('rest_api_init', function () {
    register_rest_route('landing/v1', '/lead', [
        'methods'             => 'POST',
        'callback'            => __NAMESPACE__ . '\\handle_lead',
        'permission_callback' => '__return_true',  // public; protected by honeypot + rate limit
    ]);
});

/**
 * Verify reCAPTCHA v3 token with Google.
 * Returns score (float 0.0-1.0) on success, null on network error or missing token.
 * Returns false if token is invalid (score below threshold or verification failed).
 *
 * Fail-open: returns null (not false) on network errors so forms still work
 * when Google API is unreachable.
 */
function verify_recaptcha(string $token): ?float {
    if (get_option('lp_recaptcha_enabled', '0') !== '1') {
        return null; // disabled — skip
    }

    if ($token === '') {
        return null; // no token — skip (frontend may not have loaded yet)
    }

    $secret_enc = (string) get_option('lp_recaptcha_secret_key_enc', '');
    if ($secret_enc === '') {
        return null; // not configured — skip
    }

    $secret = $secret_enc;
    if (str_starts_with($secret_enc, 'v1:')) {
        $secret = \LandingConfig\Encryption\decrypt($secret_enc);
    }
    if ($secret === '') {
        return null;
    }

    $response = wp_remote_post('https://www.google.com/recaptcha/api/siteverify', [
        'timeout' => 5,
        'body'    => ['secret' => $secret, 'response' => $token],
    ]);

    if (is_wp_error($response)) {
        return null; // network error — fail open
    }

    $body = json_decode(wp_remote_retrieve_body($response), true);
    if (!is_array($body) || empty($body['success'])) {
        return 0.0; // invalid token
    }

    return (float) ($body['score'] ?? 0.0);
}

/**
 * Insert one row into landing_lead_audit. Called at the very start of handle_lead
 * (before any checks) and updated with lead_id on success.
 * Returns the audit row id so the caller can update it later.
 */
function audit_log_insert(array $params, string $ip): int {
    global $wpdb;
    $table = get_lead_audit_table_name();
    $wpdb->insert($table, [
        'ip'                    => sanitize_text_field($ip),
        'user_agent'            => sanitize_text_field($_SERVER['HTTP_USER_AGENT'] ?? ''),
        'name'                  => sanitize_text_field(wp_unslash($params['name'] ?? '')),
        'phone'                 => sanitize_text_field(wp_unslash($params['phone'] ?? '')),
        'email'                 => sanitize_email(wp_unslash($params['email'] ?? '')),
        'message'               => sanitize_text_field(wp_unslash($params['message'] ?? '')),
        'source_block'          => sanitize_text_field(wp_unslash($params['source_block'] ?? '')),
        'utm_source'            => sanitize_text_field(wp_unslash($params['utm_source'] ?? '')),
        'utm_medium'            => sanitize_text_field(wp_unslash($params['utm_medium'] ?? '')),
        'utm_campaign'          => sanitize_text_field(wp_unslash($params['utm_campaign'] ?? '')),
        'roistat_visit'         => sanitize_text_field(wp_unslash($params['roistat_visit'] ?? '')),
        'pd_consent'            => sanitize_text_field(wp_unslash($params['pd_consent'] ?? '')),
        'recaptcha_token_present' => ($params['recaptcha_token'] ?? '') !== '' ? 1 : 0,
        'blocked_by'            => null,
        'block_detail'          => null,
        'lead_id'               => null,
    ]);
    return (int) $wpdb->insert_id;
}

function audit_log_block(int $audit_id, string $reason, string $detail = ''): void {
    if ($audit_id <= 0) return;
    global $wpdb;
    $wpdb->update(
        get_lead_audit_table_name(),
        ['blocked_by' => $reason, 'block_detail' => $detail ?: null],
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

function handle_lead($request) {
    $params = $request->get_params();
    $ip = $_SERVER['REMOTE_ADDR'] ?? 'unknown';

    // Audit: записываем ВСЁ до любых проверок
    $audit_id = audit_log_insert($params, $ip);

    // Honeypot: field 'website' must be empty (real users don't fill it; bots do).
    if (!empty($params['website'])) {
        audit_log_block($audit_id, 'honeypot');
        return new \WP_REST_Response(['ok' => false, 'error' => 'invalid'], 400);
    }

    // Rate limit per IP — transient-based.
    $rl_key = 'landing_lead_rl_' . md5($ip);
    $rl_count = (int) get_transient($rl_key);
    if ($rl_count >= get_rate_limit()) {
        audit_log_block($audit_id, 'rate_limit', 'count=' . $rl_count . ' limit=' . get_rate_limit());
        return new \WP_REST_Response(['ok' => false, 'error' => 'rate_limit'], 429);
    }
    set_transient($rl_key, $rl_count + 1, HOUR_IN_SECONDS);

    // reCAPTCHA v3 verification (fail-open on network errors)
    $recaptcha_token = sanitize_text_field(wp_unslash($params['recaptcha_token'] ?? ''));
    $recaptcha_score = verify_recaptcha($recaptcha_token);
    $threshold = (float) get_option('lp_recaptcha_threshold', '0.5');
    if ($recaptcha_score !== null && $recaptcha_score < $threshold) {
        audit_log_block($audit_id, 'recaptcha_failed', 'score=' . number_format((float)$recaptcha_score, 2));
        return new \WP_REST_Response(['ok' => false, 'error' => 'recaptcha_failed'], 403);
    }

    // Required: at least one of phone or email
    $name = sanitize_text_field(wp_unslash($params['name'] ?? ''));
    $phone = sanitize_text_field(wp_unslash($params['phone'] ?? ''));
    $email = sanitize_email(wp_unslash($params['email'] ?? ''));
    if ($phone === '' && $email === '') {
        audit_log_block($audit_id, 'validation', 'phone and email both empty');
        return new \WP_REST_Response(
            ['ok' => false, 'error' => 'phone or email required'],
            400
        );
    }

    $data = [
        'name'             => $name,
        'phone'            => $phone,
        'email'            => $email,
        'message'          => sanitize_text_field(wp_unslash($params['message'] ?? '')),
        'source_block'     => sanitize_text_field(wp_unslash($params['source_block'] ?? '')),
        'utm_source'       => sanitize_text_field(wp_unslash($params['utm_source'] ?? '')),
        'utm_medium'       => sanitize_text_field(wp_unslash($params['utm_medium'] ?? '')),
        'utm_campaign'     => sanitize_text_field(wp_unslash($params['utm_campaign'] ?? '')),
        'utm_term'         => sanitize_text_field(wp_unslash($params['utm_term'] ?? '')),
        'utm_content'      => sanitize_text_field(wp_unslash($params['utm_content'] ?? '')),
        'roistat_visit'    => sanitize_text_field(wp_unslash($params['roistat_visit'] ?? '')),
        'ip'               => sanitize_text_field($ip),
        'user_agent'       => sanitize_text_field($_SERVER['HTTP_USER_AGENT'] ?? ''),
        'created_at'       => current_time('mysql'),
        'processed_status'      => 'pending',
        'pd_consent_granted_at' => current_time('mysql'),
        'recaptcha_score'       => $recaptcha_score !== null ? number_format((float)$recaptcha_score, 2, '.', '') : null,
    ];

    global $wpdb;
    $inserted = $wpdb->insert(get_leads_table_name(), $data);
    if ($inserted === false || $inserted === 0) {
        audit_log_block($audit_id, 'db_error', $wpdb->last_error);
        return new \WP_REST_Response(['ok' => false, 'error' => 'db_error'], 500);
    }
    $lead_id = $wpdb->insert_id;

    // Audit: пометить как успешно сохранённую заявку
    audit_log_success($audit_id, $lead_id);

    // Email fallback — never block user response on this; wp_mail silently fails if SMTP down
    send_admin_email($data, $lead_id);

    // Dispatch to all active integrations
    dispatch_all_integrations(['id' => $lead_id] + $data);

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

        if ($type === 'telegram') {
            _send_telegram($integration['settings'], $lead);
        } else {
            $map = [
                'email'    => '\\LandingConfig\\Adapters\\EmailAdapter',
                'whatsapp' => '\\LandingConfig\\Adapters\\WhatsAppAdapter',
                'amocrm'   => '\\LandingConfig\\Adapters\\AmoCRMAdapter',
                'bitrix24' => '\\LandingConfig\\Adapters\\Bitrix24Adapter',
                'hubspot'  => '\\LandingConfig\\Adapters\\HubSpotAdapter',
                'roistat'  => '\\LandingConfig\\Adapters\\RoistatAdapter',
            ];
            if (!empty($map[$type]) && class_exists($map[$type])) {
                $adapter = new $map[$type]();
                $adapter->send($lead);
            }
        }
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

function _send_telegram(array $settings, array $lead): void {
    $token_raw = $settings['bot_token'] ?? '';
    $token     = $token_raw ? (str_starts_with($token_raw, 'v1:') ? \LandingConfig\Encryption\decrypt($token_raw) : $token_raw) : '';
    $chat_id   = $settings['chat_id'] ?? '';
    if ($token === '' || $chat_id === '') return;

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
        'timeout' => 10,
        'body'    => ['chat_id' => $chat_id, 'text' => $text, 'parse_mode' => 'Markdown'],
    ]);

    // Log failures instead of failing silently — makes future issues visible
    // in Debug Log Manager / debug.log instead of requiring manual API testing.
    if (\is_wp_error($resp)) {
        error_log('[landing-config] Telegram send error: ' . $resp->get_error_message());
    } else {
        $code = \wp_remote_retrieve_response_code($resp);
        if ($code !== 200) {
            error_log('[landing-config] Telegram API error ' . $code . ': ' . \wp_remote_retrieve_body($resp));
        }
    }
}

function send_admin_email(array $data, int $lead_id): void {
    $admin_email = get_bloginfo('admin_email');
    if (empty($admin_email)) return;

    $subject = sprintf('[%s] Новая заявка #%d', get_bloginfo('name'), $lead_id);
    $body = "Получена новая заявка:\n\n";
    foreach (['name', 'phone', 'email', 'message', 'source_block'] as $field) {
        if (!empty($data[$field])) {
            $body .= ucfirst($field) . ': ' . $data[$field] . "\n";
        }
    }
    $utm_parts = [];
    foreach (['utm_source', 'utm_medium', 'utm_campaign'] as $u) {
        if (!empty($data[$u])) {
            $utm_parts[] = "$u={$data[$u]}";
        }
    }
    if ($utm_parts) {
        $body .= "\nUTM: " . implode(', ', $utm_parts) . "\n";
    }
    wp_mail($admin_email, $subject, $body);
}
