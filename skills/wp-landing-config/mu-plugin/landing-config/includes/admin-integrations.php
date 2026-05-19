<?php
namespace LandingConfig\Admin\Integrations;

if (!defined('ABSPATH')) { exit; }

use LandingConfig\Adapters\EmailAdapter;
use LandingConfig\Adapters\TelegramAdapter;
use LandingConfig\Adapters\WhatsAppAdapter;
use LandingConfig\Adapters\AmoCRMAdapter;
use LandingConfig\Adapters\Bitrix24Adapter;
use LandingConfig\Adapters\HubSpotAdapter;
use function LandingConfig\Encryption\encrypt;
use function LandingConfig\Encryption\decrypt;
use function LandingConfig\Encryption\mask;

function all_adapters(): array {
    return [
        EmailAdapter::class,
        TelegramAdapter::class,
        WhatsAppAdapter::class,
        AmoCRMAdapter::class,
        Bitrix24Adapter::class,
        HubSpotAdapter::class,
    ];
}

add_action('admin_menu', function () {
    add_submenu_page(
        'landing-config',
        'Интеграции',
        'Интеграции',
        'manage_options',
        'landing-config-integrations',
        __NAMESPACE__ . '\\render_page'
    );
});

add_action('admin_init', function () {
    foreach (all_adapters() as $cls) {
        $name = $cls::name();
        register_setting('landing_integrations', "landing_integration_{$name}_enabled", ['type' => 'boolean']);
        foreach ($cls::field_defs() as $field => $meta) {
            register_setting('landing_integrations', "landing_integration_{$name}_{$field}", [
                'type' => 'string',
                'sanitize_callback' => $meta['type'] === 'password'
                    ? __NAMESPACE__ . '\\sanitize_secret'
                    : 'sanitize_text_field',
            ]);
        }
    }
});

function sanitize_secret($input): string {
    // If unchanged (still bullet-masked), signal to keep existing
    if (preg_match('/^•+/u', $input)) {
        return '';
    }
    return $input === '' ? '' : encrypt($input);
}

// Pre-save hook: if sanitize returned '' (masked unchanged), restore previous value
add_filter('pre_update_option', function ($value, $option) {
    if (strpos($option, 'landing_integration_') === 0 && $value === '') {
        $existing = get_option($option, '');
        if ($existing !== '') return $existing;
    }
    return $value;
}, 10, 2);

function render_page(): void {
    if (!current_user_can('manage_options')) { wp_die('Insufficient permissions'); }
    ?>
    <div class="wrap">
        <h1>Интеграции</h1>
        <form method="post" action="options.php">
            <?php settings_fields('landing_integrations'); ?>
            <?php foreach (all_adapters() as $cls):
                $name = $cls::name();
                $enabled = (bool)get_option("landing_integration_{$name}_enabled");
            ?>
                <h2><?php echo esc_html($cls::label()); ?></h2>
                <table class="form-table">
                    <tr>
                        <th>Включён</th>
                        <td><label>
                            <input type="checkbox" name="landing_integration_<?php echo $name; ?>_enabled" value="1" <?php checked($enabled); ?>>
                            Отправлять заявки в <?php echo esc_html($cls::label()); ?>
                        </label></td>
                    </tr>
                    <?php foreach ($cls::field_defs() as $field => $meta):
                        $opt_key = "landing_integration_{$name}_{$field}";
                        $stored = get_option($opt_key, '');
                        $display_value = $meta['type'] === 'password' && $stored !== ''
                            ? mask(decrypt($stored))
                            : $stored;
                    ?>
                        <tr>
                            <th><label for="<?php echo $opt_key; ?>"><?php echo esc_html($meta['label']); ?></label></th>
                            <td>
                                <input type="text" id="<?php echo $opt_key; ?>"
                                    name="<?php echo $opt_key; ?>"
                                    value="<?php echo esc_attr($display_value); ?>"
                                    placeholder="<?php echo esc_attr($meta['placeholder'] ?? ''); ?>"
                                    class="regular-text">
                            </td>
                        </tr>
                    <?php endforeach; ?>
                    <tr>
                        <th></th>
                        <td>
                            <button type="button" class="button landing-test-btn" data-adapter="<?php echo $name; ?>">
                                Test connection
                            </button>
                            <span class="landing-test-result" id="landing-test-result-<?php echo $name; ?>"></span>
                        </td>
                    </tr>
                </table>
            <?php endforeach; ?>
            <?php submit_button(); ?>
        </form>
    </div>
    <script>
    document.querySelectorAll('.landing-test-btn').forEach(function(btn) {
        btn.addEventListener('click', function() {
            const name = btn.dataset.adapter;
            const result = document.getElementById('landing-test-result-' + name);
            result.textContent = 'Тестирую...';
            result.style.color = '#666';
            const fd = new FormData();
            fd.append('action', 'landing_test_adapter');
            fd.append('adapter', name);
            fd.append('_wpnonce', '<?php echo wp_create_nonce('landing_test_adapter'); ?>');
            fetch(ajaxurl, {method: 'POST', body: fd})
                .then(r => r.json())
                .then(d => {
                    result.textContent = (d.ok ? '✅ ' : '❌ ') + d.message;
                    result.style.color = d.ok ? 'green' : 'red';
                })
                .catch(e => {
                    result.textContent = '❌ ' + e.message;
                    result.style.color = 'red';
                });
        });
    });
    </script>
    <?php
}

add_action('wp_ajax_landing_test_adapter', function () {
    if (!current_user_can('manage_options')) { wp_send_json(['ok' => false, 'message' => 'No permissions']); }
    check_admin_referer('landing_test_adapter');

    $name = sanitize_text_field($_POST['adapter'] ?? '');
    foreach (all_adapters() as $cls) {
        if ($cls::name() === $name) {
            $result = (new $cls())->test_connection();
            wp_send_json($result);
        }
    }
    wp_send_json(['ok' => false, 'message' => 'Unknown adapter']);
});

// Dispatch lead to all enabled adapters when a lead is received
add_action('landing_config_lead_received', function ($lead_id, $lead) {
    foreach (all_adapters() as $cls) {
        $name = $cls::name();
        if (!get_option("landing_integration_{$name}_enabled")) continue;

        $instance = new $cls();
        $result = $instance->send($lead);

        global $wpdb;
        $log_table = \LandingConfig\DB\get_lead_log_table_name();
        $wpdb->insert($log_table, [
            'lead_id' => $lead_id,
            'adapter' => $name,
            'attempt' => 1,
            'status' => $result['ok'] ? 'success' : 'failed',
            'response_code' => $result['response_code'],
            'response_body' => mb_substr((string)($result['response_body'] ?? ''), 0, 1000),
            'error_text' => $result['error'],
            'created_at' => current_time('mysql'),
        ]);

        if (!$result['ok']) {
            wp_schedule_single_event(time() + 60, 'landing_retry_adapter', [$lead_id, $name, 2]);
        }
    }
}, 10, 2);

// Retry handler
add_action('landing_retry_adapter', function ($lead_id, $adapter_name, $attempt) {
    if ($attempt > 3) return;

    global $wpdb;
    $leads = \LandingConfig\DB\get_leads_table_name();
    $lead = $wpdb->get_row($wpdb->prepare("SELECT * FROM `$leads` WHERE id = %d", $lead_id), ARRAY_A);
    if (!$lead) return;

    foreach (all_adapters() as $cls) {
        if ($cls::name() !== $adapter_name) continue;
        $result = (new $cls())->send($lead);

        $log_table = \LandingConfig\DB\get_lead_log_table_name();
        $wpdb->insert($log_table, [
            'lead_id' => $lead_id, 'adapter' => $adapter_name, 'attempt' => $attempt,
            'status' => $result['ok'] ? 'success' : 'failed',
            'response_code' => $result['response_code'],
            'response_body' => mb_substr((string)($result['response_body'] ?? ''), 0, 1000),
            'error_text' => $result['error'],
            'created_at' => current_time('mysql'),
        ]);

        if (!$result['ok'] && $attempt < 3) {
            $delays = [2 => 300, 3 => 1800];
            wp_schedule_single_event(time() + $delays[$attempt + 1], 'landing_retry_adapter',
                [$lead_id, $adapter_name, $attempt + 1]);
        }
        return;
    }
}, 10, 3);
