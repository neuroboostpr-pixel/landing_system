<?php
/**
 * Admin-mode helper — abstracts network-admin (multisite) vs site-admin (single-site).
 *
 * The landing-config admin editors were originally written for multisite only:
 * they register under `network_admin_menu`, require `manage_network_options`, and
 * redirect via `network_admin_url()`. On a single-site install those hooks never
 * fire, so the editors silently disappear and only the read-only stubs show up.
 *
 * These helpers return the multisite values verbatim when `is_multisite()` is
 * true (so multisite behaviour is byte-for-byte unchanged), and the single-site
 * equivalents otherwise. The 5 control editors call them instead of hard-coding
 * the multisite primitives.
 */
namespace LandingConfig\AdminMode;

if (!defined('ABSPATH')) { exit; }

/**
 * Capability required to manage landing-config settings.
 * Multisite: super-admin only. Single-site: regular admin.
 */
function cap(): string {
    return \is_multisite() ? 'manage_network_options' : 'manage_options';
}

/**
 * Build an admin URL for the current mode.
 * Multisite → network_admin_url(); single-site → admin_url().
 *
 * @param string $path e.g. 'admin.php?page=landing-config-network-cta'
 */
function admin_url_for(string $path): string {
    return \is_multisite() ? \network_admin_url($path) : \admin_url($path);
}

/**
 * Menu action hook for registering the editor pages.
 * Multisite → 'network_admin_menu'; single-site → 'admin_menu'.
 */
function menu_hook(): string {
    return \is_multisite() ? 'network_admin_menu' : 'admin_menu';
}

/**
 * Parent menu slug the editor submenus attach to.
 * Multisite top-level is 'landing-config-network' (admin-pages.php network_admin_menu);
 * single-site top-level is 'landing-config' (admin-pages.php admin_menu).
 */
function parent_slug(): string {
    return \is_multisite() ? 'landing-config-network' : 'landing-config';
}

/**
 * Page slug for a given editor.
 * Multisite uses 'landing-config-network-<key>'; single-site uses 'landing-config-<key>'
 * so it matches the existing site-admin menu links.
 *
 * @param string $key  e.g. 'cta', 'snippets', 'integrations', 'lead-statuses'
 */
function page_slug(string $key): string {
    return \is_multisite() ? 'landing-config-network-' . $key : 'landing-config-' . $key;
}
