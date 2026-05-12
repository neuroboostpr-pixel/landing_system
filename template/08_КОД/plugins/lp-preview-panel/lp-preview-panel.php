<?php
/**
 * Plugin Name: LP Preview Panel
 * Description: Runtime preview panel for switching palettes and hero variants on landing pages.
 * Version: 0.1.0
 * Requires PHP: 7.4
 * Author: landing-system
 * License: proprietary
 */

if ( ! defined( 'ABSPATH' ) ) {
    exit;
}

define( 'LP_PREVIEW_PANEL_FILE', __FILE__ );
define( 'LP_PREVIEW_PANEL_DIR', plugin_dir_path( __FILE__ ) );
define( 'LP_PREVIEW_PANEL_URL', plugin_dir_url( __FILE__ ) );
define( 'LP_PREVIEW_PANEL_OPTION', 'lp_preview_panel' );

require_once LP_PREVIEW_PANEL_DIR . 'includes/class-axes.php';
require_once LP_PREVIEW_PANEL_DIR . 'includes/class-panel.php';
require_once LP_PREVIEW_PANEL_DIR . 'includes/class-settings.php';

add_action( 'plugins_loaded', function () {
    LP_Preview_Panel_Panel::register();
    LP_Preview_Panel_Settings::register();
} );
