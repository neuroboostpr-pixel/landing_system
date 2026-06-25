<?php
namespace LandingConfig\Adapters;

if (!defined('ABSPATH')) { exit; }

use function LandingConfig\Encryption\decrypt;

class AmoCRMAdapter implements AdapterInterface {
    public static function name(): string { return 'amocrm'; }
    public static function label(): string { return 'AmoCRM'; }

    public static function field_defs(): array {
        return [
            'subdomain'    => ['label' => 'Subdomain (xxx.amocrm.ru)', 'type' => 'text', 'placeholder' => 'mycompany'],
            'access_token' => ['label' => 'Long-lived access token', 'type' => 'password', 'placeholder' => 'eyJ0eXAi...'],
            'responsible_user_id' => ['label' => 'Responsible user ID', 'type' => 'text', 'placeholder' => '12345'],
        ];
    }

    public static function field_definitions(): array {
        return [
            'subdomain'           => ['type' => 'text', 'label' => 'AmoCRM поддомен', 'required' => true, 'placeholder' => 'acme'],
            'access_token'        => ['type' => 'password', 'label' => 'Access Token (long-lived)', 'encrypt' => true, 'required' => true],
            'pipeline_id'         => ['type' => 'text', 'label' => 'Pipeline ID', 'placeholder' => '7891234'],
            'status_id'           => ['type' => 'text', 'label' => 'Status ID (новый лид)', 'placeholder' => '11223344'],
            'responsible_user_id' => ['type' => 'text', 'label' => 'Responsible user ID', 'placeholder' => '5566'],
        ];
    }

    public static function settings(): array {
        $r = \LandingConfig\Integrations\resolve_integration(static::name(), \get_current_blog_id());
        if ($r !== null) {
            return $r['settings'];
        }
        // Legacy fallback: old admin-integrations.php stored each field as a separate wp_options key:
        // landing_integration_{name}_{field}. Password-type fields were stored encrypted — callers
        // that need plaintext must call decrypt() themselves (same as current send()/test_connection()).
        $name = static::name();
        $out = [];
        foreach (array_keys(static::field_defs()) as $field) {
            $val = \get_option("landing_integration_{$name}_{$field}", '');
            if ($val !== '' && $val !== false) {
                $out[$field] = $val;
            }
        }
        return $out;
    }

    public function send(array $lead): array {
        $s = static::settings();
        $sub = $s['subdomain'] ?? \landing_config_get('integration_amocrm_subdomain');
        $token_raw = $s['access_token'] ?? \landing_config_get('integration_amocrm_access_token');
        $token = $token_raw ? (str_starts_with($token_raw, 'v1:') ? decrypt($token_raw) : $token_raw) : '';
        if ($sub === '' || $token === '') {
            return ['ok' => false, 'response_code' => null, 'response_body' => '', 'error' => 'subdomain or token missing'];
        }

        $payload = [[
            'name' => "Заявка с сайта: {$lead['name']}",
            'created_at' => time(),
            'responsible_user_id' => (int)\landing_config_get('integration_amocrm_responsible_user_id', 0) ?: null,
            '_embedded' => [
                'contacts' => [[
                    'name' => $lead['name'] ?: 'Без имени',
                    'custom_fields_values' => [
                        ['field_code' => 'PHONE', 'values' => [['value' => $lead['phone'], 'enum_code' => 'WORK']]],
                        ['field_code' => 'EMAIL', 'values' => [['value' => $lead['email'], 'enum_code' => 'WORK']]],
                    ],
                ]],
            ],
        ]];

        $resp = \wp_remote_post("https://{$sub}.amocrm.ru/api/v4/leads/complex", [
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
        $s = static::settings();
        $sub = $s['subdomain'] ?? \landing_config_get('integration_amocrm_subdomain');
        $token_raw = $s['access_token'] ?? \landing_config_get('integration_amocrm_access_token');
        $token = $token_raw ? (str_starts_with($token_raw, 'v1:') ? decrypt($token_raw) : $token_raw) : '';
        if ($sub === '' || $token === '') return ['ok' => false, 'message' => 'subdomain или token не заданы'];

        $resp = \wp_remote_get("https://{$sub}.amocrm.ru/api/v4/account", [
            'timeout' => 10,
            'headers' => ['Authorization' => "Bearer {$token}"],
        ]);
        if (\is_wp_error($resp)) return ['ok' => false, 'message' => 'Network: ' . $resp->get_error_message()];
        $code = \wp_remote_retrieve_response_code($resp);
        if ($code === 200) {
            $body = json_decode(\wp_remote_retrieve_body($resp), true);
            return ['ok' => true, 'message' => 'Аккаунт: ' . ($body['name'] ?? '(нет имени)')];
        }
        return ['ok' => false, 'message' => "API вернул {$code}: " . substr(\wp_remote_retrieve_body($resp), 0, 200)];
    }

    private static function normalize_response($resp): array {
        if (\is_wp_error($resp)) return ['ok' => false, 'response_code' => null, 'response_body' => '', 'error' => $resp->get_error_message()];
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
