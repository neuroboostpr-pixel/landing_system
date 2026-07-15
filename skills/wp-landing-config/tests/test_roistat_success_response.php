<?php
require_once __DIR__ . '/fixtures/wp-bootstrap.php';
require_once __DIR__ . '/../mu-plugin/landing-config/includes/encryption.php';
require_once __DIR__ . '/../mu-plugin/landing-config/includes/helpers.php';
require_once __DIR__ . '/../mu-plugin/landing-config/includes/cascade.php';
require_once __DIR__ . '/../mu-plugin/landing-config/includes/integrations.php';
require_once __DIR__ . '/../mu-plugin/landing-config/adapters/AdapterInterface.php';
require_once __DIR__ . '/../mu-plugin/landing-config/adapters/RoistatAdapter.php';

$failures = 0;
$assert = static function (bool $condition, string $message) use (&$failures): void {
    if (!$condition) {
        $failures++;
        fwrite(STDERR, "FAIL: {$message}\n");
    }
};

$adapter = new \LandingConfig\Adapters\RoistatAdapter();
$lead = [
    'id' => 901,
    'name' => 'Roistat response test',
    'phone' => '+971500000901',
    'email' => '',
    'message' => 'TEST',
    'source_block' => 'https://hybridautos.ae/li-auto/',
    'roistat_visit' => '0',
];
$settings = [
    'webhook_url' => 'https://example.test/roistat',
    'site_url' => 'https://hybridautos.ae/',
];

$GLOBALS['_lr_http'] = [
    'response' => ['code' => 200],
    'body' => "Lead was successfully created\n",
];
$plain = $adapter->send($lead, $settings);
$assert(($plain['ok'] ?? false) === true, 'known Roistat plain-text success is accepted');

$GLOBALS['_lr_http'] = [
    'response' => ['code' => 200],
    'body' => '{"status":"ok"}',
];
$json = $adapter->send($lead, $settings);
$assert(($json['ok'] ?? false) === true, 'Roistat JSON status=ok remains accepted');

$GLOBALS['_lr_http'] = [
    'response' => ['code' => 200],
    'body' => 'Lead was not created',
];
$error = $adapter->send($lead, $settings);
$assert(($error['ok'] ?? true) === false, 'unrecognised HTTP 200 body is not a false success');

$GLOBALS['_lr_http'] = [
    'response' => ['code' => 200],
    'body' => 'lead was successfully created',
];
$case_variant = $adapter->send($lead, $settings);
$assert(($case_variant['ok'] ?? true) === false, 'plain-text success phrase is case-sensitive and exact');

$GLOBALS['_lr_http'] = [
    'response' => ['code' => 500],
    'body' => 'Lead was successfully created',
];
$server_error = $adapter->send($lead, $settings);
$assert(($server_error['ok'] ?? true) === false, 'non-2xx response is never accepted');

echo $failures === 0 ? "PASS: Roistat success response\n" : "FAILURES: {$failures}\n";
exit($failures === 0 ? 0 : 1);
