<?php
namespace LandingConfig\Adapters;

if (!defined('ABSPATH')) { exit; }

use function LandingConfig\Encryption\decrypt;

class TelegramAdapter implements AdapterInterface {

    public static function name(): string { return 'telegram'; }
    public static function label(): string { return 'Telegram (Bot API)'; }

    public static function field_defs(): array {
        return [
            'bot_token' => ['label' => 'Bot token', 'type' => 'password', 'placeholder' => '123456:ABC-DEF...'],
            'chat_id'   => ['label' => 'Chat ID или @channel', 'type' => 'text', 'placeholder' => '-100123456789 или @mychannel'],
        ];
    }

    public static function field_definitions(): array {
        return [
            'bot_token' => ['type' => 'password', 'label' => 'Bot Token', 'encrypt' => true, 'required' => true,
                            'placeholder' => '123456:ABC-DEF...'],
            'chat_id'   => ['type' => 'text', 'label' => 'Chat ID', 'required' => true,
                            'placeholder' => '-1001234567890'],
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
        $token_enc = $s['bot_token'] ?? \landing_config_get('integration_telegram_bot_token');
        $token = $token_enc ? decrypt($token_enc) : '';
        $chat_id = $s['chat_id'] ?? \landing_config_get('integration_telegram_chat_id');
        if ($token === '' || $chat_id === '') {
            return ['ok' => false, 'response_code' => null, 'response_body' => '', 'error' => 'Token or chat_id missing'];
        }

        $text = "🔔 *Новая заявка #{$lead['id']}*\n\n"
              . "👤 Имя: {$lead['name']}\n"
              . "📱 Телефон: `{$lead['phone']}`\n"
              . "📧 Email: {$lead['email']}\n"
              . ($lead['message'] ? "💬 Сообщение: {$lead['message']}\n" : '')
              . "📦 Блок: {$lead['source_block']}\n"
              . ($lead['utm_source'] ? "🔗 UTM source: {$lead['utm_source']}\n" : '');

        $resp = \wp_remote_post("https://api.telegram.org/bot{$token}/sendMessage", [
            'timeout' => 10,
            'body' => ['chat_id' => $chat_id, 'text' => $text, 'parse_mode' => 'Markdown'],
        ]);
        return self::normalize_response($resp);
    }

    public function test_connection(): array {
        $s = static::settings();
        $token_enc = $s['bot_token'] ?? \landing_config_get('integration_telegram_bot_token');
        $token = $token_enc ? decrypt($token_enc) : '';
        if ($token === '') return ['ok' => false, 'message' => 'Bot token не задан'];

        $resp = \wp_remote_get("https://api.telegram.org/bot{$token}/getMe", ['timeout' => 10]);
        if (\is_wp_error($resp)) return ['ok' => false, 'message' => 'Network error: ' . $resp->get_error_message()];

        $code = \wp_remote_retrieve_response_code($resp);
        $body = json_decode(\wp_remote_retrieve_body($resp), true);
        if ($code === 200 && !empty($body['ok'])) {
            return ['ok' => true, 'message' => 'Бот: @' . $body['result']['username']];
        }
        return ['ok' => false, 'message' => "API вернул {$code}: " . substr(\wp_remote_retrieve_body($resp), 0, 200)];
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
