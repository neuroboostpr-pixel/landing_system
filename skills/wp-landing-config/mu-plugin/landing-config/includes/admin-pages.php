<?php
namespace LandingConfig\Admin;

if (!defined('ABSPATH')) { exit; }

const CAP_MANAGE = 'manage_options';
const MENU_SLUG = 'landing-config';

add_action('admin_menu', function () {
    add_menu_page(
        'Лендинг',
        'Лендинг',
        CAP_MANAGE,
        MENU_SLUG,
        __NAMESPACE__ . '\\render_dashboard',
        'dashicons-megaphone',
        58
    );

    // Sub-pages (Заявки / CTA / Head&SEO / Интеграции) регистрируются
    // каждым admin-*.php самостоятельно через add_submenu_page с реальным
    // callback. Stub'ы с '__return_null' вызывали пустые страницы, потому что
    // patch $submenu[slug][N][3] в дочерних файлах меняет TITLE, а не callback.
});

add_action('network_admin_menu', function () {
    add_menu_page(
        'Лендинг (сеть)',
        'Лендинг',
        'manage_network_options',
        MENU_SLUG . '-network',
        __NAMESPACE__ . '\\render_network_dashboard',
        'dashicons-megaphone',
        25
    );
});

function render_dashboard(): void {
    ?>
    <div class="wrap">
        <h1>Лендинг — настройки</h1>
        <p>Выберите раздел в левом меню:</p>
        <ul>
            <li><strong>Заявки</strong> — список полученных заявок, экспорт CSV</li>
            <li><strong>CTA-кнопки</strong> — настройка 5 пресетов кнопок</li>
            <li><strong>Head &amp; SEO</strong> — счётчики, мета-теги, верификации</li>
            <li><strong>Интеграции</strong> — подключение CRM, Telegram, WhatsApp</li>
        </ul>
        <p><em>Версия: <?php echo esc_html(LANDING_CONFIG_VERSION); ?></em></p>
    </div>
    <?php
}

function render_network_dashboard(): void {
    ?>
    <div class="wrap">
        <h1>Лендинг — сетевые настройки</h1>
        <p>Здесь настраиваются дефолты, применяемые ко всем сегментам сети.
        Каждый сегмент может переопределить их в своей админке.</p>
    </div>
    <?php
}
