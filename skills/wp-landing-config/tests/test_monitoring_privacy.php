<?php
require __DIR__ . '/fixtures/lead-reliability-bootstrap.php';
require_once __DIR__ . '/../mu-plugin/landing-config/includes/db.php';
require_once __DIR__ . '/../mu-plugin/landing-config/includes/encryption.php';
require_once __DIR__ . '/../mu-plugin/landing-config/includes/helpers.php';
require_once __DIR__ . '/../mu-plugin/landing-config/includes/cascade.php';
require_once __DIR__ . '/../mu-plugin/landing-config/includes/integrations.php';
require_once __DIR__ . '/../mu-plugin/landing-config/adapters/AdapterInterface.php';
require_once __DIR__ . '/../mu-plugin/landing-config/adapters/EmailAdapter.php';
require_once __DIR__ . '/../mu-plugin/landing-config/includes/rest-fallback-token.php';
require_once __DIR__ . '/../mu-plugin/landing-config/includes/monitoring-alerts.php';
require_once __DIR__ . '/../mu-plugin/landing-config/includes/lead-delivery-worker.php';
require_once __DIR__ . '/../mu-plugin/landing-config/includes/rest-lead.php';
require_once __DIR__ . '/../mu-plugin/landing-config/includes/rest-health.php';
require_once __DIR__ . '/../mu-plugin/landing-config/includes/admin-monitoring.php';

$failures = 0;
$assert = static function (bool $condition, string $message) use (&$failures): void {
    if (!$condition) { $failures++; fwrite(STDERR, "FAIL: {$message}\n"); }
};

$bootstrap = file_get_contents(__DIR__ . '/../mu-plugin/landing-config/landing-config.php');
$modules = [
    'includes/rest-fallback-token.php', 'includes/monitoring-alerts.php',
    'includes/lead-delivery-worker.php', 'includes/rest-lead.php',
    'includes/rest-form-events.php', 'includes/rest-health.php',
    'includes/admin-pages.php', 'includes/admin-lead-audit.php', 'includes/admin-monitoring.php',
];
foreach ($modules as $module) {
    $assert(substr_count((string)$bootstrap, $module) === 1, "bootstrap loads {$module} exactly once");
}
$positions = array_map(static fn(string $module): int => (int)strpos((string)$bootstrap, $module), $modules);
for ($i = 1; $i < count($positions); $i++) {
    $assert($positions[$i - 1] < $positions[$i], "bootstrap dependency order is preserved for {$modules[$i]}");
}
$adapter_position = (int)strpos((string)$bootstrap, 'adapters/AdapterInterface.php');
$token_position = (int)strpos((string)$bootstrap, 'includes/rest-fallback-token.php');
$assert($adapter_position > 0 && $adapter_position < $token_position, 'all adapter contracts load before async worker stack');

// Reservation/scheduling failure can never revoke a durable lead success.
final class ThrowingDeliveryLogWpdb extends MockWpdbInsert {
    public function insert($table, $data, $formats = null) {
        if (str_ends_with((string)$table, 'landing_lead_log')) { throw new RuntimeException('CONTACT-MARKER EXCEPTION'); }
        return parent::insert($table, $data, $formats);
    }
}
lr_reset_state();
$GLOBALS['wpdb'] = new ThrowingDeliveryLogWpdb();
$GLOBALS['_mock_posts'] = [];
$GLOBALS['_mock_post_meta'] = [];
$GLOBALS['_mock_next_post_id'] = 1;
\LandingConfig\Integrations\save_integration(
    'email', 'Launch mailbox', '', ['to' => 'elapova00@gmail.com'], false, 1, [], true
);
$_SERVER['REMOTE_ADDR'] = '203.0.113.99';
$_SERVER['HTTP_USER_AGENT'] = 'privacy-test';
$response = \LandingConfig\REST\handle_lead(new WP_REST_Request([
    'name' => 'CONTACT-MARKER NAME', 'phone' => '+971501111111', 'email' => 'contact@example.com',
    'message' => 'CONTACT-MARKER MESSAGE', 'source_block' => 'test', 'pd_consent' => '1',
]));
$assert($response->get_status() === 200 && (int)($response->get_data()['lead_id'] ?? 0) > 0, 'saved lead stays HTTP 200 when reservation throws');

$production = '';
foreach (['rest-lead.php','lead-delivery-worker.php','monitoring-alerts.php','rest-fallback-token.php','rest-health.php','admin-monitoring.php','admin-lead-audit.php'] as $new_file) {
    $production .= file_get_contents(__DIR__ . '/../mu-plugin/landing-config/includes/' . $new_file);
}
foreach (['getMessage()', 'error_sha256', 'hash(\'sha256\', $e', 'hash("sha256", $e'] as $unsafe) {
    $assert(!str_contains($production, $unsafe), "new stack never logs or hashes raw exception text: {$unsafe}");
}
$monitor_source = file_get_contents(__DIR__ . '/../mu-plugin/landing-config/includes/monitoring-alerts.php');
foreach (['name VARCHAR','phone VARCHAR','email VARCHAR','message TEXT','user_agent','response_body','webhook_url'] as $pii_field) {
    $assert(!str_contains((string)$monitor_source, $pii_field), "monitoring module stores no {$pii_field}");
}

$admin_source = file_get_contents(__DIR__ . '/../mu-plugin/landing-config/includes/admin-monitoring.php');
$assert(str_contains((string)$admin_source, "'testRestNonce' => wp_create_nonce('wp_rest')"), 'REST nonce is created only in one-time admin claim helper');
$assert(!str_contains((string)$bootstrap, 'testRestNonce'), 'plugin bootstrap/cached output contains no test REST nonce');
$assert(!str_contains((string)$bootstrap, 'LP_FALLBACK_SIGNING_SECRET'), 'bootstrap never renders signing secret');
$assert(!str_contains((string)$bootstrap, 'LP_FALLBACK_STATUS_SECRET'), 'bootstrap never renders status secret');

echo $failures === 0 ? "PASS: monitoring privacy and bootstrap\n" : "FAILURES: {$failures}\n";
exit($failures === 0 ? 0 : 1);
