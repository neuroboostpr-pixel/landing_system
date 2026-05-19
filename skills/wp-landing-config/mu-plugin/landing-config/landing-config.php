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
require_once LANDING_CONFIG_DIR . '/includes/rest-lead.php';
require_once LANDING_CONFIG_DIR . '/includes/admin-pages.php';
require_once LANDING_CONFIG_DIR . '/includes/admin-leads.php';

add_action('init', function () {
    \LandingConfig\DB\maybe_install_or_migrate();
}, 1);
