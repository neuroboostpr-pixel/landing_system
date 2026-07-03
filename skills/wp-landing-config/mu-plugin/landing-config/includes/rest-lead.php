<?php
namespace LandingConfig\REST;

if (!defined('ABSPATH')) { exit; }

use function LandingConfig\DB\get_leads_table_name;

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

function handle_lead($request) {
    $params = $request->get_params();

    // Honeypot: field 'website' must be empty (real users don't fill it; bots do).
    if (!empty($params['website'])) {
        return new \WP_REST_Response(['ok' => false, 'error' => 'invalid'], 400);
    }

    // Rate limit per IP — transient-based.
    $ip = $_SERVER['REMOTE_ADDR'] ?? 'unknown';
    $rl_key = 'landing_lead_rl_' . md5($ip);
    $rl_count = (int) get_transient($rl_key);
    if ($rl_count >= get_rate_limit()) {
        return new \WP_REST_Response(['ok' => false, 'error' => 'rate_limit'], 429);
    }
    set_transient($rl_key, $rl_count + 1, HOUR_IN_SECONDS);

    // pd_consent (152-ФЗ ст.9): обязательное явное согласие. Принимаем только '1'.
    $pd_consent = (string) ($params['pd_consent'] ?? '');
    if ($pd_consent !== '1') {
        return new \WP_REST_Response(
            ['ok' => false, 'error' => 'pd_consent_required'],
            400
        );
    }

    // Required: at least one of phone or email
    $name = sanitize_text_field(wp_unslash($params['name'] ?? ''));
    $phone = sanitize_text_field(wp_unslash($params['phone'] ?? ''));
    $email = sanitize_email(wp_unslash($params['email'] ?? ''));
    if ($phone === '' && $email === '') {
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
    ];

    global $wpdb;
    $inserted = $wpdb->insert(get_leads_table_name(), $data);
    if ($inserted === false || $inserted === 0) {
        return new \WP_REST_Response(['ok' => false, 'error' => 'db_error'], 500);
    }
    $lead_id = $wpdb->insert_id;

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

function _send_telegram(array $settings, array $lead): void {
    $token_raw = $settings['bot_token'] ?? '';
    $token     = $token_raw ? (str_starts_with($token_raw, 'v1:') ? \LandingConfig\Encryption\decrypt($token_raw) : $token_raw) : '';
    $chat_id   = $settings['chat_id'] ?? '';
    if ($token === '' || $chat_id === '') return;

    $id      = $lead['id'] ?? '?';
    $name    = $lead['name'] ?? '';
    $phone   = $lead['phone'] ?? '';
    $email   = $lead['email'] ?? '';
    $message = $lead['message'] ?? '';
    $source  = $lead['source_block'] ?? '';
    $utm     = $lead['utm_source'] ?? '';

    $text = "\xF0\x9F\x94\x94 *Новая заявка #$id*\n\n"
          . "\xF0\x9F\x91\xA4 Имя: " . ($name    ?: '—') . "\n"
          . "\xF0\x9F\x93\xB1 Телефон: " . ($phone   ? "`$phone`" : '—') . "\n"
          . "\xF0\x9F\x93\xA7 Email: " . ($email   ?: '—') . "\n"
          . "\xF0\x9F\x92\xAC Сообщение: " . ($message ?: '—') . "\n"
          . "\xF0\x9F\x93\xA6 Источник: " . ($source  ?: '—') . "\n"
          . "\xF0\x9F\x94\x97 UTM: " . ($utm     ?: '—') . "\n";

    \wp_remote_post("https://api.telegram.org/bot{$token}/sendMessage", [
        'timeout' => 10,
        'body'    => ['chat_id' => $chat_id, 'text' => $text, 'parse_mode' => 'Markdown'],
    ]);
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
