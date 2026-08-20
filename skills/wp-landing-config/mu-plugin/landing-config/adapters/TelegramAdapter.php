<?php
namespace LandingConfig\Adapters;

if (!defined('ABSPATH')) { exit; }

use function LandingConfig\Encryption\decrypt;

class TelegramAdapter implements AdapterInterface {

    private const MESSAGE_TEXT_LIMIT = 3900;

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

    public function send(array $lead, ?array $settings = null): array {
        $explicit = $settings !== null;
        $s = $explicit ? $settings : static::settings();
        $token_raw = $s['bot_token'] ?? ($explicit ? '' : \landing_config_get('integration_telegram_bot_token'));
        $token = $token_raw ? (str_starts_with($token_raw, 'v1:') ? decrypt($token_raw) : $token_raw) : '';
        $chat_id = $s['chat_id'] ?? ($explicit ? '' : \landing_config_get('integration_telegram_chat_id'));
        if ($token === '' || $chat_id === '') {
            return ['ok' => false, 'status' => 'failed_permanent', 'response_code' => null, 'response_body' => '', 'error' => 'Token or chat_id missing'];
        }

        $text = self::build_lead_message($lead);

        $resp = \wp_remote_post("https://api.telegram.org/bot{$token}/sendMessage", [
            'timeout' => 10,
            'redirection' => 0,
            'body' => ['chat_id' => $chat_id, 'text' => $text, 'parse_mode' => 'HTML'],
        ]);
        return self::normalize_response($resp);
    }

    public function test_connection(): array {
        $s = static::settings();
        $token_raw = $s['bot_token'] ?? \landing_config_get('integration_telegram_bot_token');
        $token = $token_raw ? (str_starts_with($token_raw, 'v1:') ? decrypt($token_raw) : $token_raw) : '';
        $chat_id = $s['chat_id'] ?? \landing_config_get('integration_telegram_chat_id');
        if ($token === '') return ['ok' => false, 'message' => 'Bot token не задан'];
        if ($chat_id === '') return ['ok' => false, 'message' => 'Chat ID не задан'];

        $site = \get_bloginfo('name') ?: \get_bloginfo('url');
        $resp = \wp_remote_post("https://api.telegram.org/bot{$token}/sendMessage", [
            'timeout' => 10,
            'body'    => [
                'chat_id'    => $chat_id,
                'text'       => "\xE2\x9C\x85 Тест соединения\n\nИнтеграция настроена корректно.\nСайт: {$site}",
                'parse_mode' => 'Markdown',
            ],
        ]);
        if (\is_wp_error($resp)) return ['ok' => false, 'message' => 'Network error: ' . $resp->get_error_message()];

        $code = \wp_remote_retrieve_response_code($resp);
        $body = json_decode(\wp_remote_retrieve_body($resp), true);
        if ($code === 200 && !empty($body['ok'])) {
            return ['ok' => true, 'message' => 'Сообщение отправлено в чат'];
        }
        $err = $body['description'] ?? substr(\wp_remote_retrieve_body($resp), 0, 200);
        return ['ok' => false, 'message' => "Ошибка {$code}: {$err}"];
    }

    private static function utf8_length(string $value): int {
        if (\function_exists('mb_strlen')) {
            return (int) \mb_strlen($value, 'UTF-8');
        }
        $count = \preg_match_all('/./us', $value, $unused);
        return $count === false ? \strlen($value) : $count;
    }

    private static function utf8_characters(string $value): array {
        $characters = \preg_split('//u', $value, -1, PREG_SPLIT_NO_EMPTY);
        if (\is_array($characters)) { return $characters; }

        // WordPress normally rejects invalid UTF-8 before this adapter. Keep a
        // defensive fallback so a damaged legacy row cannot produce invalid HTML.
        $safe = \htmlspecialchars($value, ENT_QUOTES | ENT_SUBSTITUTE, 'UTF-8');
        $characters = \preg_split('//u', $safe, -1, PREG_SPLIT_NO_EMPTY);
        return \is_array($characters) ? $characters : [];
    }

    private static function escaped_value(string $value, int $limit): string {
        $value = $value !== '' ? $value : '—';
        $escaped = \htmlspecialchars($value, ENT_QUOTES | ENT_SUBSTITUTE, 'UTF-8');
        if (self::utf8_length($escaped) <= $limit) { return $escaped; }

        $ellipsis = '…';
        $budget = \max(0, $limit - self::utf8_length($ellipsis));
        $result = '';
        foreach (self::utf8_characters($value) as $character) {
            $piece = \htmlspecialchars($character, ENT_QUOTES | ENT_SUBSTITUTE, 'UTF-8');
            if (self::utf8_length($result) + self::utf8_length($piece) > $budget) { break; }
            $result .= $piece;
        }
        return $result . $ellipsis;
    }

    private static function append_line(string &$text, string $prefix, string $value, int $value_limit): void {
        $available = self::MESSAGE_TEXT_LIMIT - self::utf8_length($text) - self::utf8_length($prefix) - 1;
        if ($available <= 0) { return; }
        $text .= $prefix . self::escaped_value($value, \min($value_limit, $available)) . "\n";
    }

    private static function build_lead_message(array $lead): string {
        $id = \htmlspecialchars((string)($lead['id'] ?? '?'), ENT_QUOTES | ENT_SUBSTITUTE, 'UTF-8');
        $text = "🔔 <b>Новая заявка #{$id}</b>\n\n";
        self::append_line($text, "👤 Имя: ", (string)($lead['name'] ?? ''), 400);

        $phone = self::escaped_value((string)($lead['phone'] ?? ''), 256);
        $text .= "📱 Телефон: <code>{$phone}</code>\n";
        self::append_line($text, "📧 Email: ", (string)($lead['email'] ?? ''), 384);
        self::append_line($text, "💬 Сообщение: ", (string)($lead['message'] ?? ''), 600);
        self::append_line($text, "📦 Источник: ", (string)($lead['source_block'] ?? ''), 900);

        foreach (['utm_source', 'utm_medium', 'utm_campaign', 'utm_term', 'utm_content'] as $field) {
            self::append_line($text, "🔗 {$field}=", (string)($lead[$field] ?? ''), 160);
        }

        return $text;
    }

    private static function normalize_retry_after($value): int {
        if (\is_int($value)) { return \max(1, \min(3600, $value)); }
        if (\is_string($value) && \ctype_digit(\trim($value))) {
            return \max(1, \min(3600, (int)\trim($value)));
        }
        return 60;
    }

    private static function normalize_response($resp): array {
        if (\is_wp_error($resp)) {
            return [
                'ok' => false,
                'status' => 'unknown',
                'response_code' => null,
                'response_body' => '',
                'provider_id' => null,
                'retry_after' => null,
                'error' => 'transport_error',
            ];
        }

        $code = (int) \wp_remote_retrieve_response_code($resp);
        $body = (string) \wp_remote_retrieve_body($resp);
        $decoded = \json_decode($body, true);
        $message_id = \is_array($decoded) && \is_array($decoded['result'] ?? null)
            ? ($decoded['result']['message_id'] ?? null)
            : null;
        $positive_message_id = (\is_int($message_id)
                || (\is_string($message_id) && \ctype_digit($message_id)))
            && (int)$message_id > 0;

        if ($code === 200 && \is_array($decoded) && ($decoded['ok'] ?? null) === true && $positive_message_id) {
            return [
                'ok' => true,
                'status' => 'success',
                'response_code' => 200,
                'response_body' => $body,
                'provider_id' => (string)$message_id,
                'retry_after' => null,
                'error' => null,
            ];
        }

        $telegram_error_code = \is_array($decoded) && \is_numeric($decoded['error_code'] ?? null)
            ? (int)$decoded['error_code']
            : null;
        // A 5xx response is ambiguous even if its body happens to contain 429:
        // never auto-resend after the provider may already have accepted data.
        if ($code === 429 || ($code === 200 && $telegram_error_code === 429)) {
            $retry_after = \is_array($decoded) && \is_array($decoded['parameters'] ?? null)
                ? ($decoded['parameters']['retry_after'] ?? null)
                : null;
            return [
                'ok' => false,
                'status' => 'retry_wait',
                'response_code' => 429,
                'response_body' => $body,
                'provider_id' => null,
                'retry_after' => self::normalize_retry_after($retry_after),
                'error' => 'rate_limited',
            ];
        }

        $status = ($code >= 500 || $code === 0 || ($code >= 200 && $code < 300))
            ? 'unknown'
            : 'failed_permanent';
        return [
            'ok' => false,
            'status' => $status,
            'response_code' => $code > 0 ? $code : null,
            'response_body' => $body,
            'provider_id' => null,
            'retry_after' => null,
            'error' => $status === 'unknown' ? 'telegram_not_confirmed' : 'provider_4xx',
        ];
    }
}
