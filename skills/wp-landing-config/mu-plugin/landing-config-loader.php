<?php
/**
 * Loader for landing-config mu-plugin.
 *
 * WordPress auto-loads only top-level .php files in wp-content/mu-plugins/,
 * not subdirectories. This stub lives at mu-plugins/landing-config-loader.php
 * and requires the real plugin at mu-plugins/landing-config/landing-config.php.
 */

if (!defined('ABSPATH')) { exit; }

require_once __DIR__ . '/landing-config/landing-config.php';
