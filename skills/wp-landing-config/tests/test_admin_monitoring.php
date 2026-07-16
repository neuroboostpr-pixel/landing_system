<?php
require __DIR__ . '/fixtures/lead-reliability-bootstrap.php';
require_once __DIR__ . '/../mu-plugin/landing-config/includes/db.php';
require_once __DIR__ . '/../mu-plugin/landing-config/includes/encryption.php';
require_once __DIR__ . '/../mu-plugin/landing-config/includes/helpers.php';
require_once __DIR__ . '/../mu-plugin/landing-config/includes/cascade.php';
require_once __DIR__ . '/../mu-plugin/landing-config/includes/integrations.php';
require_once __DIR__ . '/../mu-plugin/landing-config/includes/rest-fallback-token.php';
require_once __DIR__ . '/../mu-plugin/landing-config/includes/monitoring-alerts.php';

if (!defined('LP_FALLBACK_ENABLED')) { define('LP_FALLBACK_ENABLED', false); }
if (!defined('LP_FALLBACK_TEST_MODE')) { define('LP_FALLBACK_TEST_MODE', true); }
if (!defined('LP_FALLBACK_URL')) { define('LP_FALLBACK_URL', 'https://fallback.invalid/api/v1/fallback'); }
if (!defined('LP_FALLBACK_SIGNING_SECRET')) { define('LP_FALLBACK_SIGNING_SECRET', str_repeat('0123456789abcdef', 4)); }
if (!defined('LP_FALLBACK_STATUS_SECRET')) { define('LP_FALLBACK_STATUS_SECRET', str_repeat('abcdef0123456789', 4)); }

$module = __DIR__ . '/../mu-plugin/landing-config/includes/admin-monitoring.php';
if (is_file($module)) { require_once $module; }

$failures = 0;
$assert = static function (bool $condition, string $message) use (&$failures): void {
    if (!$condition) { $failures++; fwrite(STDERR, "FAIL: {$message}\n"); }
};

$exists = function_exists('LandingConfig\\MonitoringAdmin\\render_page');
$assert($exists, 'read-only monitoring admin exists');
if (!$exists) { echo "FAILURES: {$failures}\n"; exit(1); }

lr_reset_state();
$target_email_id = \LandingConfig\Integrations\save_integration(
    'email', 'Launch mailbox', '', ['to' => 'elapova00@gmail.com'], false, 1, [], true
);
$old_email_id = \LandingConfig\Integrations\save_integration(
    'email', 'Neuroboost old mailbox', '', ['to' => 'old-neuroboost@example.com'], false, 1, [], false
);
$telegram_id = \LandingConfig\Integrations\save_integration(
    'telegram', 'HybridCars leads', '', ['bot_token' => 'SECRET-BOT', 'chat_id' => '-100123'], false, 1, [], true
);
$roistat_id = \LandingConfig\Integrations\save_integration(
    'roistat', 'Roistat primary', '', ['webhook_url' => 'https://roistat.invalid/secret'], false, 1, [], true
);
$status = \LandingConfig\Monitoring\configuration_status();
$assert(($status['email_binding_ok'] ?? false) === true, 'exactly one enabled Email is bound to launch mailbox');
$assert(($status['neuroboost_disabled'] ?? false) === true, 'old Neuroboost integration is disabled');
$assert(($status['telegram_enabled'] ?? false) === true, 'Telegram lead integration is enabled');
$assert(($status['roistat_crm_enabled'] ?? false) === true, 'Roistat/CRM integration is enabled');
$assert(($status['email_integration_id'] ?? 0) === $target_email_id, 'safe evidence returns target Email ID');
$assert(($status['telegram_integration_id'] ?? 0) === $telegram_id, 'safe evidence returns Telegram ID');
$assert(($status['roistat_crm_integration_id'] ?? 0) === $roistat_id, 'safe evidence returns Roistat/CRM ID');
$assert(!str_contains(json_encode($status), 'elapova00@gmail.com'), 'configuration evidence never returns recipient value');

$GLOBALS['_lr_logged_in'] = true;
$GLOBALS['_lr_capabilities'] = ['manage_options' => true];
ob_start();
\LandingConfig\MonitoringAdmin\render_page();
$html = (string)ob_get_clean();
foreach (['email_binding_ok','neuroboost_disabled','roistat_crm_enabled','Отправить [TEST — DO NOT CONTACT]'] as $safe_label) {
    $assert(str_contains($html, $safe_label), "dashboard shows safe label {$safe_label}");
}
foreach (['elapova00@gmail.com','old-neuroboost@example.com','SECRET-BOT','roistat.invalid/secret'] as $secret) {
    $assert(!str_contains($html, $secret), "dashboard never renders {$secret}");
}
$assert(str_contains($html, 'method="post"'), 'controlled failure is armed only through POST form');
$assert(str_contains($html, 'lp_fallback_arm_controlled_failure'), 'admin-only controlled failure action is explicit');

$GLOBALS['_lr_current_user_id'] = 55;
$GLOBALS['_lr_nonce_actions'] = ['lp_fallback_arm_controlled_failure' => true];
$_SERVER['REQUEST_METHOD'] = 'POST';
try { \LandingConfig\MonitoringAdmin\handle_arm_controlled_failure(); }
catch (RuntimeException $ignored) {}
$key = 'lp_fallback_controlled_failure_55';
$assert(($GLOBALS['_mock_transients'][$key] ?? '') === 'armed', 'valid admin POST arms exact user transient');
$assert(($GLOBALS['_mock_transient_ttls'][$key] ?? 0) === 60, 'controlled failure claim lasts only 60 seconds');
$redirect = $GLOBALS['_lr_redirects'][0] ?? [];
$assert(($redirect['url'] ?? '') === 'https://hybridautos.test/' && ($redirect['status'] ?? 0) === 303, 'handler redirects cleanly to home with HTTP 303');
$assert(!str_contains((string)($redirect['url'] ?? ''), '?'), 'redirect contains no nonce or query');

$claim = \LandingConfig\MonitoringAdmin\consume_controlled_failure_claim(55);
$assert($claim === ['testMode' => true, 'forcePrimaryFailure' => true, 'testRestNonce' => 'nonce-wp_rest'], 'clean no-store bootstrap receives one authorized REST nonce');
$assert(\LandingConfig\MonitoringAdmin\consume_controlled_failure_claim(55) === null, 'controlled failure claim is consumed once under lock');

unset($GLOBALS['_mock_transients'][$key]);
$_SERVER['REQUEST_METHOD'] = 'GET';
try { \LandingConfig\MonitoringAdmin\handle_arm_controlled_failure(); }
catch (RuntimeException $ignored) {}
$assert(!isset($GLOBALS['_mock_transients'][$key]), 'GET cannot arm controlled failure');

// A second enabled Email blocks release and old recipients remain hidden.
\LandingConfig\Integrations\save_integration(
    'email', 'Unexpected mailbox', '', ['to' => 'unexpected@example.com'], false, 1, [], true
);
$mismatch = \LandingConfig\Monitoring\configuration_status();
$assert(($mismatch['email_binding_ok'] ?? true) === false, 'additional enabled Email blocks release');
$assert(!str_contains(json_encode($mismatch), 'unexpected@example.com'), 'mismatch evidence still hides recipient');

$source = file_get_contents($module);
foreach (['check_admin_referer', 'current_user_can', 'Referrer-Policy: no-referrer', 'wp_safe_redirect', '303'] as $guard) {
    $assert(str_contains((string)$source, $guard), "admin action includes {$guard}");
}
$assert(!str_contains((string)$source, 'type="text" name="'), 'dashboard has no free-text technical alert input');

echo $failures === 0 ? "PASS: monitoring admin\n" : "FAILURES: {$failures}\n";
exit($failures === 0 ? 0 : 1);
