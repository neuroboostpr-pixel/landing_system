<?php
require __DIR__ . '/fixtures/lead-reliability-bootstrap.php';

$failures = 0;
$assert = static function (bool $condition, string $message) use (&$failures): void {
    if (!$condition) {
        $failures++;
        fwrite(STDERR, "FAIL: {$message}\n");
    }
};

lr_reset_state();
global $wpdb;
$leads = $wpdb->get_blog_prefix() . 'landing_leads';
$log = $wpdb->get_blog_prefix() . 'landing_lead_log';

$assert($wpdb->insert($leads, ['submission_id' => '11111111-1111-4111-8111-111111111111']) === 1, 'first UUID inserts');
$assert($wpdb->insert($leads, ['submission_id' => '11111111-1111-4111-8111-111111111111']) === false, 'duplicate UUID is rejected');
$assert(str_contains($wpdb->last_error, 'submission_id'), 'duplicate names submission_id');

$attempt = ['lead_id' => 1, 'adapter' => 'email', 'integration_id' => 7, 'attempt' => 1];
$assert($wpdb->insert($log, $attempt) === 1, 'first delivery attempt inserts');
$assert($wpdb->insert($log, $attempt) === false, 'duplicate delivery attempt is rejected');

lr_queue_query_count(1);
$assert($wpdb->query('UPDATE wp_landing_lead_log SET status=\'sending\' WHERE id=1') === 1, 'claim reports one changed row');
lr_queue_query_count(0);
$assert($wpdb->query('UPDATE wp_landing_lead_log SET status=\'sending\' WHERE id=1') === 0, 'second claim loses race');

lr_set_http(['response' => ['code' => 503], 'body' => 'busy', 'headers' => []]);
$http = wp_remote_post('https://provider.invalid', []);
$assert(wp_remote_retrieve_response_code($http) === 503, 'HTTP response is controllable');

$request = new WP_REST_Request([], '', ['X-LP-Timestamp' => '1784190000']);
$assert($request->get_header('x-lp-timestamp') === '1784190000', 'REST mock reads headers case-insensitively');
lr_set_http(['response' => ['code' => 404], 'body' => '{"ok":true,"exists":false,"stored":false}', 'headers' => []]);
$http = wp_remote_get('https://fallback.invalid/api/v1/receipts/uuid', []);
$assert(wp_remote_retrieve_response_code($http) === 404, 'HTTP GET mock is controllable');

echo $failures === 0 ? "PASS: lead reliability fixture\n" : "FAILURES: {$failures}\n";
exit($failures === 0 ? 0 : 1);
