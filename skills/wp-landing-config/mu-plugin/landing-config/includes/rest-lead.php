<?php
namespace LandingConfig\REST;

if (!defined('ABSPATH')) { exit; }

use function LandingConfig\DB\get_leads_table_name;

const RATE_LIMIT_PER_HOUR = 10;

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

    // Rate limit per IP — transient-based, 10 req/hour.
    $ip = $_SERVER['REMOTE_ADDR'] ?? 'unknown';
    $rl_key = 'landing_lead_rl_' . md5($ip);
    $rl_count = (int) get_transient($rl_key);
    if ($rl_count >= RATE_LIMIT_PER_HOUR) {
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

    // Adapter dispatch happens in A5; A1 just stores + emails
    do_action('landing_config_lead_received', $lead_id, $data);

    return new \WP_REST_Response([
        'ok'      => true,
        'lead_id' => $lead_id,
    ], 200);
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
