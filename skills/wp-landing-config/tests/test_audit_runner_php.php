<?php
require_once __DIR__ . '/fixtures/wp-bootstrap.php';
require_once dirname(__DIR__) . '/mu-plugin/landing-config/includes/seo-audit/audit-runner.php';

$tests = 0; $failures = 0;
function assert_test($cond, $msg) {
    global $tests, $failures;
    $tests++;
    if (!$cond) { $failures++; echo "FAIL: $msg\n"; }
    else { echo "PASS: $msg\n"; }
}

// T1: build_python_command — single URL mode
$cmd = \LandingConfig\SEOAudit\Runner\build_python_command(
    ['urls' => ['https://example.com/'], 'out_dir' => '/tmp/x'],
    '/usr/bin/python3',
    '/path/to/run-audit.py'
);
assert_test(strpos($cmd, '--url ') !== false && strpos($cmd, 'example.com') !== false,
    'T1a single URL mode has --url');
assert_test(strpos($cmd, '--with-fix-hints') !== false,
    'T1b always includes --with-fix-hints');
assert_test(strpos($cmd, '--json') !== false,
    'T1c always includes --json');

// T2: build_python_command — multi-URL mode via hosts file
$cmd2 = \LandingConfig\SEOAudit\Runner\build_python_command(
    ['urls' => ['https://a.com/', 'https://b.com/'], 'out_dir' => '/tmp/x', 'hosts_file' => '/tmp/h.txt'],
    '/usr/bin/python3',
    '/path/to/run-audit.py'
);
assert_test(strpos($cmd2, '--hosts-file ') !== false && strpos($cmd2, 'h.txt') !== false,
    'T2a multi-URL uses --hosts-file');
assert_test(strpos($cmd2, '--url ') === false,
    'T2b multi-URL does NOT include --url');

// T3: parse_audit_output — valid JSON
$json = json_encode(['sites' => [['host' => 'https://x/', 'passed' => true]],
                    'total_sites' => 1, 'sites_passed' => 1, 'overall_passed' => true]);
$parsed = \LandingConfig\SEOAudit\Runner\parse_audit_output($json);
assert_test($parsed !== null, 'T3a parses valid JSON');
assert_test($parsed['overall_passed'] === true, 'T3b parsed shape correct');

// T4: parse_audit_output — invalid JSON returns null
$bad = \LandingConfig\SEOAudit\Runner\parse_audit_output('not json');
assert_test($bad === null, 'T4 invalid JSON returns null');

// T5: cache key naming
assert_test(\LandingConfig\SEOAudit\Runner\cache_key(0) === 'landing_seo_audit_0',
    'T5a cache_key(0) = network');
assert_test(\LandingConfig\SEOAudit\Runner\cache_key(3) === 'landing_seo_audit_3',
    'T5b cache_key(3) = per-blog');
assert_test(\LandingConfig\SEOAudit\Runner\aggregate_cache_key() === 'landing_seo_audit_aggregate',
    'T5c aggregate cache key');

echo "$tests tests, $failures failures\n";
exit($failures > 0 ? 1 : 0);
