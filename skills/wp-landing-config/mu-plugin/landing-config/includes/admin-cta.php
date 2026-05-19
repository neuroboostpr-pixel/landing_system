<?php
namespace LandingConfig\Admin\CTA;

if (!defined('ABSPATH')) { exit; }

const PRESET_NAMES = ['primary', 'whatsapp', 'phone', 'form_modal', 'learn_more'];

add_action('admin_menu', function () {
    global $submenu;
    if (isset($submenu['landing-config'])) {
        foreach ($submenu['landing-config'] as &$item) {
            if ($item[2] === 'landing-config-cta') {
                $item[3] = __NAMESPACE__ . '\\render_page';
            }
        }
    }
}, 99);

add_action('admin_init', function () {
    register_setting('landing_cta', 'landing_cta_presets', [
        'type' => 'array',
        'sanitize_callback' => __NAMESPACE__ . '\\sanitize_presets',
        'default' => default_presets(),
    ]);
});

function default_presets(): array {
    return [
        'primary'    => ['type' => 'scroll', 'target' => '#contact-form', 'label' => 'Оставить заявку'],
        'whatsapp'   => ['type' => 'whatsapp', 'phone' => '', 'message_template' => 'Здравствуйте! Интересует {block_context}', 'label' => 'Написать в WhatsApp'],
        'phone'      => ['type' => 'tel', 'phone' => '', 'label' => 'Позвонить'],
        'form_modal' => ['type' => 'modal', 'form_id' => 'main', 'label' => 'Получить предложение'],
        'learn_more' => ['type' => 'anchor', 'target' => '', 'label' => 'Подробнее'],
    ];
}

function sanitize_presets($input): array {
    if (!is_array($input)) return default_presets();
    $clean = [];
    foreach (PRESET_NAMES as $name) {
        $p = $input[$name] ?? [];
        $clean[$name] = [
            'type'    => sanitize_text_field($p['type'] ?? 'scroll'),
            'target'  => sanitize_text_field($p['target'] ?? ''),
            'phone'   => sanitize_text_field($p['phone'] ?? ''),
            'form_id' => sanitize_text_field($p['form_id'] ?? ''),
            'message_template' => sanitize_text_field($p['message_template'] ?? ''),
            'label'   => sanitize_text_field($p['label'] ?? ''),
        ];
    }
    return $clean;
}

function render_page(): void {
    if (!current_user_can('manage_options')) { wp_die('Insufficient permissions'); }
    $presets = get_option('landing_cta_presets', default_presets());
    ?>
    <div class="wrap">
        <h1>CTA-кнопки</h1>
        <p>Настройте 5 пресетов кнопок. Темы обращаются к ним через <code>landing_get_cta('preset_name')</code>.
        При смене значения здесь — обновятся все кнопки на сайте.</p>
        <form method="post" action="options.php">
            <?php settings_fields('landing_cta'); ?>
            <?php foreach (PRESET_NAMES as $name): $p = $presets[$name]; ?>
                <h2><?php echo esc_html($name); ?></h2>
                <table class="form-table">
                    <tr>
                        <th>Тип</th>
                        <td><select name="landing_cta_presets[<?php echo $name; ?>][type]">
                            <?php foreach (['scroll','whatsapp','tel','mailto','modal','anchor','url'] as $t): ?>
                                <option value="<?php echo $t; ?>" <?php selected($p['type'], $t); ?>><?php echo $t; ?></option>
                            <?php endforeach; ?>
                        </select></td>
                    </tr>
                    <tr><th>Label по умолчанию</th>
                        <td><input type="text" name="landing_cta_presets[<?php echo $name; ?>][label]" value="<?php echo esc_attr($p['label'] ?? ''); ?>" class="regular-text"></td>
                    </tr>
                    <tr><th>Target / URL / Phone</th>
                        <td>
                            <input type="text" name="landing_cta_presets[<?php echo $name; ?>][target]" value="<?php echo esc_attr($p['target'] ?? ''); ?>" placeholder="#contact-form, https://...">
                            <input type="text" name="landing_cta_presets[<?php echo $name; ?>][phone]" value="<?php echo esc_attr($p['phone'] ?? ''); ?>" placeholder="+71234567890 (для tel/whatsapp)">
                            <input type="text" name="landing_cta_presets[<?php echo $name; ?>][form_id]" value="<?php echo esc_attr($p['form_id'] ?? ''); ?>" placeholder="main (для modal)">
                        </td>
                    </tr>
                    <tr><th>Шаблон сообщения (WhatsApp)</th>
                        <td><input type="text" name="landing_cta_presets[<?php echo $name; ?>][message_template]" value="<?php echo esc_attr($p['message_template'] ?? ''); ?>" class="large-text" placeholder="Здравствуйте! Интересует {model}"></td>
                    </tr>
                </table>
            <?php endforeach; ?>
            <?php submit_button(); ?>
        </form>
    </div>
    <?php
}
