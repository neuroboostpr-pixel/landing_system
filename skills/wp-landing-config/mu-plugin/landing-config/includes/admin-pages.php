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
            <li><strong>Снипеты</strong> — счётчики, мета-теги, виджеты, любой HTML в head/body/footer</li>
            <li><strong>Интеграции</strong> — подключение CRM, Telegram, WhatsApp</li>
        </ul>
        <p><em>Версия: <?php echo esc_html(LANDING_CONFIG_VERSION); ?></em></p>
    </div>
    <?php
}

function render_network_dashboard(): void {
    $sites = \function_exists('get_sites') ? \get_sites(['number' => 0]) : [];
    $network_snippets = \LandingConfig\Snippets\list_network_snippets();
    $network_snip_count = count($network_snippets);

    // Per-site counters: leads + site snippets. switch_to_blog inside a loop
    // is cheap on shared hosting (≤10 subsites typical).
    $site_stats = [];
    foreach ($sites as $site) {
        $bid = (int) $site->blog_id;
        \switch_to_blog($bid);
        try {
            global $wpdb;
            $leads_table = \LandingConfig\DB\get_leads_table_name();
            // Table may not exist yet on a freshly-created subsite — guard.
            $leads_count = (int) $wpdb->get_var("SELECT COUNT(*) FROM `$leads_table`");
            $pending_count = (int) $wpdb->get_var(
                "SELECT COUNT(*) FROM `$leads_table` WHERE processed_status = 'pending'"
            );
            $site_snip_count = count(\LandingConfig\Snippets\list_site_snippets());
        } catch (\Throwable $e) {
            $leads_count = 0;
            $pending_count = 0;
            $site_snip_count = 0;
        } finally {
            \restore_current_blog();
        }
        $site_stats[$bid] = [
            'host'        => $site->domain . rtrim($site->path, '/'),
            'leads'       => $leads_count,
            'pending'     => $pending_count,
            'snippets'    => $site_snip_count,
            'admin_url'   => \get_admin_url($bid, 'admin.php?page=landing-config'),
            'leads_url'   => \get_admin_url($bid, 'admin.php?page=landing-config-leads'),
            'snippets_url'=> \get_admin_url($bid, 'admin.php?page=landing-config-snippets'),
            'is_main'     => $bid === \get_main_site_id(),
        ];
    }

    $net_leads_url    = \network_admin_url('admin.php?page=landing-config-network-leads');
    $net_snippets_url = \network_admin_url('admin.php?page=landing-config-network-snippets');
    ?>
    <div class="wrap">
        <h1>Лендинг — сетевые настройки</h1>
        <p>Управляйте всеми сегментами сети из одной точки. Ниже карточки сегментов
        со счётчиками заявок и снипетов. Сетевые настройки распространяются на все
        сегменты, локальные настройки сегмента их перекрывают.</p>

        <h2 style="margin-top:2em;">Сетевые ресурсы</h2>
        <div style="display:flex; gap:1em; flex-wrap:wrap; margin-bottom:2em;">
            <a href="<?php echo \esc_url($net_leads_url); ?>" class="button button-secondary" style="padding:1em 1.5em; height:auto;">
                <strong>Заявки (все сегменты)</strong><br>
                <span style="color:#666;">Свод заявок по сети</span>
            </a>
            <a href="<?php echo \esc_url($net_snippets_url); ?>" class="button button-secondary" style="padding:1em 1.5em; height:auto;">
                <strong>Снипеты сети</strong><br>
                <span style="color:#666;"><?php echo (int) $network_snip_count; ?> network snippets</span>
            </a>
        </div>

        <h2>Сегменты сети (<?php echo count($sites); ?>)</h2>
        <?php if (empty($sites)): ?>
            <p><em>В сети пока нет сегментов. Создайте первый через
                <code>/landing-segment &lt;slug&gt;</code>.</em></p>
        <?php else: ?>
            <div style="display:grid; grid-template-columns:repeat(auto-fill, minmax(320px, 1fr)); gap:1em;">
                <?php foreach ($site_stats as $bid => $s): ?>
                    <div style="border:1px solid #ccd0d4; background:#fff; padding:1em; border-radius:4px;">
                        <h3 style="margin-top:0;">
                            <a href="<?php echo \esc_url($s['admin_url']); ?>">
                                <?php echo \esc_html($s['host']); ?>
                            </a>
                            <?php if ($s['is_main']): ?>
                                <span class="dashicons dashicons-star-filled" title="Главный сайт сети" style="color:#f0b849;"></span>
                            <?php endif; ?>
                        </h3>
                        <p style="color:#666; font-size:12px; margin:0 0 .8em;">blog_id=<?php echo (int) $bid; ?></p>
                        <ul style="margin:0; list-style:none; padding:0;">
                            <li style="margin:.3em 0;">
                                <strong><?php echo (int) $s['leads']; ?></strong> заявок
                                <?php if ($s['pending'] > 0): ?>
                                    (<span style="color:#d63638;"><?php echo (int) $s['pending']; ?> новых</span>)
                                <?php endif; ?>
                                — <a href="<?php echo \esc_url($s['leads_url']); ?>">открыть</a>
                            </li>
                            <li style="margin:.3em 0;">
                                <strong><?php echo (int) $s['snippets']; ?></strong> site-снипетов
                                — <a href="<?php echo \esc_url($s['snippets_url']); ?>">открыть</a>
                            </li>
                        </ul>
                    </div>
                <?php endforeach; ?>
            </div>
        <?php endif; ?>
        <p style="margin-top:2em; color:#666;"><em>Версия mu-plugin: <?php echo \esc_html(LANDING_CONFIG_VERSION); ?></em></p>
    </div>
    <?php
}
