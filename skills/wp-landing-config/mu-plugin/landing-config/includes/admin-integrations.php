<?php
namespace LandingConfig\Admin\Integrations;

if (!defined('ABSPATH')) { exit; }

use function LandingConfig\Integrations\list_integrations;
use function LandingConfig\Integrations\get_integration;
use function LandingConfig\Integrations\save_integration;
use function LandingConfig\Integrations\delete_integration;
use const LandingConfig\Integrations\VALID_ADAPTERS;
use function LandingConfig\AdminMode\cap;
use function LandingConfig\AdminMode\admin_url_for;
use function LandingConfig\AdminMode\menu_hook;
use function LandingConfig\AdminMode\parent_slug;
use function LandingConfig\AdminMode\page_slug;

function adapter_class(string $name): string {
    $map = [
        'email'    => '\\LandingConfig\\Adapters\\EmailAdapter',
        'telegram' => '\\LandingConfig\\Adapters\\TelegramAdapter',
        'whatsapp' => '\\LandingConfig\\Adapters\\WhatsAppAdapter',
        'amocrm'   => '\\LandingConfig\\Adapters\\AmoCRMAdapter',
        'bitrix24' => '\\LandingConfig\\Adapters\\Bitrix24Adapter',
        'hubspot'  => '\\LandingConfig\\Adapters\\HubSpotAdapter',
        'roistat'  => '\\LandingConfig\\Adapters\\RoistatAdapter',
    ];
    return $map[$name] ?? '';
}

function adapter_label(string $type): string {
    $labels = [
        'email'    => 'Email',
        'telegram' => 'Telegram',
        'whatsapp' => 'WhatsApp',
        'amocrm'   => 'AmoCRM',
        'bitrix24' => 'Bitrix24',
        'hubspot'  => 'HubSpot',
        'roistat'  => 'Roistat',
    ];
    return $labels[$type] ?? $type;
}

function mask_secret(string $val): string {
    if ($val === '') return '';
    if (strlen($val) <= 4) return '••••';
    return str_repeat('•', max(0, strlen($val) - 4)) . substr($val, -4);
}

function page_url(array $extra = []): string {
    $base = admin_url_for('admin.php?page=' . page_slug('integrations'));
    foreach ($extra as $k => $v) $base .= '&' . urlencode($k) . '=' . urlencode((string) $v);
    return $base;
}

\add_action(menu_hook(), function () {
    \add_submenu_page(
        parent_slug(),
        'Интеграции',
        'Интеграции',
        cap(),
        page_slug('integrations'),
        __NAMESPACE__ . '\\dispatch'
    );
});

\add_action('admin_post_landing_int_save',   __NAMESPACE__ . '\\handle_save');
\add_action('admin_post_landing_int_delete', __NAMESPACE__ . '\\handle_delete');
\add_action('wp_ajax_landing_int_test',      __NAMESPACE__ . '\\handle_test_ajax');

function dispatch(): void {
    if (!\current_user_can(cap())) { \wp_die('No.', 403); }

    $action = \sanitize_text_field($_GET['int_action'] ?? '');

    if ($action === 'edit' || $action === 'new') {
        render_edit_page($action);
    } else {
        render_list_page();
    }
}

function render_list_page(): void {
    $blog_id = \get_current_blog_id();
    $integrations = list_integrations($blog_id);
    $saved = !empty($_GET['saved']);
    $deleted = !empty($_GET['deleted']);
    ?>
    <div class="wrap">
        <h1 class="wp-heading-inline">Интеграции</h1>
        <a href="<?php echo \esc_url(page_url(['int_action' => 'new'])); ?>" class="page-title-action">Добавить</a>
        <hr class="wp-header-end">

        <?php if ($saved): ?>
            <div class="notice notice-success is-dismissible"><p>Интеграция сохранена.</p></div>
        <?php endif; ?>
        <?php if ($deleted): ?>
            <div class="notice notice-success is-dismissible"><p>Интеграция удалена.</p></div>
        <?php endif; ?>

        <?php if (empty($integrations)): ?>
            <div class="notice notice-info"><p>Нет настроенных интеграций. <a href="<?php echo \esc_url(page_url(['int_action' => 'new'])); ?>">Добавить первую</a></p></div>
        <?php else: ?>
        <table class="wp-list-table widefat fixed striped" style="margin-top:16px;">
            <thead>
                <tr>
                    <th style="width:30%">Название</th>
                    <th style="width:15%">Тип</th>
                    <th style="width:30%">Основные настройки</th>
                    <th style="width:10%">Статус</th>
                    <th style="width:15%">Действия</th>
                </tr>
            </thead>
            <tbody>
                <?php foreach ($integrations as $integration):
                    $cls  = adapter_class($integration['adapter_type']);
                    $defs = $cls ? $cls::field_definitions() : [];
                    $edit_url   = page_url(['int_action' => 'edit', 'int_id' => $integration['id']]);
                    $delete_url = \wp_nonce_url(
                        admin_url_for('admin-post.php?action=landing_int_delete&int_id=' . $integration['id']),
                        'landing_int_delete_' . $integration['id']
                    );
                ?>
                <tr>
                    <td>
                        <strong><a href="<?php echo \esc_url($edit_url); ?>"><?php echo \esc_html($integration['label']); ?></a></strong>
                        <?php if ($integration['description'] !== ''): ?>
                            <br><span style="color:#646970;font-size:12px;"><?php echo \esc_html($integration['description']); ?></span>
                        <?php endif; ?>
                    </td>
                    <td><span style="background:#f0f0f1;padding:2px 8px;border-radius:3px;font-size:12px;"><?php echo \esc_html(adapter_label($integration['adapter_type'])); ?></span></td>
                    <td style="color:#646970;font-size:12px;">
                        <?php
                        $shown = 0;
                        foreach ($defs as $field => $meta) {
                            $val = $integration['settings'][$field] ?? '';
                            if ($val === '') continue;
                            $display = !empty($meta['encrypt']) ? mask_secret((string) $val) : \esc_html(mb_strimwidth((string) $val, 0, 40, '…'));
                            echo '<div><strong>' . \esc_html($meta['label'] ?? $field) . ':</strong> ' . $display . '</div>';
                            if (++$shown >= 2) break;
                        }
                        if ($shown === 0) echo '<em>— нет данных —</em>';
                        ?>
                    </td>
                    <td>
                        <?php if ($integration['enabled']): ?>
                            <span style="color:#00a32a;font-weight:600;">Активна</span>
                        <?php else: ?>
                            <span style="color:#d63638;font-weight:600;">Выключена</span>
                        <?php endif; ?>
                    </td>
                    <td>
                        <a href="<?php echo \esc_url($edit_url); ?>">Изменить</a>
                        &nbsp;|&nbsp;
                        <button type="button"
                            class="button-link lp-test-btn"
                            data-id="<?php echo (int) $integration['id']; ?>"
                            data-nonce="<?php echo \esc_attr(\wp_create_nonce('landing_int_test_' . $integration['id'])); ?>"
                            style="color:#2271b1;cursor:pointer;">Тест</button>
                        &nbsp;|&nbsp;
                        <a href="<?php echo \esc_url($delete_url); ?>"
                           style="color:#b32d2e;"
                           onclick="return confirm('Удалить эту интеграцию?');">Удалить</a>
                    </td>
                </tr>
                <?php endforeach; ?>
            </tbody>
        </table>
        <?php endif; ?>
    </div>

    <script>
    document.querySelectorAll('.lp-test-btn').forEach(function(btn) {
        btn.addEventListener('click', function() {
            var id    = btn.dataset.id;
            var nonce = btn.dataset.nonce;
            btn.textContent = 'Проверяю…';
            btn.disabled = true;
            fetch(ajaxurl, {
                method: 'POST',
                headers: {'Content-Type': 'application/x-www-form-urlencoded'},
                body: 'action=landing_int_test&int_id=' + encodeURIComponent(id) + '&_ajax_nonce=' + encodeURIComponent(nonce)
            })
            .then(function(r) { return r.json(); })
            .then(function(data) {
                btn.disabled = false;
                btn.textContent = 'Тест';
                alert(data.data ? data.data.message : 'Ошибка запроса');
            })
            .catch(function() {
                btn.disabled = false;
                btn.textContent = 'Тест';
                alert('Ошибка сети');
            });
        });
    });
    </script>
    <?php
}

function render_edit_page(string $mode): void {
    $int_id = (int) ($_GET['int_id'] ?? 0);
    $existing = ($mode === 'edit' && $int_id > 0) ? get_integration($int_id) : null;

    $adapter_type = \sanitize_text_field($_GET['adapter_type'] ?? ($existing['adapter_type'] ?? ''));
    if ($adapter_type === '' && $mode === 'new' && isset($_GET['adapter_type'])) {
        $adapter_type = \sanitize_text_field($_GET['adapter_type']);
    }

    $title = $mode === 'edit' ? 'Изменить интеграцию' : 'Добавить интеграцию';
    ?>
    <div class="wrap">
        <h1><?php echo \esc_html($title); ?></h1>
        <a href="<?php echo \esc_url(page_url()); ?>">← Все интеграции</a>
        <hr class="wp-header-end" style="margin-top:8px;">

        <?php if ($mode === 'new' && $adapter_type === ''): ?>
            <p style="margin-top:16px;"><strong>Выберите тип интеграции:</strong></p>
            <div style="display:flex;flex-wrap:wrap;gap:12px;margin-top:8px;">
                <?php foreach (VALID_ADAPTERS as $type): ?>
                    <a href="<?php echo \esc_url(page_url(['int_action' => 'new', 'adapter_type' => $type])); ?>"
                       style="background:#fff;border:1px solid #c3c4c7;padding:12px 20px;border-radius:4px;text-decoration:none;color:#1d2327;font-weight:600;">
                        <?php echo \esc_html(adapter_label($type)); ?>
                    </a>
                <?php endforeach; ?>
            </div>
        <?php else:
            if ($adapter_type === '') $adapter_type = 'telegram';
            $cls  = adapter_class($adapter_type);
            $defs = $cls ? $cls::field_definitions() : [];
            $current_settings = $existing ? $existing['settings'] : [];
            $current_label    = $existing ? $existing['label'] : '';
            $current_desc     = $existing ? $existing['description'] : '';
            $current_enabled  = $existing ? $existing['enabled'] : true;
            $encrypted_fields = [];
            foreach ($defs as $f => $m) if (!empty($m['encrypt'])) $encrypted_fields[] = $f;
        ?>
            <form method="post" action="<?php echo \esc_url(admin_url_for('admin-post.php')); ?>" style="margin-top:16px;max-width:600px;">
                <?php \wp_nonce_field('landing_int_save'); ?>
                <input type="hidden" name="action" value="landing_int_save">
                <input type="hidden" name="adapter_type" value="<?php echo \esc_attr($adapter_type); ?>">
                <input type="hidden" name="int_id" value="<?php echo $int_id; ?>">

                <table class="form-table">
                    <tr>
                        <th><label for="lp_int_label">Название <span style="color:#d63638">*</span></label></th>
                        <td>
                            <input type="text" id="lp_int_label" name="int_label"
                                   value="<?php echo \esc_attr($current_label); ?>"
                                   placeholder="Например: Менеджер Али"
                                   class="regular-text" required>
                            <p class="description">Отображается в таблице. Поможет отличить несколько интеграций одного типа.</p>
                        </td>
                    </tr>
                    <tr>
                        <th><label for="lp_int_desc">Описание</label></th>
                        <td>
                            <input type="text" id="lp_int_desc" name="int_description"
                                   value="<?php echo \esc_attr($current_desc); ?>"
                                   placeholder="Необязательно — для других пользователей"
                                   class="regular-text">
                        </td>
                    </tr>
                    <tr>
                        <th>Тип</th>
                        <td>
                            <span style="background:#f0f0f1;padding:3px 10px;border-radius:3px;font-size:13px;">
                                <?php echo \esc_html(adapter_label($adapter_type)); ?>
                            </span>
                        </td>
                    </tr>
                    <?php foreach ($defs as $field => $meta):
                        $val = $current_settings[$field] ?? '';
                        $input_type = $meta['type'] ?? 'text';
                        if ($input_type === 'password') $input_type = 'text';
                        if (!empty($meta['encrypt']) && $val !== '') {
                            $placeholder  = '(сохранено: ' . mask_secret((string) $val) . ' — оставьте пустым, чтобы не менять)';
                            $val_for_form = '';
                        } else {
                            $placeholder  = $meta['placeholder'] ?? '';
                            $val_for_form = $val;
                        }
                    ?>
                        <tr>
                            <th><label><?php echo \esc_html($meta['label'] ?? $field); ?><?php if (!empty($meta['required'])): ?> <span style="color:#d63638">*</span><?php endif; ?></label></th>
                            <td>
                                <input type="<?php echo \esc_attr($input_type); ?>"
                                       name="field[<?php echo \esc_attr($field); ?>]"
                                       value="<?php echo \esc_attr((string) $val_for_form); ?>"
                                       placeholder="<?php echo \esc_attr($placeholder); ?>"
                                       class="regular-text"
                                       <?php if (!empty($meta['required']) && $val === '') echo 'required'; ?>>
                            </td>
                        </tr>
                    <?php endforeach; ?>
                    <tr>
                        <th>Состояние</th>
                        <td>
                            <label>
                                <input type="checkbox" name="int_enabled" value="1" <?php \checked($current_enabled); ?>>
                                Активна (заявки будут отправляться)
                            </label>
                        </td>
                    </tr>
                </table>
                <p>
                    <button type="submit" class="button button-primary">Сохранить</button>
                    <a href="<?php echo \esc_url(page_url()); ?>" class="button" style="margin-left:8px;">Отмена</a>
                    <?php if ($int_id > 0): ?>
                        <button type="button"
                            class="button lp-test-btn-form"
                            data-id="<?php echo $int_id; ?>"
                            data-nonce="<?php echo \esc_attr(\wp_create_nonce('landing_int_test_' . $int_id)); ?>"
                            style="margin-left:16px;">Проверить соединение</button>
                        <span id="lp-test-result" style="margin-left:8px;"></span>
                    <?php endif; ?>
                </p>
            </form>
            <?php if ($int_id > 0): ?>
            <script>
            document.querySelector('.lp-test-btn-form')?.addEventListener('click', function(btn) {
                var el    = this;
                var id    = el.dataset.id;
                var nonce = el.dataset.nonce;
                var result = document.getElementById('lp-test-result');
                el.disabled = true;
                el.textContent = 'Проверяю…';
                fetch(ajaxurl, {
                    method: 'POST',
                    headers: {'Content-Type': 'application/x-www-form-urlencoded'},
                    body: 'action=landing_int_test&int_id=' + encodeURIComponent(id) + '&_ajax_nonce=' + encodeURIComponent(nonce)
                })
                .then(function(r) { return r.json(); })
                .then(function(data) {
                    el.disabled = false;
                    el.textContent = 'Проверить соединение';
                    var msg = data.data ? data.data.message : 'Ошибка запроса';
                    var ok  = data.success && data.data && data.data.ok;
                    result.innerHTML = '<span style="color:' + (ok ? '#00a32a' : '#d63638') + ';font-weight:600;">' +
                        (ok ? '✓ ' : '✗ ') + msg.replace(/</g,'&lt;') + '</span>';
                })
                .catch(function() {
                    el.disabled = false;
                    el.textContent = 'Проверить соединение';
                    result.textContent = 'Ошибка сети';
                });
            });
            </script>
            <?php endif; ?>
        <?php endif; ?>
    </div>
    <?php
}

function handle_save(): void {
    if (!\current_user_can(cap())) { \wp_die('No.', 403); }
    \check_admin_referer('landing_int_save');

    $adapter_type = \sanitize_text_field($_POST['adapter_type'] ?? '');
    if (!in_array($adapter_type, VALID_ADAPTERS, true)) \wp_die('Invalid adapter type', 400);

    $int_id      = (int) ($_POST['int_id'] ?? 0);
    $label       = \sanitize_text_field($_POST['int_label'] ?? '');
    $description = \sanitize_text_field($_POST['int_description'] ?? '');
    $enabled     = !empty($_POST['int_enabled']);
    $blog_id     = \get_current_blog_id();

    if ($label === '') \wp_die('Название обязательно', 400);

    $cls  = adapter_class($adapter_type);
    $defs = $cls ? $cls::field_definitions() : [];
    $encrypted_fields = [];
    foreach ($defs as $f => $m) if (!empty($m['encrypt'])) $encrypted_fields[] = $f;

    $existing_settings = [];
    if ($int_id > 0) {
        $existing = get_integration($int_id);
        if ($existing) $existing_settings = $existing['settings'];
    }

    $new_settings = [];
    foreach ($defs as $field => $meta) {
        $input = (string) ($_POST['field'][$field] ?? '');
        if (!empty($meta['encrypt']) && $input === '' && isset($existing_settings[$field])) {
            $new_settings[$field] = $existing_settings[$field];
        } else {
            $new_settings[$field] = \sanitize_text_field($input);
        }
    }

    $saved_id = save_integration(
        $adapter_type,
        $label,
        $description,
        $new_settings,
        false,
        $blog_id,
        $encrypted_fields,
        $enabled,
        $int_id
    );

    if (!$saved_id) \wp_die('Ошибка сохранения', 500);

    \wp_safe_redirect(page_url(['saved' => '1']));
    exit;
}

function handle_delete(): void {
    if (!\current_user_can(cap())) { \wp_die('No.', 403); }
    $int_id = (int) ($_GET['int_id'] ?? 0);
    if (!$int_id) \wp_die('Invalid', 400);
    \check_admin_referer('landing_int_delete_' . $int_id);

    delete_integration($int_id);

    \wp_safe_redirect(page_url(['deleted' => '1']));
    exit;
}

function handle_test_ajax(): void {
    $int_id = (int) ($_POST['int_id'] ?? 0);
    \check_ajax_referer('landing_int_test_' . $int_id);
    if (!\current_user_can(cap())) \wp_send_json_error(['message' => 'Нет доступа']);

    $integration = get_integration($int_id);
    if (!$integration) \wp_send_json_error(['message' => 'Интеграция не найдена']);

    $cls = adapter_class($integration['adapter_type']);
    if (!$cls) \wp_send_json_error(['message' => 'Неизвестный тип адаптера']);

    $adapter = new $cls();
    $result  = $adapter->test_connection();

    if ($result['ok'] ?? false) {
        \wp_send_json_success(['ok' => true, 'message' => $result['message'] ?? 'OK']);
    } else {
        \wp_send_json_success(['ok' => false, 'message' => $result['message'] ?? 'Ошибка соединения']);
    }
}
