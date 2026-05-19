<?php
namespace LandingConfig\Adapters;

if (!defined('ABSPATH')) { exit; }

use function LandingConfig\Encryption\decrypt;

/**
 * WhatsApp via Business Cloud API (Meta Graph API).
 * For simple "click to chat" links, use CTA preset 'whatsapp' instead — no API key needed.
 * This adapter SENDS messages programmatically when a lead arrives, requires Business API.
 */
class WhatsAppAdapter implements AdapterInterface {

    public static function name(): string { return 'whatsapp'; }
    public static function label(): string { return 'WhatsApp Business Cloud API'; }

    public static function field_defs(): array {
        return [
            'access_token' => ['label' => 'Access token', 'type' => 'password', 'placeholder' => 'EAAxxx...'],
            'phone_id'     => ['label' => 'Phone Number ID', 'type' => 'text', 'placeholder' => '123456789012345'],
            'to_phone'     => ['label' => 'Получатель (E.164)', 'type' => 'text', 'placeholder' => '+79991234567'],
        ];
    }

    public static function field_definitions(): array {
        return [
            'phone_number_id' => ['type' => 'text', 'label' => 'Phone Number ID', 'required' => true],
            'access_token'    => ['type' => 'password', 'label' => 'Access Token', 'encrypt' => true, 'required' => true],
            'template_name'   => ['type' => 'text', 'label' => 'Template name', 'placeholder' => 'new_lead_notification'],
            'to_number'       => ['type' => 'text', 'label' => 'WhatsApp получатель', 'required' => true,
                                  'placeholder' => '+79001234567'],
        ];
    }

    public static function settings(): array {
        $r = \LandingConfig\Integrations\resolve_integration(static::name(), \get_current_blog_id());
        if ($r === null) {
            $legacy = \get_option('landing_integration_' . static::name(), []);
            return is_array($legacy) ? $legacy : [];
        }
        return $r['settings'];
    }

    public function send(array $lead): array {
        $token_enc = \landing_config_get('integration_whatsapp_access_token');
        $token = $token_enc ? decrypt($token_enc) : '';
        $phone_id = \landing_config_get('integration_whatsapp_phone_id');
        $to = preg_replace('/[^0-9]/', '', \landing_config_get('integration_whatsapp_to_phone'));
        if ($token === '' || $phone_id === '' || $to === '') {
            return ['ok' => false, 'response_code' => null, 'response_body' => '', 'error' => 'Token/phone_id/to missing'];
        }

        $text = "Новая заявка #{$lead['id']}: {$lead['name']}, {$lead['phone']}, {$lead['email']}";
        $resp = \wp_remote_post("https://graph.facebook.com/v18.0/{$phone_id}/messages", [
            'timeout' => 10,
            'headers' => ['Authorization' => "Bearer {$token}", 'Content-Type' => 'application/json'],
            'body' => json_encode([
                'messaging_product' => 'whatsapp',
                'to' => $to,
                'type' => 'text',
                'text' => ['body' => $text],
            ]),
        ]);
        return self::normalize_response($resp);
    }

    public function test_connection(): array {
        $token_enc = \landing_config_get('integration_whatsapp_access_token');
        $token = $token_enc ? decrypt($token_enc) : '';
        $phone_id = \landing_config_get('integration_whatsapp_phone_id');
        if ($token === '' || $phone_id === '') {
            return ['ok' => false, 'message' => 'Access token или Phone ID не заданы'];
        }
        $resp = \wp_remote_get("https://graph.facebook.com/v18.0/{$phone_id}", [
            'timeout' => 10,
            'headers' => ['Authorization' => "Bearer {$token}"],
        ]);
        if (\is_wp_error($resp)) return ['ok' => false, 'message' => 'Network: ' . $resp->get_error_message()];
        $code = \wp_remote_retrieve_response_code($resp);
        if ($code === 200) return ['ok' => true, 'message' => 'Phone Number ID валиден'];
        return ['ok' => false, 'message' => "API вернул {$code}"];
    }

    private static function normalize_response($resp): array {
        if (\is_wp_error($resp)) {
            return ['ok' => false, 'response_code' => null, 'response_body' => '', 'error' => $resp->get_error_message()];
        }
        $code = \wp_remote_retrieve_response_code($resp);
        $body = \wp_remote_retrieve_body($resp);
        return [
            'ok' => $code >= 200 && $code < 300,
            'response_code' => $code,
            'response_body' => $body,
            'error' => $code >= 400 ? "HTTP {$code}" : null,
        ];
    }
}
