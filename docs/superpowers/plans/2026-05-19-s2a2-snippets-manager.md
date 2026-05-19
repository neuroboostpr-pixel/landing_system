# S2-A.2 Snippets Manager — Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Заменить экран «Head & SEO» (11 фиксированных полей) в landing-config mu-plugin универсальным менеджером snippet'ов на основе CPT `lp_snippet`. Поддержка head/body_open/body_close позиций, global vs local scope, on/off toggle, priority.

**Architecture:** CPT registered hidden from main menu, post_meta хранит code/position/scope/target_post_ids/enabled/priority. Renderer цепляется на `wp_head` / `wp_body_open` / `wp_footer`. Admin: list (WP_List_Table) + edit form + meta-box в Page/Post редакторе.

**Tech Stack:**
- PHP 8.3 on Beget shared hosting (WordPress 6.9 Multisite)
- WP CPT + post_meta API
- WP_List_Table
- `wp_kses` с расширенным allow-list
- `wp_enqueue_code_editor` (core ≥4.9) для CodeMirror в textarea
- PHP CLI tests с mock wp-bootstrap (расширим)

**Spec:** [docs/superpowers/specs/2026-05-19-s2a2-snippets-manager.md](../specs/2026-05-19-s2a2-snippets-manager.md)

---

## Pre-requisites

- S2-A `landing-config` mu-plugin задеплоен (merged в main, на ailexi.ru работает)
- Все 47 PHP + 5 bats тестов S2-A проходят
- PHP 8.3 локально (`php` в PATH + extension=openssl auto-loaded)

---

## Task 1: Удалить admin-head-seo + landing_render_head_extras

**Files:**
- Delete: `skills/wp-landing-config/mu-plugin/landing-config/includes/admin-head-seo.php`
- Modify: `skills/wp-landing-config/mu-plugin/landing-config/landing-config.php`
- Modify: `skills/wp-landing-config/mu-plugin/landing-config/includes/helpers.php`
- Modify: `skills/wp-landing-config/mu-plugin/landing-config/includes/admin-pages.php`

- [ ] **Step 1: Delete admin-head-seo.php**

```bash
git rm skills/wp-landing-config/mu-plugin/landing-config/includes/admin-head-seo.php
```

- [ ] **Step 2: Remove require + hook from landing-config.php**

Edit `landing-config.php`, remove these two lines:

```php
require_once LANDING_CONFIG_DIR . '/includes/admin-head-seo.php';
```

```php
add_action('wp_head', 'landing_render_head_extras', 5);
```

- [ ] **Step 3: Remove landing_render_head_extras from helpers.php**

Edit `helpers.php`, delete the entire `landing_render_head_extras()` function (whole block from docblock to closing `}`).

- [ ] **Step 4: Update dashboard description in admin-pages.php**

Replace this `<li>`:

```php
<li><strong>Head &amp; SEO</strong> — счётчики, мета-теги, верификации</li>
```

with:

```php
<li><strong>Снипеты</strong> — счётчики, мета-теги, виджеты, любой HTML в head/body/footer</li>
```

- [ ] **Step 5: php -l on all modified files**

```bash
php -l skills/wp-landing-config/mu-plugin/landing-config/landing-config.php
php -l skills/wp-landing-config/mu-plugin/landing-config/includes/helpers.php
php -l skills/wp-landing-config/mu-plugin/landing-config/includes/admin-pages.php
```
Expected: `No syntax errors detected` on all three.

- [ ] **Step 6: Re-run helpers test (should still pass — landing_get_cta unchanged)**

```bash
php skills/wp-landing-config/tests/test_helpers.php
```
Expected: `12 tests, 0 failures`.

- [ ] **Step 7: Commit**

```bash
git add -A
git commit -m "refactor(wp-landing-config): remove Head & SEO admin + landing_render_head_extras

S2-A.2: replacing with universal snippets manager (CPT lp_snippet).
No production data exists for the 11 deleted fields (deploy was new),
so no migration needed.

Co-Authored-By: Claude Opus 4.7 (1M context) <noreply@anthropic.com>"
```

---

## Task 2: Extend wp-bootstrap.php with CPT + post_meta + wp_kses mocks

**Files:**
- Modify: `skills/wp-landing-config/tests/fixtures/wp-bootstrap.php`

- [ ] **Step 1: Append CPT/post mocks**

Append to bottom of `wp-bootstrap.php`:

```php

// CPT + post_meta + wp_kses mocks for snippets.php tests

$GLOBALS['_mock_post_types'] = [];
$GLOBALS['_mock_posts'] = [];            // [id => ['post_type'=>..., 'post_title'=>..., 'post_status'=>...]]
$GLOBALS['_mock_post_meta'] = [];        // [post_id => [key => value]]
$GLOBALS['_mock_queried_object_id'] = 0;
$GLOBALS['_mock_next_post_id'] = 1;
$GLOBALS['_mock_kses_calls'] = [];

function register_post_type($name, $args = []) {
    $GLOBALS['_mock_post_types'][$name] = $args;
    return (object) ['name' => $name];
}

function wp_insert_post($postarr, $wp_error = false) {
    $id = $GLOBALS['_mock_next_post_id']++;
    $GLOBALS['_mock_posts'][$id] = array_merge(
        ['post_type' => 'post', 'post_status' => 'publish', 'post_title' => ''],
        $postarr,
        ['ID' => $id]
    );
    return $id;
}

function wp_update_post($postarr) {
    $id = (int) ($postarr['ID'] ?? 0);
    if ($id && isset($GLOBALS['_mock_posts'][$id])) {
        $GLOBALS['_mock_posts'][$id] = array_merge($GLOBALS['_mock_posts'][$id], $postarr);
    }
    return $id;
}

function wp_delete_post($id, $force = false) {
    unset($GLOBALS['_mock_posts'][$id]);
    unset($GLOBALS['_mock_post_meta'][$id]);
    return true;
}

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

function get_post($id) {
    return isset($GLOBALS['_mock_posts'][$id]) ? (object) $GLOBALS['_mock_posts'][$id] : null;
}

function update_post_meta($post_id, $key, $value) {
    $GLOBALS['_mock_post_meta'][$post_id][$key] = $value;
    return true;
}

function get_post_meta($post_id, $key = '', $single = false) {
    if ($key === '') {
        return $GLOBALS['_mock_post_meta'][$post_id] ?? [];
    }
    $value = $GLOBALS['_mock_post_meta'][$post_id][$key] ?? '';
    return $single ? $value : ($value === '' ? [] : [$value]);
}

function delete_post_meta($post_id, $key) {
    unset($GLOBALS['_mock_post_meta'][$post_id][$key]);
    return true;
}

function get_queried_object_id() {
    return (int) $GLOBALS['_mock_queried_object_id'];
}

function set_mock_queried_object_id($id) {
    $GLOBALS['_mock_queried_object_id'] = (int) $id;
}

function wp_kses($content, $allowed_html, $allowed_protocols = []) {
    $GLOBALS['_mock_kses_calls'][] = ['content' => $content, 'allowed' => $allowed_html];
    // Minimal mock: strip tags NOT in allow-list.
    // We don't fully replicate WP's parser; tests check that wp_kses was called
    // with the right allow-list and that disallowed tags are stripped.
    $allowed_tags = array_keys($allowed_html);
    return strip_tags($content, $allowed_tags);
}

function esc_textarea($v) { return htmlspecialchars((string)$v, ENT_QUOTES, 'UTF-8'); }
function esc_url($v) { return filter_var((string)$v, FILTER_SANITIZE_URL); }
function selected($a, $b, $echo = true) {
    $s = ((string)$a === (string)$b) ? ' selected="selected"' : '';
    if ($echo) echo $s;
    return $s;
}
function checked($a, $b = true, $echo = true) {
    $s = ((bool)$a === (bool)$b) ? ' checked="checked"' : '';
    if ($echo) echo $s;
    return $s;
}
```

If any of these functions already exists in wp-bootstrap.php (e.g. `esc_textarea` was added in head-seo task, but we just deleted that — verify), wrap them in `if (!function_exists('xxx')) { ... }`.

- [ ] **Step 2: php -l**

```bash
php -l skills/wp-landing-config/tests/fixtures/wp-bootstrap.php
```

- [ ] **Step 3: Sanity test — run existing tests, they must still pass**

```bash
for t in skills/wp-landing-config/tests/test_*.php; do php "$t" 2>&1 | tail -1; done
```
Expected: db_schema 8/8, encryption 13/13, helpers 12/12, rest_lead 14/14. None broken by mock additions.

- [ ] **Step 4: Commit**

```bash
git add skills/wp-landing-config/tests/fixtures/wp-bootstrap.php
git commit -m "test(wp-landing-config): extend wp-bootstrap mock with CPT + post_meta + wp_kses

Adds: register_post_type, wp_insert_post, wp_update_post, wp_delete_post,
get_posts (with meta_value_num orderby), get_post, update/get/delete_post_meta,
get_queried_object_id (+ set_mock_queried_object_id), wp_kses (strip_tags
fallback), esc_textarea, esc_url, selected, checked.

All existing 47 tests still pass.

Co-Authored-By: Claude Opus 4.7 (1M context) <noreply@anthropic.com>"
```

---

## Task 3: snippets.php — CPT registration + sanitize + helpers

**Files:**
- Create: `skills/wp-landing-config/mu-plugin/landing-config/includes/snippets.php`
- Create: `skills/wp-landing-config/tests/test_snippets_helpers.php`
- Modify: `skills/wp-landing-config/mu-plugin/landing-config/landing-config.php`

- [ ] **Step 1: Failing test for sanitize + CRUD helpers**

Create `skills/wp-landing-config/tests/test_snippets_helpers.php`:

```php
<?php
require_once __DIR__ . '/fixtures/wp-bootstrap.php';
require_once __DIR__ . '/../mu-plugin/landing-config/includes/snippets.php';

use function LandingConfig\Snippets\sanitize_code;
use function LandingConfig\Snippets\save_snippet;
use function LandingConfig\Snippets\get_snippet;
use function LandingConfig\Snippets\delete_snippet;
use function LandingConfig\Snippets\list_snippets;

$failures = 0;
$tests = 0;

function assert_test($condition, $message) {
    global $failures, $tests;
    $tests++;
    if (!$condition) {
        echo "FAIL: $message\n";
        $failures++;
    }
}

// Reset mock state
function reset_snippets() {
    $GLOBALS['_mock_posts'] = [];
    $GLOBALS['_mock_post_meta'] = [];
    $GLOBALS['_mock_next_post_id'] = 1;
    $GLOBALS['_mock_kses_calls'] = [];
}

// Test 1: sanitize_code keeps script/meta/link/iframe; strips form/onclick
reset_snippets();
$clean = sanitize_code('<script src="https://ya.ru/x.js" async></script><form><input></form>');
assert_test(
    strpos($clean, '<script') !== false && strpos($clean, '<form') === false,
    "sanitize_code keeps script, strips form (got: $clean)"
);

// Test 2: save_snippet creates CPT post with all meta
reset_snippets();
$id = save_snippet([
    'title' => 'Y.Metrika',
    'code' => '<script>ym(1,"init");</script>',
    'position' => 'head',
    'scope' => 'global',
    'enabled' => true,
    'priority' => 5,
]);
assert_test($id > 0, "save_snippet returns post_id (got: $id)");
$post = get_post($id);
assert_test(
    $post && $post->post_type === 'lp_snippet' && $post->post_title === 'Y.Metrika',
    "saved post has post_type=lp_snippet and right title"
);
assert_test(
    get_post_meta($id, '_lp_snippet_position', true) === 'head',
    "position meta saved"
);
assert_test(
    get_post_meta($id, '_lp_snippet_scope', true) === 'global',
    "scope meta saved"
);
assert_test(
    (int)get_post_meta($id, '_lp_snippet_priority', true) === 5,
    "priority meta saved"
);
assert_test(
    get_post_meta($id, '_lp_snippet_enabled', true) === '1',
    "enabled saved as '1'"
);

// Test 3: get_snippet returns array with all fields
$s = get_snippet($id);
assert_test(
    $s['id'] === $id && $s['title'] === 'Y.Metrika' && $s['position'] === 'head'
    && $s['scope'] === 'global' && $s['priority'] === 5 && $s['enabled'] === true,
    "get_snippet returns full array (got: " . json_encode($s) . ")"
);

// Test 4: save_snippet update path (existing id)
$id2 = save_snippet([
    'id' => $id,
    'title' => 'Y.Metrika v2',
    'code' => '<script>ym(2,"init");</script>',
    'position' => 'head',
    'scope' => 'global',
    'enabled' => false,
    'priority' => 10,
]);
assert_test($id2 === $id, "save_snippet updates existing id (got: $id2)");
$s = get_snippet($id);
assert_test(
    $s['title'] === 'Y.Metrika v2' && $s['enabled'] === false && $s['priority'] === 10,
    "updated fields persist (got: " . json_encode($s) . ")"
);

// Test 5: local snippet stores target_post_ids as array of int
reset_snippets();
$id = save_snippet([
    'title' => 'Schema Home',
    'code' => '<script type="application/ld+json">{}</script>',
    'position' => 'head',
    'scope' => 'local',
    'target_post_ids' => [42, 99, 100],
    'enabled' => true,
    'priority' => 10,
]);
$s = get_snippet($id);
assert_test(
    $s['scope'] === 'local' && $s['target_post_ids'] === [42, 99, 100],
    "local scope + target_post_ids round-trip (got: " . json_encode($s) . ")"
);

// Test 6: list_snippets returns all lp_snippet posts as arrays
reset_snippets();
save_snippet(['title' => 'A', 'code' => 'a', 'position' => 'head', 'scope' => 'global', 'priority' => 1]);
save_snippet(['title' => 'B', 'code' => 'b', 'position' => 'body_open', 'scope' => 'global', 'priority' => 1]);
$all = list_snippets();
assert_test(count($all) === 2, "list_snippets returns 2 (got: " . count($all) . ")");

// Test 7: list_snippets with filter by position
$head = list_snippets(['position' => 'head']);
assert_test(
    count($head) === 1 && $head[0]['title'] === 'A',
    "list_snippets filters by position (got: " . count($head) . ")"
);

// Test 8: delete_snippet removes post + meta
reset_snippets();
$id = save_snippet(['title' => 'X', 'code' => 'x', 'position' => 'head', 'scope' => 'global']);
delete_snippet($id);
assert_test(get_post($id) === null, "delete_snippet removes post");
assert_test(empty(get_post_meta($id, '', false)), "delete_snippet removes meta");

// Test 9: save_snippet defaults
reset_snippets();
$id = save_snippet(['title' => 'min', 'code' => 'c']);
$s = get_snippet($id);
assert_test(
    $s['position'] === 'head' && $s['scope'] === 'global'
    && $s['enabled'] === true && $s['priority'] === 10
    && $s['target_post_ids'] === [],
    "save_snippet applies defaults (got: " . json_encode($s) . ")"
);

// Test 10: save_snippet rejects invalid position
reset_snippets();
$id = save_snippet(['title' => 'bad', 'code' => 'c', 'position' => 'evil']);
$s = get_snippet($id);
assert_test(
    $s['position'] === 'head',
    "invalid position falls back to 'head' (got: " . $s['position'] . ")"
);

echo "\n$tests tests, $failures failures\n";
exit($failures > 0 ? 1 : 0);
```

- [ ] **Step 2: Run test, expect fatal (file not found)**

```bash
php skills/wp-landing-config/tests/test_snippets_helpers.php
```

- [ ] **Step 3: Implement snippets.php**

Create `skills/wp-landing-config/mu-plugin/landing-config/includes/snippets.php`:

```php
<?php
namespace LandingConfig\Snippets;

if (!defined('ABSPATH')) { exit; }

const POST_TYPE = 'lp_snippet';
const VALID_POSITIONS = ['head', 'body_open', 'body_close'];
const VALID_SCOPES = ['global', 'local'];

const ALLOWED_HTML = [
    'script'   => ['src' => true, 'async' => true, 'defer' => true, 'type' => true,
                   'crossorigin' => true, 'integrity' => true, 'nonce' => true,
                   'id' => true, 'class' => true],
    'meta'     => ['name' => true, 'content' => true, 'property' => true,
                   'http-equiv' => true, 'charset' => true, 'itemprop' => true],
    'link'     => ['rel' => true, 'href' => true, 'type' => true, 'crossorigin' => true,
                   'sizes' => true, 'as' => true, 'media' => true, 'integrity' => true],
    'style'    => ['type' => true, 'media' => true, 'id' => true, 'class' => true],
    'noscript' => ['id' => true, 'class' => true],
    'iframe'   => ['src' => true, 'width' => true, 'height' => true, 'frameborder' => true,
                   'allowfullscreen' => true, 'allow' => true, 'loading' => true,
                   'sandbox' => true, 'id' => true, 'class' => true, 'style' => true,
                   'title' => true, 'name' => true],
    'div'      => ['id' => true, 'class' => true, 'style' => true,
                   'role' => true, 'aria-label' => true],
    'span'     => ['id' => true, 'class' => true, 'style' => true],
    'img'      => ['src' => true, 'alt' => true, 'width' => true, 'height' => true,
                   'style' => true, 'class' => true, 'id' => true],
    'a'        => ['href' => true, 'target' => true, 'rel' => true, 'class' => true,
                   'id' => true, 'style' => true],
    'p'        => ['class' => true, 'id' => true],
    'br'       => [],
];

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
            'edit_post'         => 'manage_options',
            'edit_posts'        => 'manage_options',
            'edit_others_posts' => 'manage_options',
            'publish_posts'     => 'manage_options',
            'read_post'         => 'manage_options',
            'delete_post'       => 'manage_options',
        ],
    ]);
}

function sanitize_code(string $code): string {
    return wp_kses($code, ALLOWED_HTML);
}

function save_snippet(array $args): int {
    $title = sanitize_text_field($args['title'] ?? '');
    $code  = sanitize_code($args['code'] ?? '');

    $position = $args['position'] ?? 'head';
    if (!in_array($position, VALID_POSITIONS, true)) $position = 'head';

    $scope = $args['scope'] ?? 'global';
    if (!in_array($scope, VALID_SCOPES, true)) $scope = 'global';

    $enabled  = !empty($args['enabled']) || (!isset($args['enabled']) && !isset($args['id']));
    $priority = isset($args['priority']) ? (int) $args['priority'] : 10;
    $targets  = array_values(array_map('intval', (array) ($args['target_post_ids'] ?? [])));

    $post = ['post_type' => POST_TYPE, 'post_status' => 'publish', 'post_title' => $title];

    if (!empty($args['id'])) {
        $post['ID'] = (int) $args['id'];
        $id = wp_update_post($post);
    } else {
        $id = wp_insert_post($post);
    }

    update_post_meta($id, '_lp_snippet_code', $code);
    update_post_meta($id, '_lp_snippet_position', $position);
    update_post_meta($id, '_lp_snippet_scope', $scope);
    update_post_meta($id, '_lp_snippet_target_post_ids', $targets);
    update_post_meta($id, '_lp_snippet_enabled', $enabled ? '1' : '0');
    update_post_meta($id, '_lp_snippet_priority', $priority);

    return (int) $id;
}

function get_snippet(int $id): ?array {
    $p = get_post($id);
    if (!$p || ($p->post_type ?? '') !== POST_TYPE) return null;
    return [
        'id'              => $id,
        'title'           => $p->post_title ?? '',
        'code'            => (string) get_post_meta($id, '_lp_snippet_code', true),
        'position'        => (string) get_post_meta($id, '_lp_snippet_position', true) ?: 'head',
        'scope'           => (string) get_post_meta($id, '_lp_snippet_scope', true) ?: 'global',
        'target_post_ids' => array_map('intval', (array) get_post_meta($id, '_lp_snippet_target_post_ids', true)),
        'enabled'         => (string) get_post_meta($id, '_lp_snippet_enabled', true) === '1',
        'priority'        => (int) get_post_meta($id, '_lp_snippet_priority', true),
    ];
}

function delete_snippet(int $id): bool {
    return (bool) wp_delete_post($id, true);
}

function list_snippets(array $filter = []): array {
    $posts = get_posts([
        'post_type'      => POST_TYPE,
        'posts_per_page' => -1,
        'post_status'    => 'publish',
        'orderby'        => 'meta_value_num',
        'meta_key'       => '_lp_snippet_priority',
        'order'          => 'ASC',
    ]);
    $out = [];
    foreach ($posts as $p) {
        $s = get_snippet((int) $p->ID);
        if (!$s) continue;
        if (!empty($filter['position']) && $s['position'] !== $filter['position']) continue;
        if (!empty($filter['scope'])    && $s['scope']    !== $filter['scope'])    continue;
        if (isset($filter['enabled'])   && $s['enabled']  !== (bool) $filter['enabled']) continue;
        $out[] = $s;
    }
    return $out;
}
```

- [ ] **Step 4: Add require in landing-config.php**

In `landing-config.php`, after `require_once .../includes/helpers.php`, add:

```php
require_once LANDING_CONFIG_DIR . '/includes/snippets.php';
```

- [ ] **Step 5: Run test, expect pass**

```bash
php skills/wp-landing-config/tests/test_snippets_helpers.php
```
Expected: `10 tests, 0 failures`.

- [ ] **Step 6: php -l on snippets.php and landing-config.php**

- [ ] **Step 7: Commit**

```bash
git add skills/wp-landing-config/mu-plugin/landing-config/includes/snippets.php \
        skills/wp-landing-config/mu-plugin/landing-config/landing-config.php \
        skills/wp-landing-config/tests/test_snippets_helpers.php
git commit -m "feat(wp-landing-config): snippets.php — CPT + sanitize + CRUD

CPT lp_snippet hidden from main menu (show_ui=false).
ALLOWED_HTML allow-list covers script/meta/link/style/iframe/div/span/img/a.
Functions: sanitize_code, save_snippet, get_snippet, delete_snippet, list_snippets.

10 unit tests cover sanitize, CRUD, scope/target_post_ids round-trip,
defaults, invalid-position fallback.

Co-Authored-By: Claude Opus 4.7 (1M context) <noreply@anthropic.com>"
```

---

## Task 4: snippets.php renderer (wp_head / wp_body_open / wp_footer)

**Files:**
- Modify: `skills/wp-landing-config/mu-plugin/landing-config/includes/snippets.php`
- Create: `skills/wp-landing-config/tests/test_snippets_renderer.php`

- [ ] **Step 1: Failing test**

Create `skills/wp-landing-config/tests/test_snippets_renderer.php`:

```php
<?php
require_once __DIR__ . '/fixtures/wp-bootstrap.php';
require_once __DIR__ . '/../mu-plugin/landing-config/includes/snippets.php';

use function LandingConfig\Snippets\save_snippet;
use function LandingConfig\Snippets\render;

$failures = 0;
$tests = 0;

function assert_test($condition, $message) {
    global $failures, $tests;
    $tests++;
    if (!$condition) {
        echo "FAIL: $message\n";
        $failures++;
    }
}

function reset_state() {
    $GLOBALS['_mock_posts'] = [];
    $GLOBALS['_mock_post_meta'] = [];
    $GLOBALS['_mock_next_post_id'] = 1;
    set_mock_queried_object_id(0);
}

function capture(callable $fn): string {
    ob_start();
    $fn();
    return (string) ob_get_clean();
}

// Test 1: render('head') outputs head global snippets ordered by priority ASC
reset_state();
save_snippet(['title' => 'B', 'code' => '<meta name="b">', 'position' => 'head', 'priority' => 20]);
save_snippet(['title' => 'A', 'code' => '<meta name="a">', 'position' => 'head', 'priority' => 5]);
$out = capture(function () { render('head'); });
assert_test(
    strpos($out, 'name="a"') < strpos($out, 'name="b"'),
    "head snippets sorted by priority ASC (got: $out)"
);

// Test 2: position is isolated — body_open snippet doesn't leak into head
reset_state();
save_snippet(['title' => 'Body', 'code' => '<div>BODYMARK</div>', 'position' => 'body_open']);
save_snippet(['title' => 'Head', 'code' => '<meta name="headmark">', 'position' => 'head']);
$head_out = capture(function () { render('head'); });
$body_out = capture(function () { render('body_open'); });
assert_test(
    strpos($head_out, 'BODYMARK') === false && strpos($head_out, 'headmark') !== false,
    "head output contains only head snippets"
);
assert_test(
    strpos($body_out, 'BODYMARK') !== false && strpos($body_out, 'headmark') === false,
    "body_open output contains only body_open snippets"
);

// Test 3: disabled snippet not rendered
reset_state();
save_snippet(['title' => 'X', 'code' => '<meta name="x">', 'position' => 'head', 'enabled' => false]);
$out = capture(function () { render('head'); });
assert_test(
    strpos($out, 'name="x"') === false,
    "disabled snippet not rendered (got: $out)"
);

// Test 4: local snippet only renders when current post is in target_post_ids
reset_state();
save_snippet(['title' => 'Local-42', 'code' => '<meta name="for42">', 'position' => 'head',
              'scope' => 'local', 'target_post_ids' => [42]]);
set_mock_queried_object_id(10);
$out_other = capture(function () { render('head'); });
set_mock_queried_object_id(42);
$out_target = capture(function () { render('head'); });
assert_test(
    strpos($out_other, 'for42') === false,
    "local snippet not rendered on other page"
);
assert_test(
    strpos($out_target, 'for42') !== false,
    "local snippet rendered on target page"
);

// Test 5: locals output AFTER globals (lower-priority caskade win)
reset_state();
save_snippet(['title' => 'Global', 'code' => '<meta name="g">', 'position' => 'head',
              'scope' => 'global', 'priority' => 10]);
save_snippet(['title' => 'Local', 'code' => '<meta name="l">', 'position' => 'head',
              'scope' => 'local', 'target_post_ids' => [42], 'priority' => 10]);
set_mock_queried_object_id(42);
$out = capture(function () { render('head'); });
assert_test(
    strpos($out, 'name="g"') < strpos($out, 'name="l"'),
    "global before local at same priority (got: $out)"
);

// Test 6: empty snippet (after sanitize) wraps still happens but body empty
// (we accept either: no output, or just comment wrapper). Sanity: doesn't fatal.
reset_state();
save_snippet(['title' => 'Empty', 'code' => '', 'position' => 'head']);
$out = capture(function () { render('head'); });
assert_test(is_string($out), "empty snippet doesn't fatal (got: " . strlen($out) . " bytes)");

// Test 7: output includes debug comment with snippet id and title
reset_state();
$id = save_snippet(['title' => 'Debugged', 'code' => '<meta name="d">', 'position' => 'head']);
$out = capture(function () { render('head'); });
assert_test(
    strpos($out, "lp_snippet:$id") !== false && strpos($out, 'Debugged') !== false,
    "render includes debug comment with id+title (got: $out)"
);

// Test 8: invalid position arg → no output, no error
reset_state();
save_snippet(['title' => 'Z', 'code' => '<meta>', 'position' => 'head']);
$out = capture(function () { render('invalid-pos'); });
assert_test($out === '', "invalid position returns empty (got: " . var_export($out, true) . ")");

echo "\n$tests tests, $failures failures\n";
exit($failures > 0 ? 1 : 0);
```

- [ ] **Step 2: Run test, expect fail (render() doesn't exist)**

```bash
php skills/wp-landing-config/tests/test_snippets_renderer.php
```

- [ ] **Step 3: Append render() + hooks to snippets.php**

Append to bottom of `snippets.php`:

```php

add_action('wp_head',      __NAMESPACE__ . '\\render_head',       5);
add_action('wp_body_open', __NAMESPACE__ . '\\render_body_open',  5);
add_action('wp_footer',    __NAMESPACE__ . '\\render_body_close', 99);

function render_head(): void       { render('head'); }
function render_body_open(): void  { render('body_open'); }
function render_body_close(): void { render('body_close'); }

function render(string $position): void {
    if (!in_array($position, VALID_POSITIONS, true)) return;

    $all = list_snippets(['position' => $position, 'enabled' => true]);
    if (empty($all)) return;

    $current_id = get_queried_object_id();
    $globals = [];
    $locals  = [];
    foreach ($all as $s) {
        if ($s['scope'] === 'global') {
            $globals[] = $s;
        } elseif ($s['scope'] === 'local' && in_array($current_id, $s['target_post_ids'], true)) {
            $locals[] = $s;
        }
    }
    // list_snippets already sorted by priority ASC; preserve that within each bucket.
    foreach (array_merge($globals, $locals) as $s) {
        printf("\n<!-- lp_snippet:%d %s -->\n", $s['id'], $s['title']);
        echo $s['code'];
        printf("\n<!-- /lp_snippet:%d -->\n", $s['id']);
    }
}
```

- [ ] **Step 4: Run test, expect pass**

```bash
php skills/wp-landing-config/tests/test_snippets_renderer.php
```
Expected: `8 tests, 0 failures`.

- [ ] **Step 5: php -l**

- [ ] **Step 6: Commit**

```bash
git add skills/wp-landing-config/mu-plugin/landing-config/includes/snippets.php \
        skills/wp-landing-config/tests/test_snippets_renderer.php
git commit -m "feat(wp-landing-config): snippets renderer — wp_head/body_open/wp_footer hooks

render(position): list enabled snippets at that position, split by scope.
Globals output first (priority ASC), then locals (target_post_ids matches
get_queried_object_id) — locals cascade-override at same position.

Each snippet wrapped in <!-- lp_snippet:ID title --> comments for debug.

8 unit tests cover ordering, position isolation, disabled, local target
matching, global-before-local cascade, empty/invalid position safety.

Co-Authored-By: Claude Opus 4.7 (1M context) <noreply@anthropic.com>"
```

---

## Task 5: admin-snippets.php — list page (WP_List_Table-style)

**Files:**
- Create: `skills/wp-landing-config/mu-plugin/landing-config/includes/admin-snippets.php`
- Modify: `skills/wp-landing-config/mu-plugin/landing-config/landing-config.php`

- [ ] **Step 1: Write admin-snippets.php (list view + dispatch)**

Create:

```php
<?php
namespace LandingConfig\Admin\Snippets;

if (!defined('ABSPATH')) { exit; }

use function LandingConfig\Snippets\list_snippets;
use function LandingConfig\Snippets\get_snippet;
use function LandingConfig\Snippets\save_snippet;
use function LandingConfig\Snippets\delete_snippet;

add_action('admin_menu', function () {
    add_submenu_page(
        'landing-config',
        'Снипеты',
        'Снипеты',
        'manage_options',
        'landing-config-snippets',
        __NAMESPACE__ . '\\dispatch'
    );
});

function dispatch(): void {
    if (!current_user_can('manage_options')) { wp_die('Insufficient permissions'); }

    $action = $_REQUEST['action'] ?? 'list';

    if ($action === 'save' && check_admin_referer('landing_snippets_save')) {
        handle_save();
        return;
    }
    if ($action === 'delete' && check_admin_referer('landing_snippets_delete')) {
        handle_delete();
        return;
    }
    if ($action === 'edit' || $action === 'new') {
        render_edit_form();
        return;
    }
    render_list();
}

function render_list(): void {
    $snippets = list_snippets();
    $add_url  = admin_url('admin.php?page=landing-config-snippets&action=new');
    ?>
    <div class="wrap">
        <h1>
            Снипеты
            <a href="<?php echo esc_url($add_url); ?>" class="page-title-action">Добавить снипет</a>
        </h1>
        <p>HTML-снипеты для <code>&lt;head&gt;</code>, <code>&lt;body&gt;</code> (начало)
        и <code>&lt;footer&gt;</code>. Глобальные применяются ко всем страницам,
        локальные — только к выбранным. Локальные выводятся ПОСЛЕ глобальных в той
        же позиции (каскадно перекрывают).</p>

        <table class="wp-list-table widefat striped">
            <thead>
                <tr>
                    <th>Title</th><th>Position</th><th>Scope</th>
                    <th>Enabled</th><th>Priority</th><th>Actions</th>
                </tr>
            </thead>
            <tbody>
                <?php if (empty($snippets)): ?>
                    <tr><td colspan="6"><em>Снипетов пока нет. Нажмите «Добавить снипет».</em></td></tr>
                <?php else: foreach ($snippets as $s):
                    $edit_url = admin_url('admin.php?page=landing-config-snippets&action=edit&id=' . $s['id']);
                    $delete_url = wp_nonce_url(
                        admin_url('admin.php?page=landing-config-snippets&action=delete&id=' . $s['id']),
                        'landing_snippets_delete'
                    );
                    $scope_label = $s['scope'] === 'local'
                        ? 'local (' . count($s['target_post_ids']) . ' страниц)'
                        : 'global';
                ?>
                    <tr>
                        <td><strong><?php echo esc_html($s['title']); ?></strong></td>
                        <td><code><?php echo esc_html($s['position']); ?></code></td>
                        <td><?php echo esc_html($scope_label); ?></td>
                        <td><?php echo $s['enabled'] ? '✅' : '❌'; ?></td>
                        <td><?php echo (int) $s['priority']; ?></td>
                        <td>
                            <a href="<?php echo esc_url($edit_url); ?>">Edit</a>
                            |
                            <a href="<?php echo esc_url($delete_url); ?>"
                               onclick="return confirm('Удалить снипет?');"
                               style="color:#a00;">Delete</a>
                        </td>
                    </tr>
                <?php endforeach; endif; ?>
            </tbody>
        </table>
    </div>
    <?php
}

function render_edit_form(): void {
    $id = isset($_GET['id']) ? (int) $_GET['id'] : 0;
    $snippet = $id ? get_snippet($id) : [
        'id' => 0, 'title' => '', 'code' => '',
        'position' => 'head', 'scope' => 'global',
        'target_post_ids' => [], 'enabled' => true, 'priority' => 10,
    ];
    if (!$snippet) {
        echo '<div class="wrap"><h1>Снипет не найден</h1></div>';
        return;
    }
    $action_url = admin_url('admin.php?page=landing-config-snippets');
    $pages = get_posts(['post_type' => 'page', 'posts_per_page' => 200, 'post_status' => 'publish']);
    $posts_list = get_posts(['post_type' => 'post', 'posts_per_page' => 200, 'post_status' => 'publish']);
    $all_targets = array_merge($pages, $posts_list);
    ?>
    <div class="wrap">
        <h1><?php echo $id ? 'Редактирование снипета' : 'Новый снипет'; ?></h1>
        <form method="post" action="<?php echo esc_url($action_url); ?>">
            <?php wp_nonce_field('landing_snippets_save'); ?>
            <input type="hidden" name="action" value="save">
            <input type="hidden" name="id" value="<?php echo (int) $snippet['id']; ?>">
            <table class="form-table">
                <tr>
                    <th><label for="title">Title</label></th>
                    <td><input type="text" id="title" name="title" required
                            value="<?php echo esc_attr($snippet['title']); ?>"
                            class="regular-text" placeholder="Y.Metrika, GTM, Schema.org Home..."></td>
                </tr>
                <tr>
                    <th>Position</th>
                    <td>
                        <?php foreach (['head' => '&lt;head&gt;',
                                        'body_open' => 'начало &lt;body&gt;',
                                        'body_close' => 'перед &lt;/body&gt; (footer)'] as $v => $label): ?>
                            <label style="margin-right:1em;">
                                <input type="radio" name="position" value="<?php echo $v; ?>"
                                    <?php checked($snippet['position'], $v); ?>>
                                <?php echo $label; ?>
                            </label>
                        <?php endforeach; ?>
                    </td>
                </tr>
                <tr>
                    <th>Scope</th>
                    <td>
                        <label style="margin-right:1em;">
                            <input type="radio" name="scope" value="global"
                                <?php checked($snippet['scope'], 'global'); ?>>
                            global (на всех страницах сайта)
                        </label>
                        <label>
                            <input type="radio" name="scope" value="local"
                                <?php checked($snippet['scope'], 'local'); ?>>
                            local (только на выбранных)
                        </label>
                    </td>
                </tr>
                <tr>
                    <th>Target pages (для local)</th>
                    <td>
                        <select name="target_post_ids[]" multiple style="width:60%;min-height:8em;">
                            <?php foreach ($all_targets as $t):
                                $sel = in_array((int) $t->ID, $snippet['target_post_ids'], true);
                            ?>
                                <option value="<?php echo (int) $t->ID; ?>" <?php echo $sel ? 'selected' : ''; ?>>
                                    [<?php echo esc_html($t->post_type); ?>]
                                    <?php echo esc_html($t->post_title ?: '(без названия)'); ?>
                                    (id=<?php echo (int) $t->ID; ?>)
                                </option>
                            <?php endforeach; ?>
                        </select>
                        <p class="description">Удерживайте Ctrl/Cmd для выбора нескольких.</p>
                    </td>
                </tr>
                <tr>
                    <th>Enabled</th>
                    <td>
                        <label>
                            <input type="checkbox" name="enabled" value="1"
                                <?php checked($snippet['enabled']); ?>>
                            Активен
                        </label>
                    </td>
                </tr>
                <tr>
                    <th><label for="priority">Priority</label></th>
                    <td><input type="number" id="priority" name="priority"
                            value="<?php echo (int) $snippet['priority']; ?>" min="1" max="999" style="width:6em;">
                        <p class="description">Меньшее число = раньше в выводе. Default 10.</p></td>
                </tr>
                <tr>
                    <th><label for="code">Code (HTML)</label></th>
                    <td>
                        <textarea id="code" name="code" rows="14" class="large-text code"
                            placeholder="<!-- Вставьте сюда snippet целиком: <script>...</script>, <meta ...>, ваш виджет --><?php echo "\n"; ?>"
                            style="font-family: Consolas, Monaco, monospace;"><?php echo esc_textarea($snippet['code']); ?></textarea>
                        <p class="description">Разрешено: script, meta, link, style, noscript, iframe, div, span, img, a, p, br.
                            Остальное фильтруется.</p>
                    </td>
                </tr>
            </table>
            <p>
                <button type="submit" class="button button-primary">Сохранить</button>
                <a href="<?php echo esc_url($action_url); ?>" class="button">Cancel</a>
            </p>
        </form>
    </div>
    <?php
}

function handle_save(): void {
    $id = save_snippet([
        'id'              => isset($_POST['id']) ? (int) $_POST['id'] : 0,
        'title'           => $_POST['title'] ?? '',
        'code'            => wp_unslash($_POST['code'] ?? ''),
        'position'        => $_POST['position'] ?? 'head',
        'scope'           => $_POST['scope'] ?? 'global',
        'target_post_ids' => (array) ($_POST['target_post_ids'] ?? []),
        'enabled'         => !empty($_POST['enabled']),
        'priority'        => (int) ($_POST['priority'] ?? 10),
    ]);
    $url = admin_url('admin.php?page=landing-config-snippets&saved=' . $id);
    wp_safe_redirect($url);
    exit;
}

function handle_delete(): void {
    $id = isset($_GET['id']) ? (int) $_GET['id'] : 0;
    if ($id > 0) delete_snippet($id);
    wp_safe_redirect(admin_url('admin.php?page=landing-config-snippets&deleted=1'));
    exit;
}
```

- [ ] **Step 2: Add require in landing-config.php**

After `require_once .../snippets.php`, add:

```php
require_once LANDING_CONFIG_DIR . '/includes/admin-snippets.php';
```

- [ ] **Step 3: php -l on both**

- [ ] **Step 4: Commit**

```bash
git add skills/wp-landing-config/mu-plugin/landing-config/includes/admin-snippets.php \
        skills/wp-landing-config/mu-plugin/landing-config/landing-config.php
git commit -m "feat(wp-landing-config): admin-snippets.php — list + edit page

Menu entry 'Лендинг → Снипеты'. WP_List_Table-style list with columns
Title/Position/Scope/Enabled/Priority/Actions + Add new.

Edit form: title, position (head/body_open/body_close), scope (global/local),
target pages multi-select (visible always; ignored when scope=global),
enabled checkbox, priority number, code textarea (monospace).

Save/delete go through nonced POST/GET handlers, redirect back to list.
Capability checks (manage_options) on every entry point.

Co-Authored-By: Claude Opus 4.7 (1M context) <noreply@anthropic.com>"
```

---

## Task 6: Live smoke на ailexi.ru + docs

**Files:**
- Modify: `CLAUDE.md`
- Modify: `docs/SETUP.md`
- Modify: `docs/beget-cookbook.md`

- [ ] **Step 1: Re-deploy**

```bash
bash skills/wp-landing-config/scripts/install-mu-plugin.sh /tmp/test-s2a
```

Expected: deploy completes; меню «Лендинг → Снипеты» появляется.

- [ ] **Step 2: Manual UI smoke в браузере**

1. `http://ailexi.ru/wp-admin/admin.php?page=landing-config-snippets` — пустой список + кнопка Add.
2. Нажать Add → форма.
3. Title=«Y.Metrika smoke», position=head, scope=global, enabled=on, priority=10, code=полный snippet с ya.ru.
4. Save → редирект на список, видна 1 строка.
5. `curl -s http://ailexi.ru/ | grep -c "mc.yandex.ru/metrika"` → ≥ 1.
6. Edit snippet → Disable → Save. `curl` → 0.
7. Re-enable. Add второй snippet «GTM noscript», position=body_open, code=`<noscript><iframe src="https://www.googletagmanager.com/ns.html?id=GTM-XXX" height="0" width="0" style="display:none;visibility:hidden"></iframe></noscript>`. Save.
8. `curl http://ailexi.ru/ | grep -c "GTM-XXX"` → ≥ 1.
9. Delete оба snippet'а → `curl` чисто.

- [ ] **Step 3: Update CLAUDE.md**

Найти в `CLAUDE.md` секцию `## Landing-config mu-plugin (S2-A)`, заменить bullet:

```
- Head & SEO (GA4, Y.Metrika, FB Pixel, GSC, OG, custom HTML)
```

на:

```
- Снипеты (любые HTML/JS-снипеты в head/body_open/footer; global или local-per-page)
```

- [ ] **Step 4: Update docs/SETUP.md**

Найти секцию «В wp-admin появляется меню «Лендинг» с подстраницами:» и заменить строку:

```
- Head & SEO (счётчики, OG, GSC, raw HTML)
```

на:

```
- Снипеты (любой HTML в head/body/footer, global + local-per-page)
```

Добавить в конец того же файла раздел:

```markdown

## Snippets manager (S2-A.2)

Универсальный менеджер snippet'ов заменяет старый экран «Head & SEO».

### Создание snippet'а

«Лендинг → Снипеты → Добавить». Поля: Title (для админки), Position
(head/body_open/body_close), Scope (global или local), Target pages (для local),
Enabled, Priority, Code.

### Что можно вставлять

Allow-list тегов: `script`, `meta`, `link`, `style`, `noscript`, `iframe`,
`div`, `span`, `img`, `a`, `p`, `br`. Это покрывает GA4, Y.Metrika,
FB Pixel, TikTok Pixel, VK Pixel, MyTarget, GTM (head + noscript),
schema.org JSON-LD, любые виджеты-чаты (JivoSite, Calendly, Intercom),
font preload, custom CSS.

### Безопасность

Capability `manage_options` (только admin/super-admin). `<script>` разрешён
именно потому что это admin-only поле — но это значит **скомпрометированный
admin = XSS на всех страницах**. Не давайте `manage_options` кому попало.

### Локальные snippet'ы

При `scope=local` snippet выводится только если `get_queried_object_id()`
в `target_post_ids`. Локальные snippet'ы той же `position` выводятся
ПОСЛЕ глобальных, поэтому каскадно перекрывают (например, локальный
JSON-LD на странице «Услуги» дополняет глобальный schema.org).
```

- [ ] **Step 5: Update docs/beget-cookbook.md**

Добавить в конец:

```markdown

## S2-A.2 Snippets manager live smoke (2026-05-19)

Validated на ailexi.ru:
- mu-plugin re-deploy через install-mu-plugin.sh — OK
- Меню «Снипеты» появилось (заменило «Head & SEO»)
- Add snippet form работает: Y.Metrika snippet сохранён, проявился в `<head>` (curl + grep)
- Disable → snippet исчез; Enable → вернулся
- Body_open snippet (GTM noscript) проявился в начале `<body>`
- Локальный snippet рендерится только на target Page

CPT `lp_snippet` создан per-blog (hidden from main Posts menu).
Старые `wp_options::landing_<ga4_id|yandex_metrika_id|...>` удалены —
не было production-данных, migration не понадобилась.
```

- [ ] **Step 6: Commit**

```bash
git add CLAUDE.md docs/SETUP.md docs/beget-cookbook.md
git commit -m "docs(s2a2): snippets manager — CLAUDE.md + SETUP.md + cookbook updates

Replace 'Head & SEO' references with 'Снипеты' across all 3 docs.
SETUP.md gets dedicated 'Snippets manager' section explaining allow-list,
security model (manage_options is the boundary), local cascade.
Cookbook documents live smoke validation on ailexi.ru.

Co-Authored-By: Claude Opus 4.7 (1M context) <noreply@anthropic.com>"
```

---

## Self-Review

**1. Spec coverage:** all spec sections covered by tasks:
- §2 удаление старой Head & SEO → Task 1
- §3.1 CPT lp_snippet → Task 3
- §3.2 Renderer → Task 4
- §3.3 sanitize wp_kses → Task 3
- §3.4.1+§3.4.2 list + edit form → Task 5
- §3.4.3 meta-box в Page/Post редакторе → **DEFERRED to next iteration** (not in this plan — see "Out of scope" below)
- §4 меню → Tasks 1+5
- §5 файлы → Tasks 1-5
- §6 тесты → Tasks 3+4
- §7 live smoke → Task 6
- §10 migration cleanup → не нужно (нет prod-данных)

**2. Placeholder scan:** None found — all steps have runnable code or commands.

**3. Type consistency:**
- `save_snippet($args)`, `get_snippet($id)`, `list_snippets($filter=[])`, `delete_snippet($id)`, `render($position)` — consistent across plan
- post_meta keys `_lp_snippet_*` consistent
- VALID_POSITIONS const used in both save_snippet validation and render() arg check

**4. Deferred from spec:**
- §3.4.3 ad-hoc meta-box в Page/Post editor — отдельный спринт (S2-A.2.1). Pure UX-добавка, не блокирует основной функционал.

---

## Execution

Use superpowers:subagent-driven-development. Each task → one impl subagent + spec review + code-quality review.
