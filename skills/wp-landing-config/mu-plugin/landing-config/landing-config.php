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
require_once LANDING_CONFIG_DIR . '/includes/rest-lead.php';
require_once LANDING_CONFIG_DIR . '/includes/admin-pages.php';
require_once LANDING_CONFIG_DIR . '/includes/admin-leads.php';
require_once LANDING_CONFIG_DIR . '/includes/admin-leads-network.php';
require_once LANDING_CONFIG_DIR . '/includes/admin-cta.php';
require_once LANDING_CONFIG_DIR . '/includes/admin-cta-readonly.php';
require_once LANDING_CONFIG_DIR . '/includes/admin-snippets.php';
require_once LANDING_CONFIG_DIR . '/includes/admin-snippets-readonly.php';
require_once LANDING_CONFIG_DIR . '/includes/admin-integrations-readonly.php';
require_once LANDING_CONFIG_DIR . '/adapters/AdapterInterface.php';
require_once LANDING_CONFIG_DIR . '/adapters/EmailAdapter.php';
require_once LANDING_CONFIG_DIR . '/adapters/TelegramAdapter.php';
require_once LANDING_CONFIG_DIR . '/adapters/WhatsAppAdapter.php';
require_once LANDING_CONFIG_DIR . '/adapters/AmoCRMAdapter.php';
require_once LANDING_CONFIG_DIR . '/adapters/Bitrix24Adapter.php';
require_once LANDING_CONFIG_DIR . '/adapters/HubSpotAdapter.php';
require_once LANDING_CONFIG_DIR . '/includes/admin-integrations.php';

add_action('init', function () {
    \LandingConfig\DB\maybe_install_or_migrate();
}, 1);

add_action('admin_init', function () {
    if (\function_exists('current_user_can') && \current_user_can('manage_network_options')) {
        \LandingConfig\Migrate\maybe_run();
    }
});
