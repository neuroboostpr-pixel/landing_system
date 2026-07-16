<?php
namespace LandingConfig\Adapters;

if (!defined('ABSPATH')) { exit; }

use function LandingConfig\Encryption\decrypt;

class RoistatAdapter implements AdapterInterface {
    public static function name(): string { return 'roistat'; }
    public static function label(): string { return 'Roistat (webhook)'; }

    public static function field_defs(): array {
        return [
            'webhook_url' => ['label' => 'Webhook URL', 'type' => 'password',
                              'placeholder' => 'https://cloud.roistat.com/integration/webhook?key=...'],
            'site_url'    => ['label' => 'URL сайта', 'type' => 'text',
                              'placeholder' => 'https://hybridautos.ae/'],
        ];
    }

    public static function field_definitions(): array {
        return [
            'webhook_url' => ['type' => 'url', 'label' => 'Webhook URL', 'encrypt' => true, 'required' => true,
                              'placeholder' => 'https://cloud.roistat.com/integration/webhook?key=...'],
            'site_url'    => ['type' => 'text', 'label' => 'URL сайта', 'required' => true,
                              'placeholder' => 'https://hybridautos.ae/'],
        ];
    }

    public static function settings(): array {
        $r = \LandingConfig\Integrations\resolve_integration(static::name(), \get_current_blog_id());
        if ($r !== null) {
            return $r['settings'];
        }
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

    public function send(array $lead, ?array $settings = null): array {
        $s = $settings ?? static::settings();
        $url_raw = $s['webhook_url'] ?? '';
        $url = $url_raw ? (str_starts_with($url_raw, 'v1:') ? decrypt($url_raw) : $url_raw) : '';
        if ($url === '') return ['ok' => false, 'status' => 'failed_permanent', 'response_code' => null, 'response_body' => '', 'error' => 'webhook URL missing'];

        $site_url = rtrim($s['site_url'] ?? get_home_url(), '/') . '/';
        $name  = $lead['name'] ?? '';
        $phone = $lead['phone'] ?? '';
        $email = $lead['email'] ?? '';

        // Страница из source_block (содержит URL)
        $source_url = $lead['source_block'] ?? '';
        $path = parse_url($source_url, PHP_URL_PATH) ?? '/';
        $segments = array_filter(explode('/', trim($path, '/')));
        $page = count($segments) ? end($segments) : 'main';

        $comment_parts = [];
        $comment_parts[] = 'Страница: ' . $page;
        if (!empty($lead['message']) && strpos($lead['message'], 'Model:') === 0) {
            $comment_parts[] = trim($lead['message']);
        } elseif (!empty($lead['message'])) {
            $comment_parts[] = 'Сообщение: ' . $lead['message'];
        }
        $comment = implode("\n", $comment_parts);

        $payload = [
            'title'         => 'Заявка с сайта ' . $site_url . ($name ? ' — ' . $name : ''),
            'name'          => $name,
            'phone'         => $phone,
            'email'         => $email,
            'comment'       => $comment,
            'roistat_visit' => $lead['roistat_visit'] ?? '',
            'fields'        => [
                'site'   => $site_url,
                'source' => $lead['source_block'] ?: 'site',
            ],
        ];

        $resp = \wp_remote_post($url, [
            'timeout' => 15,
            'headers' => ['Content-Type' => 'application/json'],
            'body'    => wp_json_encode($payload),
        ]);
        return self::normalize_response($resp);
    }

    public function test_connection(): array {
        $s = static::settings();
        $url_raw = $s['webhook_url'] ?? '';
        $url = $url_raw ? (str_starts_with($url_raw, 'v1:') ? decrypt($url_raw) : $url_raw) : '';
        if ($url === '') return ['ok' => false, 'message' => 'Webhook URL не задан'];

        // Roistat не имеет отдельного ping-endpoint — шлём минимальную тестовую сделку
        $site_url = rtrim($s['site_url'] ?? get_home_url(), '/') . '/';
        $payload = [
            'title'         => 'Тест подключения ' . $site_url,
            'name'          => 'Тест',
            'phone'         => '+971000000000',
            'email'         => 'test@' . parse_url($site_url, PHP_URL_HOST),
            'comment'       => 'Тестовый запрос от landing-config',
            'roistat_visit' => '0',
            'fields'        => ['site' => $site_url, 'source' => 'test'],
        ];
        $resp = \wp_remote_post($url, [
            'timeout' => 10,
            'headers' => ['Content-Type' => 'application/json'],
            'body'    => wp_json_encode($payload),
        ]);
        if (\is_wp_error($resp)) return ['ok' => false, 'message' => 'Network: ' . $resp->get_error_message()];
        $code = \wp_remote_retrieve_response_code($resp);
        $body = \wp_remote_retrieve_body($resp);
        $json = json_decode($body, true);
        if (self::is_confirmed_success($code, $body, $json)) {
            return ['ok' => true, 'message' => 'Roistat подтвердил создание сделки'];
        }
        $msg = $json['message'] ?? $body;
        return ['ok' => false, 'message' => "HTTP {$code}: {$msg}"];
    }

    private static function normalize_response($resp): array {
        if (\is_wp_error($resp)) return ['ok' => false, 'response_code' => null, 'response_body' => '', 'error' => $resp->get_error_message()];
        $code = \wp_remote_retrieve_response_code($resp);
        $body = \wp_remote_retrieve_body($resp);
        $json = json_decode($body, true);
        $ok   = self::is_confirmed_success($code, $body, $json);
        return [
            'ok' => $ok,
            'response_code' => $code,
            'response_body' => $body,
            'error' => !$ok ? ($json['message'] ?? "HTTP {$code}") : null,
            'retry_after' => \wp_remote_retrieve_header($resp, 'retry-after'),
        ];
    }

    /**
     * Roistat has returned JSON status values "ok" and "success", plus the
     * integration's plain-text confirmation in production. Accept only those
     * explicit success contracts, never an arbitrary HTTP 2xx body.
     */
    private static function is_confirmed_success(int $code, string $body, $json): bool {
        if ($code < 200 || $code >= 300) return false;
        if (is_array($json) && in_array(($json['status'] ?? ''), ['ok', 'success'], true)) return true;
        return trim($body) === 'Lead was successfully created';
    }
}
