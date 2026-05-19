<?php
namespace LandingConfig\Adapters;

if (!defined('ABSPATH')) { exit; }

use function LandingConfig\Encryption\decrypt;

class HubSpotAdapter implements AdapterInterface {
    public static function name(): string { return 'hubspot'; }
    public static function label(): string { return 'HubSpot'; }

    public static function field_defs(): array {
        return [
            'access_token' => ['label' => 'Private app access token', 'type' => 'password', 'placeholder' => 'pat-eu1-...'],
        ];
    }

    public function send(array $lead): array {
        $token_enc = \landing_config_get('integration_hubspot_access_token');
        $token = $token_enc ? decrypt($token_enc) : '';
        if ($token === '') return ['ok' => false, 'response_code' => null, 'response_body' => '', 'error' => 'token missing'];

        $payload = [
            'properties' => [
                'firstname' => $lead['name'],
                'phone' => $lead['phone'],
                'email' => $lead['email'],
                'message' => $lead['message'],
                'lifecyclestage' => 'lead',
                'lead_source_detail' => $lead['source_block'],
                'hs_analytics_source' => $lead['utm_source'] ?: 'OTHER_CAMPAIGNS',
            ],
        ];

        $resp = \wp_remote_post('https://api.hubapi.com/crm/v3/objects/contacts', [
            'timeout' => 15,
            'headers' => [
                'Authorization' => "Bearer {$token}",
                'Content-Type' => 'application/json',
            ],
            'body' => json_encode($payload),
        ]);
        return self::normalize_response($resp);
    }

    public function test_connection(): array {
        $token_enc = \landing_config_get('integration_hubspot_access_token');
        $token = $token_enc ? decrypt($token_enc) : '';
        if ($token === '') return ['ok' => false, 'message' => 'Token не задан'];

        $resp = \wp_remote_get('https://api.hubapi.com/account-info/v3/details', [
            'timeout' => 10,
            'headers' => ['Authorization' => "Bearer {$token}"],
        ]);
        if (\is_wp_error($resp)) return ['ok' => false, 'message' => 'Network: ' . $resp->get_error_message()];
        $code = \wp_remote_retrieve_response_code($resp);
        if ($code === 200) {
            $body = json_decode(\wp_remote_retrieve_body($resp), true);
            return ['ok' => true, 'message' => 'Portal ID: ' . ($body['portalId'] ?? 'unknown')];
        }
        return ['ok' => false, 'message' => "API вернул {$code}"];
    }

    private static function normalize_response($resp): array {
        if (\is_wp_error($resp)) return ['ok' => false, 'response_code' => null, 'response_body' => '', 'error' => $resp->get_error_message()];
        $code = \wp_remote_retrieve_response_code($resp);
        $body = \wp_remote_retrieve_body($resp);
        return ['ok' => $code >= 200 && $code < 300, 'response_code' => $code, 'response_body' => $body, 'error' => $code >= 400 ? "HTTP {$code}" : null];
    }
}
