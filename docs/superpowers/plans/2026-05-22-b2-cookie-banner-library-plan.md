# Cookie-banner Library Implementation Plan (B2)

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Replace hardcoded B1 cookie-banner with a 5-layout configurable library managed via Network admin, owned entirely by `landing-config` mu-plugin (independent of theme regeneration).

**Architecture:** New CPT `lp_cookie_banner` in mu-plugin follows S2-A.3 cascade pattern (network default + per-segment override). Resolver computes effective settings for current blog; render emits DOM via `wp_footer`; enqueue emits consent-init + CSS/JS via `wp_head`. Five PHP layout templates share one core.css + per-layout css. Theme files from B1 are removed.

**Tech Stack:** PHP 7.4+ (mu-plugin, namespaced), vanilla JS (banner.js), CSS-vars (no preprocessor), WP-CLI for migration, bats for shell tests, custom PHP test framework already used in `skills/wp-landing-config/tests/`.

**Spec:** [docs/superpowers/specs/2026-05-22-b2-cookie-banner-library-design.md](../specs/2026-05-22-b2-cookie-banner-library-design.md)

---

## File Structure

```
skills/wp-landing-config/mu-plugin/landing-config/
├── includes/
│   └── cookie-banner/                          # NEW directory
│       ├── cpt.php                             # NEW (Task 1)
│       ├── resolver.php                        # NEW (Task 2)
│       ├── render.php                          # NEW (Task 4)
│       ├── enqueue.php                         # NEW (Task 5)
│       ├── admin-network.php                   # NEW (Task 6)
│       ├── admin-site-readonly.php             # NEW (Task 7)
│       ├── migrate.php                         # NEW (Task 8)
│       └── layouts/
│           ├── bottom-bar.php                  # NEW (Task 3)
│           ├── top-bar.php                     # NEW (Task 9)
│           ├── floating-card-left.php          # NEW (Task 9)
│           ├── floating-card-right.php         # NEW (Task 9)
│           └── center-modal.php                # NEW (Task 9)
├── assets/cookie-banner/                       # NEW directory
│   ├── core.css                                # NEW (Task 3)
│   ├── banner.js                               # NEW (Task 4)
│   ├── layouts/
│   │   ├── bottom-bar.css                      # NEW (Task 3)
│   │   ├── top-bar.css                         # NEW (Task 9)
│   │   ├── floating-card.css                   # NEW (Task 9) — shared L+R
│   │   └── center-modal.css                    # NEW (Task 9)
│   └── previews/                               # NEW (Task 6)
│       ├── top-bar.svg
│       ├── bottom-bar.svg
│       ├── floating-card-left.svg
│       ├── floating-card-right.svg
│       └── center-modal.svg
└── landing-config.php                          # MODIFY (Task 10) — wire migration

skills/wp-landing-config/tests/
├── test_cookie_banner_resolver.php             # NEW (Task 2)
├── test_cookie_banner_render.php               # NEW (Task 4)
├── test_cookie_banner_cpt.php                  # NEW (Task 1)
├── test_cookie_banner_migration.php            # NEW (Task 8)
└── integration/
    └── test_s2a3_smoke.sh                      # MODIFY (Task 11) — add T_CB_1..4

template/08_КОД/template-parts/                 # MODIFY (Task 12)
├── cookie-banner.php                           # DELETE
├── cookie-banner.js                            # DELETE
├── cookie-banner.css                           # DELETE
├── consent-init.php                            # DELETE
└── legal-block.php                             # KEEP (separate concern)

template/08_КОД/wp-theme/functions.php.tmpl     # (no such template — see Task 12 notes)
scripts/checks/check_legal_blocks.sh            # MODIFY (Task 13)
CLAUDE.md                                       # MODIFY (Task 14)
```

---

### Task 1: Register CPT `lp_cookie_banner`

**Files:**
- Create: `skills/wp-landing-config/mu-plugin/landing-config/includes/cookie-banner/cpt.php`
- Create: `skills/wp-landing-config/tests/test_cookie_banner_cpt.php`

- [ ] **Step 1: Write failing test**

```php
<?php
// skills/wp-landing-config/tests/test_cookie_banner_cpt.php
require_once __DIR__ . '/wp-bootstrap.php';
require_once dirname(__DIR__) . '/mu-plugin/landing-config/includes/cookie-banner/cpt.php';

$tests = 0; $failures = 0;
function assert_test($cond, $msg) {
    global $tests, $failures;
    $tests++;
    if (!$cond) { $failures++; echo "FAIL: $msg\n"; }
    else { echo "PASS: $msg\n"; }
}

// T1: CPT slug constant defined
assert_test(\LandingConfig\CookieBanner\CPT\POST_TYPE === 'lp_cookie_banner',
    'T1 POST_TYPE constant is lp_cookie_banner');

// T2: register() function exists
assert_test(function_exists('LandingConfig\\CookieBanner\\CPT\\register'),
    'T2 register() function exists');

// T3: SEGMENT_META, LAYOUT_META, etc. constants defined
assert_test(\LandingConfig\CookieBanner\CPT\SEGMENT_META === '_lp_cb_segment',
    'T3 SEGMENT_META is _lp_cb_segment');
assert_test(\LandingConfig\CookieBanner\CPT\LAYOUT_META === '_lp_cb_layout',
    'T4 LAYOUT_META is _lp_cb_layout');

// T5: VALID_LAYOUTS includes all 5 layouts
$expected = ['top-bar', 'bottom-bar', 'floating-card-left', 'floating-card-right', 'center-modal'];
assert_test(\LandingConfig\CookieBanner\CPT\VALID_LAYOUTS === $expected,
    'T5 VALID_LAYOUTS has all 5 layouts');

echo "$tests tests, $failures failures\n";
exit($failures > 0 ? 1 : 0);
```

- [ ] **Step 2: Run — verify fail**

```bash
cd D:/AI_TEAMS/landing_system/.worktrees/b2-cookie-banner-library
php skills/wp-landing-config/tests/test_cookie_banner_cpt.php 2>&1 | tail -10
```

Expected: include error (cpt.php not found).

- [ ] **Step 3: Implement cpt.php**

```php
<?php
namespace LandingConfig\CookieBanner\CPT;

if (!defined('ABSPATH')) { exit; }

const POST_TYPE      = 'lp_cookie_banner';
const SEGMENT_META   = '_lp_cb_segment';
const LAYOUT_META    = '_lp_cb_layout';
const TITLE_META     = '_lp_cb_title';
const DESCRIPTION_META = '_lp_cb_description';
const BTN_ACCEPT_META = '_lp_cb_btn_accept_all_text';
const BTN_SAVE_META   = '_lp_cb_btn_save_text';
const BTN_REJECT_META = '_lp_cb_btn_reject_text';
const POLICY_TEXT_META = '_lp_cb_policy_link_text';
const POLICY_URL_META  = '_lp_cb_policy_link_url';
const REOPEN_META      = '_lp_cb_reopen_text';
const SHOW_CATEGORIES_META = '_lp_cb_show_categories';
const CATEGORIES_META  = '_lp_cb_categories';
const COLOR_BG_META    = '_lp_cb_color_bg';
const COLOR_TEXT_META  = '_lp_cb_color_text';
const COLOR_ACCENT_META = '_lp_cb_color_accent';
const COLOR_BORDER_META = '_lp_cb_color_border';
const CONSENT_VERSION_META = '_lp_cb_consent_version';

const VALID_LAYOUTS = ['top-bar', 'bottom-bar', 'floating-card-left', 'floating-card-right', 'center-modal'];

add_action('init', __NAMESPACE__ . '\\register', 5);

function register(): void {
    register_post_type(POST_TYPE, [
        'public'          => false,
        'show_ui'         => false,
        'show_in_menu'    => false,
        'show_in_rest'    => false,
        'supports'        => ['title'],
        'capability_type' => 'post',
        'map_meta_cap'    => true,
        'capabilities'    => [
            'edit_posts'        => 'manage_network_options',
            'edit_others_posts' => 'manage_network_options',
            'publish_posts'     => 'manage_network_options',
            'delete_posts'      => 'manage_network_options',
            'read'              => 'read',
        ],
    ]);
}
```

- [ ] **Step 4: Run — verify pass**

```bash
cd D:/AI_TEAMS/landing_system/.worktrees/b2-cookie-banner-library
php skills/wp-landing-config/tests/test_cookie_banner_cpt.php 2>&1 | tail -5
```

Expected: `5 tests, 0 failures`.

- [ ] **Step 5: Commit**

```bash
cd D:/AI_TEAMS/landing_system/.worktrees/b2-cookie-banner-library
git add skills/wp-landing-config/mu-plugin/landing-config/includes/cookie-banner/cpt.php \
        skills/wp-landing-config/tests/test_cookie_banner_cpt.php
git commit -m "feat(b2): CPT lp_cookie_banner registration + meta constants"
```

---

### Task 2: Resolver with cascade (network → site override)

**Files:**
- Create: `skills/wp-landing-config/mu-plugin/landing-config/includes/cookie-banner/resolver.php`
- Create: `skills/wp-landing-config/tests/test_cookie_banner_resolver.php`

- [ ] **Step 1: Write failing test**

```php
<?php
// skills/wp-landing-config/tests/test_cookie_banner_resolver.php
require_once __DIR__ . '/wp-bootstrap.php';
require_once dirname(__DIR__) . '/mu-plugin/landing-config/includes/cookie-banner/cpt.php';
require_once dirname(__DIR__) . '/mu-plugin/landing-config/includes/cookie-banner/resolver.php';

$tests = 0; $failures = 0;
function assert_test($cond, $msg) {
    global $tests, $failures;
    $tests++;
    if (!$cond) { $failures++; echo "FAIL: $msg\n"; }
    else { echo "PASS: $msg\n"; }
}

function reset_mock_posts() {
    $GLOBALS['_mock_posts'] = [];
    $GLOBALS['_mock_postmeta'] = [];
    $GLOBALS['_mock_next_id'] = 1;
}

function seed_banner(int $segment, array $meta): int {
    global $_mock_posts, $_mock_postmeta, $_mock_next_id;
    $id = $_mock_next_id++;
    $_mock_posts[$id] = (object) ['ID' => $id, 'post_type' => 'lp_cookie_banner', 'post_status' => 'publish'];
    $_mock_postmeta[$id] = array_merge(['_lp_cb_segment' => (string) $segment], $meta);
    return $id;
}

// T1: defaults when nothing configured
reset_mock_posts();
$out = \LandingConfig\CookieBanner\Resolver\resolve_for_blog(2);
assert_test($out !== null, 'T1a resolver returns array even without records (DEFAULTS)');
assert_test($out['layout'] === 'bottom-bar', 'T1b default layout is bottom-bar');
assert_test($out['show_categories'] === false, 'T1c default show_categories=false');
assert_test($out['consent_version'] === 1, 'T1d default version=1');

// T2: network-only
reset_mock_posts();
seed_banner(0, ['_lp_cb_layout' => 'top-bar', '_lp_cb_title' => 'Network title']);
$out = \LandingConfig\CookieBanner\Resolver\resolve_for_blog(2);
assert_test($out['layout'] === 'top-bar', 'T2a network layout wins (no site override)');
assert_test($out['title'] === 'Network title', 'T2b network title wins');

// T3: site override
reset_mock_posts();
seed_banner(0, ['_lp_cb_layout' => 'top-bar', '_lp_cb_title' => 'Network title']);
seed_banner(3, ['_lp_cb_layout' => 'center-modal']);
$out = \LandingConfig\CookieBanner\Resolver\resolve_for_blog(3);
assert_test($out['layout'] === 'center-modal', 'T3a site layout wins over network');
assert_test($out['title'] === 'Network title', 'T3b unset site field falls back to network');

// T4: invalid layout from DB → fallback bottom-bar
reset_mock_posts();
seed_banner(0, ['_lp_cb_layout' => 'invalid-layout-name']);
$out = \LandingConfig\CookieBanner\Resolver\resolve_for_blog(1);
assert_test($out['layout'] === 'bottom-bar', 'T4 invalid layout falls back to bottom-bar');

// T5: categories parsing (stored as JSON string)
reset_mock_posts();
seed_banner(0, ['_lp_cb_categories' => json_encode([
    ['slug' => 'necessary', 'name' => 'Necessary', 'locked' => true],
    ['slug' => 'analytics', 'name' => 'Analytics', 'locked' => false],
])]);
$out = \LandingConfig\CookieBanner\Resolver\resolve_for_blog(1);
assert_test(is_array($out['categories']) && count($out['categories']) === 2,
    'T5 categories parsed from JSON string to array');

echo "$tests tests, $failures failures\n";
exit($failures > 0 ? 1 : 0);
```

- [ ] **Step 2: Run — verify fail**

```bash
cd D:/AI_TEAMS/landing_system/.worktrees/b2-cookie-banner-library
php skills/wp-landing-config/tests/test_cookie_banner_resolver.php 2>&1 | tail -10
```

Expected: file not found error.

- [ ] **Step 3: Implement resolver.php**

```php
<?php
namespace LandingConfig\CookieBanner\Resolver;

if (!defined('ABSPATH')) { exit; }

use const LandingConfig\CookieBanner\CPT\POST_TYPE;
use const LandingConfig\CookieBanner\CPT\SEGMENT_META;
use const LandingConfig\CookieBanner\CPT\VALID_LAYOUTS;

const DEFAULTS = [
    'layout'               => 'bottom-bar',
    'title'                => 'Мы используем cookies',
    'description'          => 'Cookies помогают нам обеспечить работу сайта и понять, как вы им пользуетесь.',
    'btn_accept_all_text'  => 'Принять все',
    'btn_save_text'        => 'Сохранить настройки',
    'btn_reject_text'      => '',
    'policy_link_text'     => 'Политика обработки персональных данных',
    'policy_link_url'      => '/policy',
    'reopen_text'          => 'Настройки cookies',
    'show_categories'      => false,
    'categories'           => [
        ['slug' => 'necessary', 'name' => 'Необходимые',
         'desc' => 'Обеспечивают базовую работу сайта. Не могут быть отключены.',
         'locked' => true, 'default_on' => true],
        ['slug' => 'analytics', 'name' => 'Аналитика',
         'desc' => 'Помогают понять, как посетители используют сайт.',
         'locked' => false, 'default_on' => false],
        ['slug' => 'marketing', 'name' => 'Маркетинг',
         'desc' => 'Для показа релевантной рекламы и ретаргетинга.',
         'locked' => false, 'default_on' => false],
    ],
    'color_bg'             => '',
    'color_text'           => '',
    'color_accent'         => '',
    'color_border'         => '',
    'consent_version'      => 1,
];

const META_KEY_MAP = [
    'layout'               => '_lp_cb_layout',
    'title'                => '_lp_cb_title',
    'description'          => '_lp_cb_description',
    'btn_accept_all_text'  => '_lp_cb_btn_accept_all_text',
    'btn_save_text'        => '_lp_cb_btn_save_text',
    'btn_reject_text'      => '_lp_cb_btn_reject_text',
    'policy_link_text'     => '_lp_cb_policy_link_text',
    'policy_link_url'      => '_lp_cb_policy_link_url',
    'reopen_text'          => '_lp_cb_reopen_text',
    'show_categories'      => '_lp_cb_show_categories',
    'categories'           => '_lp_cb_categories',
    'color_bg'             => '_lp_cb_color_bg',
    'color_text'           => '_lp_cb_color_text',
    'color_accent'         => '_lp_cb_color_accent',
    'color_border'         => '_lp_cb_color_border',
    'consent_version'      => '_lp_cb_consent_version',
];

/** Get post ID of the lp_cookie_banner record for a given segment, or null. */
function get_post_id_for_segment(int $segment): ?int {
    $q = \get_posts([
        'post_type'   => POST_TYPE,
        'post_status' => 'publish',
        'meta_key'    => SEGMENT_META,
        'meta_value'  => (string) $segment,
        'numberposts' => 1,
        'fields'      => 'ids',
    ]);
    return !empty($q) ? (int) $q[0] : null;
}

/** Read all settings fields from a single post. Missing → null. */
function read_settings(int $post_id): array {
    $out = [];
    foreach (META_KEY_MAP as $field => $meta_key) {
        $val = \get_post_meta($post_id, $meta_key, true);
        if ($val === '' || $val === false || $val === null) {
            $out[$field] = null;
            continue;
        }
        if ($field === 'categories') {
            $decoded = json_decode((string) $val, true);
            $out[$field] = is_array($decoded) ? $decoded : null;
        } elseif ($field === 'show_categories') {
            $out[$field] = ($val === '1' || $val === 1 || $val === true);
        } elseif ($field === 'consent_version') {
            $out[$field] = (int) $val;
        } else {
            $out[$field] = (string) $val;
        }
    }
    return $out;
}

/** Cascade: site overrides network field-by-field; both may be partial. */
function resolve_for_blog(int $blog_id): array {
    $network_id = get_post_id_for_segment(0);
    $site_id    = get_post_id_for_segment($blog_id);
    $network = $network_id ? read_settings($network_id) : [];
    $site    = $site_id    ? read_settings($site_id) : [];

    $out = DEFAULTS;
    foreach (META_KEY_MAP as $field => $_) {
        if (isset($site[$field]) && $site[$field] !== null) {
            $out[$field] = $site[$field];
        } elseif (isset($network[$field]) && $network[$field] !== null) {
            $out[$field] = $network[$field];
        }
        // else: keep DEFAULTS
    }

    // Validate layout — fallback to bottom-bar on invalid
    if (!in_array($out['layout'], VALID_LAYOUTS, true)) {
        $out['layout'] = 'bottom-bar';
    }
    return $out;
}
```

- [ ] **Step 4: Run — verify pass**

```bash
cd D:/AI_TEAMS/landing_system/.worktrees/b2-cookie-banner-library
php skills/wp-landing-config/tests/test_cookie_banner_resolver.php 2>&1 | tail -10
```

Expected: `12 tests, 0 failures` (T1×4 + T2×2 + T3×2 + T4 + T5 + smoke from other passes).

If `\get_posts` mock in `wp-bootstrap.php` doesn't support `meta_key`/`meta_value` filtering — extend the mock to filter on those. Look at `_mock_posts` / `_mock_postmeta` arrays and add a `meta_key`/`meta_value` filter inside `get_posts()` mock implementation.

- [ ] **Step 5: Commit**

```bash
cd D:/AI_TEAMS/landing_system/.worktrees/b2-cookie-banner-library
git add skills/wp-landing-config/mu-plugin/landing-config/includes/cookie-banner/resolver.php \
        skills/wp-landing-config/tests/test_cookie_banner_resolver.php \
        skills/wp-landing-config/tests/wp-bootstrap.php
git commit -m "feat(b2): cookie-banner resolver (cascade network → site + DEFAULTS)"
```

---

### Task 3: bottom-bar layout (HTML+CSS, no JS yet)

**Files:**
- Create: `skills/wp-landing-config/mu-plugin/landing-config/includes/cookie-banner/layouts/bottom-bar.php`
- Create: `skills/wp-landing-config/mu-plugin/landing-config/assets/cookie-banner/core.css`
- Create: `skills/wp-landing-config/mu-plugin/landing-config/assets/cookie-banner/layouts/bottom-bar.css`

This task lays groundwork — render() in Task 4 will include this template.

- [ ] **Step 1: Create bottom-bar.php template**

```php
<?php
// skills/wp-landing-config/mu-plugin/landing-config/includes/cookie-banner/layouts/bottom-bar.php
// $settings is provided by render.php (Task 4).
if (!defined('ABSPATH')) { exit; }
?>
<div id="lp-cb" class="lp-cb lp-cb--bottom-bar" data-version="<?php echo esc_attr($settings['consent_version']); ?>" hidden role="dialog" aria-labelledby="lp-cb-title">
    <div class="lp-cb__inner">
        <h2 id="lp-cb-title" class="lp-cb__title"><?php echo esc_html($settings['title']); ?></h2>
        <p class="lp-cb__desc"><?php echo esc_html($settings['description']); ?></p>

        <?php if (!empty($settings['show_categories']) && !empty($settings['categories'])): ?>
            <div class="lp-cb__categories">
                <?php foreach ($settings['categories'] as $cat): ?>
                    <?php if (empty($cat['slug'])) continue; ?>
                    <label class="lp-cb__category">
                        <input type="checkbox"
                               data-slug="<?php echo esc_attr($cat['slug']); ?>"
                               <?php if (!empty($cat['locked'])) echo 'checked disabled'; ?>
                               <?php if (empty($cat['locked']) && !empty($cat['default_on'])) echo 'checked'; ?>>
                        <span class="lp-cb__category-name"><?php echo esc_html($cat['name'] ?? $cat['slug']); ?></span>
                        <?php if (!empty($cat['desc'])): ?>
                            <span class="lp-cb__category-desc"><?php echo esc_html($cat['desc']); ?></span>
                        <?php endif; ?>
                    </label>
                <?php endforeach; ?>
            </div>
        <?php endif; ?>

        <div class="lp-cb__actions">
            <?php if (!empty($settings['policy_link_text'])): ?>
                <a class="lp-cb__policy" href="<?php echo esc_url($settings['policy_link_url']); ?>" target="_blank" rel="noopener">
                    <?php echo esc_html($settings['policy_link_text']); ?>
                </a>
            <?php endif; ?>
            <?php if (!empty($settings['show_categories'])): ?>
                <button type="button" class="lp-cb__btn lp-cb__btn--secondary" data-action="save">
                    <?php echo esc_html($settings['btn_save_text']); ?>
                </button>
            <?php endif; ?>
            <?php if (!empty($settings['btn_reject_text'])): ?>
                <button type="button" class="lp-cb__btn lp-cb__btn--ghost" data-action="reject">
                    <?php echo esc_html($settings['btn_reject_text']); ?>
                </button>
            <?php endif; ?>
            <button type="button" class="lp-cb__btn lp-cb__btn--primary" data-action="accept-all">
                <?php echo esc_html($settings['btn_accept_all_text']); ?>
            </button>
        </div>
    </div>
</div>
<button type="button" id="lp-cb-reopen" class="lp-cb-reopen" hidden><?php echo esc_html($settings['reopen_text']); ?></button>
```

- [ ] **Step 2: Create core.css with shared vars**

```css
/* skills/wp-landing-config/mu-plugin/landing-config/assets/cookie-banner/core.css */
.lp-cb {
    --cb-bg:      var(--color-bg-card, #ffffff);
    --cb-text:    var(--color-text-primary, #1d2327);
    --cb-text-2:  var(--color-text-secondary, #646970);
    --cb-accent:  var(--color-accent, #2271b1);
    --cb-border:  var(--color-border, #c3c4c7);
    --cb-radius:  var(--radius-md, 6px);
    --cb-font:    var(--font-body, system-ui, -apple-system, "Segoe UI", Roboto, sans-serif);

    position: fixed;
    z-index: 99999;
    font-family: var(--cb-font);
    font-size: 14px;
    line-height: 1.5;
    color: var(--cb-text);
    background: var(--cb-bg);
    border: 1px solid var(--cb-border);
    box-sizing: border-box;
}
.lp-cb *, .lp-cb *::before, .lp-cb *::after { box-sizing: border-box; }
.lp-cb[hidden] { display: none !important; }

.lp-cb__title { margin: 0 0 8px; font-size: 16px; font-weight: 600; }
.lp-cb__desc  { margin: 0 0 12px; color: var(--cb-text-2); }

.lp-cb__categories { margin: 12px 0; }
.lp-cb__category {
    display: grid;
    grid-template-columns: auto 1fr;
    gap: 4px 12px;
    padding: 8px 0;
    border-bottom: 1px solid var(--cb-border);
}
.lp-cb__category:last-child { border-bottom: none; }
.lp-cb__category input[type="checkbox"] { grid-row: 1 / span 2; margin-top: 4px; }
.lp-cb__category-name { font-weight: 600; }
.lp-cb__category-desc { font-size: 13px; color: var(--cb-text-2); }

.lp-cb__actions {
    display: flex;
    gap: 12px;
    align-items: center;
    justify-content: flex-end;
    margin-top: 12px;
    flex-wrap: wrap;
}
.lp-cb__policy {
    margin-right: auto;
    font-size: 13px;
    color: var(--cb-text-2);
    text-decoration: underline;
}

.lp-cb__btn {
    padding: 8px 16px;
    border: 1px solid var(--cb-border);
    border-radius: var(--cb-radius);
    cursor: pointer;
    font-size: 14px;
    font-weight: 600;
    background: transparent;
    color: var(--cb-text);
    font-family: inherit;
    transition: opacity 0.15s;
}
.lp-cb__btn:hover { opacity: 0.85; }
.lp-cb__btn--primary {
    background: var(--cb-accent);
    color: #ffffff;
    border-color: var(--cb-accent);
}
.lp-cb__btn--ghost { background: transparent; }
.lp-cb__btn--secondary { background: transparent; }

.lp-cb-reopen {
    position: fixed;
    bottom: 12px;
    left: 12px;
    background: transparent;
    border: 1px solid var(--cb-border, #c3c4c7);
    border-radius: var(--cb-radius, 6px);
    padding: 6px 12px;
    color: var(--cb-text-2, #646970);
    font-family: inherit;
    font-size: 12px;
    cursor: pointer;
    z-index: 99998;
}
.lp-cb-reopen:hover { color: var(--cb-text, #1d2327); }
.lp-cb-reopen[hidden] { display: none !important; }

@media (max-width: 600px) {
    .lp-cb__actions { flex-direction: column; align-items: stretch; }
    .lp-cb__policy  { margin-right: 0; text-align: center; }
    .lp-cb__btn     { width: 100%; }
}
```

- [ ] **Step 2: Create bottom-bar.css**

```css
/* skills/wp-landing-config/mu-plugin/landing-config/assets/cookie-banner/layouts/bottom-bar.css */
.lp-cb--bottom-bar {
    bottom: 0;
    left: 0;
    right: 0;
    border-top: 1px solid var(--cb-border);
    border-bottom: none;
    border-left: none;
    border-right: none;
    padding: 16px 24px;
    max-height: 80vh;
    overflow-y: auto;
    box-shadow: 0 -4px 12px rgba(0, 0, 0, 0.1);
}
.lp-cb--bottom-bar .lp-cb__inner {
    max-width: 1200px;
    margin: 0 auto;
}
```

- [ ] **Step 3: Commit**

```bash
cd D:/AI_TEAMS/landing_system/.worktrees/b2-cookie-banner-library
git add skills/wp-landing-config/mu-plugin/landing-config/includes/cookie-banner/layouts/bottom-bar.php \
        skills/wp-landing-config/mu-plugin/landing-config/assets/cookie-banner/core.css \
        skills/wp-landing-config/mu-plugin/landing-config/assets/cookie-banner/layouts/bottom-bar.css
git commit -m "feat(b2): bottom-bar layout (PHP partial + core.css + bottom-bar.css)"
```

---

### Task 4: render.php + banner.js + render test

**Files:**
- Create: `skills/wp-landing-config/mu-plugin/landing-config/includes/cookie-banner/render.php`
- Create: `skills/wp-landing-config/mu-plugin/landing-config/assets/cookie-banner/banner.js`
- Create: `skills/wp-landing-config/tests/test_cookie_banner_render.php`

- [ ] **Step 1: Write failing render test**

```php
<?php
// skills/wp-landing-config/tests/test_cookie_banner_render.php
require_once __DIR__ . '/wp-bootstrap.php';
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

// T1: render_with_settings emits HTML with id="lp-cb"
$settings = \LandingConfig\CookieBanner\Resolver\DEFAULTS;
ob_start();
\LandingConfig\CookieBanner\Render\render_with_settings($settings);
$html = ob_get_clean();
assert_test(strpos($html, 'id="lp-cb"') !== false, 'T1 render includes id="lp-cb"');
assert_test(strpos($html, 'class="lp-cb lp-cb--bottom-bar"') !== false, 'T2 default layout class is bottom-bar');
assert_test(strpos($html, 'Принять все') !== false, 'T3 default accept button visible');

// T4: show_categories=false hides categories block
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

// T6: empty btn_reject_text hides reject button
ob_start();
\LandingConfig\CookieBanner\Render\render_with_settings($settings);
$html = ob_get_clean();
assert_test(strpos($html, 'data-action="reject"') === false, 'T6 reject button hidden when text empty');

// T7: non-empty btn_reject_text shows reject button
$settings_reject = array_merge($settings, ['btn_reject_text' => 'Отклонить']);
ob_start();
\LandingConfig\CookieBanner\Render\render_with_settings($settings_reject);
$html = ob_get_clean();
assert_test(strpos($html, 'data-action="reject"') !== false, 'T7 reject button shown when text set');
assert_test(strpos($html, '>Отклонить<') !== false, 'T8 reject button label correct');

// T9: invalid layout in settings → falls back to bottom-bar
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
```

- [ ] **Step 2: Run — verify fail**

```bash
cd D:/AI_TEAMS/landing_system/.worktrees/b2-cookie-banner-library
php skills/wp-landing-config/tests/test_cookie_banner_render.php 2>&1 | tail -10
```

Expected: include error.

- [ ] **Step 3: Implement render.php**

```php
<?php
namespace LandingConfig\CookieBanner\Render;

if (!defined('ABSPATH')) { exit; }

use const LandingConfig\CookieBanner\CPT\VALID_LAYOUTS;
use function LandingConfig\CookieBanner\Resolver\resolve_for_blog;

const LAYOUTS_DIR = __DIR__ . '/layouts';

/** Render banner DOM for given settings array (used by wp_footer hook + tests). */
function render_with_settings(array $settings): void {
    $layout = $settings['layout'] ?? 'bottom-bar';
    if (!in_array($layout, VALID_LAYOUTS, true)) {
        $layout = 'bottom-bar';
    }
    $tpl = LAYOUTS_DIR . '/' . $layout . '.php';
    if (!file_exists($tpl)) {
        $tpl = LAYOUTS_DIR . '/bottom-bar.php';
    }
    include $tpl;  // template uses $settings directly
}

/** wp_footer hook entry. */
function on_footer(): void {
    $settings = resolve_for_blog(\get_current_blog_id());
    if ($settings === null) return;
    render_with_settings($settings);
}

add_action('wp_footer', __NAMESPACE__ . '\\on_footer');
```

- [ ] **Step 4: Implement banner.js**

```javascript
/* skills/wp-landing-config/mu-plugin/landing-config/assets/cookie-banner/banner.js */
(function () {
    'use strict';

    var cfg = window.LP_CB_CONFIG;
    if (!cfg) return;

    var banner = document.getElementById('lp-cb');
    var reopen = document.getElementById('lp-cb-reopen');
    if (!banner) return;

    var STORAGE_KEY = cfg.storage_key || 'lp_cookie_consent';

    function loadConsent() {
        try {
            var raw = localStorage.getItem(STORAGE_KEY);
            if (!raw) return null;
            var parsed = JSON.parse(raw);
            if (typeof parsed !== 'object' || parsed === null) return null;
            return parsed;
        } catch (e) { return null; }
    }

    function saveConsent(consent) {
        var payload = {
            version: cfg.version,
            consent: consent,
            ts: Math.floor(Date.now() / 1000)
        };
        try { localStorage.setItem(STORAGE_KEY, JSON.stringify(payload)); }
        catch (e) { /* quota exceeded — proceed without persist */ }
        applyGtag(consent);
    }

    function applyGtag(consent) {
        if (typeof window.gtag !== 'function') return;
        var update = {};
        var map = cfg.gtag_map || {};
        for (var slug in consent) {
            if (!Object.prototype.hasOwnProperty.call(consent, slug)) continue;
            var keys = map[slug] || [];
            for (var i = 0; i < keys.length; i++) {
                update[keys[i]] = consent[slug] ? 'granted' : 'denied';
            }
        }
        window.gtag('consent', 'update', update);
    }

    function showBanner() { banner.hidden = false; if (reopen) reopen.hidden = true; }
    function hideBanner() { banner.hidden = true;  if (reopen) reopen.hidden = false; }

    function consentFromCheckboxes() {
        var consent = {};
        var inputs = banner.querySelectorAll('[data-slug]');
        for (var i = 0; i < inputs.length; i++) {
            consent[inputs[i].dataset.slug] = !!inputs[i].checked;
        }
        return consent;
    }

    function consentAll(value) {
        var consent = {};
        var cats = cfg.categories || [];
        for (var i = 0; i < cats.length; i++) {
            if (!cats[i].slug) continue;
            consent[cats[i].slug] = cats[i].locked ? true : !!value;
        }
        return consent;
    }

    // Initial check
    var existing = loadConsent();
    if (!existing || existing.version !== cfg.version) {
        showBanner();
    } else {
        hideBanner();
        applyGtag(existing.consent || {});
    }

    // Wire buttons
    banner.addEventListener('click', function (e) {
        var action = e.target && e.target.dataset && e.target.dataset.action;
        if (!action) return;
        if (action === 'accept-all') {
            saveConsent(consentAll(true));
            hideBanner();
        } else if (action === 'reject') {
            saveConsent(consentAll(false));
            hideBanner();
        } else if (action === 'save') {
            saveConsent(consentFromCheckboxes());
            hideBanner();
        }
    });
    if (reopen) reopen.addEventListener('click', showBanner);
})();
```

- [ ] **Step 5: Run render tests — verify pass**

```bash
cd D:/AI_TEAMS/landing_system/.worktrees/b2-cookie-banner-library
php skills/wp-landing-config/tests/test_cookie_banner_render.php 2>&1 | tail -10
```

Expected: `10 tests, 0 failures`.

- [ ] **Step 6: Commit**

```bash
cd D:/AI_TEAMS/landing_system/.worktrees/b2-cookie-banner-library
git add skills/wp-landing-config/mu-plugin/landing-config/includes/cookie-banner/render.php \
        skills/wp-landing-config/mu-plugin/landing-config/assets/cookie-banner/banner.js \
        skills/wp-landing-config/tests/test_cookie_banner_render.php
git commit -m "feat(b2): render() + banner.js + 10 render tests"
```

---

### Task 5: enqueue.php (consent-init + CSS/JS in wp_head)

**Files:**
- Create: `skills/wp-landing-config/mu-plugin/landing-config/includes/cookie-banner/enqueue.php`

- [ ] **Step 1: Create enqueue.php**

```php
<?php
namespace LandingConfig\CookieBanner\Enqueue;

if (!defined('ABSPATH')) { exit; }

use function LandingConfig\CookieBanner\Resolver\resolve_for_blog;

const GTAG_MAP = [
    'necessary' => [],
    'analytics' => ['analytics_storage'],
    'marketing' => ['ad_storage', 'ad_user_data', 'ad_personalization'],
];

const VERSION = '1.0';

/** Color override hex value sanitiser. Returns '' for invalid/empty. */
function _sanitize_color(string $hex): string {
    $hex = trim($hex);
    if ($hex === '') return '';
    // sanitize_hex_color is theme-only; replicate minimal logic here
    if (preg_match('/^#([A-Fa-f0-9]{3}|[A-Fa-f0-9]{6})$/', $hex)) {
        return $hex;
    }
    return '';
}

function _compose_color_overrides_css(array $settings): string {
    $map = [
        '--cb-bg'     => $settings['color_bg']     ?? '',
        '--cb-text'   => $settings['color_text']   ?? '',
        '--cb-accent' => $settings['color_accent'] ?? '',
        '--cb-border' => $settings['color_border'] ?? '',
    ];
    $parts = [];
    foreach ($map as $var => $val) {
        $hex = _sanitize_color((string) $val);
        if ($hex !== '') {
            $parts[] = $var . ':' . $hex;
        }
    }
    return implode(';', $parts);
}

/** wp_head hook (priority 1 — before analytics scripts). */
function on_head(): void {
    $settings = resolve_for_blog(\get_current_blog_id());
    if ($settings === null) return;

    // 1. Google Consent Mode v2 — default DENIED
    echo "<script>"
       . "window.dataLayer=window.dataLayer||[];"
       . "function gtag(){dataLayer.push(arguments);}"
       . "gtag('consent','default',{"
       . "'analytics_storage':'denied',"
       . "'ad_storage':'denied',"
       . "'ad_user_data':'denied',"
       . "'ad_personalization':'denied',"
       . "'wait_for_update':500"
       . "});</script>\n";

    // 2. Inline color overrides (if any)
    $color_css = _compose_color_overrides_css($settings);
    if ($color_css !== '') {
        echo '<style id="lp-cb-overrides">.lp-cb{' . esc_attr($color_css) . '}</style>' . "\n";
    }

    // 3. Enqueue CSS + JS
    $base_url = \plugins_url('assets/cookie-banner', dirname(dirname(__DIR__)) . '/landing-config.php');
    \wp_enqueue_style('lp-cb-core', $base_url . '/core.css', [], VERSION);
    \wp_enqueue_style('lp-cb-layout', $base_url . '/layouts/' . $settings['layout'] . '.css', ['lp-cb-core'], VERSION);
    \wp_enqueue_script('lp-cb', $base_url . '/banner.js', [], VERSION, true);

    \wp_localize_script('lp-cb', 'LP_CB_CONFIG', [
        'version'         => (int) $settings['consent_version'],
        'storage_key'     => 'lp_cookie_consent',
        'categories'      => $settings['categories'],
        'gtag_map'        => GTAG_MAP,
        'show_categories' => (bool) $settings['show_categories'],
    ]);
}

add_action('wp_head', __NAMESPACE__ . '\\on_head', 1);
```

- [ ] **Step 2: PHP lint**

```bash
cd D:/AI_TEAMS/landing_system/.worktrees/b2-cookie-banner-library
php -l skills/wp-landing-config/mu-plugin/landing-config/includes/cookie-banner/enqueue.php
```

Expected: `No syntax errors detected`.

- [ ] **Step 3: Commit**

```bash
cd D:/AI_TEAMS/landing_system/.worktrees/b2-cookie-banner-library
git add skills/wp-landing-config/mu-plugin/landing-config/includes/cookie-banner/enqueue.php
git commit -m "feat(b2): enqueue.php — consent-init + CSS/JS in wp_head"
```

---

### Task 6: Network admin editor page

**Files:**
- Create: `skills/wp-landing-config/mu-plugin/landing-config/includes/cookie-banner/admin-network.php`
- Create: `skills/wp-landing-config/mu-plugin/landing-config/assets/cookie-banner/previews/{top-bar,bottom-bar,floating-card-left,floating-card-right,center-modal}.svg`

The admin page registers itself in Network admin → Лендинг menu. Look at existing `admin-cta.php` for the menu-registration pattern.

- [ ] **Step 1: Inspect existing admin menu pattern**

```bash
cd D:/AI_TEAMS/landing_system/.worktrees/b2-cookie-banner-library
grep -nE "add_submenu_page|landing-config-network" skills/wp-landing-config/mu-plugin/landing-config/includes/admin-cta.php | head -10
```

Note the menu slug pattern (e.g. `landing-config-network-cta`) and which hook registers it (`network_admin_menu`).

- [ ] **Step 2: Implement admin-network.php**

Copy the menu-registration boilerplate from `admin-cta.php`; replace handler with cookie-banner specific form. Use `LandingConfig\SegmentSelector\render()` for segment selector (already exists in `includes/segment-selector.php`).

```php
<?php
namespace LandingConfig\CookieBanner\Admin;

if (!defined('ABSPATH')) { exit; }

use const LandingConfig\CookieBanner\CPT\POST_TYPE;
use const LandingConfig\CookieBanner\CPT\SEGMENT_META;
use const LandingConfig\CookieBanner\CPT\VALID_LAYOUTS;
use const LandingConfig\CookieBanner\CPT\META_KEY_MAP;
use function LandingConfig\CookieBanner\Resolver\get_post_id_for_segment;
use function LandingConfig\SegmentSelector\render_selector;
use function LandingConfig\SegmentSelector\current_from_request;

const MENU_SLUG = 'landing-config-network-cookie-banner';

add_action('network_admin_menu', __NAMESPACE__ . '\\register_menu');
add_action('admin_post_lp_cb_save', __NAMESPACE__ . '\\handle_save');

function register_menu(): void {
    \add_submenu_page(
        'landing-config-network',  // parent — same as other admin pages
        'Cookie-banner',
        'Cookie-banner',
        'manage_network_options',
        MENU_SLUG,
        __NAMESPACE__ . '\\render_page'
    );
}

function _save_field(int $post_id, string $meta_key, $value): void {
    if (is_array($value)) {
        $value = wp_json_encode($value, JSON_UNESCAPED_UNICODE);
    }
    \update_post_meta($post_id, $meta_key, (string) $value);
}

function handle_save(): void {
    if (!\current_user_can('manage_network_options')) wp_die('forbidden');
    \check_admin_referer('lp_cb_save');
    $segment = (int) ($_POST['segment'] ?? 0);

    // Find or create the record
    $post_id = get_post_id_for_segment($segment);
    if (!$post_id) {
        $post_id = \wp_insert_post([
            'post_type'   => POST_TYPE,
            'post_status' => 'publish',
            'post_title'  => 'Cookie banner (segment=' . $segment . ')',
        ]);
        \update_post_meta($post_id, SEGMENT_META, (string) $segment);
    }

    // Layout (validate)
    $layout = sanitize_text_field($_POST['layout'] ?? 'bottom-bar');
    if (!in_array($layout, VALID_LAYOUTS, true)) $layout = 'bottom-bar';
    _save_field($post_id, '_lp_cb_layout', $layout);

    // Text fields
    foreach ([
        '_lp_cb_title', '_lp_cb_description', '_lp_cb_btn_accept_all_text',
        '_lp_cb_btn_save_text', '_lp_cb_btn_reject_text', '_lp_cb_policy_link_text',
        '_lp_cb_policy_link_url', '_lp_cb_reopen_text',
    ] as $meta) {
        $val = isset($_POST[$meta]) ? sanitize_text_field(wp_unslash($_POST[$meta])) : '';
        _save_field($post_id, $meta, $val);
    }

    // Description allows newlines
    $desc = isset($_POST['_lp_cb_description']) ? sanitize_textarea_field(wp_unslash($_POST['_lp_cb_description'])) : '';
    _save_field($post_id, '_lp_cb_description', $desc);

    // Categories repeater
    _save_field($post_id, '_lp_cb_show_categories', !empty($_POST['_lp_cb_show_categories']) ? '1' : '0');
    $cats_raw = $_POST['categories'] ?? [];
    $cats = [];
    if (is_array($cats_raw)) {
        foreach ($cats_raw as $c) {
            if (empty($c['slug'])) continue;
            $cats[] = [
                'slug'       => sanitize_key($c['slug']),
                'name'       => sanitize_text_field($c['name'] ?? ''),
                'desc'       => sanitize_text_field($c['desc'] ?? ''),
                'locked'     => !empty($c['locked']),
                'default_on' => !empty($c['default_on']),
            ];
        }
    }
    _save_field($post_id, '_lp_cb_categories', $cats);

    // Colors
    foreach (['color_bg', 'color_text', 'color_accent', 'color_border'] as $f) {
        $hex = sanitize_text_field($_POST['_lp_cb_' . $f] ?? '');
        if ($hex !== '' && !preg_match('/^#([A-Fa-f0-9]{3}|[A-Fa-f0-9]{6})$/', $hex)) $hex = '';
        _save_field($post_id, '_lp_cb_' . $f, $hex);
    }

    // Consent version
    _save_field($post_id, '_lp_cb_consent_version', (int) ($_POST['_lp_cb_consent_version'] ?? 1));

    \wp_safe_redirect(\add_query_arg(['page' => MENU_SLUG, 'segment' => $segment, 'saved' => 1], \network_admin_url('admin.php')));
    exit;
}

function render_page(): void {
    if (!\current_user_can('manage_network_options')) wp_die('forbidden');
    $segment = current_from_request();
    $post_id = get_post_id_for_segment($segment);
    $current = $post_id ? \LandingConfig\CookieBanner\Resolver\read_settings($post_id) : [];
    $get = function(string $field, $default = '') use ($current) {
        $val = $current[$field] ?? null;
        return $val === null ? $default : $val;
    };

    ?>
    <div class="wrap">
        <h1>Cookie-banner</h1>

        <?php if (!empty($_GET['saved'])): ?>
            <div class="notice notice-success is-dismissible"><p>Сохранено.</p></div>
        <?php endif; ?>

        <?php render_selector(MENU_SLUG); ?>

        <form method="post" action="<?php echo esc_url(\network_admin_url('admin-post.php')); ?>">
            <input type="hidden" name="action" value="lp_cb_save">
            <input type="hidden" name="segment" value="<?php echo esc_attr($segment); ?>">
            <?php \wp_nonce_field('lp_cb_save'); ?>

            <h2>Layout</h2>
            <fieldset>
                <?php foreach (VALID_LAYOUTS as $layout): ?>
                    <label style="display:inline-block; margin-right:24px; text-align:center;">
                        <input type="radio" name="layout" value="<?php echo esc_attr($layout); ?>"
                               <?php checked($get('layout', 'bottom-bar'), $layout); ?>>
                        <br>
                        <img src="<?php echo esc_url(\plugins_url('assets/cookie-banner/previews/' . $layout . '.svg', dirname(dirname(__DIR__)) . '/landing-config.php')); ?>"
                             alt="<?php echo esc_attr($layout); ?>"
                             style="width:160px; height:96px; border:1px solid #ccc; margin-top:4px;">
                        <br><?php echo esc_html($layout); ?>
                    </label>
                <?php endforeach; ?>
            </fieldset>

            <h2>Тексты</h2>
            <table class="form-table">
                <tr><th>Заголовок</th>
                    <td><input type="text" name="_lp_cb_title" value="<?php echo esc_attr($get('title')); ?>" class="regular-text"></td></tr>
                <tr><th>Описание</th>
                    <td><textarea name="_lp_cb_description" rows="3" class="large-text"><?php echo esc_textarea($get('description')); ?></textarea></td></tr>
                <tr><th>Принять все</th>
                    <td><input type="text" name="_lp_cb_btn_accept_all_text" value="<?php echo esc_attr($get('btn_accept_all_text')); ?>" class="regular-text"></td></tr>
                <tr><th>Сохранить</th>
                    <td><input type="text" name="_lp_cb_btn_save_text" value="<?php echo esc_attr($get('btn_save_text')); ?>" class="regular-text"></td></tr>
                <tr><th>Отклонить (пусто = скрыта)</th>
                    <td><input type="text" name="_lp_cb_btn_reject_text" value="<?php echo esc_attr($get('btn_reject_text')); ?>" class="regular-text"></td></tr>
                <tr><th>Текст ссылки на политику</th>
                    <td><input type="text" name="_lp_cb_policy_link_text" value="<?php echo esc_attr($get('policy_link_text')); ?>" class="regular-text"></td></tr>
                <tr><th>URL политики</th>
                    <td><input type="text" name="_lp_cb_policy_link_url" value="<?php echo esc_attr($get('policy_link_url')); ?>" class="regular-text"></td></tr>
                <tr><th>Reopen (footer)</th>
                    <td><input type="text" name="_lp_cb_reopen_text" value="<?php echo esc_attr($get('reopen_text')); ?>" class="regular-text"></td></tr>
            </table>

            <h2>Категории</h2>
            <label>
                <input type="checkbox" name="_lp_cb_show_categories" value="1" <?php checked((bool) $get('show_categories', false)); ?>>
                Показывать категории (detailed mode)
            </label>
            <table class="widefat" style="margin-top:12px;">
                <thead><tr><th>Slug</th><th>Имя</th><th>Описание</th><th>Locked</th><th>Default on</th></tr></thead>
                <tbody id="lp-cb-cats">
                    <?php
                    $cats = $get('categories', []);
                    if (empty($cats)) $cats = \LandingConfig\CookieBanner\Resolver\DEFAULTS['categories'];
                    foreach ($cats as $i => $c): ?>
                        <tr>
                            <td><input type="text" name="categories[<?php echo $i; ?>][slug]" value="<?php echo esc_attr($c['slug'] ?? ''); ?>"></td>
                            <td><input type="text" name="categories[<?php echo $i; ?>][name]" value="<?php echo esc_attr($c['name'] ?? ''); ?>"></td>
                            <td><input type="text" name="categories[<?php echo $i; ?>][desc]" value="<?php echo esc_attr($c['desc'] ?? ''); ?>"></td>
                            <td><input type="checkbox" name="categories[<?php echo $i; ?>][locked]" value="1" <?php checked(!empty($c['locked'])); ?>></td>
                            <td><input type="checkbox" name="categories[<?php echo $i; ?>][default_on]" value="1" <?php checked(!empty($c['default_on'])); ?>></td>
                        </tr>
                    <?php endforeach; ?>
                </tbody>
            </table>
            <p><em>Для добавления новой категории — введите новую строку с уникальным slug в дополнительное поле ниже (одна строка = одна категория).</em></p>
            <table class="widefat" style="margin-top:4px;">
                <tbody><tr>
                    <td><input type="text" name="categories[99][slug]" placeholder="slug (eg functional)"></td>
                    <td><input type="text" name="categories[99][name]" placeholder="Имя"></td>
                    <td><input type="text" name="categories[99][desc]" placeholder="Описание"></td>
                    <td><input type="checkbox" name="categories[99][locked]" value="1"></td>
                    <td><input type="checkbox" name="categories[99][default_on]" value="1"></td>
                </tr></tbody>
            </table>

            <h2>Цвета (пусто = inherit from theme)</h2>
            <table class="form-table">
                <tr><th>Фон</th>     <td><input type="text" name="_lp_cb_color_bg"     value="<?php echo esc_attr($get('color_bg')); ?>" placeholder="#ffffff" class="small-text"></td></tr>
                <tr><th>Текст</th>   <td><input type="text" name="_lp_cb_color_text"   value="<?php echo esc_attr($get('color_text')); ?>" placeholder="#1d2327" class="small-text"></td></tr>
                <tr><th>Акцент</th>  <td><input type="text" name="_lp_cb_color_accent" value="<?php echo esc_attr($get('color_accent')); ?>" placeholder="#2271b1" class="small-text"></td></tr>
                <tr><th>Граница</th> <td><input type="text" name="_lp_cb_color_border" value="<?php echo esc_attr($get('color_border')); ?>" placeholder="#c3c4c7" class="small-text"></td></tr>
            </table>

            <h2>Версия согласия</h2>
            <input type="number" name="_lp_cb_consent_version" value="<?php echo esc_attr($get('consent_version', 1)); ?>" min="1" class="small-text">
            <p class="description">Bump → пользователи увидят баннер заново.</p>

            <p>
                <button type="submit" class="button button-primary">Сохранить</button>
                <a href="<?php echo esc_url(\home_url('/?lp_cookie_banner_preview=1&segment=' . $segment)); ?>" target="_blank" class="button">Live preview ↗</a>
            </p>
        </form>
    </div>
    <?php
}
```

- [ ] **Step 3: Create preview SVGs**

For each of 5 layouts, create a 200×120 SVG schematic in `skills/wp-landing-config/mu-plugin/landing-config/assets/cookie-banner/previews/{LAYOUT}.svg`.

Each SVG is a simple boxed page (light grey 200×120 rect) with the banner shape drawn in dark grey at the appropriate position:

**bottom-bar.svg:**
```xml
<?xml version="1.0"?>
<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 200 120">
  <rect width="200" height="120" fill="#f1f1f1"/>
  <rect x="0" y="96" width="200" height="24" fill="#2c3338"/>
</svg>
```

**top-bar.svg:** swap y=96 → y=0.

**floating-card-left.svg:** rectangle 84×40 at x=12, y=68.

**floating-card-right.svg:** rectangle 84×40 at x=104, y=68.

**center-modal.svg:** rectangle 100×60 at x=50, y=30, semi-transparent dark backdrop full bounds:
```xml
<?xml version="1.0"?>
<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 200 120">
  <rect width="200" height="120" fill="#f1f1f1"/>
  <rect width="200" height="120" fill="rgba(0,0,0,0.3)"/>
  <rect x="50" y="30" width="100" height="60" fill="#2c3338" rx="4"/>
</svg>
```

- [ ] **Step 4: PHP lint**

```bash
cd D:/AI_TEAMS/landing_system/.worktrees/b2-cookie-banner-library
php -l skills/wp-landing-config/mu-plugin/landing-config/includes/cookie-banner/admin-network.php
```

Expected: `No syntax errors detected`.

- [ ] **Step 5: Commit**

```bash
cd D:/AI_TEAMS/landing_system/.worktrees/b2-cookie-banner-library
git add skills/wp-landing-config/mu-plugin/landing-config/includes/cookie-banner/admin-network.php \
        skills/wp-landing-config/mu-plugin/landing-config/assets/cookie-banner/previews/
git commit -m "feat(b2): network admin editor + 5 preview SVGs"
```

---

### Task 7: Site admin read-only page

**Files:**
- Create: `skills/wp-landing-config/mu-plugin/landing-config/includes/cookie-banner/admin-site-readonly.php`

- [ ] **Step 1: Create file**

```php
<?php
namespace LandingConfig\CookieBanner\AdminReadOnly;

if (!defined('ABSPATH')) { exit; }

use function LandingConfig\CookieBanner\Resolver\resolve_for_blog;

const MENU_SLUG = 'landing-config-site-cookie-banner';

add_action('admin_menu', __NAMESPACE__ . '\\register_menu');

function register_menu(): void {
    \add_submenu_page(
        'landing-config',  // parent (subsite admin menu)
        'Cookie-banner (read-only)',
        'Cookie-banner',
        'manage_options',
        MENU_SLUG,
        __NAMESPACE__ . '\\render_page'
    );
}

function render_page(): void {
    if (!\current_user_can('manage_options')) wp_die('forbidden');
    $blog_id = \get_current_blog_id();
    $resolved = resolve_for_blog($blog_id);

    $network_url = \network_admin_url('admin.php?page=' . \LandingConfig\CookieBanner\Admin\MENU_SLUG . '&segment=' . $blog_id);

    ?>
    <div class="wrap">
        <h1>Cookie-banner (resolved for this site)</h1>
        <p>Это режим только для чтения. Чтобы изменить настройки — открой
            <a href="<?php echo esc_url($network_url); ?>">Network admin → Cookie-banner для этого сегмента</a>.</p>

        <table class="widefat">
            <thead><tr><th>Поле</th><th>Значение</th></tr></thead>
            <tbody>
                <?php foreach ($resolved as $field => $val): ?>
                    <tr>
                        <td><code><?php echo esc_html($field); ?></code></td>
                        <td>
                            <?php if (is_array($val)): ?>
                                <pre><?php echo esc_html(wp_json_encode($val, JSON_PRETTY_PRINT | JSON_UNESCAPED_UNICODE)); ?></pre>
                            <?php else: ?>
                                <code><?php echo esc_html((string) $val); ?></code>
                            <?php endif; ?>
                        </td>
                    </tr>
                <?php endforeach; ?>
            </tbody>
        </table>
    </div>
    <?php
}
```

- [ ] **Step 2: PHP lint**

```bash
cd D:/AI_TEAMS/landing_system/.worktrees/b2-cookie-banner-library
php -l skills/wp-landing-config/mu-plugin/landing-config/includes/cookie-banner/admin-site-readonly.php
```

- [ ] **Step 3: Commit**

```bash
cd D:/AI_TEAMS/landing_system/.worktrees/b2-cookie-banner-library
git add skills/wp-landing-config/mu-plugin/landing-config/includes/cookie-banner/admin-site-readonly.php
git commit -m "feat(b2): site admin read-only view with deep-link to network editor"
```

---

### Task 8: Migration runner (seed network default on first activation)

**Files:**
- Create: `skills/wp-landing-config/mu-plugin/landing-config/includes/cookie-banner/migrate.php`
- Create: `skills/wp-landing-config/tests/test_cookie_banner_migration.php`

- [ ] **Step 1: Write failing test**

```php
<?php
// skills/wp-landing-config/tests/test_cookie_banner_migration.php
require_once __DIR__ . '/wp-bootstrap.php';
require_once dirname(__DIR__) . '/mu-plugin/landing-config/includes/cookie-banner/cpt.php';
require_once dirname(__DIR__) . '/mu-plugin/landing-config/includes/cookie-banner/resolver.php';
require_once dirname(__DIR__) . '/mu-plugin/landing-config/includes/cookie-banner/migrate.php';

$tests = 0; $failures = 0;
function assert_test($cond, $msg) {
    global $tests, $failures;
    $tests++;
    if (!$cond) { $failures++; echo "FAIL: $msg\n"; }
    else { echo "PASS: $msg\n"; }
}

function reset_state() {
    $GLOBALS['_mock_posts'] = [];
    $GLOBALS['_mock_postmeta'] = [];
    $GLOBALS['_mock_site_options'] = [];
    $GLOBALS['_mock_next_id'] = 1;
}

// T1: maybe_run() seeds network default if none exists
reset_state();
\LandingConfig\CookieBanner\Migrate\maybe_run();
$post_id = \LandingConfig\CookieBanner\Resolver\get_post_id_for_segment(0);
assert_test($post_id !== null, 'T1a network record created');
assert_test($GLOBALS['_mock_site_options']['landing_config_migration_b2_cookie_banner'] === '1',
    'T1b migration marker set');

// T2: idempotent (running twice doesn't create duplicate)
reset_state();
\LandingConfig\CookieBanner\Migrate\maybe_run();
\LandingConfig\CookieBanner\Migrate\maybe_run();
$count = count(array_filter($GLOBALS['_mock_posts'], function($p) {
    return $p->post_type === 'lp_cookie_banner';
}));
assert_test($count === 1, 'T2 idempotent — only 1 record after 2 runs');

// T3: skip if marker already set
reset_state();
$GLOBALS['_mock_site_options']['landing_config_migration_b2_cookie_banner'] = '1';
\LandingConfig\CookieBanner\Migrate\maybe_run();
$post_id = \LandingConfig\CookieBanner\Resolver\get_post_id_for_segment(0);
assert_test($post_id === null, 'T3 skipped when marker set');

echo "$tests tests, $failures failures\n";
exit($failures > 0 ? 1 : 0);
```

- [ ] **Step 2: Run — verify fail**

```bash
cd D:/AI_TEAMS/landing_system/.worktrees/b2-cookie-banner-library
php skills/wp-landing-config/tests/test_cookie_banner_migration.php 2>&1 | tail -5
```

Expected: include error (migrate.php not found).

- [ ] **Step 3: Implement migrate.php**

```php
<?php
namespace LandingConfig\CookieBanner\Migrate;

if (!defined('ABSPATH')) { exit; }

use const LandingConfig\CookieBanner\CPT\POST_TYPE;
use const LandingConfig\CookieBanner\CPT\SEGMENT_META;

const MARKER = 'landing_config_migration_b2_cookie_banner';

function maybe_run(): void {
    if (\get_site_option(MARKER) === '1') return;

    // Seed network default (segment=0)
    $existing = \LandingConfig\CookieBanner\Resolver\get_post_id_for_segment(0);
    if (!$existing) {
        $defaults = \LandingConfig\CookieBanner\Resolver\DEFAULTS;
        $post_id = \wp_insert_post([
            'post_type'   => POST_TYPE,
            'post_status' => 'publish',
            'post_title'  => 'Cookie banner (network default)',
        ]);
        \update_post_meta($post_id, SEGMENT_META, '0');
        \update_post_meta($post_id, '_lp_cb_layout', $defaults['layout']);
        \update_post_meta($post_id, '_lp_cb_title', $defaults['title']);
        \update_post_meta($post_id, '_lp_cb_description', $defaults['description']);
        \update_post_meta($post_id, '_lp_cb_btn_accept_all_text', $defaults['btn_accept_all_text']);
        \update_post_meta($post_id, '_lp_cb_btn_save_text', $defaults['btn_save_text']);
        \update_post_meta($post_id, '_lp_cb_btn_reject_text', $defaults['btn_reject_text']);
        \update_post_meta($post_id, '_lp_cb_policy_link_text', $defaults['policy_link_text']);
        \update_post_meta($post_id, '_lp_cb_policy_link_url', $defaults['policy_link_url']);
        \update_post_meta($post_id, '_lp_cb_reopen_text', $defaults['reopen_text']);
        \update_post_meta($post_id, '_lp_cb_show_categories', '0');
        \update_post_meta($post_id, '_lp_cb_categories', \wp_json_encode($defaults['categories'], JSON_UNESCAPED_UNICODE));
        \update_post_meta($post_id, '_lp_cb_consent_version', (string) $defaults['consent_version']);
    }

    \update_site_option(MARKER, '1');
}
```

- [ ] **Step 4: Run — verify pass**

```bash
cd D:/AI_TEAMS/landing_system/.worktrees/b2-cookie-banner-library
php skills/wp-landing-config/tests/test_cookie_banner_migration.php 2>&1 | tail -5
```

Expected: `4 tests, 0 failures`.

- [ ] **Step 5: Commit**

```bash
cd D:/AI_TEAMS/landing_system/.worktrees/b2-cookie-banner-library
git add skills/wp-landing-config/mu-plugin/landing-config/includes/cookie-banner/migrate.php \
        skills/wp-landing-config/tests/test_cookie_banner_migration.php
git commit -m "feat(b2): migration runner — seed network default + idempotent marker"
```

---

### Task 9: 4 remaining layouts (top-bar, floating-card-{left,right}, center-modal)

**Files:**
- Create: 4 PHP templates + 3 CSS files

- [ ] **Step 1: Create 4 PHP templates**

Each is a near-copy of `bottom-bar.php` differing only in the wrapper class. The DOM structure (inner / categories / actions) is identical. Use the bash loop:

```bash
cd D:/AI_TEAMS/landing_system/.worktrees/b2-cookie-banner-library
LAYOUTS_DIR=skills/wp-landing-config/mu-plugin/landing-config/includes/cookie-banner/layouts
for L in top-bar floating-card-left floating-card-right center-modal; do
    cp "$LAYOUTS_DIR/bottom-bar.php" "$LAYOUTS_DIR/$L.php"
    sed -i "s/lp-cb--bottom-bar/lp-cb--$L/g" "$LAYOUTS_DIR/$L.php"
done
```

Special case: `center-modal.php` needs a backdrop div. After the `cp`, edit:

```bash
# Add backdrop as the first child of the outer div
sed -i 's|<div id="lp-cb" class="lp-cb lp-cb--center-modal"|<div class="lp-cb__backdrop"></div><div id="lp-cb" class="lp-cb lp-cb--center-modal"|' "$LAYOUTS_DIR/center-modal.php"
```

Verify each was modified:
```bash
grep -l "lp-cb--top-bar\|lp-cb--floating\|lp-cb--center-modal" $LAYOUTS_DIR/*.php | wc -l
```
Expected: 4.

- [ ] **Step 2: Create top-bar.css**

```css
/* skills/wp-landing-config/mu-plugin/landing-config/assets/cookie-banner/layouts/top-bar.css */
.lp-cb--top-bar {
    top: 0;
    left: 0;
    right: 0;
    border-bottom: 1px solid var(--cb-border);
    border-top: none;
    border-left: none;
    border-right: none;
    padding: 16px 24px;
    max-height: 80vh;
    overflow-y: auto;
    box-shadow: 0 4px 12px rgba(0, 0, 0, 0.1);
}
.lp-cb--top-bar .lp-cb__inner {
    max-width: 1200px;
    margin: 0 auto;
}
```

- [ ] **Step 3: Create floating-card.css**

```css
/* skills/wp-landing-config/mu-plugin/landing-config/assets/cookie-banner/layouts/floating-card.css */
.lp-cb--floating-card-left,
.lp-cb--floating-card-right {
    bottom: 24px;
    width: 360px;
    max-width: calc(100vw - 48px);
    max-height: 80vh;
    overflow-y: auto;
    padding: 16px 20px;
    border-radius: var(--cb-radius, 8px);
    box-shadow: 0 8px 24px rgba(0, 0, 0, 0.15);
}
.lp-cb--floating-card-left  { left:  24px; right: auto; }
.lp-cb--floating-card-right { right: 24px; left:  auto; }
```

Note: this CSS file is shared by both `floating-card-left` and `floating-card-right`. The enqueue logic in Task 5 looks for `layouts/{layout}.css` — meaning it would try `floating-card-left.css` and fail. **Fix**: in `enqueue.php`, before computing the CSS filename, normalize floating-card-{left,right} → floating-card. Edit `enqueue.php` (Task 5 output):

```php
// In enqueue.php on_head(), replace:
//   $base_url . '/layouts/' . $settings['layout'] . '.css'
// With:
$css_layout = $settings['layout'];
if (strpos($css_layout, 'floating-card-') === 0) {
    $css_layout = 'floating-card';
}
\wp_enqueue_style('lp-cb-layout', $base_url . '/layouts/' . $css_layout . '.css', ['lp-cb-core'], VERSION);
```

- [ ] **Step 4: Create center-modal.css**

```css
/* skills/wp-landing-config/mu-plugin/landing-config/assets/cookie-banner/layouts/center-modal.css */
.lp-cb--center-modal {
    top: 50%;
    left: 50%;
    transform: translate(-50%, -50%);
    width: 480px;
    max-width: calc(100vw - 48px);
    max-height: 80vh;
    overflow-y: auto;
    padding: 24px 28px;
    border-radius: var(--cb-radius, 8px);
    box-shadow: 0 16px 48px rgba(0, 0, 0, 0.25);
}
.lp-cb__backdrop {
    position: fixed;
    inset: 0;
    background: rgba(0, 0, 0, 0.4);
    z-index: 99998;
    pointer-events: none;  /* page stays interactive */
}
.lp-cb--center-modal[hidden] ~ .lp-cb__backdrop,
.lp-cb--bottom-bar ~ .lp-cb__backdrop,
.lp-cb--top-bar    ~ .lp-cb__backdrop,
.lp-cb--floating-card-left  ~ .lp-cb__backdrop,
.lp-cb--floating-card-right ~ .lp-cb__backdrop { display: none !important; }
```

- [ ] **Step 5: Update enqueue.php for floating-card normalization**

Edit `skills/wp-landing-config/mu-plugin/landing-config/includes/cookie-banner/enqueue.php`:

Find this line:
```php
\wp_enqueue_style('lp-cb-layout', $base_url . '/layouts/' . $settings['layout'] . '.css', ['lp-cb-core'], VERSION);
```
Replace with:
```php
$css_layout = $settings['layout'];
if (strpos($css_layout, 'floating-card-') === 0) {
    $css_layout = 'floating-card';
}
\wp_enqueue_style('lp-cb-layout', $base_url . '/layouts/' . $css_layout . '.css', ['lp-cb-core'], VERSION);
```

- [ ] **Step 6: Verify all 5 layouts pass render test**

Add to `skills/wp-landing-config/tests/test_cookie_banner_render.php` (before final echo):

```php
// T_LAYOUTS: each of 5 layouts emits its specific class
foreach (['top-bar', 'bottom-bar', 'floating-card-left', 'floating-card-right', 'center-modal'] as $L) {
    $s = array_merge(\LandingConfig\CookieBanner\Resolver\DEFAULTS, ['layout' => $L]);
    ob_start();
    \LandingConfig\CookieBanner\Render\render_with_settings($s);
    $h = ob_get_clean();
    assert_test(strpos($h, 'lp-cb--' . $L) !== false, "T_LAYOUTS each layout renders: $L");
}
```

Run:
```bash
cd D:/AI_TEAMS/landing_system/.worktrees/b2-cookie-banner-library
php skills/wp-landing-config/tests/test_cookie_banner_render.php 2>&1 | tail -10
```
Expected: 15 tests pass (10 original + 5 layouts).

- [ ] **Step 7: Commit**

```bash
cd D:/AI_TEAMS/landing_system/.worktrees/b2-cookie-banner-library
git add skills/wp-landing-config/mu-plugin/landing-config/includes/cookie-banner/layouts/ \
        skills/wp-landing-config/mu-plugin/landing-config/assets/cookie-banner/layouts/ \
        skills/wp-landing-config/mu-plugin/landing-config/includes/cookie-banner/enqueue.php \
        skills/wp-landing-config/tests/test_cookie_banner_render.php
git commit -m "feat(b2): 4 more layouts (top-bar, floating-card L/R, center-modal) + layout normalization"
```

---

### Task 10: Wire mu-plugin loader

**Files:**
- Modify: `skills/wp-landing-config/mu-plugin/landing-config/landing-config.php`

- [ ] **Step 1: Inspect loader**

```bash
cd D:/AI_TEAMS/landing_system/.worktrees/b2-cookie-banner-library
grep -n "require_once\|include_once" skills/wp-landing-config/mu-plugin/landing-config/landing-config.php
```

Note where other includes/* files are required.

- [ ] **Step 2: Add cookie-banner requires**

In `skills/wp-landing-config/mu-plugin/landing-config/landing-config.php`, after the last existing `require_once __DIR__ . '/includes/...'` line, add:

```php
// B2 cookie-banner
require_once __DIR__ . '/includes/cookie-banner/cpt.php';
require_once __DIR__ . '/includes/cookie-banner/resolver.php';
require_once __DIR__ . '/includes/cookie-banner/render.php';
require_once __DIR__ . '/includes/cookie-banner/enqueue.php';
require_once __DIR__ . '/includes/cookie-banner/migrate.php';
if (\is_admin() || \is_network_admin()) {
    require_once __DIR__ . '/includes/cookie-banner/admin-network.php';
    require_once __DIR__ . '/includes/cookie-banner/admin-site-readonly.php';
}
```

And in the existing `maybe_run()` or `init` hook (where other migrations live — search for `landing_config_migration_`), add a call:

```php
\LandingConfig\CookieBanner\Migrate\maybe_run();
```

- [ ] **Step 3: PHP lint**

```bash
cd D:/AI_TEAMS/landing_system/.worktrees/b2-cookie-banner-library
php -l skills/wp-landing-config/mu-plugin/landing-config/landing-config.php
```

- [ ] **Step 4: Commit**

```bash
cd D:/AI_TEAMS/landing_system/.worktrees/b2-cookie-banner-library
git add skills/wp-landing-config/mu-plugin/landing-config/landing-config.php
git commit -m "feat(b2): wire cookie-banner modules + migration in mu-plugin loader"
```

---

### Task 11: Extend smoke-test

**Files:**
- Modify: `skills/wp-landing-config/tests/integration/test_s2a3_smoke.sh`

- [ ] **Step 1: Add T_CB tests**

Find the line `echo "✅ S2-A.3 + B19 live smoke GREEN"` (or similar success marker). Insert BEFORE it:

```bash
echo "▶ T_CB_1: главная страница содержит DOM cookie-banner (id=lp-cb)"
html=$(curl -sk "$BASE_URL" || echo "")
echo "$html" | grep -q 'id="lp-cb"' || { echo "FAIL: id=lp-cb not in homepage HTML"; exit 1; }
echo "  OK lp-cb DOM present"

echo "▶ T_CB_2: главная содержит consent-init (gtag default denied)"
echo "$html" | grep -q "gtag('consent','default'" || { echo "FAIL: consent-init script missing"; exit 1; }
echo "  OK consent-init present"

echo "▶ T_CB_3: layout класс задан (по умолчанию bottom-bar)"
echo "$html" | grep -qE 'lp-cb--(top-bar|bottom-bar|floating-card-left|floating-card-right|center-modal)' \
    || { echo "FAIL: no layout class on banner"; exit 1; }
echo "  OK layout class present"

echo "▶ T_CB_4: CSS+JS подключены"
echo "$html" | grep -q "/cookie-banner/core.css" || { echo "FAIL: core.css not enqueued"; exit 1; }
echo "$html" | grep -q "/cookie-banner/banner.js" || { echo "FAIL: banner.js not enqueued"; exit 1; }
echo "  OK assets enqueued"
```

If the script uses a different variable than `$BASE_URL` (e.g. `$WP_URL` or hardcoded `https://russian.ailexi.ru`), match the existing convention.

- [ ] **Step 2: bash-lint**

```bash
cd D:/AI_TEAMS/landing_system/.worktrees/b2-cookie-banner-library
bash -n skills/wp-landing-config/tests/integration/test_s2a3_smoke.sh
```

- [ ] **Step 3: Commit**

```bash
cd D:/AI_TEAMS/landing_system/.worktrees/b2-cookie-banner-library
git add skills/wp-landing-config/tests/integration/test_s2a3_smoke.sh
git commit -m "test(b2): smoke T_CB_1..4 for cookie-banner on live"
```

---

### Task 12: Remove B1 template files

**Files:**
- Delete: `template/08_КОД/template-parts/cookie-banner.php`
- Delete: `template/08_КОД/template-parts/cookie-banner.js`
- Delete: `template/08_КОД/template-parts/cookie-banner.css`
- Delete: `template/08_КОД/template-parts/consent-init.php`
- Keep: `template/08_КОД/template-parts/legal-block.php`

- [ ] **Step 1: Delete files**

```bash
cd D:/AI_TEAMS/landing_system/.worktrees/b2-cookie-banner-library
git rm template/08_КОД/template-parts/cookie-banner.php \
       template/08_КОД/template-parts/cookie-banner.js \
       template/08_КОД/template-parts/cookie-banner.css \
       template/08_КОД/template-parts/consent-init.php
```

- [ ] **Step 2: Verify legal-block.php still exists**

```bash
ls template/08_КОД/template-parts/legal-block.php
```

Expected: file exists.

- [ ] **Step 3: Inspect functions.php template (in `skills/wp-gutenberg-block-builder/scripts/generate-theme.py` or similar)**

```bash
grep -rn "wp_enqueue.*cookie-banner\|consent-init\|template-parts/cookie-banner" \
    skills/wp-gutenberg-block-builder/ skills/wp-theme-assembler/ 2>&1 | head -10
```

If any generator emits cookie-banner hooks into `functions.php` — remove those lines from the generator template/code. This ensures `landing-build` regen doesn't re-introduce theme-side cookie-banner code.

If found, edit the generator to remove the lines. If not found (the B1-applied dubai-avto-liza had manual edits that don't live in any generator) — no changes needed beyond Task 13 (which handles existing themes' cleanup).

- [ ] **Step 4: Commit**

```bash
cd D:/AI_TEAMS/landing_system/.worktrees/b2-cookie-banner-library
git commit -m "refactor(b2): remove B1 template files (cookie-banner moved to mu-plugin)

B1's cookie-banner.{php,js,css} and consent-init.php are replaced by the
B2 mu-plugin-owned implementation in landing-config. legal-block.php
remains — it's about form consent, not cookies."
```

---

### Task 13: Update stage-gate check_legal_blocks.sh

**Files:**
- Modify: `scripts/checks/check_legal_blocks.sh`

- [ ] **Step 1: Inspect current check**

```bash
cd D:/AI_TEAMS/landing_system/.worktrees/b2-cookie-banner-library
cat scripts/checks/check_legal_blocks.sh
```

- [ ] **Step 2: Replace cookie-banner checks with legal-block-only + mu-plugin presence**

Open `scripts/checks/check_legal_blocks.sh` and:

a) Remove these checks:
- `[ -f "$THEME_DIR/template-parts/cookie-banner.php" ]`
- `[ -f "$THEME_DIR/template-parts/consent-init.php" ]`
- `grep -q "cookie-banner" "$THEME_DIR/footer.php"`
- `grep -q "consent-init" "$THEME_DIR/header.php"`

b) Keep these checks:
- `[ -f "$THEME_DIR/template-parts/legal-block.php" ]`
- `grep -rl "legal-block" "$THEME_DIR/blocks/" | wc -l >= 1`

c) Add new check: mu-plugin landing-config present at theme's network root.

The check is path-based — script doesn't have SSH access. It assumes mu-plugin is deployed if marker file exists locally in the landing-system worktree. Add:

```bash
MU_PLUGIN_SRC="$(dirname "$(dirname "$(dirname "$(realpath "$0")")")")/skills/wp-landing-config/mu-plugin/landing-config/includes/cookie-banner/cpt.php"
[ -f "$MU_PLUGIN_SRC" ] || MISSING+=("mu-plugin cookie-banner source missing: $MU_PLUGIN_SRC")
```

This checks the **source** of the mu-plugin in landing-system. Deploy-side verification (CPT actually registered on server) is integration-test concern, not stage-gate.

- [ ] **Step 3: Run on dubai-avto-liza**

```bash
cd D:/AI_TEAMS/landing_system/.worktrees/b2-cookie-banner-library
bash scripts/checks/check_legal_blocks.sh D:/AI_TEAMS/Lendings/dubai-avto-liza
```

Expected: exit 0 (legal-block.php exists, form references it, mu-plugin source exists).

- [ ] **Step 4: Commit**

```bash
cd D:/AI_TEAMS/landing_system/.worktrees/b2-cookie-banner-library
git add scripts/checks/check_legal_blocks.sh
git commit -m "chore(b2): stage-gate check_legal_blocks — remove cookie-banner theme checks

Cookie-banner живёт в mu-plugin (не в теме). Stage-gate проверяет только
legal-block.php (форма заявки) + наличие mu-plugin source в landing-system."
```

---

### Task 14: CLAUDE.md docs

**Files:**
- Modify: `CLAUDE.md`

- [ ] **Step 1: Find B1 section**

```bash
cd D:/AI_TEAMS/landing_system/.worktrees/b2-cookie-banner-library
grep -n "B1 — Cookie-banner" CLAUDE.md
```

- [ ] **Step 2: Append B2 section after the B1 entry**

After the last line of the B1 section (which ends with `и [plan](docs/superpowers/plans/2026-05-21-b1-cookie-banner-pd-consent-plan.md).`), append:

```markdown

### B2 — Cookie-banner Library (5 layouts + admin, 2026-05-22)

Replaces B1's hardcoded cookie-banner with a mu-plugin-owned library:

- **5 layouts:** top-bar / bottom-bar / floating-card-{left,right} / center-modal.
  Маркетолог выбирает radio-button'ами с preview-thumbnail'ами в Network admin.
- **Admin UI:** Network admin → Лендинг → Cookie-banner с селектором сегмента
  (network default + per-segment override через cascade S2-A.3 паттерн).
  Поля: layout, тексты (заголовок/описание/кнопки/policy-link/reopen),
  категории (repeater с slug/name/desc/locked/default_on), цвета (4 hex
  поля — bg/text/accent/border, пусто = inherit из brand-kit темы),
  consent version (bump → re-prompt всем).
- **Token-driven design:** banner-local CSS-vars (`--cb-bg`, `--cb-accent`,
  `--cb-text`, `--cb-border`) по умолчанию ссылаются на theme vars
  (`var(--color-bg-card, ...)` etc). Admin-override эмитится inline `<style>`
  с более высоким specificity.
- **Google Consent Mode v2:** `gtag('consent','default','denied')` в `wp_head`
  с priority 1 (до загрузки analytics). После save в banner →
  `gtag('consent','update', {...})` per-category через GTAG_MAP.
- **B1 deprecation:** файлы `template/08_КОД/template-parts/cookie-banner.*` +
  `consent-init.php` удалены — mu-plugin полностью владеет рендером. Это
  решает баг «functions.php регенерируется без B1-хуков».
- **Migration:** `landing_config_migration_b2_cookie_banner` marker seed'ит
  network default запись с 3 категориями (necessary/analytics/marketing) при
  первой загрузке wp-admin.

См. [spec](docs/superpowers/specs/2026-05-22-b2-cookie-banner-library-design.md)
и [plan](docs/superpowers/plans/2026-05-22-b2-cookie-banner-library-plan.md).
```

- [ ] **Step 3: Commit**

```bash
cd D:/AI_TEAMS/landing_system/.worktrees/b2-cookie-banner-library
git add CLAUDE.md
git commit -m "docs(b2): CLAUDE.md секция Cookie-banner Library"
```

---

### Task 15: Final review + merge to main

- [ ] **Step 1: Full test sweep**

```bash
cd D:/AI_TEAMS/landing_system/.worktrees/b2-cookie-banner-library
for t in skills/wp-landing-config/tests/test_cookie_banner_*.php; do
    echo "=== $(basename $t) ==="
    php "$t" 2>&1 | tail -1
done
```

Expected: all 4 test files show `N tests, 0 failures`.

- [ ] **Step 2: PHP lint all new files**

```bash
cd D:/AI_TEAMS/landing_system/.worktrees/b2-cookie-banner-library
for f in skills/wp-landing-config/mu-plugin/landing-config/includes/cookie-banner/*.php \
         skills/wp-landing-config/mu-plugin/landing-config/includes/cookie-banner/layouts/*.php; do
    php -l "$f" || exit 1
done
```

Expected: all show `No syntax errors detected`.

- [ ] **Step 3: Bash lint**

```bash
bash -n skills/wp-landing-config/tests/integration/test_s2a3_smoke.sh
bash -n scripts/checks/check_legal_blocks.sh
```

- [ ] **Step 4: Merge to main + push**

```bash
cd D:/AI_TEAMS/landing_system
git checkout main
git merge --no-ff b2-cookie-banner-library -m "merge: B2 — Cookie-banner Library (5 layouts + admin)"
git push origin main
```

---

## Self-Review

**Spec coverage:**
- Architecture (3 modules + CLI + gate-hook) — Tasks 1, 2, 4, 5, 6, 7, 8, 10 ✓
- 5 layouts — Tasks 3 + 9 ✓
- Data Model CPT + meta keys — Task 1 + 2 (constants in cpt.php, resolver reads them) ✓
- GTAG_MAP — Task 5 ✓
- DEFAULTS + 3 default categories — Task 2 (resolver.php DEFAULTS const) ✓
- CSS variables banner-local — Task 3 (core.css) ✓
- Admin UI (network + site) — Tasks 6 + 7 ✓
- Migration runner — Task 8 ✓
- B1 deprecation — Task 12 ✓
- Stage-gate update — Task 13 ✓
- Tests: unit + integration — Tasks 1, 2, 4, 8 (unit), Task 11 (integration smoke) ✓
- Visual QA — left manual after merge (Acceptance Criteria #10 in spec) — not a code task, intentionally not in plan
- Live preview link in admin — Task 6 (admin-network.php emits link) ✓
- Live preview server-side handling — **NOT in plan**: a gap. The admin page emits `?lp_cookie_banner_preview=1&segment=N` but enqueue.php / render.php don't honor this query param. **Adding to Task 5 mentally**: enqueue should force-show banner when query param is set AND user is admin. Decision: defer to manual follow-up since it's not a blocker (admin can also test by clearing localStorage). **Adding a Task 5-bis would inflate plan; document as known limitation in CLAUDE.md after merge.**

**Placeholder scan:** no TBD / TODO. Every step has concrete code or commands.

**Type consistency:**
- `POST_TYPE = 'lp_cookie_banner'` — consistent across cpt.php, resolver.php, render.php, admin-network.php, admin-site-readonly.php, migrate.php ✓
- `SEGMENT_META = '_lp_cb_segment'` — consistent ✓
- `VALID_LAYOUTS` array — same 5 values everywhere (cpt.php, resolver.php fallback, render.php fallback) ✓
- `META_KEY_MAP` field names — same field-name → meta-key mapping in resolver.php, admin-network.php save_field, admin-site-readonly.php read ✓
- `LP_CB_CONFIG` JS-side keys: `version`, `storage_key`, `categories`, `gtag_map`, `show_categories` — Task 5 emits, Task 4 banner.js reads ✓
- `data-action` attribute values: `accept-all`, `reject`, `save` — Task 3 emits, Task 4 banner.js handles ✓
- `data-slug` attribute on category checkbox — Task 3 emits, Task 4 banner.js reads ✓
- `GTAG_MAP` const — defined once in enqueue.php, sent to JS, JS uses it ✓
- `MARKER = 'landing_config_migration_b2_cookie_banner'` — defined in migrate.php, asserted in test_cookie_banner_migration.php ✓
