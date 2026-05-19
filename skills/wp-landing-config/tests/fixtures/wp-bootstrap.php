<?php
/**
 * Minimal WP-functions mock for PHP CLI tests.
 * Only mocks functions used by db.php / encryption.php / helpers.php.
 *
 * Tests source this BEFORE requiring the file under test.
 */

if (!defined('ABSPATH')) { define('ABSPATH', '/tmp/mock-wp/'); }

// In-memory option store, scoped per blog_id.
$GLOBALS['_mock_options'] = [];     // [blog_id => [key => value]]
$GLOBALS['_mock_site_meta'] = [];   // [key => value] — for network options
$GLOBALS['_mock_current_blog_id'] = 1;
$GLOBALS['_mock_dbdelta_calls'] = [];

function get_current_blog_id() {
    return $GLOBALS['_mock_current_blog_id'];
}

function set_mock_current_blog_id($id) {
    $GLOBALS['_mock_current_blog_id'] = (int)$id;
}

function get_option($key, $default = false) {
    $bid = get_current_blog_id();
    return $GLOBALS['_mock_options'][$bid][$key] ?? $default;
}

function update_option($key, $value) {
    $bid = get_current_blog_id();
    $GLOBALS['_mock_options'][$bid][$key] = $value;
    return true;
}

function get_site_option($key, $default = false) {
    return $GLOBALS['_mock_site_meta'][$key] ?? $default;
}

function update_site_option($key, $value) {
    $GLOBALS['_mock_site_meta'][$key] = $value;
    return true;
}

function wp_salt($scheme = 'auth') {
    // Stable test salt — DO NOT use in production.
    return 'TEST_SALT_' . $scheme . '_xyz12345';
}

function dbDelta($sql) {
    $GLOBALS['_mock_dbdelta_calls'][] = $sql;
    return [];
}

// $wpdb mock — minimal surface for db.php
class MockWpdb {
    public $prefix = 'wp_';
    public $base_prefix = 'wp_';

    public function get_blog_prefix($blog_id = null) {
        $bid = $blog_id ?: get_current_blog_id();
        return $bid === 1 ? 'wp_' : 'wp_' . $bid . '_';
    }

    public function get_charset_collate() {
        return 'DEFAULT CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci';
    }
}

$GLOBALS['wpdb'] = new MockWpdb();

function get_sites($args = []) {
    // Default: 3 sites for tests
    return [
        (object)['blog_id' => 1, 'domain' => 'example.com', 'path' => '/'],
        (object)['blog_id' => 2, 'domain' => 'alpha.example.com', 'path' => '/'],
        (object)['blog_id' => 3, 'domain' => 'beta.example.com', 'path' => '/'],
    ];
}

function switch_to_blog($blog_id) {
    set_mock_current_blog_id($blog_id);
    return true;
}

function restore_current_blog() {
    set_mock_current_blog_id(1);
    return true;
}

function is_multisite() { return true; }
