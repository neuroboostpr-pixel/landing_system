<?php
require_once __DIR__ . '/fixtures/wp-bootstrap.php';
require_once dirname(__DIR__) . '/mu-plugin/landing-config/includes/head-seo-admin.php';

$tests = 0; $failures = 0;
function assert_test($cond, $msg) {
    global $tests, $failures;
    $tests++;
    if (!$cond) { $failures++; echo "FAIL: $msg\n"; }
    else { echo "PASS: $msg\n"; }
}

// T1: save_settings_for_segment writes options
$saved = \LandingConfig\HeadSEOAdmin\save_settings_for_segment(1, [
    'description' => 'Test description here at least 70 chars long for spec compliance check yes yes',
    'og_image' => 'https://x/og.png',
    'og_type' => 'website',
    'twitter_card' => 'summary_large_image',
    'llms_txt' => "# Test\n\n- [Link](https://x/)",
]);
assert_test($saved === true, 'T1 save_settings returns true');
assert_test(\get_option('landing_seo_description') === 'Test description here at least 70 chars long for spec compliance check yes yes',
    'T1a description saved');
assert_test(\get_option('landing_seo_og_image') === 'https://x/og.png',
    'T1b og_image saved');

// T2: invalid og_type rejected
$saved2 = \LandingConfig\HeadSEOAdmin\save_settings_for_segment(1, [
    'og_type' => 'evil-injected-value',
]);
assert_test(\get_option('landing_seo_og_type') === 'website',
    'T2 invalid og_type defaults to website');

// T3: invalid twitter_card rejected
\LandingConfig\HeadSEOAdmin\save_settings_for_segment(1, ['twitter_card' => 'evil']);
assert_test(\get_option('landing_seo_twitter_card') === 'summary_large_image',
    'T3 invalid twitter_card defaults');

echo "$tests tests, $failures failures\n";
exit($failures > 0 ? 1 : 0);
