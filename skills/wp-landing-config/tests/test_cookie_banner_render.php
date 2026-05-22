<?php
require_once __DIR__ . '/fixtures/wp-bootstrap.php';
require_once dirname(__DIR__) . '/mu-plugin/landing-config/includes/cookie-banner/cpt.php';
require_once dirname(__DIR__) . '/mu-plugin/landing-config/includes/cookie-banner/resolver.php';
require_once dirname(__DIR__) . '/mu-plugin/landing-config/includes/cookie-banner/render.php';

$tests = 0; $failures = 0;
function assert_test($cond, $msg) {
    global $tests, $failures;
    $tests++;
    if (!$cond) { $failures++; echo "FAIL: $msg\n"; }
    else { echo "PASS: $msg\n"; }
}

// T1-T3: render_with_settings emits HTML
$settings = \LandingConfig\CookieBanner\Resolver\DEFAULTS;
ob_start();
\LandingConfig\CookieBanner\Render\render_with_settings($settings);
$html = ob_get_clean();
assert_test(strpos($html, 'id="lp-cb"') !== false, 'T1 render includes id="lp-cb"');
assert_test(strpos($html, 'class="lp-cb lp-cb--bottom-bar"') !== false, 'T2 default layout class is bottom-bar');
assert_test(strpos($html, 'Принять все') !== false, 'T3 default accept button visible');

// T4: show_categories=false hides categories
$settings_no_cats = array_merge($settings, ['show_categories' => false]);
ob_start();
\LandingConfig\CookieBanner\Render\render_with_settings($settings_no_cats);
$html = ob_get_clean();
assert_test(strpos($html, 'lp-cb__categories') === false, 'T4 categories block hidden when show_categories=false');

// T5: show_categories=true shows categories
$settings_with_cats = array_merge($settings, ['show_categories' => true]);
ob_start();
\LandingConfig\CookieBanner\Render\render_with_settings($settings_with_cats);
$html = ob_get_clean();
assert_test(strpos($html, 'lp-cb__categories') !== false, 'T5 categories block visible when show_categories=true');

// T6-T8: btn_reject_text controls reject button visibility
ob_start();
\LandingConfig\CookieBanner\Render\render_with_settings($settings);
$html = ob_get_clean();
assert_test(strpos($html, 'data-action="reject"') === false, 'T6 reject button hidden when text empty');

$settings_reject = array_merge($settings, ['btn_reject_text' => 'Отклонить']);
ob_start();
\LandingConfig\CookieBanner\Render\render_with_settings($settings_reject);
$html = ob_get_clean();
assert_test(strpos($html, 'data-action="reject"') !== false, 'T7 reject button shown when text set');
assert_test(strpos($html, '>Отклонить<') !== false, 'T8 reject button label correct');

// T9: invalid layout → fallback bottom-bar
$settings_bad = array_merge($settings, ['layout' => 'nonexistent']);
ob_start();
\LandingConfig\CookieBanner\Render\render_with_settings($settings_bad);
$html = ob_get_clean();
assert_test(strpos($html, 'lp-cb--bottom-bar') !== false, 'T9 invalid layout falls back to bottom-bar template');

// T10: data-version attr present
ob_start();
\LandingConfig\CookieBanner\Render\render_with_settings($settings);
$html = ob_get_clean();
assert_test(strpos($html, 'data-version="1"') !== false, 'T10 data-version attribute present');

echo "$tests tests, $failures failures\n";
exit($failures > 0 ? 1 : 0);
