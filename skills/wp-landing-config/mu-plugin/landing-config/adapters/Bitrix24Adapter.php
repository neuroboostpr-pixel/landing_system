<?php
namespace LandingConfig\Adapters;

if (!defined('ABSPATH')) { exit; }

use function LandingConfig\Encryption\decrypt;

class Bitrix24Adapter implements AdapterInterface {
    public static function name(): string { return 'bitrix24'; }
    public static function label(): string { return 'Bitrix24 (webhook)'; }

    public static function field_defs(): array {
        return [
            'webhook_url' => ['label' => 'Inbound webhook URL', 'type' => 'password', 'placeholder' => 'https://mycompany.bitrix24.ru/rest/1/abcXYZ/'],
        ];
    }

    public static function field_definitions(): array {
        return [
            'webhook_url'    => ['type' => 'url', 'label' => 'Webhook URL', 'encrypt' => true, 'required' => true,
                                 'placeholder' => 'https://acme.bitrix24.ru/rest/N/TOKEN/'],
            'category_id'    => ['type' => 'text', 'label' => 'Category ID (опционально)'],
            'assigned_by_id' => ['type' => 'text', 'label' => 'Assigned user ID'],
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
        $url_enc = \landing_config_get('integration_bitrix24_webhook_url');
        $url = $url_enc ? decrypt($url_enc) : '';
        if ($url === '') return ['ok' => false, 'response_code' => null, 'response_body' => '', 'error' => 'webhook URL missing'];

        $endpoint = rtrim($url, '/') . '/crm.lead.add.json';
        $payload = [
            'fields' => [
                'TITLE' => "Заявка с сайта: " . ($lead['name'] ?: 'Без имени'),
                'NAME' => $lead['name'],
                'PHONE' => [['VALUE' => $lead['phone'], 'VALUE_TYPE' => 'WORK']],
                'EMAIL' => [['VALUE' => $lead['email'], 'VALUE_TYPE' => 'WORK']],
                'COMMENTS' => $lead['message'] . "\n\nИсточник: {$lead['source_block']}\nUTM: {$lead['utm_source']}/{$lead['utm_medium']}/{$lead['utm_campaign']}",
                'SOURCE_ID' => 'WEB',
            ],
        ];

        $resp = \wp_remote_post($endpoint, [
            'timeout' => 15,
            'body' => $payload,
        ]);
        return self::normalize_response($resp);
    }

    public function test_connection(): array {
        $url_enc = \landing_config_get('integration_bitrix24_webhook_url');
        $url = $url_enc ? decrypt($url_enc) : '';
        if ($url === '') return ['ok' => false, 'message' => 'Webhook URL не задан'];

        $endpoint = rtrim($url, '/') . '/profile.json';
        $resp = \wp_remote_get($endpoint, ['timeout' => 10]);
        if (\is_wp_error($resp)) return ['ok' => false, 'message' => 'Network: ' . $resp->get_error_message()];
        $code = \wp_remote_retrieve_response_code($resp);
        if ($code === 200) {
            $body = json_decode(\wp_remote_retrieve_body($resp), true);
            $name = ($body['result']['NAME'] ?? '') . ' ' . ($body['result']['LAST_NAME'] ?? '');
            return ['ok' => true, 'message' => 'Профиль: ' . trim($name)];
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
