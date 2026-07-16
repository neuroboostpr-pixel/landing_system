<?php
/**
 * Plugin Name: Landing Config
 * Description: Admin UI for CRM, CTA, head/SEO, and lead capture. Multisite-aware.
 * Version: 0.1.0
 * Author: landing-system
 * Network: true
 */

if (!defined('ABSPATH')) { exit; }

define('LANDING_CONFIG_VERSION', '0.1.0');
define('LANDING_CONFIG_DIR', __DIR__);
define('LANDING_CONFIG_URL', plugins_url('', __FILE__));

require_once LANDING_CONFIG_DIR . '/includes/admin-mode.php';
require_once LANDING_CONFIG_DIR . '/includes/db.php';
require_once LANDING_CONFIG_DIR . '/includes/encryption.php';
require_once LANDING_CONFIG_DIR . '/includes/helpers.php';
require_once LANDING_CONFIG_DIR . '/includes/cascade.php';
require_once LANDING_CONFIG_DIR . '/includes/cta.php';
require_once LANDING_CONFIG_DIR . '/includes/integrations.php';
require_once LANDING_CONFIG_DIR . '/includes/lead-statuses.php';
require_once LANDING_CONFIG_DIR . '/includes/lead-status-log.php';
require_once LANDING_CONFIG_DIR . '/includes/migrate-to-s2a3.php';
require_once LANDING_CONFIG_DIR . '/includes/segment-selector.php';
require_once LANDING_CONFIG_DIR . '/includes/snippets.php';

// Integration contracts and concrete adapters must exist before the async
// delivery worker is loaded.
require_once LANDING_CONFIG_DIR . '/adapters/AdapterInterface.php';
require_once LANDING_CONFIG_DIR . '/adapters/EmailAdapter.php';
require_once LANDING_CONFIG_DIR . '/adapters/TelegramAdapter.php';
require_once LANDING_CONFIG_DIR . '/adapters/WhatsAppAdapter.php';
require_once LANDING_CONFIG_DIR . '/adapters/AmoCRMAdapter.php';
require_once LANDING_CONFIG_DIR . '/adapters/Bitrix24Adapter.php';
require_once LANDING_CONFIG_DIR . '/adapters/HubSpotAdapter.php';
require_once LANDING_CONFIG_DIR . '/adapters/RoistatAdapter.php';

// Reliability stack: strict shared HMAC decoder, monitor, worker, primary
// endpoint, anonymous telemetry, then signed health/reconciliation routes.
require_once LANDING_CONFIG_DIR . '/includes/rest-fallback-token.php';
require_once LANDING_CONFIG_DIR . '/includes/monitoring-alerts.php';
require_once LANDING_CONFIG_DIR . '/includes/lead-delivery-worker.php';
require_once LANDING_CONFIG_DIR . '/includes/rest-lead.php';
require_once LANDING_CONFIG_DIR . '/includes/rest-form-events.php';
require_once LANDING_CONFIG_DIR . '/includes/rest-health.php';

// Administrator modules load only after their storage and runtime services.
require_once LANDING_CONFIG_DIR . '/includes/admin-pages.php';
require_once LANDING_CONFIG_DIR . '/includes/admin-general-settings.php';
require_once LANDING_CONFIG_DIR . '/includes/admin-leads.php';
require_once LANDING_CONFIG_DIR . '/includes/admin-leads-network.php';
require_once LANDING_CONFIG_DIR . '/includes/admin-lead-audit.php';
require_once LANDING_CONFIG_DIR . '/includes/admin-form-events.php';
require_once LANDING_CONFIG_DIR . '/includes/admin-cta.php';
require_once LANDING_CONFIG_DIR . '/includes/admin-snippets.php';
require_once LANDING_CONFIG_DIR . '/includes/admin-lead-statuses.php';
require_once LANDING_CONFIG_DIR . '/includes/admin-lead-detail.php';
require_once LANDING_CONFIG_DIR . '/includes/admin-integrations.php';
require_once LANDING_CONFIG_DIR . '/includes/admin-monitoring.php';

// Read-only stubs override the editor submenus on single-site, hiding the real
// editors. They are only meaningful on multisite (subsite = read-only, super-admin
// edits from network). On single-site the editors above own the pages.
if (\is_multisite()) {
    require_once LANDING_CONFIG_DIR . '/includes/admin-cta-readonly.php';
    require_once LANDING_CONFIG_DIR . '/includes/admin-snippets-readonly.php';
    require_once LANDING_CONFIG_DIR . '/includes/admin-lead-statuses-readonly.php';
    require_once LANDING_CONFIG_DIR . '/includes/admin-integrations-readonly.php';
}

// B2 cookie-banner
require_once __DIR__ . '/includes/cookie-banner/cpt.php';
require_once __DIR__ . '/includes/cookie-banner/resolver.php';
require_once __DIR__ . '/includes/cookie-banner/render.php';
require_once __DIR__ . '/includes/cookie-banner/enqueue.php';
require_once __DIR__ . '/includes/cookie-banner/migrate.php';
if (\is_admin() || \is_network_admin()) {
    require_once __DIR__ . '/includes/cookie-banner/admin-network.php';
    // Read-only subsite view only makes sense on multisite; on single-site the
    // editor (admin-network.php) owns the page directly.
    if (\is_multisite()) {
        require_once __DIR__ . '/includes/cookie-banner/admin-site-readonly.php';
    }
}

// SEO head injector (meta description + Open Graph + favicon)
require_once __DIR__ . '/includes/head-seo.php';

// S2-E.4: SEO Audit dashboard + Head & SEO admin + llms.txt rewrite
require_once __DIR__ . '/includes/seo-audit/audit-runner.php';
require_once __DIR__ . '/includes/seo-audit/deep-links.php';
require_once __DIR__ . '/includes/llms-txt-rewrite.php';
if (\is_admin() || \is_network_admin()) {
    require_once __DIR__ . '/includes/seo-audit/admin-network.php';
    require_once __DIR__ . '/includes/head-seo-admin.php';
}

add_action('init', function () {
    \LandingConfig\DB\maybe_install_or_migrate();
    \LandingConfig\DB\maybe_migrate_b1_pd_consent();
    \LandingConfig\DB\maybe_migrate_roistat_visit();
    \LandingConfig\DB\maybe_migrate_recaptcha_score();
    \LandingConfig\DB\maybe_migrate_lead_audit();
}, 1);

add_action('admin_init', function () {
    if (\function_exists('current_user_can') && \current_user_can(\LandingConfig\AdminMode\cap())) {
        \LandingConfig\Migrate\maybe_run();
        \LandingConfig\CookieBanner\Migrate\maybe_run();
    }
});
