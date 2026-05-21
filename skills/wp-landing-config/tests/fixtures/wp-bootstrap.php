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

$GLOBALS['_mock_is_multisite'] = true;
function is_multisite() { return (bool)$GLOBALS['_mock_is_multisite']; }

// REST + insert + transient + mail mocks for rest-lead.php tests

$GLOBALS['_mock_rest_routes'] = [];
$GLOBALS['_mock_inserted_leads'] = [];
$GLOBALS['_mock_mail_sent'] = [];
$GLOBALS['_mock_transients'] = [];
$GLOBALS['_mock_actions_fired'] = [];

if (!defined('HOUR_IN_SECONDS')) { define('HOUR_IN_SECONDS', 3600); }

function register_rest_route($namespace, $route, $args) {
    $GLOBALS['_mock_rest_routes'][] = [$namespace, $route, $args];
    return true;
}

function add_action($hook, $callback, $priority = 10) {
    return true;
}

function add_filter($hook, $callback, $priority = 10) {
    return true;
}

function do_action($hook, ...$args) {
    $GLOBALS['_mock_actions_fired'][] = ['hook' => $hook, 'args' => $args];
}

function wp_unslash($v) { return is_string($v) ? stripslashes($v) : $v; }
function sanitize_text_field($v) { return is_string($v) ? trim(strip_tags($v)) : ''; }
function sanitize_email($v) { return is_string($v) ? filter_var(trim($v), FILTER_SANITIZE_EMAIL) : ''; }
function esc_html($v) { return htmlspecialchars((string)$v, ENT_QUOTES, 'UTF-8'); }
function current_time($fmt) { return date('Y-m-d H:i:s'); }

function wp_mail($to, $subject, $body, $headers = []) {
    $GLOBALS['_mock_mail_sent'][] = compact('to', 'subject', 'body');
    return true;
}

function get_bloginfo($key) {
    $map = ['admin_email' => 'admin@example.com', 'name' => 'Test Site'];
    return $map[$key] ?? '';
}

function get_transient($key) {
    return $GLOBALS['_mock_transients'][$key] ?? false;
}

function set_transient($key, $value, $ttl = 0) {
    $GLOBALS['_mock_transients'][$key] = $value;
    return true;
}

class MockWpdbInsert extends MockWpdb {
    public $insert_id = 0;
    public function insert($table, $data, $formats = null) {
        $GLOBALS['_mock_inserted_leads'][] = ['table' => $table, 'data' => $data];
        $this->insert_id = count($GLOBALS['_mock_inserted_leads']) + 100;
        return 1;
    }
}

// Replace wpdb mock with insert-aware version (preserves blog-prefix behavior)
$GLOBALS['wpdb'] = new MockWpdbInsert();

// Mock REST response + request classes
class WP_REST_Response {
    public $data; public $status;
    public function __construct($data, $status = 200) {
        $this->data = $data;
        $this->status = $status;
    }
    public function get_status() { return $this->status; }
    public function get_data() { return $this->data; }
}

class WP_REST_Request {
    private $params = [];
    public function __construct(array $params = []) { $this->params = $params; }
    public function get_params() { return $this->params; }
    public function get_param($key) { return $this->params[$key] ?? null; }
}

function wp_remote_post($url, $args) {
    return ['response' => ['code' => 200], 'body' => '{"ok":true}'];
}
function is_wp_error($v) { return false; }
function wp_remote_retrieve_response_code($r) { return $r['response']['code'] ?? 0; }
function wp_remote_retrieve_body($r) { return $r['body'] ?? ''; }

// CPT + post_meta + wp_kses mocks for snippets.php tests

$GLOBALS['_mock_post_types'] = [];
$GLOBALS['_mock_posts'] = [];
$GLOBALS['_mock_post_meta'] = [];
$GLOBALS['_mock_queried_object_id'] = 0;
$GLOBALS['_mock_next_post_id'] = 1;
$GLOBALS['_mock_kses_calls'] = [];

if (!function_exists('register_post_type')) {
    function register_post_type($name, $args = []) {
        $GLOBALS['_mock_post_types'][$name] = $args;
        return (object) ['name' => $name];
    }
}

if (!function_exists('wp_insert_post')) {
    function wp_insert_post($postarr, $wp_error = false) {
        $id = $GLOBALS['_mock_next_post_id']++;
        $GLOBALS['_mock_posts'][$id] = array_merge(
            ['post_type' => 'post', 'post_status' => 'publish', 'post_title' => ''],
            $postarr,
            ['ID' => $id]
        );
        return $id;
    }
}

if (!function_exists('wp_update_post')) {
    function wp_update_post($postarr) {
        $id = (int) ($postarr['ID'] ?? 0);
        if ($id && isset($GLOBALS['_mock_posts'][$id])) {
            $GLOBALS['_mock_posts'][$id] = array_merge($GLOBALS['_mock_posts'][$id], $postarr);
        }
        return $id;
    }
}

if (!function_exists('wp_delete_post')) {
    function wp_delete_post($id, $force = false) {
        unset($GLOBALS['_mock_posts'][$id]);
        unset($GLOBALS['_mock_post_meta'][$id]);
        return true;
    }
}

if (!function_exists('get_posts')) {
    function get_posts($args = []) {
        $type = $args['post_type'] ?? 'post';
        $limit = $args['numberposts'] ?? $args['posts_per_page'] ?? -1;
        $orderby = $args['orderby'] ?? 'date';
        $order = strtoupper($args['order'] ?? 'DESC');
        $results = [];
        foreach ($GLOBALS['_mock_posts'] as $id => $p) {
            if (($p['post_type'] ?? '') !== $type) continue;
            if (($p['post_status'] ?? '') !== 'publish' && empty($args['post_status'])) continue;
            $results[] = (object) $p;
        }
        if ($orderby === 'meta_value_num' && !empty($args['meta_key'])) {
            $key = $args['meta_key'];
            usort($results, function ($a, $b) use ($key, $order) {
                $av = (int) ($GLOBALS['_mock_post_meta'][$a->ID][$key] ?? 0);
                $bv = (int) ($GLOBALS['_mock_post_meta'][$b->ID][$key] ?? 0);
                return $order === 'ASC' ? $av - $bv : $bv - $av;
            });
        }
        if ($limit > 0) $results = array_slice($results, 0, $limit);
        return $results;
    }
}

if (!function_exists('get_post')) {
    function get_post($id) {
        return isset($GLOBALS['_mock_posts'][$id]) ? (object) $GLOBALS['_mock_posts'][$id] : null;
    }
}

if (!function_exists('update_post_meta')) {
    function update_post_meta($post_id, $key, $value) {
        $GLOBALS['_mock_post_meta'][$post_id][$key] = $value;
        return true;
    }
}

if (!function_exists('get_post_meta')) {
    function get_post_meta($post_id, $key = '', $single = false) {
        if ($key === '') {
            return $GLOBALS['_mock_post_meta'][$post_id] ?? [];
        }
        $value = $GLOBALS['_mock_post_meta'][$post_id][$key] ?? '';
        return $single ? $value : ($value === '' ? [] : [$value]);
    }
}

if (!function_exists('delete_post_meta')) {
    function delete_post_meta($post_id, $key) {
        unset($GLOBALS['_mock_post_meta'][$post_id][$key]);
        return true;
    }
}

if (!function_exists('get_queried_object_id')) {
    function get_queried_object_id() {
        return (int) $GLOBALS['_mock_queried_object_id'];
    }
}

if (!function_exists('set_mock_queried_object_id')) {
    function set_mock_queried_object_id($id) {
        $GLOBALS['_mock_queried_object_id'] = (int) $id;
    }
}

if (!function_exists('wp_kses')) {
    function wp_kses($content, $allowed_html, $allowed_protocols = []) {
        $GLOBALS['_mock_kses_calls'][] = ['content' => $content, 'allowed' => $allowed_html];
        $allowed_tags = array_keys($allowed_html);
        return strip_tags($content, $allowed_tags);
    }
}

if (!function_exists('esc_textarea')) {
    function esc_textarea($v) { return htmlspecialchars((string)$v, ENT_QUOTES, 'UTF-8'); }
}
if (!function_exists('esc_url')) {
    function esc_url($v) { return filter_var((string)$v, FILTER_SANITIZE_URL); }
}
if (!function_exists('selected')) {
    function selected($a, $b, $echo = true) {
        $s = ((string)$a === (string)$b) ? ' selected="selected"' : '';
        if ($echo) echo $s;
        return $s;
    }
}
if (!function_exists('checked')) {
    function checked($a, $b = true, $echo = true) {
        $s = ((bool)$a === (bool)$b) ? ' checked="checked"' : '';
        if ($echo) echo $s;
        return $s;
    }
}
