<?php
require __DIR__ . '/fixtures/lead-reliability-bootstrap.php';

if (!defined('LP_FALLBACK_TEST_MODE')) { define('LP_FALLBACK_TEST_MODE', false); }
require_once __DIR__ . '/../mu-plugin/landing-config/includes/db.php';
require_once __DIR__ . '/../mu-plugin/landing-config/includes/encryption.php';
require_once __DIR__ . '/../mu-plugin/landing-config/includes/helpers.php';
require_once __DIR__ . '/../mu-plugin/landing-config/includes/cascade.php';
require_once __DIR__ . '/../mu-plugin/landing-config/includes/integrations.php';
require_once __DIR__ . '/../mu-plugin/landing-config/includes/rest-fallback-token.php';
require_once __DIR__ . '/../mu-plugin/landing-config/includes/monitoring-alerts.php';
require_once __DIR__ . '/../mu-plugin/landing-config/includes/admin-monitoring.php';

$failures = 0;
$assert = static function (bool $condition, string $message) use (&$failures): void {
    if (!$condition) { $failures++; fwrite(STDERR, "FAIL: {$message}\n"); }
};

$uuid = '88888888-8888-4888-8888-888888888888';
$exists = function_exists('LandingConfig\\MonitoringAdmin\\arm_status_smoke_at');
$assert($exists, 'disabled build still exposes fail-closed internal helper');
if ($exists) {
    $assert(!\LandingConfig\MonitoringAdmin\arm_status_smoke_at($uuid, 180, 1789000000),
        'test mode false makes arming fully unavailable');
}
$GLOBALS['_lr_logged_in'] = true;
$GLOBALS['_lr_capabilities'] = ['manage_options' => true];
$GLOBALS['_lr_current_user_id'] = 55;
$GLOBALS['_lr_nonce_actions'] = ['lp_fallback_arm_status_smoke' => true];
$_SERVER['REQUEST_METHOD'] = 'POST';
$_POST = ['smoke_submission_id' => $uuid];
try { \LandingConfig\MonitoringAdmin\handle_arm_status_smoke(); } catch (RuntimeException $ignored) {}
$assert($GLOBALS['_mock_transients'] === [], 'even an authorized admin cannot arm when test mode is false');

echo $failures === 0 ? "PASS: disabled status smoke\n" : "FAILURES: {$failures}\n";
exit($failures === 0 ? 0 : 1);
