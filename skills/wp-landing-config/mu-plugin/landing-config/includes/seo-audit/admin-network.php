<?php
namespace LandingConfig\SEOAudit\Admin;

if (!defined('ABSPATH')) { exit; }

use function LandingConfig\SEOAudit\Runner\run_audit_for_urls;
use function LandingConfig\SEOAudit\Runner\cache_key;
use function LandingConfig\SEOAudit\Runner\aggregate_cache_key;
use function LandingConfig\SEOAudit\Runner\timestamp_key;

const MENU_SLUG    = 'landing-config-seo-audit';
const VALID_TABS   = ['overview', 'html', 'network', 'schema', 'ai_readiness'];

add_action('network_admin_menu', __NAMESPACE__ . '\\register_menu');
add_action('admin_post_lp_seo_audit_run', __NAMESPACE__ . '\\handle_run');
add_action('admin_enqueue_scripts', __NAMESPACE__ . '\\enqueue_assets');

function register_menu(): void {
    \add_submenu_page(
        'landing-config-network',
        'Аудит',
        'Аудит',
        'manage_network_options',
        MENU_SLUG,
        __NAMESPACE__ . '\\render_page'
    );
}

function enqueue_assets($hook): void {
    $page = isset($_GET['page']) ? (string) $_GET['page'] : '';
    if (strpos((string) $hook, MENU_SLUG) === false && $page !== MENU_SLUG) return;
    $url = \plugins_url('assets/seo-audit/admin.css',
                        dirname(dirname(__DIR__)) . '/landing-config.php');
    \wp_enqueue_style('lp-seo-audit-admin', $url, [], '1.0');
}

/** Multisite host list (https://<host>) for all blogs in the network. */
function get_all_hosts(): array {
    $hosts = [];
    foreach (\get_sites(['fields' => 'ids']) as $bid) {
        $url = \get_site_url((int) $bid);
        if ($url) $hosts[] = rtrim($url, '/') . '/';
    }
    return $hosts;
}

function handle_run(): void {
    if (!\current_user_can('manage_network_options')) wp_die('forbidden');
    \check_admin_referer('lp_seo_audit_run');

    $segment = isset($_POST['segment']) ? (string) $_POST['segment'] : '0';

    if ($segment === 'all') {
        $hosts = get_all_hosts();
        $res = run_audit_for_urls($hosts);
        if ($res['ok']) {
            \update_site_option(aggregate_cache_key(), \wp_json_encode($res['data'], JSON_UNESCAPED_UNICODE));
            \update_site_option(timestamp_key(0) . '_aggregate', time());
            // Also save per-site reports from aggregate.sites
            foreach (($res['data']['sites'] ?? []) as $site) {
                $host = $site['host'] ?? '';
                $blog_id = host_to_blog_id($host);
                if ($blog_id !== null) {
                    \update_site_option(cache_key($blog_id), \wp_json_encode($site, JSON_UNESCAPED_UNICODE));
                    \update_site_option(timestamp_key($blog_id), time());
                }
            }
        }
        $redirect_segment = 'all';
    } else {
        $blog_id = (int) $segment;
        $url = \get_site_url($blog_id);
        if (!$url) { wp_die('invalid segment'); }
        $url = rtrim($url, '/') . '/';
        $res = run_audit_for_urls([$url]);
        if ($res['ok']) {
            $site = $res['data']['sites'][0] ?? null;
            if ($site) {
                \update_site_option(cache_key($blog_id), \wp_json_encode($site, JSON_UNESCAPED_UNICODE));
                \update_site_option(timestamp_key($blog_id), time());
            }
        }
        $redirect_segment = (string) $blog_id;
    }

    $tab = isset($_POST['tab']) && in_array($_POST['tab'], VALID_TABS, true) ? $_POST['tab'] : 'overview';
    $args = [
        'page' => MENU_SLUG,
        'tab' => $tab,
        'segment' => $redirect_segment,
        'audited' => $res['ok'] ? 1 : 0,
    ];
    if (!$res['ok']) {
        $args['error'] = urlencode($res['error'] ?? 'unknown');
    }
    \wp_safe_redirect(\add_query_arg($args, \network_admin_url('admin.php')));
    exit;
}

function host_to_blog_id(string $url): ?int {
    $host = parse_url($url, PHP_URL_HOST);
    if (!$host) return null;
    foreach (\get_sites(['fields' => 'ids']) as $bid) {
        $site_host = parse_url(\get_site_url((int) $bid), PHP_URL_HOST);
        if ($site_host === $host) return (int) $bid;
    }
    return null;
}

function load_cached_report(string $segment): ?array {
    if ($segment === 'all') {
        $raw = \get_site_option(aggregate_cache_key());
    } else {
        $raw = \get_site_option(cache_key((int) $segment));
    }
    if (!$raw) return null;
    $data = json_decode($raw, true);
    return is_array($data) ? $data : null;
}

function load_timestamp(string $segment): int {
    if ($segment === 'all') {
        return (int) \get_site_option(timestamp_key(0) . '_aggregate', 0);
    }
    return (int) \get_site_option(timestamp_key((int) $segment), 0);
}

function render_segment_selector(string $current, string $tab): void {
    ?>
    <select onchange="window.location.href='<?php echo esc_js(\network_admin_url('admin.php?page=' . MENU_SLUG . '&tab=' . $tab)); ?>&segment=' + this.value">
        <option value="all" <?php selected($current, 'all'); ?>>Все сегменты (multisite)</option>
        <option value="0" <?php selected($current, '0'); ?>>Network default (root)</option>
        <?php foreach (\get_sites(['fields' => 'ids']) as $bid):
            $url = \get_site_url((int) $bid);
            $val = (string) (int) $bid; ?>
            <option value="<?php echo esc_attr($val); ?>" <?php selected($current, $val); ?>>
                blog #<?php echo (int) $bid; ?> — <?php echo esc_html((string) $url); ?>
            </option>
        <?php endforeach; ?>
    </select>
    <?php
}

function render_page(): void {
    if (!\current_user_can('manage_network_options')) wp_die('forbidden');
    $tab = isset($_GET['tab']) && in_array($_GET['tab'], VALID_TABS, true) ? $_GET['tab'] : 'overview';
    $segment = isset($_GET['segment']) ? (string) $_GET['segment'] : 'all';

    ?>
    <div class="wrap">
        <h1>SEO Аудит</h1>

        <?php if (!empty($_GET['audited'])): ?>
            <div class="notice notice-success is-dismissible"><p>Аудит выполнен.</p></div>
        <?php endif; ?>
        <?php if (!empty($_GET['error'])): ?>
            <div class="notice notice-error is-dismissible">
                <p>Ошибка: <?php echo esc_html(urldecode((string) $_GET['error'])); ?></p>
            </div>
        <?php endif; ?>

        <div class="lp-audit-header">
            <div class="lp-audit-header__segment-selector">
                <label>Сегмент: </label>
                <?php render_segment_selector($segment, $tab); ?>
            </div>
            <div class="lp-audit-header__last-run">
                <?php $ts = load_timestamp($segment);
                if ($ts > 0):
                    $diff = human_time_diff($ts, time()); ?>
                    Последний прогон: <?php echo esc_html($diff); ?> назад
                <?php else: ?>
                    Аудит ещё не запускался
                <?php endif; ?>
            </div>
            <form method="post" action="<?php echo esc_url(\admin_url('admin-post.php')); ?>" style="margin:0;">
                <?php \wp_nonce_field('lp_seo_audit_run'); ?>
                <input type="hidden" name="action" value="lp_seo_audit_run">
                <input type="hidden" name="segment" value="<?php echo esc_attr($segment); ?>">
                <input type="hidden" name="tab" value="<?php echo esc_attr($tab); ?>">
                <button type="submit" class="button button-primary lp-audit-header__btn">
                    <?php echo $segment === 'all' ? 'Запустить для всех сегментов' : 'Запустить для этого сегмента'; ?>
                </button>
            </form>
        </div>

        <div class="lp-audit-tabs">
            <?php
            $tabs = [
                'overview' => 'Обзор',
                'html' => 'HTML / On-page',
                'network' => 'Network / Robots / Sitemap',
                'schema' => 'Schema / Open Graph',
                'ai_readiness' => 'AI readiness',
            ];
            foreach ($tabs as $key => $label):
                $url = \add_query_arg([
                    'page' => MENU_SLUG, 'tab' => $key, 'segment' => $segment,
                ], \network_admin_url('admin.php'));
                $class = $key === $tab ? 'is-active' : ''; ?>
                <a href="<?php echo esc_url($url); ?>" class="<?php echo esc_attr($class); ?>">
                    <?php echo esc_html($label); ?>
                </a>
            <?php endforeach; ?>
        </div>

        <?php
        $tab_file = __DIR__ . '/tabs/' . $tab . '.php';
        if (file_exists($tab_file)) {
            $report = load_cached_report($segment);
            include $tab_file;
        } else {
            echo '<div class="lp-audit-empty">Tab template missing: ' . esc_html($tab) . '</div>';
        }
        ?>
    </div>
    <?php
}
