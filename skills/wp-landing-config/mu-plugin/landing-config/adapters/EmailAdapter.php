<?php
namespace LandingConfig\Adapters;

if (!defined('ABSPATH')) { exit; }

class EmailAdapter implements AdapterInterface {

    public static function name(): string { return 'email'; }
    public static function label(): string { return 'Email уведомления'; }

    public static function field_defs(): array {
        return [
            'to'      => ['label' => 'Email получателя', 'type' => 'text', 'placeholder' => 'manager@example.com'],
            'subject' => ['label' => 'Тема письма', 'type' => 'text', 'placeholder' => 'Новая заявка с сайта'],
        ];
    }

    public static function field_definitions(): array {
        return [
            'to'      => ['type' => 'email', 'label' => 'Email получатель', 'required' => true, 'placeholder' => 'sales@company.ru'],
            'subject' => ['type' => 'text', 'label' => 'Тема письма', 'placeholder' => 'Новая заявка с сайта'],
            'from'    => ['type' => 'email', 'label' => 'From (опционально)', 'placeholder' => 'no-reply@site.ru'],
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
        $to = \landing_config_get('integration_email_to');
        if ($to === '') {
            return ['ok' => false, 'response_code' => null, 'response_body' => '', 'error' => 'No recipient configured'];
        }
        $subject = \landing_config_get('integration_email_subject', 'Новая заявка');
        $body = "Получена заявка #{$lead['id']}\n\n"
              . "Имя:      {$lead['name']}\n"
              . "Телефон:  {$lead['phone']}\n"
              . "Email:    {$lead['email']}\n"
              . "Сообщение:{$lead['message']}\n"
              . "Блок:     {$lead['source_block']}\n"
              . "UTM:      src={$lead['utm_source']} med={$lead['utm_medium']} cmp={$lead['utm_campaign']}\n"
              . "Время:    {$lead['created_at']}\n";

        $sent = \wp_mail($to, $subject, $body);
        return [
            'ok' => $sent,
            'response_code' => $sent ? 200 : null,
            'response_body' => $sent ? 'wp_mail returned true' : '',
            'error' => $sent ? null : 'wp_mail returned false',
        ];
    }

    public function test_connection(): array {
        $to = \landing_config_get('integration_email_to');
        if ($to === '') {
            return ['ok' => false, 'message' => 'Email получателя не указан'];
        }
        if (!\is_email($to)) {
            return ['ok' => false, 'message' => 'Неверный формат email: ' . $to];
        }
        $sent = \wp_mail($to, '[Test] landing-config', 'Тестовое письмо — проверка подключения email.');
        return [
            'ok' => $sent,
            'message' => $sent ? 'Тестовое письмо отправлено' : 'wp_mail вернул false (проверьте SMTP)',
        ];
    }
}
