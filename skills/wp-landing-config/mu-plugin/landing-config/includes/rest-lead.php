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

function log_delivery_attempt(int $lead_id, string $adapter, array $result): void {
    if ($lead_id <= 0 || $adapter === '') return;

    global $wpdb;
    $safe = safe_delivery_summary($result);
    $wpdb->insert(\LandingConfig\DB\get_lead_log_table_name(), [
        'lead_id'       => $lead_id,
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
        '[landing-config] delivery lead_id=%d adapter=%s status=%s',
        $lead_id,
        sanitize_key($adapter),
        $safe['status']
    ));
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

    // Consent must be an explicit affirmative value from a real checkbox.
    // The early audit above preserves the attempted contact for diagnosis.
    if ((string) ($params['pd_consent'] ?? '') !== '1') {
        audit_log_block($audit_id, 'pd_consent', 'explicit consent missing');
        return new \WP_REST_Response(['ok' => false, 'error' => 'pd_consent'], 400);
    }

    // Rate limit per IP — transient-based.
    $rl_key = 'landing_lead_rl_' . md5($ip);
    $rl_count = (int) get_transient($rl_key);
    if ($rl_count >= get_rate_limit()) {
        audit_log_block($audit_id, 'rate_limit', 'count=' . $rl_count . ' limit=' . get_rate_limit());
        return new \WP_REST_Response(['ok' => false, 'error' => 'rate_limit'], 429);
    }
    set_transient($rl_key, $rl_count + 1, HOUR_IN_SECONDS);

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
        'recaptcha_score'       => null,
    ];

    global $wpdb;
    $inserted = $wpdb->insert(get_leads_table_name(), $data);
    if ($inserted === false || $inserted === 0) {
        audit_log_block($audit_id, 'db_error', $wpdb->last_error);
        return new \WP_REST_Response(['ok' => false, 'error' => 'db_error'], 500);
    }
    $lead_id = (int) $wpdb->insert_id;
    if ($lead_id <= 0) {
        audit_log_block($audit_id, 'db_error', 'lead insert did not return a positive id');
        return new \WP_REST_Response(['ok' => false, 'error' => 'db_error'], 500);
    }

    // Audit: пометить как успешно сохранённую заявку
    audit_log_success($audit_id, $lead_id);

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
        log_delivery_attempt((int) ($lead['id'] ?? 0), (string) $type, $result);
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
