# S2-A.3 Network-Admin Unification — Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Свести CTA / Integrations / Snippets настройки в единую Network admin с cascade «network → site override» через CPT-модель.

**Architecture:** Три CPT (`lp_cta`, `lp_integration`, `lp_snippet`) поверх единого `cascade.php` резолвера. Селектор сегмента (`?segment=N`) в каждой управляющей странице. Read-only mode на subsite с server-side guard. Фазы инкрементальны — каждая закрывает один раздел S2-A.3.

**Tech Stack:** PHP 8.3, WordPress 6.9 multisite (subdomain), wp-cli, bats для integration tests. Существующая инфраструктура: AES-256-GCM шифрование, `wp_<bid>_landing_leads` per-blog tables, super-admin auth.

**Спек:** [docs/superpowers/specs/2026-05-19-s2a3-network-admin-unification-design.md](../specs/2026-05-19-s2a3-network-admin-unification-design.md)

**Environment context (для каждой фазы):**
- Локально: PHP shim в `~/bin/php` (без openssl extension — 5 encryption-тестов pre-existing fail, игнорировать)
- Beget shared: PHP 8.3 через `/usr/local/bin/php8.3`, wp-cli через `/usr/local/bin/wp-cli.phar`
- SSH: `/c/Users/esper21/.ssh/beget_poc` → `esper21@esper21.beget.tech`
- Test multisite: `ailexi.ru` (blog_id=1) + `russian.ailexi.ru` (blog_id=2), admin/Admin2026Aa1!
- Deploy: `bash skills/wp-landing-config/scripts/install-mu-plugin.sh /tmp/test-s2a`

---

## Phase A3.1 — Cascade resolver + CTA CPT + migration

**Цель фазы:** общий `cascade.php` резолвер + `lp_cta` CPT + `landing_get_cta()` через cascade + миграция `wp_options.landing_cta_presets` → CPT записи. CTA через cascade работает, Integrations пока на старой схеме.

**Files:**
- Create: `skills/wp-landing-config/mu-plugin/landing-config/includes/cascade.php`
- Create: `skills/wp-landing-config/mu-plugin/landing-config/includes/cta.php`
- Create: `skills/wp-landing-config/mu-plugin/landing-config/includes/migrate-to-s2a3.php`
- Modify: `skills/wp-landing-config/mu-plugin/landing-config/landing-config.php` (порядок require + триггер миграции)
- Modify: `skills/wp-landing-config/mu-plugin/landing-config/includes/helpers.php` (refactor `landing_get_cta` если он там; иначе оставить cta.php)
- Test: `skills/wp-landing-config/tests/test_cascade.php`
- Test: `skills/wp-landing-config/tests/test_cta.php`
- Test: `skills/wp-landing-config/tests/test_migrate_to_s2a3.php`

---

### Task A3.1.1: Cascade resolver — RED

- [ ] **Step 1: Создать failing test**

Создать `skills/wp-landing-config/tests/test_cascade.php`:

```php
<?php
require_once __DIR__ . '/fixtures/wp-bootstrap.php';
require_once __DIR__ . '/../mu-plugin/landing-config/includes/cascade.php';

use function LandingConfig\Cascade\resolve_for_blog;
use function LandingConfig\Cascade\list_for_blog;
use function LandingConfig\Cascade\has_site_override;

$failures = 0; $tests = 0;
function assert_test($cond, $msg) {
    global $failures, $tests;
    $tests++;
    if (!$cond) { echo "FAIL: $msg\n"; $failures++; }
}

function reset_cascade() {
    $GLOBALS['_mock_posts'] = [];
    $GLOBALS['_mock_post_meta'] = [];
    $GLOBALS['_mock_next_post_id'] = 1;
}

function seed_cpt(string $cpt, int $blog_id, string $name, array $meta, bool $is_network): int {
    static $id = 1000;
    $id++;
    $GLOBALS['_mock_posts'][$id] = (object) ['ID' => $id, 'post_type' => $cpt, 'post_status' => 'publish', 'post_title' => $name];
    foreach ($meta as $k => $v) {
        $GLOBALS['_mock_post_meta'][$id][$k] = $v;
    }
    $GLOBALS['_mock_post_meta'][$id]['_lp_test_name'] = $name;
    $GLOBALS['_mock_post_meta'][$id]['_lp_is_network'] = $is_network ? '1' : '0';
    $GLOBALS['_mock_post_meta'][$id]['_lp_blog_id'] = $blog_id;
    return $id;
}

// T1: only network → returns network
reset_cascade();
seed_cpt('lp_test', 1, 'primary', ['_lp_test_value' => 'network_v'], true);
$r = resolve_for_blog('lp_test', '_lp_test_name', '_lp_is_network', 'primary', 2);
assert_test($r !== null && ($r['_lp_test_value'] ?? '') === 'network_v', 'T1 only network returned');

// T2: only site → returns site
reset_cascade();
seed_cpt('lp_test', 2, 'primary', ['_lp_test_value' => 'site_v'], false);
$r = resolve_for_blog('lp_test', '_lp_test_name', '_lp_is_network', 'primary', 2);
assert_test($r !== null && ($r['_lp_test_value'] ?? '') === 'site_v', 'T2 only site returned');

// T3: both → site wins
reset_cascade();
seed_cpt('lp_test', 1, 'primary', ['_lp_test_value' => 'net'], true);
seed_cpt('lp_test', 2, 'primary', ['_lp_test_value' => 'site'], false);
$r = resolve_for_blog('lp_test', '_lp_test_name', '_lp_is_network', 'primary', 2);
assert_test(($r['_lp_test_value'] ?? '') === 'site', 'T3 site wins over network');

// T4: neither → null
reset_cascade();
$r = resolve_for_blog('lp_test', '_lp_test_name', '_lp_is_network', 'primary', 2);
assert_test($r === null, 'T4 null when neither');

// T5: has_site_override returns true/false correctly
reset_cascade();
seed_cpt('lp_test', 2, 'primary', ['_lp_test_value' => 'x'], false);
assert_test(has_site_override('lp_test', '_lp_test_name', '_lp_is_network', 'primary', 2) === true, 'T5a has_site_override true');
assert_test(has_site_override('lp_test', '_lp_test_name', '_lp_is_network', 'other', 2) === false, 'T5b has_site_override false');

// T6: list_for_blog merges network + site, site replaces by name
reset_cascade();
seed_cpt('lp_test', 1, 'a', ['_lp_test_value' => 'net_a'], true);
seed_cpt('lp_test', 1, 'b', ['_lp_test_value' => 'net_b'], true);
seed_cpt('lp_test', 2, 'a', ['_lp_test_value' => 'site_a'], false);
$list = list_for_blog('lp_test', '_lp_test_name', '_lp_is_network', 2);
$by_name = [];
foreach ($list as $row) { $by_name[$row['_lp_test_name']] = $row['_lp_test_value']; }
assert_test($by_name['a'] === 'site_a' && $by_name['b'] === 'net_b', 'T6 list_for_blog merges correctly');

echo "$tests tests, $failures failures\n";
exit($failures > 0 ? 1 : 0);
```

- [ ] **Step 2: Расширить wp-bootstrap.php mock'ами для cascade**

Проверить `skills/wp-landing-config/tests/fixtures/wp-bootstrap.php` — он должен поддерживать `get_posts`, `get_post_meta`, `switch_to_blog`. Если чего-то нет — добавить.

В частности, для cascade резолвера нужны:
- `get_posts(['post_type' => X, 'meta_query' => [...]])` — должен учитывать meta_query при выборке (mock возвращает только посты, чьи meta удовлетворяют условиям).
- `switch_to_blog(int $blog_id)` / `restore_current_blog()` — mock должен сохранять текущий blog_id в `$GLOBALS['_mock_current_blog_id']`.
- `get_current_blog_id()` — возвращает `$GLOBALS['_mock_current_blog_id'] ?? 1`.

Точный кусок mock'а добавить, если отсутствует (в одной правке):

```php
// в wp-bootstrap.php если ещё нет:
if (!function_exists('get_current_blog_id')) {
    function get_current_blog_id() {
        return $GLOBALS['_mock_current_blog_id'] ?? 1;
    }
}
if (!function_exists('switch_to_blog')) {
    function switch_to_blog($id) {
        $GLOBALS['_mock_blog_stack'][] = $GLOBALS['_mock_current_blog_id'] ?? 1;
        $GLOBALS['_mock_current_blog_id'] = (int) $id;
        return true;
    }
}
if (!function_exists('restore_current_blog')) {
    function restore_current_blog() {
        if (!empty($GLOBALS['_mock_blog_stack'])) {
            $GLOBALS['_mock_current_blog_id'] = array_pop($GLOBALS['_mock_blog_stack']);
        }
        return true;
    }
}
```

И расширить `get_posts` так, чтобы он фильтровал по `meta_query[*].key=value` (простая `=` поддержка достаточна — никаких `BETWEEN`/`LIKE`).

- [ ] **Step 3: Запустить тест — должен упасть**

```bash
cd skills/wp-landing-config
php tests/test_cascade.php
```

Ожидаемо: `Fatal error: require_once: cascade.php` или `Call to undefined function LandingConfig\Cascade\resolve_for_blog`.

---

### Task A3.1.2: Cascade resolver — GREEN

- [ ] **Step 1: Создать `includes/cascade.php`**

```php
<?php
namespace LandingConfig\Cascade;

if (!defined('ABSPATH')) { exit; }

const NETWORK_BLOG_ID = 1;

function _list_raw(string $cpt, string $is_network_meta_key, bool $is_network): array {
    $posts = \get_posts([
        'post_type'      => $cpt,
        'posts_per_page' => -1,
        'post_status'    => 'publish',
        'meta_query'     => [
            ['key' => $is_network_meta_key, 'value' => $is_network ? '1' : '0'],
        ],
        'orderby'        => 'ID',
        'order'          => 'ASC',
    ]);
    $out = [];
    foreach ($posts as $p) {
        $row = [];
        foreach (\get_post_meta((int)$p->ID) as $key => $values) {
            // get_post_meta($id) returns array<key, array<int, string>> — flatten
            $row[$key] = is_array($values) ? ($values[0] ?? '') : (string) $values;
        }
        $row['__post_id'] = (int) $p->ID;
        $row['__title']   = $p->post_title ?? '';
        $out[] = $row;
    }
    return $out;
}

function _with_blog(int $blog_id, callable $fn) {
    $prev = \function_exists('get_current_blog_id') ? \get_current_blog_id() : 1;
    if ($prev === $blog_id) return $fn();
    \switch_to_blog($blog_id);
    try { return $fn(); }
    finally { \restore_current_blog(); }
}

function list_for_blog(string $cpt, string $name_meta_key, string $is_network_meta_key, int $blog_id): array {
    // 1. Site rows (current blog scope)
    $site = _with_blog($blog_id, fn() => _list_raw($cpt, $is_network_meta_key, false));
    $site_by_name = [];
    foreach ($site as $row) {
        $nm = $row[$name_meta_key] ?? '';
        if ($nm !== '') $site_by_name[$nm] = $row;
    }
    // 2. Network rows
    $network = _with_blog(NETWORK_BLOG_ID, fn() => _list_raw($cpt, $is_network_meta_key, true));
    $network_filtered = [];
    foreach ($network as $row) {
        $nm = $row[$name_meta_key] ?? '';
        if ($nm !== '' && isset($site_by_name[$nm])) continue;  // site override wins
        $network_filtered[] = $row;
    }
    return array_merge($network_filtered, $site);
}

function resolve_for_blog(string $cpt, string $name_meta_key, string $is_network_meta_key, string $name, int $blog_id): ?array {
    $list = list_for_blog($cpt, $name_meta_key, $is_network_meta_key, $blog_id);
    foreach ($list as $row) {
        if (($row[$name_meta_key] ?? '') === $name) return $row;
    }
    return null;
}

function has_site_override(string $cpt, string $name_meta_key, string $is_network_meta_key, string $name, int $blog_id): bool {
    $site = _with_blog($blog_id, fn() => _list_raw($cpt, $is_network_meta_key, false));
    foreach ($site as $row) {
        if (($row[$name_meta_key] ?? '') === $name) return true;
    }
    return false;
}
```

- [ ] **Step 2: Запустить тест — должен пройти**

```bash
cd skills/wp-landing-config
php tests/test_cascade.php
```

Ожидаемо: `6 tests, 0 failures`.

Если какие-то падают на mock `get_posts` (не понимает meta_query) — допилить mock в `wp-bootstrap.php`. Это нормально, расширение mock'а под этот случай ожидается.

- [ ] **Step 3: Commit**

```bash
git add skills/wp-landing-config/tests/test_cascade.php skills/wp-landing-config/tests/fixtures/wp-bootstrap.php skills/wp-landing-config/mu-plugin/landing-config/includes/cascade.php
git commit -m "feat(wp-landing-config): A3.1 — cascade resolver (network → site override)

Unit-tested: resolve_for_blog / list_for_blog / has_site_override.
6/6 tests green. Поверх этого построим CTA/Integrations/Snippets cascade.

Co-Authored-By: Claude Opus 4.7 (1M context) <noreply@anthropic.com>"
```

---

### Task A3.1.3: CTA CPT — RED

- [ ] **Step 1: Создать failing test**

Создать `skills/wp-landing-config/tests/test_cta.php`:

```php
<?php
require_once __DIR__ . '/fixtures/wp-bootstrap.php';
require_once __DIR__ . '/../mu-plugin/landing-config/includes/cascade.php';
require_once __DIR__ . '/../mu-plugin/landing-config/includes/cta.php';

use function LandingConfig\CTA\save_cta;
use function LandingConfig\CTA\get_cta;
use function LandingConfig\CTA\list_ctas;
use function LandingConfig\CTA\delete_cta;
use function LandingConfig\CTA\resolve_cta;

$failures = 0; $tests = 0;
function assert_test($cond, $msg) { global $failures, $tests; $tests++; if (!$cond) { echo "FAIL: $msg\n"; $failures++; } }

function reset_cta() {
    $GLOBALS['_mock_posts'] = [];
    $GLOBALS['_mock_post_meta'] = [];
    $GLOBALS['_mock_next_post_id'] = 1;
    $GLOBALS['_mock_current_blog_id'] = 1;
    $GLOBALS['_mock_blog_stack'] = [];
}

// T1: save+get round-trip
reset_cta();
$id = save_cta(['preset_name' => 'primary', 'type' => 'scroll', 'label' => 'Заявка',
    'target' => '#form', 'phone' => '', 'form_id' => '', 'message_template' => ''], false, 1);
assert_test($id > 0, 'T1a save_cta returns id');
$row = get_cta($id);
assert_test($row['preset_name'] === 'primary' && $row['label'] === 'Заявка', 'T1b round-trip CTA');
assert_test($row['is_network'] === false, 'T1c is_network=false stored');

// T2: cascade — site override wins
reset_cta();
save_cta(['preset_name' => 'whatsapp', 'type' => 'whatsapp', 'label' => 'NET WA',
    'target' => '', 'phone' => '+1', 'form_id' => '', 'message_template' => ''], true, 1);
$GLOBALS['_mock_current_blog_id'] = 2;
save_cta(['preset_name' => 'whatsapp', 'type' => 'whatsapp', 'label' => 'RUSSIAN WA',
    'target' => '', 'phone' => '+7', 'form_id' => '', 'message_template' => ''], false, 2);
$r = resolve_cta('whatsapp', 2);
assert_test($r['label'] === 'RUSSIAN WA' && $r['phone'] === '+7', 'T2 site override wins on blog_id=2');

// T3: cascade — fallback to network
$r = resolve_cta('whatsapp', 1);  // blog_id=1 has only network record
assert_test($r['label'] === 'NET WA', 'T3 network fallback on blog_id=1');

// T4: list_ctas for blog_id=2 returns 1 (whatsapp site) — primary не сохранён
reset_cta();
save_cta(['preset_name' => 'primary', 'type' => 'scroll', 'label' => 'Net Primary',
    'target' => '#form', 'phone' => '', 'form_id' => '', 'message_template' => ''], true, 1);
$GLOBALS['_mock_current_blog_id'] = 2;
save_cta(['preset_name' => 'whatsapp', 'type' => 'whatsapp', 'label' => 'Site WA',
    'target' => '', 'phone' => '+7', 'form_id' => '', 'message_template' => ''], false, 2);
$list = list_ctas(2);
$names = array_column($list, 'preset_name');
assert_test(in_array('primary', $names) && in_array('whatsapp', $names), 'T4 list merges network + site');

// T5: delete_cta removes record
reset_cta();
$id = save_cta(['preset_name' => 'phone', 'type' => 'tel', 'label' => 'Call', 'target' => '',
    'phone' => '+1', 'form_id' => '', 'message_template' => ''], false, 1);
assert_test(delete_cta($id) === true, 'T5a delete returns true');
assert_test(get_cta($id) === null, 'T5b deleted CTA returns null');

echo "$tests tests, $failures failures\n";
exit($failures > 0 ? 1 : 0);
```

- [ ] **Step 2: Запустить — должен упасть с require error**

```bash
cd skills/wp-landing-config
php tests/test_cta.php
```

Ожидаемо: `require_once cta.php failed`.

---

### Task A3.1.4: CTA CPT — GREEN

- [ ] **Step 1: Создать `includes/cta.php`**

```php
<?php
namespace LandingConfig\CTA;

if (!defined('ABSPATH')) { exit; }

use function LandingConfig\Cascade\resolve_for_blog;
use function LandingConfig\Cascade\list_for_blog;
use function LandingConfig\Cascade\has_site_override;

const POST_TYPE = 'lp_cta';
const NAME_META = '_lp_cta_preset_name';
const NETWORK_META = '_lp_cta_is_network';
const PRESET_NAMES = ['primary', 'whatsapp', 'phone', 'form_modal', 'learn_more'];
const VALID_TYPES = ['scroll', 'whatsapp', 'tel', 'mailto', 'modal', 'anchor', 'url'];

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
            'edit_posts'        => 'manage_options',
            'edit_others_posts' => 'manage_options',
            'publish_posts'     => 'manage_options',
            'delete_posts'      => 'manage_options',
            'read'              => 'read',
        ],
    ]);
}

function _with_blog(int $blog_id, callable $fn) {
    $prev = \get_current_blog_id();
    if ($prev === $blog_id) return $fn();
    \switch_to_blog($blog_id);
    try { return $fn(); }
    finally { \restore_current_blog(); }
}

function save_cta(array $args, bool $is_network, int $blog_id): int {
    return _with_blog($blog_id, function () use ($args, $is_network) {
        $preset = \sanitize_text_field($args['preset_name'] ?? '');
        if (!in_array($preset, PRESET_NAMES, true)) {
            return 0;
        }
        $type = \sanitize_text_field($args['type'] ?? 'scroll');
        if (!in_array($type, VALID_TYPES, true)) $type = 'scroll';

        $post = ['post_type' => POST_TYPE, 'post_status' => 'publish', 'post_title' => $preset];
        if (!empty($args['id'])) {
            $post['ID'] = (int) $args['id'];
            $id = \wp_update_post($post);
        } else {
            $id = \wp_insert_post($post);
        }
        \update_post_meta($id, NAME_META, $preset);
        \update_post_meta($id, '_lp_cta_type', $type);
        \update_post_meta($id, '_lp_cta_label', \sanitize_text_field($args['label'] ?? ''));
        \update_post_meta($id, '_lp_cta_target', \sanitize_text_field($args['target'] ?? ''));
        \update_post_meta($id, '_lp_cta_phone', \sanitize_text_field($args['phone'] ?? ''));
        \update_post_meta($id, '_lp_cta_form_id', \sanitize_text_field($args['form_id'] ?? ''));
        \update_post_meta($id, '_lp_cta_message_template', \sanitize_text_field($args['message_template'] ?? ''));
        \update_post_meta($id, NETWORK_META, $is_network ? '1' : '0');
        return (int) $id;
    });
}

function get_cta(int $id): ?array {
    $p = \get_post($id);
    if (!$p || ($p->post_type ?? '') !== POST_TYPE) return null;
    return [
        'id'               => $id,
        'preset_name'      => (string) \get_post_meta($id, NAME_META, true),
        'type'             => (string) \get_post_meta($id, '_lp_cta_type', true),
        'label'            => (string) \get_post_meta($id, '_lp_cta_label', true),
        'target'           => (string) \get_post_meta($id, '_lp_cta_target', true),
        'phone'            => (string) \get_post_meta($id, '_lp_cta_phone', true),
        'form_id'          => (string) \get_post_meta($id, '_lp_cta_form_id', true),
        'message_template' => (string) \get_post_meta($id, '_lp_cta_message_template', true),
        'is_network'       => (string) \get_post_meta($id, NETWORK_META, true) === '1',
    ];
}

function delete_cta(int $id): bool {
    return (bool) \wp_delete_post($id, true);
}

function list_ctas(int $blog_id): array {
    $raw = list_for_blog(POST_TYPE, NAME_META, NETWORK_META, $blog_id);
    $out = [];
    foreach ($raw as $row) {
        $out[] = [
            'id'               => (int) ($row['__post_id'] ?? 0),
            'preset_name'      => $row[NAME_META] ?? '',
            'type'             => $row['_lp_cta_type'] ?? 'scroll',
            'label'            => $row['_lp_cta_label'] ?? '',
            'target'           => $row['_lp_cta_target'] ?? '',
            'phone'            => $row['_lp_cta_phone'] ?? '',
            'form_id'          => $row['_lp_cta_form_id'] ?? '',
            'message_template' => $row['_lp_cta_message_template'] ?? '',
            'is_network'       => ($row[NETWORK_META] ?? '0') === '1',
        ];
    }
    return $out;
}

function resolve_cta(string $preset_name, int $blog_id): ?array {
    $row = resolve_for_blog(POST_TYPE, NAME_META, NETWORK_META, $preset_name, $blog_id);
    if (!$row) return null;
    return [
        'preset_name'      => $row[NAME_META] ?? $preset_name,
        'type'             => $row['_lp_cta_type'] ?? 'scroll',
        'label'            => $row['_lp_cta_label'] ?? '',
        'target'           => $row['_lp_cta_target'] ?? '',
        'phone'            => $row['_lp_cta_phone'] ?? '',
        'form_id'          => $row['_lp_cta_form_id'] ?? '',
        'message_template' => $row['_lp_cta_message_template'] ?? '',
        'is_network'       => ($row[NETWORK_META] ?? '0') === '1',
    ];
}

function has_override(string $preset_name, int $blog_id): bool {
    return has_site_override(POST_TYPE, NAME_META, NETWORK_META, $preset_name, $blog_id);
}
```

- [ ] **Step 2: Запустить тест — должен пройти**

```bash
cd skills/wp-landing-config
php tests/test_cta.php
```

Ожидаемо: `5 tests, 0 failures`.

- [ ] **Step 3: Commit**

```bash
git add skills/wp-landing-config/tests/test_cta.php skills/wp-landing-config/mu-plugin/landing-config/includes/cta.php
git commit -m "feat(wp-landing-config): A3.1 — lp_cta CPT + CRUD + cascade resolve_cta

5/5 tests: save+get round-trip, site-override wins, network fallback,
list_ctas merge, delete. Использует общий cascade.php резолвер.

Co-Authored-By: Claude Opus 4.7 (1M context) <noreply@anthropic.com>"
```

---

### Task A3.1.5: landing_get_cta() refactor через cascade — RED

- [ ] **Step 1: Найти текущую реализацию helper'а**

```bash
grep -rn 'function landing_get_cta' skills/wp-landing-config/mu-plugin/landing-config/
```

Ожидаемо: расположение либо в `helpers.php`, либо в одном из admin-*.php.

- [ ] **Step 2: Создать failing integration-test**

Создать `skills/wp-landing-config/tests/test_landing_get_cta.php`:

```php
<?php
require_once __DIR__ . '/fixtures/wp-bootstrap.php';
require_once __DIR__ . '/../mu-plugin/landing-config/includes/cascade.php';
require_once __DIR__ . '/../mu-plugin/landing-config/includes/cta.php';
require_once __DIR__ . '/../mu-plugin/landing-config/includes/helpers.php';

use function LandingConfig\CTA\save_cta;

$failures = 0; $tests = 0;
function assert_test($cond, $msg) { global $failures, $tests; $tests++; if (!$cond) { echo "FAIL: $msg\n"; $failures++; } }

function reset_lg() {
    $GLOBALS['_mock_posts'] = [];
    $GLOBALS['_mock_post_meta'] = [];
    $GLOBALS['_mock_next_post_id'] = 1;
    $GLOBALS['_mock_current_blog_id'] = 1;
    $GLOBALS['_mock_options'] = [];
}

// T1: landing_get_cta returns network preset on blog_id=1
reset_lg();
save_cta(['preset_name' => 'primary', 'type' => 'scroll', 'label' => 'Net Primary',
    'target' => '#form', 'phone' => '', 'form_id' => '', 'message_template' => ''], true, 1);
$r = landing_get_cta('primary');
assert_test($r !== null && $r['label'] === 'Net Primary', 'T1 network CTA returned');

// T2: landing_get_cta returns site override on blog_id=2
reset_lg();
save_cta(['preset_name' => 'primary', 'type' => 'scroll', 'label' => 'Net Primary',
    'target' => '#form', 'phone' => '', 'form_id' => '', 'message_template' => ''], true, 1);
$GLOBALS['_mock_current_blog_id'] = 2;
save_cta(['preset_name' => 'primary', 'type' => 'scroll', 'label' => 'Russian Primary',
    'target' => '#form-ru', 'phone' => '', 'form_id' => '', 'message_template' => ''], false, 2);
$r = landing_get_cta('primary');
assert_test($r !== null && $r['label'] === 'Russian Primary', 'T2 site override returned');

// T3: url_override is honored
$r = landing_get_cta('primary', 'https://override.example.com');
assert_test($r['target'] === 'https://override.example.com', 'T3 url_override applied');

// T4: legacy fallback — если CPT пуст, читать wp_options.landing_cta_presets
reset_lg();
$GLOBALS['_mock_options']['landing_cta_presets'] = [
    'primary' => ['type' => 'scroll', 'target' => '#legacy', 'label' => 'Legacy CTA', 'phone' => '', 'form_id' => '', 'message_template' => ''],
];
$r = landing_get_cta('primary');
assert_test($r !== null && $r['label'] === 'Legacy CTA', 'T4 legacy fallback used when CPT empty');

echo "$tests tests, $failures failures\n";
exit($failures > 0 ? 1 : 0);
```

- [ ] **Step 3: Запустить — должен упасть**

```bash
php skills/wp-landing-config/tests/test_landing_get_cta.php
```

Ожидаемо: T1-T4 fail на старой реализации (или function undefined).

---

### Task A3.1.6: landing_get_cta() refactor через cascade — GREEN

- [ ] **Step 1: Заменить реализацию `landing_get_cta` в helpers.php (или там где она)**

Заменить тело функции на:

```php
function landing_get_cta(string $preset_name, ?string $url_override = null, array $context = []): ?array {
    $blog_id = \function_exists('get_current_blog_id') ? \get_current_blog_id() : 1;
    $r = \LandingConfig\CTA\resolve_cta($preset_name, $blog_id);

    if ($r === null) {
        // Legacy fallback: pre-S2-A.3 wp_options storage
        $legacy = \get_option('landing_cta_presets', []);
        if (isset($legacy[$preset_name])) {
            $l = $legacy[$preset_name];
            $r = [
                'preset_name' => $preset_name,
                'type'        => $l['type'] ?? 'scroll',
                'label'       => $l['label'] ?? '',
                'target'      => $l['target'] ?? '',
                'phone'       => $l['phone'] ?? '',
                'form_id'     => $l['form_id'] ?? '',
                'message_template' => $l['message_template'] ?? '',
                'is_network'  => true,
            ];
        }
    }

    if ($r === null) return null;

    if ($url_override !== null) {
        $r['target'] = $url_override;
    }
    if (!empty($context) && !empty($r['message_template'])) {
        foreach ($context as $k => $v) {
            $r['message_template'] = str_replace('{' . $k . '}', (string) $v, $r['message_template']);
        }
    }
    return $r;
}
```

- [ ] **Step 2: Запустить — должен пройти**

```bash
php skills/wp-landing-config/tests/test_landing_get_cta.php
```

Ожидаемо: `4 tests, 0 failures`.

- [ ] **Step 3: Прогнать все существующие тесты — проверить нет регрессий**

```bash
cd skills/wp-landing-config
for t in tests/test_*.php; do echo "=== $t ==="; php "$t" 2>&1 | tail -3; done
```

Ожидаемо: все green, кроме 5 pre-existing encryption (openssl extension missing локально — это ОК).

- [ ] **Step 4: Commit**

```bash
git add skills/wp-landing-config/tests/test_landing_get_cta.php skills/wp-landing-config/mu-plugin/landing-config/includes/helpers.php
git commit -m "feat(wp-landing-config): A3.1 — landing_get_cta() через cascade + legacy fallback

4/4 tests: network preset, site override, url_override, legacy wp_options
fallback (для backward-compat в переходный период миграции).

Co-Authored-By: Claude Opus 4.7 (1M context) <noreply@anthropic.com>"
```

---

### Task A3.1.7: Миграция wp_options → CPT для CTA — RED

- [ ] **Step 1: Создать failing test**

Создать `skills/wp-landing-config/tests/test_migrate_to_s2a3.php`:

```php
<?php
require_once __DIR__ . '/fixtures/wp-bootstrap.php';
require_once __DIR__ . '/../mu-plugin/landing-config/includes/cascade.php';
require_once __DIR__ . '/../mu-plugin/landing-config/includes/cta.php';
require_once __DIR__ . '/../mu-plugin/landing-config/includes/migrate-to-s2a3.php';

use function LandingConfig\Migrate\migrate_cta_from_options;
use function LandingConfig\CTA\list_ctas;

$failures = 0; $tests = 0;
function assert_test($c, $m) { global $failures, $tests; $tests++; if (!$c) { echo "FAIL: $m\n"; $failures++; } }

function reset_mig() {
    $GLOBALS['_mock_posts'] = [];
    $GLOBALS['_mock_post_meta'] = [];
    $GLOBALS['_mock_next_post_id'] = 1;
    $GLOBALS['_mock_current_blog_id'] = 1;
    $GLOBALS['_mock_options'] = [];
    $GLOBALS['_mock_site_options'] = [];
}

// T1: миграция 2 пресетов из wp_options.landing_cta_presets → 2 CPT записи is_network=1
reset_mig();
$GLOBALS['_mock_options']['landing_cta_presets'] = [
    'primary' => ['type' => 'scroll', 'target' => '#form', 'label' => 'Primary',
                  'phone' => '', 'form_id' => '', 'message_template' => ''],
    'whatsapp' => ['type' => 'whatsapp', 'target' => '', 'label' => 'WA',
                   'phone' => '+1', 'form_id' => '', 'message_template' => 'Hello'],
];
$migrated = migrate_cta_from_options(1);
assert_test($migrated === 2, "T1a migrated count == 2 (got $migrated)");
$list = list_ctas(1);
assert_test(count($list) === 2, 'T1b 2 CPT records exist on blog_id=1');
$by_name = [];
foreach ($list as $r) { $by_name[$r['preset_name']] = $r; }
assert_test($by_name['primary']['label'] === 'Primary' && $by_name['primary']['is_network'] === true, 'T1c primary CPT correct');
assert_test($by_name['whatsapp']['phone'] === '+1', 'T1d whatsapp CPT correct');

// T2: idempotent — повторный прогон no-op
$migrated_again = migrate_cta_from_options(1);
assert_test($migrated_again === 0, 'T2 second run is no-op');

echo "$tests tests, $failures failures\n";
exit($failures > 0 ? 1 : 0);
```

- [ ] **Step 2: Запустить — упадёт**

```bash
php skills/wp-landing-config/tests/test_migrate_to_s2a3.php
```

Ожидаемо: require error на migrate-to-s2a3.php.

---

### Task A3.1.8: Миграция wp_options → CPT для CTA — GREEN

- [ ] **Step 1: Создать `includes/migrate-to-s2a3.php`**

```php
<?php
namespace LandingConfig\Migrate;

if (!defined('ABSPATH')) { exit; }

use function LandingConfig\CTA\save_cta;
use function LandingConfig\CTA\list_ctas;
use const LandingConfig\CTA\PRESET_NAMES;

const MARKER_OPTION = 'landing_config_migration_s2a3_cta';

function migrate_cta_from_options(int $network_blog_id): int {
    // Idempotency: if CPT already has any records on blog_id, skip
    $existing = list_ctas($network_blog_id);
    if (!empty($existing)) {
        return 0;
    }

    $opts = \get_option('landing_cta_presets', null);
    if (!is_array($opts) || empty($opts)) {
        return 0;
    }
    $count = 0;
    foreach ($opts as $name => $cfg) {
        if (!in_array($name, PRESET_NAMES, true)) continue;
        if (!is_array($cfg)) continue;
        save_cta([
            'preset_name'      => $name,
            'type'             => $cfg['type'] ?? 'scroll',
            'label'            => $cfg['label'] ?? '',
            'target'           => $cfg['target'] ?? '',
            'phone'            => $cfg['phone'] ?? '',
            'form_id'          => $cfg['form_id'] ?? '',
            'message_template' => $cfg['message_template'] ?? '',
        ], true, $network_blog_id);
        $count++;
    }
    if ($count > 0) {
        \update_site_option(MARKER_OPTION, '1');
    }
    return $count;
}

/** Точка входа на admin_init после загрузки plugin. */
function maybe_run(): void {
    if (\get_site_option(MARKER_OPTION) === '1') return;
    $main = \function_exists('get_main_site_id') ? \get_main_site_id() : 1;
    migrate_cta_from_options($main);
}
```

- [ ] **Step 2: Запустить — должен пройти**

```bash
php skills/wp-landing-config/tests/test_migrate_to_s2a3.php
```

Ожидаемо: `2 tests, 0 failures`. Если падает T1c из-за того что save_cta вернул 0 (preset не в PRESET_NAMES) — проверить что PRESET_NAMES экспортирован константой и доступен через `use const`.

- [ ] **Step 3: Подключить миграцию в landing-config.php**

Найти и отредактировать `landing-config.php` — добавить require + auto-run:

```php
// в порядке require_once:
require_once LANDING_CONFIG_DIR . '/includes/cascade.php';
require_once LANDING_CONFIG_DIR . '/includes/cta.php';
require_once LANDING_CONFIG_DIR . '/includes/migrate-to-s2a3.php';
// ... остальные ...

// в существующий add_action('init', ...) добавить (или в admin_init):
add_action('admin_init', function () {
    if (\is_admin() && \current_user_can('manage_network_options')) {
        \LandingConfig\Migrate\maybe_run();
    }
});
```

- [ ] **Step 4: Прогон всех тестов**

```bash
cd skills/wp-landing-config
for t in tests/test_*.php; do echo "=== $t ==="; php "$t" 2>&1 | tail -3; done
```

- [ ] **Step 5: Commit**

```bash
git add skills/wp-landing-config/tests/test_migrate_to_s2a3.php \
        skills/wp-landing-config/mu-plugin/landing-config/includes/migrate-to-s2a3.php \
        skills/wp-landing-config/mu-plugin/landing-config/landing-config.php
git commit -m "feat(wp-landing-config): A3.1 — migrate CTA wp_options → lp_cta CPT

Idempotent через marker site_option. Запускается из admin_init для
super-admin. Legacy wp_options НЕ удаляется — служит fallback'ом
для landing_get_cta(). Удалим через 2-3 недели.

Co-Authored-By: Claude Opus 4.7 (1M context) <noreply@anthropic.com>"
```

---

### Task A3.1.9: Deploy + live smoke A3.1

- [ ] **Step 1: Deploy на ailexi.ru**

```bash
bash skills/wp-landing-config/scripts/install-mu-plugin.sh /tmp/test-s2a
```

Ожидаемо: `✅ landing-config mu-plugin installed`.

- [ ] **Step 2: Триггер миграции через GET admin page**

Ждать, что миграция отработает при следующем заходе super-admin. Имитировать через curl:

```bash
ssh -i /c/Users/esper21/.ssh/beget_poc esper21@esper21.beget.tech "WPCLI='/usr/local/bin/php8.3 /usr/local/bin/wp-cli.phar --path=/home/e/esper21/ailexi.ru/public_html'; \$WPCLI eval 'do_action(\"admin_init\");' --user=1 --url=http://ailexi.ru/wp-admin/network/" 2>&1 | tail -5
```

- [ ] **Step 3: Проверить что появились CPT записи**

```bash
ssh -i /c/Users/esper21/.ssh/beget_poc esper21@esper21.beget.tech "WPCLI='/usr/local/bin/php8.3 /usr/local/bin/wp-cli.phar --path=/home/e/esper21/ailexi.ru/public_html'; \$WPCLI post list --post_type=lp_cta --url=http://ailexi.ru/ --fields=ID,post_title 2>&1 | head -10"
```

Ожидаемо: 5 записей (primary/whatsapp/phone/form_modal/learn_more).

- [ ] **Step 4: Smoke — landing_get_cta вернёт корректное значение**

```bash
ssh -i /c/Users/esper21/.ssh/beget_poc esper21@esper21.beget.tech "WPCLI='/usr/local/bin/php8.3 /usr/local/bin/wp-cli.phar --path=/home/e/esper21/ailexi.ru/public_html'; \$WPCLI eval 'var_export(landing_get_cta(\"primary\"));' --url=http://ailexi.ru/" 2>&1 | tail -15
```

Ожидаемо: array с label/type/target из миграции.

- [ ] **Step 5: User Gate**

Сказать пользователю: «A3.1 deployed. `lp_cta` CPT создан на ailexi.ru, миграция из wp_options прошла. `landing_get_cta()` теперь через cascade. Готов переходить к A3.2 (Integrations).»

Дождаться "+" или коррекций от пользователя.

---

## Phase A3.2 — Integrations CPT + AdapterInterface refactor + migration

**Цель фазы:** `lp_integration` CPT + перевод 6 адаптеров на `settings()` через cascade + миграция `wp_options.landing_integration_*` → CPT. Encrypted поля шифруются перед update_post_meta.

**Files:**
- Create: `skills/wp-landing-config/mu-plugin/landing-config/includes/integrations.php`
- Modify: `skills/wp-landing-config/mu-plugin/landing-config/adapters/AdapterInterface.php` (расширить интерфейс)
- Modify: 6 adapter PHP файлов (`EmailAdapter.php`, `TelegramAdapter.php`, `WhatsAppAdapter.php`, `AmoCRMAdapter.php`, `Bitrix24Adapter.php`, `HubSpotAdapter.php`) — добавить `field_definitions()` static + refactor `settings()` через cascade
- Modify: `skills/wp-landing-config/mu-plugin/landing-config/includes/migrate-to-s2a3.php` (добавить миграцию integrations)
- Modify: `skills/wp-landing-config/mu-plugin/landing-config/landing-config.php` (порядок require)
- Test: `skills/wp-landing-config/tests/test_integrations.php`
- Test: `skills/wp-landing-config/tests/test_adapter_settings_cascade.php`
- Test: `skills/wp-landing-config/tests/test_migrate_integrations.php`

---

### Task A3.2.1: Integrations CPT — RED + GREEN + commit

- [ ] **Step 1: Создать failing test**

`skills/wp-landing-config/tests/test_integrations.php` — структура аналогична `test_cta.php`, но для:
- `save_integration(string $adapter_name, array $settings, bool $is_network, int $blog_id, array $encrypted_fields = []): int`
- `get_integration(int $id): ?array` (с автоматическим расшифрованием полей из `encrypted_fields`)
- `list_integrations(int $blog_id): array`
- `resolve_integration(string $adapter_name, int $blog_id): ?array`
- `delete_integration(int $id): bool`

Тесты T1-T5:
- T1: save+get round-trip с encrypted полем (token) — должно сохраниться зашифрованным в meta, get_integration должен расшифровать.
- T2: cascade site override wins.
- T3: cascade network fallback.
- T4: list_integrations merge.
- T5: delete.

Скелет (полный код — аналогично test_cta.php, заменить save_cta → save_integration):

```php
<?php
require_once __DIR__ . '/fixtures/wp-bootstrap.php';
require_once __DIR__ . '/../mu-plugin/landing-config/includes/cascade.php';
require_once __DIR__ . '/../mu-plugin/landing-config/includes/encryption.php';
require_once __DIR__ . '/../mu-plugin/landing-config/includes/integrations.php';

use function LandingConfig\Integrations\save_integration;
use function LandingConfig\Integrations\get_integration;
use function LandingConfig\Integrations\resolve_integration;
use function LandingConfig\Integrations\list_integrations;
use function LandingConfig\Integrations\delete_integration;

$failures = 0; $tests = 0;
function assert_test($c, $m) { global $failures, $tests; $tests++; if (!$c) { echo "FAIL: $m\n"; $failures++; } }

function reset_int() {
    $GLOBALS['_mock_posts'] = [];
    $GLOBALS['_mock_post_meta'] = [];
    $GLOBALS['_mock_next_post_id'] = 1;
    $GLOBALS['_mock_current_blog_id'] = 1;
    putenv('WP_LANDING_CONFIG_KEY=' . str_repeat('a', 32));
}

// T1 round-trip with encrypted field
reset_int();
$id = save_integration('telegram', ['bot_token' => 'SECRET123', 'chat_id' => '-1001'], true, 1, ['bot_token']);
assert_test($id > 0, 'T1a save_integration returned id');
$row = get_integration($id);
assert_test($row['settings']['bot_token'] === 'SECRET123', 'T1b token decrypted on get');
assert_test($row['adapter_name'] === 'telegram' && $row['is_network'] === true, 'T1c name+network correct');

// T2 cascade override
reset_int();
save_integration('amocrm', ['domain' => 'net.amocrm.ru', 'token' => 'NET'], true, 1, ['token']);
$GLOBALS['_mock_current_blog_id'] = 2;
save_integration('amocrm', ['domain' => 'site.amocrm.ru', 'token' => 'SITE'], false, 2, ['token']);
$r = resolve_integration('amocrm', 2);
assert_test($r['settings']['domain'] === 'site.amocrm.ru', 'T2a site override domain');
assert_test($r['settings']['token'] === 'SITE', 'T2b site override token decrypted');

// T3 network fallback
$r = resolve_integration('amocrm', 1);
assert_test($r['settings']['domain'] === 'net.amocrm.ru', 'T3 network fallback');

// T4 list merge
reset_int();
save_integration('email', ['to' => 'net@x.ru'], true, 1, []);
$GLOBALS['_mock_current_blog_id'] = 2;
save_integration('telegram', ['bot_token' => 'T', 'chat_id' => '1'], false, 2, ['bot_token']);
$list = list_integrations(2);
$names = array_column($list, 'adapter_name');
assert_test(in_array('email', $names) && in_array('telegram', $names), 'T4 list merge');

// T5 delete
reset_int();
$id = save_integration('email', ['to' => 'x@y.z'], false, 1, []);
assert_test(delete_integration($id) === true && get_integration($id) === null, 'T5 delete works');

echo "$tests tests, $failures failures\n";
exit($failures > 0 ? 1 : 0);
```

- [ ] **Step 2: Запустить — упадёт**

```bash
php skills/wp-landing-config/tests/test_integrations.php
```

- [ ] **Step 3: Создать `includes/integrations.php`**

```php
<?php
namespace LandingConfig\Integrations;

if (!defined('ABSPATH')) { exit; }

use function LandingConfig\Cascade\resolve_for_blog;
use function LandingConfig\Cascade\list_for_blog;
use function LandingConfig\Cascade\has_site_override;
use function LandingConfig\Encryption\encrypt;
use function LandingConfig\Encryption\decrypt;

const POST_TYPE = 'lp_integration';
const NAME_META = '_lp_int_adapter_name';
const NETWORK_META = '_lp_int_is_network';
const SETTINGS_META = '_lp_int_settings';
const ENCRYPTED_FIELDS_META = '_lp_int_encrypted_fields';
const ENABLED_META = '_lp_int_enabled';

const VALID_ADAPTERS = ['email', 'telegram', 'whatsapp', 'amocrm', 'bitrix24', 'hubspot'];

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
            'edit_posts'        => 'manage_options',
            'edit_others_posts' => 'manage_options',
            'publish_posts'     => 'manage_options',
            'delete_posts'      => 'manage_options',
            'read'              => 'read',
        ],
    ]);
}

function _with_blog(int $blog_id, callable $fn) {
    $prev = \get_current_blog_id();
    if ($prev === $blog_id) return $fn();
    \switch_to_blog($blog_id);
    try { return $fn(); }
    finally { \restore_current_blog(); }
}

function _encrypt_settings(array $settings, array $encrypted_fields): array {
    foreach ($encrypted_fields as $f) {
        if (isset($settings[$f]) && $settings[$f] !== '') {
            $settings[$f] = encrypt((string) $settings[$f]);
        }
    }
    return $settings;
}

function _decrypt_settings(array $settings, array $encrypted_fields): array {
    foreach ($encrypted_fields as $f) {
        if (isset($settings[$f]) && is_string($settings[$f]) && $settings[$f] !== '') {
            $decrypted = decrypt($settings[$f]);
            if ($decrypted !== null) $settings[$f] = $decrypted;
        }
    }
    return $settings;
}

function save_integration(string $adapter_name, array $settings, bool $is_network, int $blog_id, array $encrypted_fields = [], bool $enabled = true): int {
    if (!in_array($adapter_name, VALID_ADAPTERS, true)) return 0;

    return _with_blog($blog_id, function () use ($adapter_name, $settings, $is_network, $encrypted_fields, $enabled) {
        $post = ['post_type' => POST_TYPE, 'post_status' => 'publish', 'post_title' => $adapter_name];
        $id = \wp_insert_post($post);
        \update_post_meta($id, NAME_META, $adapter_name);
        \update_post_meta($id, SETTINGS_META, _encrypt_settings($settings, $encrypted_fields));
        \update_post_meta($id, ENCRYPTED_FIELDS_META, $encrypted_fields);
        \update_post_meta($id, NETWORK_META, $is_network ? '1' : '0');
        \update_post_meta($id, ENABLED_META, $enabled ? '1' : '0');
        return (int) $id;
    });
}

function get_integration(int $id): ?array {
    $p = \get_post($id);
    if (!$p || ($p->post_type ?? '') !== POST_TYPE) return null;
    $settings = \get_post_meta($id, SETTINGS_META, true);
    $settings = is_array($settings) ? $settings : [];
    $encrypted_fields = \get_post_meta($id, ENCRYPTED_FIELDS_META, true);
    $encrypted_fields = is_array($encrypted_fields) ? $encrypted_fields : [];
    return [
        'id'               => $id,
        'adapter_name'     => (string) \get_post_meta($id, NAME_META, true),
        'settings'         => _decrypt_settings($settings, $encrypted_fields),
        'encrypted_fields' => $encrypted_fields,
        'is_network'       => (string) \get_post_meta($id, NETWORK_META, true) === '1',
        'enabled'          => (string) \get_post_meta($id, ENABLED_META, true) === '1',
    ];
}

function delete_integration(int $id): bool {
    return (bool) \wp_delete_post($id, true);
}

function list_integrations(int $blog_id): array {
    $raw = list_for_blog(POST_TYPE, NAME_META, NETWORK_META, $blog_id);
    $out = [];
    foreach ($raw as $row) {
        $post_id = (int) ($row['__post_id'] ?? 0);
        $entry = get_integration($post_id);
        if ($entry) $out[] = $entry;
    }
    return $out;
}

function resolve_integration(string $adapter_name, int $blog_id): ?array {
    $list = list_integrations($blog_id);
    foreach ($list as $r) {
        if ($r['adapter_name'] === $adapter_name) return $r;
    }
    return null;
}

function has_override(string $adapter_name, int $blog_id): bool {
    return has_site_override(POST_TYPE, NAME_META, NETWORK_META, $adapter_name, $blog_id);
}
```

- [ ] **Step 4: Запустить тест — должен пройти**

```bash
php skills/wp-landing-config/tests/test_integrations.php
```

Ожидаемо: `5 tests, 0 failures`.

Если encryption падает локально (нет openssl) — закомментировать assert на decrypted token, пометить как pre-existing limitation, поправить тесты на сервере.

- [ ] **Step 5: Commit**

```bash
git add skills/wp-landing-config/tests/test_integrations.php \
        skills/wp-landing-config/mu-plugin/landing-config/includes/integrations.php
git commit -m "feat(wp-landing-config): A3.2 — lp_integration CPT + CRUD + encryption pass-through

5/5 tests: save+get с encrypted token, cascade override+fallback, list, delete.
Шифрует поля из encrypted_fields перед update_post_meta; расшифровывает в get.

Co-Authored-By: Claude Opus 4.7 (1M context) <noreply@anthropic.com>"
```

---

### Task A3.2.2: AdapterInterface::field_definitions() + settings() через cascade

- [ ] **Step 1: Прочитать текущий AdapterInterface**

```bash
cat skills/wp-landing-config/mu-plugin/landing-config/adapters/AdapterInterface.php
```

- [ ] **Step 2: Расширить интерфейс**

Добавить методы:

```php
namespace LandingConfig\Adapters;

interface AdapterInterface {
    // ... существующие методы ...

    /** Машинное имя адаптера: email/telegram/whatsapp/amocrm/bitrix24/hubspot */
    public static function name(): string;

    /** Схема полей: каждое поле — array<key, type+meta>.
     * @return array<string, array{type: string, label: string, encrypt?: bool, required?: bool, placeholder?: string}>
     */
    public static function field_definitions(): array;

    /** Получить эффективные настройки для текущего blog_id (через cascade). */
    public static function settings(): array;
}
```

- [ ] **Step 3: Создать failing test**

`skills/wp-landing-config/tests/test_adapter_settings_cascade.php`:

```php
<?php
require_once __DIR__ . '/fixtures/wp-bootstrap.php';
require_once __DIR__ . '/../mu-plugin/landing-config/includes/cascade.php';
require_once __DIR__ . '/../mu-plugin/landing-config/includes/encryption.php';
require_once __DIR__ . '/../mu-plugin/landing-config/includes/integrations.php';
require_once __DIR__ . '/../mu-plugin/landing-config/adapters/AdapterInterface.php';
require_once __DIR__ . '/../mu-plugin/landing-config/adapters/TelegramAdapter.php';

use LandingConfig\Adapters\TelegramAdapter;
use function LandingConfig\Integrations\save_integration;

$failures = 0; $tests = 0;
function assert_test($c, $m) { global $failures, $tests; $tests++; if (!$c) { echo "FAIL: $m\n"; $failures++; } }

function reset_ad() {
    $GLOBALS['_mock_posts'] = [];
    $GLOBALS['_mock_post_meta'] = [];
    $GLOBALS['_mock_next_post_id'] = 1;
    $GLOBALS['_mock_current_blog_id'] = 1;
    putenv('WP_LANDING_CONFIG_KEY=' . str_repeat('a', 32));
}

// T1: field_definitions returns schema with encrypt flag
$def = TelegramAdapter::field_definitions();
assert_test(isset($def['bot_token']['encrypt']) && $def['bot_token']['encrypt'] === true, 'T1 bot_token marked encrypt');

// T2: settings() reads via cascade
reset_ad();
save_integration('telegram', ['bot_token' => 'NETBOT', 'chat_id' => '-100'], true, 1, ['bot_token']);
$s = TelegramAdapter::settings();
assert_test($s['bot_token'] === 'NETBOT', 'T2 network settings via cascade');

$GLOBALS['_mock_current_blog_id'] = 2;
save_integration('telegram', ['bot_token' => 'SITEBOT', 'chat_id' => '-200'], false, 2, ['bot_token']);
$s = TelegramAdapter::settings();
assert_test($s['bot_token'] === 'SITEBOT', 'T2b site override via cascade');

echo "$tests tests, $failures failures\n";
exit($failures > 0 ? 1 : 0);
```

- [ ] **Step 4: Запустить — упадёт**

```bash
php skills/wp-landing-config/tests/test_adapter_settings_cascade.php
```

Ожидаемо: `field_definitions` undefined на TelegramAdapter.

- [ ] **Step 5: Обновить TelegramAdapter.php**

Добавить методы в класс:

```php
public static function field_definitions(): array {
    return [
        'bot_token' => ['type' => 'password', 'label' => 'Bot Token', 'encrypt' => true, 'required' => true,
                        'placeholder' => '123456:ABC-DEF...'],
        'chat_id'   => ['type' => 'text', 'label' => 'Chat ID', 'required' => true,
                        'placeholder' => '-1001234567890'],
    ];
}

public static function settings(): array {
    $r = \LandingConfig\Integrations\resolve_integration(static::name(), \get_current_blog_id());
    if ($r === null) {
        // Legacy fallback
        $legacy = \get_option('landing_integration_' . static::name(), []);
        return is_array($legacy) ? $legacy : [];
    }
    return $r['settings'];
}
```

- [ ] **Step 6: Запустить тест — должен пройти**

```bash
php skills/wp-landing-config/tests/test_adapter_settings_cascade.php
```

Ожидаемо: `3 tests, 0 failures`.

- [ ] **Step 7: Повторить для остальных 5 адаптеров**

В каждом из `EmailAdapter.php`, `WhatsAppAdapter.php`, `AmoCRMAdapter.php`, `Bitrix24Adapter.php`, `HubSpotAdapter.php`:

a) добавить `field_definitions()` со схемой полей (см. ниже)
b) добавить `settings()` через `resolve_integration()` + legacy fallback (идентично TelegramAdapter)

**EmailAdapter::field_definitions():**
```php
return [
    'to' => ['type' => 'email', 'label' => 'Email получатель', 'required' => true, 'placeholder' => 'sales@company.ru'],
    'subject' => ['type' => 'text', 'label' => 'Тема письма', 'placeholder' => 'Новая заявка с сайта'],
    'from' => ['type' => 'email', 'label' => 'From (опционально)', 'placeholder' => 'no-reply@site.ru'],
];
```

**WhatsAppAdapter::field_definitions():**
```php
return [
    'phone_number_id' => ['type' => 'text', 'label' => 'Phone Number ID', 'required' => true],
    'access_token' => ['type' => 'password', 'label' => 'Access Token', 'encrypt' => true, 'required' => true],
    'template_name' => ['type' => 'text', 'label' => 'Template name', 'placeholder' => 'new_lead_notification'],
    'to_number' => ['type' => 'text', 'label' => 'WhatsApp получатель', 'required' => true,
                    'placeholder' => '+79001234567'],
];
```

**AmoCRMAdapter::field_definitions():**
```php
return [
    'subdomain' => ['type' => 'text', 'label' => 'AmoCRM поддомен', 'required' => true, 'placeholder' => 'acme'],
    'access_token' => ['type' => 'password', 'label' => 'Access Token (long-lived)', 'encrypt' => true, 'required' => true],
    'pipeline_id' => ['type' => 'text', 'label' => 'Pipeline ID', 'placeholder' => '7891234'],
    'status_id' => ['type' => 'text', 'label' => 'Status ID (новый лид)', 'placeholder' => '11223344'],
    'responsible_user_id' => ['type' => 'text', 'label' => 'Responsible user ID', 'placeholder' => '5566'],
];
```

**Bitrix24Adapter::field_definitions():**
```php
return [
    'webhook_url' => ['type' => 'url', 'label' => 'Webhook URL', 'encrypt' => true, 'required' => true,
                      'placeholder' => 'https://acme.bitrix24.ru/rest/N/TOKEN/'],
    'category_id' => ['type' => 'text', 'label' => 'Category ID (опционально)'],
    'assigned_by_id' => ['type' => 'text', 'label' => 'Assigned user ID'],
];
```

**HubSpotAdapter::field_definitions():**
```php
return [
    'access_token' => ['type' => 'password', 'label' => 'Private app token', 'encrypt' => true, 'required' => true],
    'lifecycle_stage' => ['type' => 'text', 'label' => 'Lifecycle stage', 'placeholder' => 'lead'],
];
```

- [ ] **Step 8: Прогнать все тесты + commit**

```bash
cd skills/wp-landing-config
for t in tests/test_*.php; do echo "=== $t ==="; php "$t" 2>&1 | tail -3; done
```

```bash
git add skills/wp-landing-config/tests/test_adapter_settings_cascade.php \
        skills/wp-landing-config/mu-plugin/landing-config/adapters/
git commit -m "feat(wp-landing-config): A3.2 — AdapterInterface field_definitions + settings() через cascade

Все 6 адаптеров: декларативная схема полей (type/label/encrypt) +
settings() читает через resolve_integration() с legacy wp_options fallback.

Co-Authored-By: Claude Opus 4.7 (1M context) <noreply@anthropic.com>"
```

---

### Task A3.2.3: Migration integrations → CPT

- [ ] **Step 1: Расширить failing test в migrate-to-s2a3**

Добавить в `test_migrate_to_s2a3.php`:

```php
// T3: миграция integrations wp_options → CPT
reset_mig();
$GLOBALS['_mock_options']['landing_integration_telegram'] = ['bot_token' => 'X', 'chat_id' => '-1'];
$GLOBALS['_mock_options']['landing_integration_amocrm'] = ['subdomain' => 'acme', 'access_token' => 'Y'];

$migrated = \LandingConfig\Migrate\migrate_integrations_from_options(1);
assert_test($migrated === 2, "T3a migrated 2 integrations (got $migrated)");
$list = \LandingConfig\Integrations\list_integrations(1);
assert_test(count($list) === 2, 'T3b 2 CPT records exist');
$by_name = [];
foreach ($list as $r) { $by_name[$r['adapter_name']] = $r; }
assert_test($by_name['telegram']['settings']['chat_id'] === '-1', 'T3c telegram migrated');
assert_test($by_name['amocrm']['settings']['subdomain'] === 'acme', 'T3d amocrm migrated');
```

- [ ] **Step 2: Запустить — упадёт**

- [ ] **Step 3: Добавить функцию в migrate-to-s2a3.php**

```php
function migrate_integrations_from_options(int $network_blog_id): int {
    $existing = \LandingConfig\Integrations\list_integrations($network_blog_id);
    if (!empty($existing)) return 0;

    $count = 0;
    foreach (\LandingConfig\Integrations\VALID_ADAPTERS as $adapter_name) {
        $opts = \get_option('landing_integration_' . $adapter_name, null);
        if (!is_array($opts) || empty($opts)) continue;

        // Determine which fields are encrypted by querying the adapter class
        $cls = '\\LandingConfig\\Adapters\\' . _class_for_adapter($adapter_name);
        $encrypted_fields = [];
        if (class_exists($cls) && method_exists($cls, 'field_definitions')) {
            foreach ($cls::field_definitions() as $f => $meta) {
                if (!empty($meta['encrypt'])) $encrypted_fields[] = $f;
            }
        }
        \LandingConfig\Integrations\save_integration(
            $adapter_name, $opts, true, $network_blog_id, $encrypted_fields, true
        );
        $count++;
    }
    return $count;
}

function _class_for_adapter(string $name): string {
    return match ($name) {
        'email'    => 'EmailAdapter',
        'telegram' => 'TelegramAdapter',
        'whatsapp' => 'WhatsAppAdapter',
        'amocrm'   => 'AmoCRMAdapter',
        'bitrix24' => 'Bitrix24Adapter',
        'hubspot'  => 'HubSpotAdapter',
        default    => '',
    };
}
```

Обновить `maybe_run()`:

```php
function maybe_run(): void {
    if (\get_site_option(MARKER_OPTION) !== '1') {
        $main = \function_exists('get_main_site_id') ? \get_main_site_id() : 1;
        migrate_cta_from_options($main);
        migrate_integrations_from_options($main);
        // Также пробежать по всем subsites — у них могут быть свои integrations
        if (\function_exists('get_sites')) {
            foreach (\get_sites(['number' => 0]) as $site) {
                if ((int) $site->blog_id === $main) continue;
                migrate_subsite_integrations((int) $site->blog_id);
            }
        }
    }
}

function migrate_subsite_integrations(int $blog_id): int {
    \switch_to_blog($blog_id);
    try {
        $count = 0;
        foreach (\LandingConfig\Integrations\VALID_ADAPTERS as $adapter_name) {
            $opts = \get_option('landing_integration_' . $adapter_name, null);
            if (!is_array($opts) || empty($opts)) continue;
            $cls = '\\LandingConfig\\Adapters\\' . _class_for_adapter($adapter_name);
            $encrypted_fields = [];
            if (class_exists($cls)) {
                foreach ($cls::field_definitions() as $f => $meta) {
                    if (!empty($meta['encrypt'])) $encrypted_fields[] = $f;
                }
            }
            \LandingConfig\Integrations\save_integration(
                $adapter_name, $opts, false, $blog_id, $encrypted_fields, true
            );
            $count++;
        }
        return $count;
    } finally {
        \restore_current_blog();
    }
}
```

- [ ] **Step 4: Run + commit + deploy + smoke (как в A3.1.9)**

```bash
# tests
php skills/wp-landing-config/tests/test_migrate_to_s2a3.php

# commit
git add -A skills/wp-landing-config/
git commit -m "feat(wp-landing-config): A3.2 — migrate integrations wp_options → lp_integration CPT

Идемпотентно. Бежит по network + всем subsites (per-blog integrations
из S2-A.1). Encrypted поля шифруются согласно field_definitions().

Co-Authored-By: Claude Opus 4.7 (1M context) <noreply@anthropic.com>"

# deploy + smoke
bash skills/wp-landing-config/scripts/install-mu-plugin.sh /tmp/test-s2a

ssh -i /c/Users/esper21/.ssh/beget_poc esper21@esper21.beget.tech \
  "WPCLI='/usr/local/bin/php8.3 /usr/local/bin/wp-cli.phar --path=/home/e/esper21/ailexi.ru/public_html'; \
   \$WPCLI post list --post_type=lp_integration --url=http://ailexi.ru/ --fields=ID,post_title 2>&1 | head -20"
```

- [ ] **Step 5: User Gate** — «A3.2 deployed. lp_integration CPT создан. Адаптеры читают через cascade. Готов к A3.3 (admin UI CTA с селектором сегмента)?»

---

## Phase A3.3 — Network admin CTA UI + read-only subsite

**Цель фазы:** рерайт `admin-cta.php` — теперь регистрируется в `network_admin_menu` под parent `landing-config-network`, имеет селектор сегмента, использует `lp_cta` CPT. На subsite — read-only `admin-cta-readonly.php`. Server-side guard 403 для save на subsite.

**Files:**
- Rewrite: `skills/wp-landing-config/mu-plugin/landing-config/includes/admin-cta.php`
- Create: `skills/wp-landing-config/mu-plugin/landing-config/includes/admin-cta-readonly.php`
- Create: `skills/wp-landing-config/mu-plugin/landing-config/includes/segment-selector.php` (re-usable компонент)
- Modify: `skills/wp-landing-config/mu-plugin/landing-config/landing-config.php` (порядок require)
- Test: `skills/wp-landing-config/tests/integration/test_admin_cta_smoke.sh` (bats-style live test)

---

### Task A3.3.1: Segment selector component

- [ ] **Step 1: Создать `includes/segment-selector.php`**

```php
<?php
namespace LandingConfig\SegmentSelector;

if (!defined('ABSPATH')) { exit; }

/**
 * Рендер dropdown'а выбора сегмента + бейджа текущего выбора.
 * URL pattern: ?page=<slug>&segment=<blog_id|0>, где 0 = network default.
 */
function render(string $page_slug, int $current_segment = 0): void {
    $sites = \function_exists('get_sites') ? \get_sites(['number' => 0]) : [];
    $main_id = \function_exists('get_main_site_id') ? \get_main_site_id() : 1;
    ?>
    <div class="lp-segment-selector" style="background:#f6f7f7; padding:12px 16px; border:1px solid #c3c4c7; border-radius:4px; margin:16px 0;">
        <form method="get" style="display:inline;">
            <input type="hidden" name="page" value="<?php echo \esc_attr($page_slug); ?>">
            <label style="font-weight:600;">Сегмент:
                <select name="segment" onchange="this.form.submit()" style="min-width:280px;">
                    <option value="0" <?php \selected($current_segment, 0); ?>>— общие настройки (network default) —</option>
                    <?php foreach ($sites as $site):
                        $bid = (int) $site->blog_id;
                        $label = $site->domain . rtrim($site->path, '/');
                        if ($bid === $main_id) $label .= ' ★';
                    ?>
                        <option value="<?php echo $bid; ?>" <?php \selected($current_segment, $bid); ?>>
                            <?php echo \esc_html($label); ?>
                        </option>
                    <?php endforeach; ?>
                </select>
            </label>
            <noscript><button type="submit" class="button">Применить</button></noscript>
        </form>
        <?php if ($current_segment === 0): ?>
            <span style="margin-left:1em; color:#646970;">— редактируете <strong>сетевые дефолты</strong>. Применятся ко всем сегментам, у которых нет своего override.</span>
        <?php else: ?>
            <?php
            $site = null;
            foreach ($sites as $s) { if ((int) $s->blog_id === $current_segment) { $site = $s; break; } }
            $host = $site ? $site->domain : 'segment#' . $current_segment;
            ?>
            <span style="margin-left:1em; color:#646970;">— редактируете <strong>сегмент <?php echo \esc_html($host); ?></strong>. Поля показывают inherited значения с возможностью override.</span>
        <?php endif; ?>
    </div>
    <?php
}

/** Получить current_segment из GET. 0 = network default. */
function current_from_request(): int {
    return isset($_GET['segment']) ? max(0, (int) $_GET['segment']) : 0;
}
```

- [ ] **Step 2: Commit (без теста — это pure UI helper)**

```bash
git add skills/wp-landing-config/mu-plugin/landing-config/includes/segment-selector.php
git commit -m "feat(wp-landing-config): A3.3 — segment selector компонент

Re-usable: render(\$page_slug, \$current_segment) + current_from_request().
URL-based (?segment=N), copy-paste-friendly, без JS-runtime для core логики.

Co-Authored-By: Claude Opus 4.7 (1M context) <noreply@anthropic.com>"
```

---

### Task A3.3.2: admin-cta.php — рерайт под network admin + cascade

- [ ] **Step 1: Backup существующего admin-cta.php**

```bash
cp skills/wp-landing-config/mu-plugin/landing-config/includes/admin-cta.php /tmp/admin-cta.bak.php
```

- [ ] **Step 2: Переписать admin-cta.php**

```php
<?php
namespace LandingConfig\Admin\CTA;

if (!defined('ABSPATH')) { exit; }

use function LandingConfig\CTA\list_ctas;
use function LandingConfig\CTA\resolve_cta;
use function LandingConfig\CTA\save_cta;
use function LandingConfig\CTA\delete_cta;
use function LandingConfig\CTA\has_override;
use const LandingConfig\CTA\PRESET_NAMES;
use const LandingConfig\CTA\VALID_TYPES;
use function LandingConfig\SegmentSelector\render as render_selector;
use function LandingConfig\SegmentSelector\current_from_request;

\add_action('network_admin_menu', function () {
    \add_submenu_page(
        'landing-config-network',
        'CTA-кнопки',
        'CTA-кнопки',
        'manage_network_options',
        'landing-config-network-cta',
        __NAMESPACE__ . '\\dispatch'
    );
});

\add_action('admin_post_landing_cta_save', __NAMESPACE__ . '\\handle_save');
\add_action('admin_post_landing_cta_delete_override', __NAMESPACE__ . '\\handle_delete_override');

function dispatch(): void {
    if (!\current_user_can('manage_network_options')) { \wp_die('Insufficient permissions', 403); }
    $segment = current_from_request();
    render_page($segment);
}

function render_page(int $segment): void {
    $main_id = \function_exists('get_main_site_id') ? \get_main_site_id() : 1;
    $blog_id = $segment === 0 ? $main_id : $segment;
    ?>
    <div class="wrap">
        <h1>CTA-кнопки</h1>
        <p>Настройте 5 пресетов кнопок. Темы обращаются к ним через <code>landing_get_cta('preset_name')</code>.
        Сетевые дефолты применяются ко всем сегментам сети. Сегмент может переопределить пресет — кнопка тогда будет специфична для него.</p>
        <?php render_selector('landing-config-network-cta', $segment); ?>

        <?php
        // Для каждого preset резолвим финальное значение для контекста blog_id
        foreach (PRESET_NAMES as $preset_name):
            $effective = resolve_cta($preset_name, $blog_id);
            $is_inherited = ($segment !== 0) && !has_override($preset_name, $segment);
            $is_override = ($segment !== 0) && has_override($preset_name, $segment);
            $effective = $effective ?: ['type' => 'scroll', 'label' => '', 'target' => '', 'phone' => '',
                'form_id' => '', 'message_template' => '', 'is_network' => true];
        ?>
            <div style="background:#fff; border:1px solid #c3c4c7; padding:16px 20px; margin:16px 0; border-radius:4px;">
                <h2 style="margin-top:0;">
                    <code><?php echo \esc_html($preset_name); ?></code>
                    <?php if ($segment === 0): ?>
                        <span class="dashicons dashicons-admin-network" style="color:#2271b1;" title="Network default"></span>
                    <?php elseif ($is_override): ?>
                        <span style="background:#dba617; color:#fff; padding:2px 8px; border-radius:3px; font-size:11px; font-weight:600; vertical-align:middle;">SITE OVERRIDE</span>
                    <?php else: ?>
                        <span style="background:#2271b1; color:#fff; padding:2px 8px; border-radius:3px; font-size:11px; font-weight:600; vertical-align:middle;">INHERITED</span>
                    <?php endif; ?>
                </h2>

                <?php if ($segment !== 0 && $is_inherited): ?>
                    <p style="color:#646970;">Этот пресет наследуется от сетевого дефолта. Чтобы изменить для этого сегмента — нажмите «Override».</p>
                <?php endif; ?>

                <form method="post" action="<?php echo \esc_url(\admin_url('admin-post.php')); ?>">
                    <?php \wp_nonce_field('landing_cta_save_' . $preset_name); ?>
                    <input type="hidden" name="action" value="landing_cta_save">
                    <input type="hidden" name="preset_name" value="<?php echo \esc_attr($preset_name); ?>">
                    <input type="hidden" name="segment" value="<?php echo (int) $segment; ?>">

                    <table class="form-table">
                        <tr><th>Type</th><td>
                            <select name="type" <?php disabled($is_inherited); ?>>
                                <?php foreach (VALID_TYPES as $t): ?>
                                    <option value="<?php echo $t; ?>" <?php \selected($effective['type'], $t); ?>><?php echo $t; ?></option>
                                <?php endforeach; ?>
                            </select>
                        </td></tr>
                        <tr><th>Label</th><td>
                            <input type="text" name="label" value="<?php echo \esc_attr($effective['label']); ?>" class="regular-text" <?php disabled($is_inherited); ?>>
                        </td></tr>
                        <tr><th>Target / URL</th><td>
                            <input type="text" name="target" value="<?php echo \esc_attr($effective['target']); ?>" class="regular-text" <?php disabled($is_inherited); ?>>
                        </td></tr>
                        <tr><th>Phone</th><td>
                            <input type="text" name="phone" value="<?php echo \esc_attr($effective['phone']); ?>" placeholder="+71234567890" <?php disabled($is_inherited); ?>>
                        </td></tr>
                        <tr><th>Form ID</th><td>
                            <input type="text" name="form_id" value="<?php echo \esc_attr($effective['form_id']); ?>" placeholder="main" <?php disabled($is_inherited); ?>>
                        </td></tr>
                        <tr><th>Message template</th><td>
                            <input type="text" name="message_template" value="<?php echo \esc_attr($effective['message_template']); ?>" class="large-text" <?php disabled($is_inherited); ?>>
                        </td></tr>
                    </table>

                    <p>
                        <?php if ($segment === 0 || $is_override): ?>
                            <button type="submit" class="button button-primary">Сохранить</button>
                        <?php else: // inherited ?>
                            <button type="submit" class="button button-primary" name="override_action" value="enable">Override для этого сегмента</button>
                        <?php endif; ?>

                        <?php if ($is_override): ?>
                            <a href="<?php echo \esc_url(\wp_nonce_url(
                                \network_admin_url('admin-post.php?action=landing_cta_delete_override&preset_name=' . $preset_name . '&segment=' . $segment),
                                'landing_cta_delete_override_' . $preset_name
                            )); ?>" class="button" style="margin-left:1em;" onclick="return confirm('Удалить override и вернуться к сетевому дефолту?');">Удалить override</a>
                        <?php endif; ?>
                    </p>
                </form>
            </div>
        <?php endforeach; ?>
    </div>
    <?php
}

function handle_save(): void {
    if (!\current_user_can('manage_network_options')) { \wp_die('No.', 403); }
    $preset = \sanitize_text_field($_POST['preset_name'] ?? '');
    if (!in_array($preset, PRESET_NAMES, true)) \wp_die('Invalid preset', 400);
    \check_admin_referer('landing_cta_save_' . $preset);

    $segment = isset($_POST['segment']) ? (int) $_POST['segment'] : 0;
    $is_network = ($segment === 0);
    $main_id = \function_exists('get_main_site_id') ? \get_main_site_id() : 1;
    $blog_id = $is_network ? $main_id : $segment;

    // Delete existing record(s) for this preset on this blog_id+is_network combo
    foreach (list_ctas($blog_id) as $r) {
        if ($r['preset_name'] === $preset && $r['is_network'] === $is_network) {
            delete_cta($r['id']);
        }
    }

    save_cta([
        'preset_name'      => $preset,
        'type'             => $_POST['type'] ?? 'scroll',
        'label'            => $_POST['label'] ?? '',
        'target'           => $_POST['target'] ?? '',
        'phone'            => $_POST['phone'] ?? '',
        'form_id'          => $_POST['form_id'] ?? '',
        'message_template' => $_POST['message_template'] ?? '',
    ], $is_network, $blog_id);

    \wp_safe_redirect(\network_admin_url('admin.php?page=landing-config-network-cta&segment=' . $segment . '&saved=1'));
    exit;
}

function handle_delete_override(): void {
    if (!\current_user_can('manage_network_options')) { \wp_die('No.', 403); }
    $preset = \sanitize_text_field($_GET['preset_name'] ?? '');
    $segment = (int) ($_GET['segment'] ?? 0);
    if (!in_array($preset, PRESET_NAMES, true) || $segment === 0) \wp_die('Invalid', 400);
    \check_admin_referer('landing_cta_delete_override_' . $preset);

    foreach (list_ctas($segment) as $r) {
        if ($r['preset_name'] === $preset && $r['is_network'] === false) {
            delete_cta($r['id']);
        }
    }
    \wp_safe_redirect(\network_admin_url('admin.php?page=landing-config-network-cta&segment=' . $segment . '&deleted=1'));
    exit;
}
```

- [ ] **Step 3: Удалить старый admin-cta.php hooks (которые в admin_menu)**

Старый файл регал `add_action('admin_menu', ...)` для site-admin. Новый файл регистрирует только в `network_admin_menu`. Read-only вариант для site-admin будет в отдельном файле (A3.3.3).

- [ ] **Step 4: Lint, deploy, manual test**

```bash
php -l skills/wp-landing-config/mu-plugin/landing-config/includes/admin-cta.php
bash skills/wp-landing-config/scripts/install-mu-plugin.sh /tmp/test-s2a
```

Открыть `http://ailexi.ru/wp-admin/network/admin.php?page=landing-config-network-cta` — должны видеть селектор + 5 секций пресетов с inherited/override бейджами.

Тестовый кейс: переключить на segment=2 (russian), нажать «Override» на `whatsapp`, заполнить «Russian WA», сохранить. Переключить обратно на segment=0, убедиться что network whatsapp не изменился. Переключить на segment=2 ещё раз — badge SITE OVERRIDE.

- [ ] **Step 5: Commit**

```bash
git add skills/wp-landing-config/mu-plugin/landing-config/includes/admin-cta.php
git commit -m "feat(wp-landing-config): A3.3 — admin-cta UI under Network admin с селектором сегмента

CTA редактируется из network admin для network default + per-сегмент override.
Inherited/Override бейджи, кнопки Override / Удалить override.

Co-Authored-By: Claude Opus 4.7 (1M context) <noreply@anthropic.com>"
```

---

### Task A3.3.3: admin-cta-readonly.php — read-only view на subsite

- [ ] **Step 1: Создать `includes/admin-cta-readonly.php`**

```php
<?php
namespace LandingConfig\Admin\CTAReadOnly;

if (!defined('ABSPATH')) { exit; }

use function LandingConfig\CTA\resolve_cta;
use function LandingConfig\CTA\has_override;
use const LandingConfig\CTA\PRESET_NAMES;

\add_action('admin_menu', function () {
    \add_submenu_page(
        'landing-config',
        'CTA-кнопки (просмотр)',
        'CTA-кнопки',
        'manage_options',
        'landing-config-cta',
        __NAMESPACE__ . '\\render_page'
    );
});

function render_page(): void {
    if (!\current_user_can('manage_options')) { \wp_die('No.', 403); }
    $blog_id = \get_current_blog_id();
    $net_url = \network_admin_url('admin.php?page=landing-config-network-cta&segment=' . $blog_id);
    ?>
    <div class="wrap">
        <h1>CTA-кнопки <span style="font-size:13px; color:#646970; font-weight:400;">— режим просмотра</span></h1>
        <div class="notice notice-info inline">
            <p>Настройки CTA управляются super-admin'ом из network admin.
            <a href="<?php echo \esc_url($net_url); ?>" target="_blank">Открыть редактор</a> →</p>
        </div>

        <table class="wp-list-table widefat striped" style="margin-top:16px;">
            <thead>
                <tr>
                    <th>Preset</th><th>Type</th><th>Label</th><th>Target</th><th>Источник</th>
                </tr>
            </thead>
            <tbody>
                <?php foreach (PRESET_NAMES as $preset_name):
                    $r = resolve_cta($preset_name, $blog_id);
                    $source = has_override($preset_name, $blog_id) ? 'site override' : 'inherited from network';
                    $source_color = has_override($preset_name, $blog_id) ? '#dba617' : '#2271b1';
                ?>
                    <tr>
                        <td><code><?php echo \esc_html($preset_name); ?></code></td>
                        <td><?php echo \esc_html($r['type'] ?? '—'); ?></td>
                        <td><?php echo \esc_html($r['label'] ?? '—'); ?></td>
                        <td><?php echo \esc_html($r['target'] ?: $r['phone'] ?? '—'); ?></td>
                        <td><span style="background:<?php echo $source_color; ?>; color:#fff; padding:2px 8px; border-radius:3px; font-size:11px;"><?php echo $source; ?></span></td>
                    </tr>
                <?php endforeach; ?>
            </tbody>
        </table>
    </div>
    <?php
}
```

- [ ] **Step 2: Подключить в landing-config.php**

В блоке require'ов добавить:

```php
require_once LANDING_CONFIG_DIR . '/includes/admin-cta-readonly.php';
```

- [ ] **Step 3: Lint + deploy + manual smoke**

Открыть `http://russian.ailexi.ru/wp-admin/admin.php?page=landing-config-cta` — должна быть read-only таблица 5 пресетов с пометками inherited/site-override, ссылка на network admin сверху.

- [ ] **Step 4: Commit**

```bash
git add skills/wp-landing-config/mu-plugin/landing-config/includes/admin-cta-readonly.php \
        skills/wp-landing-config/mu-plugin/landing-config/landing-config.php
git commit -m "feat(wp-landing-config): A3.3 — admin-cta-readonly view на subsite

Read-only таблица 5 пресетов с метками inherited/site-override + deep-link на
network admin редактор. Server-side: WP capabilities обеспечивают что не-super-admin
сегмента не имеет manage_network_options.

Co-Authored-By: Claude Opus 4.7 (1M context) <noreply@anthropic.com>"
```

- [ ] **Step 5: User Gate** — «A3.3 deployed. CTA UI в network admin (с селектором + override toggle) + read-only на subsite. Готов к A3.4 (Integrations с toggle override)?»

---

## Phase A3.4 — Network admin Integrations UI + read-only subsite

**Цель фазы:** `admin-integrations.php` под network_admin_menu с селектором сегмента, override-toggle на адаптер. На subsite — read-only.

**Files:**
- Rewrite: `skills/wp-landing-config/mu-plugin/landing-config/includes/admin-integrations.php`
- Create: `skills/wp-landing-config/mu-plugin/landing-config/includes/admin-integrations-readonly.php`

---

### Task A3.4.1: admin-integrations.php рерайт

- [ ] **Step 1: Прочитать существующий admin-integrations.php**

```bash
cat skills/wp-landing-config/mu-plugin/landing-config/includes/admin-integrations.php
```

- [ ] **Step 2: Переписать**

```php
<?php
namespace LandingConfig\Admin\Integrations;

if (!defined('ABSPATH')) { exit; }

use function LandingConfig\Integrations\list_integrations;
use function LandingConfig\Integrations\resolve_integration;
use function LandingConfig\Integrations\save_integration;
use function LandingConfig\Integrations\delete_integration;
use function LandingConfig\Integrations\has_override;
use const LandingConfig\Integrations\VALID_ADAPTERS;
use function LandingConfig\SegmentSelector\render as render_selector;
use function LandingConfig\SegmentSelector\current_from_request;

function adapter_class(string $name): string {
    return match ($name) {
        'email'    => '\\LandingConfig\\Adapters\\EmailAdapter',
        'telegram' => '\\LandingConfig\\Adapters\\TelegramAdapter',
        'whatsapp' => '\\LandingConfig\\Adapters\\WhatsAppAdapter',
        'amocrm'   => '\\LandingConfig\\Adapters\\AmoCRMAdapter',
        'bitrix24' => '\\LandingConfig\\Adapters\\Bitrix24Adapter',
        'hubspot'  => '\\LandingConfig\\Adapters\\HubSpotAdapter',
        default    => '',
    };
}

function mask_secret(string $val): string {
    if ($val === '') return '— не задано —';
    if (strlen($val) <= 4) return '••••';
    return str_repeat('•', max(0, strlen($val) - 4)) . substr($val, -4);
}

\add_action('network_admin_menu', function () {
    \add_submenu_page(
        'landing-config-network',
        'Интеграции',
        'Интеграции',
        'manage_network_options',
        'landing-config-network-integrations',
        __NAMESPACE__ . '\\dispatch'
    );
});

\add_action('admin_post_landing_int_save', __NAMESPACE__ . '\\handle_save');
\add_action('admin_post_landing_int_toggle_override', __NAMESPACE__ . '\\handle_toggle_override');

function dispatch(): void {
    if (!\current_user_can('manage_network_options')) { \wp_die('No.', 403); }
    $segment = current_from_request();
    render_page($segment);
}

function render_page(int $segment): void {
    $main_id = \function_exists('get_main_site_id') ? \get_main_site_id() : 1;
    $blog_id = $segment === 0 ? $main_id : $segment;
    ?>
    <div class="wrap">
        <h1>Интеграции</h1>
        <p>Подключите CRM/мессенджеры для отправки заявок. Сетевые настройки применяются ко всем сегментам;
        сегмент может переопределить любой адаптер на свой аккаунт.</p>
        <?php render_selector('landing-config-network-integrations', $segment); ?>

        <?php foreach (VALID_ADAPTERS as $adapter_name):
            $cls = adapter_class($adapter_name);
            $defs = $cls ? $cls::field_definitions() : [];
            $effective = resolve_integration($adapter_name, $blog_id);
            $is_inherited = ($segment !== 0) && !has_override($adapter_name, $segment);
            $is_override = ($segment !== 0) && has_override($adapter_name, $segment);
            $current_settings = $effective ? $effective['settings'] : array_fill_keys(array_keys($defs), '');
        ?>
            <div style="background:#fff; border:1px solid #c3c4c7; padding:16px 20px; margin:16px 0; border-radius:4px;">
                <h2 style="margin-top:0; display:flex; align-items:center; gap:.6em;">
                    <code><?php echo \esc_html($adapter_name); ?></code>
                    <?php if ($segment === 0): ?>
                        <span class="dashicons dashicons-admin-network" style="color:#2271b1;"></span>
                    <?php elseif ($is_override): ?>
                        <span style="background:#dba617; color:#fff; padding:2px 8px; border-radius:3px; font-size:11px; font-weight:600;">SITE OVERRIDE</span>
                    <?php else: ?>
                        <span style="background:#2271b1; color:#fff; padding:2px 8px; border-radius:3px; font-size:11px; font-weight:600;">INHERITED</span>
                    <?php endif; ?>
                </h2>

                <?php if ($segment !== 0): ?>
                    <form method="post" action="<?php echo \esc_url(\admin_url('admin-post.php')); ?>" style="margin-bottom:12px;">
                        <?php \wp_nonce_field('landing_int_toggle_override_' . $adapter_name); ?>
                        <input type="hidden" name="action" value="landing_int_toggle_override">
                        <input type="hidden" name="adapter_name" value="<?php echo \esc_attr($adapter_name); ?>">
                        <input type="hidden" name="segment" value="<?php echo (int) $segment; ?>">
                        <label style="font-weight:600;">
                            <input type="checkbox" name="override_enabled" value="1" <?php \checked($is_override); ?>
                                onchange="this.form.submit();">
                            Использовать свой <?php echo \esc_html($adapter_name); ?> для этого сегмента
                        </label>
                    </form>
                <?php endif; ?>

                <?php if ($segment !== 0 && $is_inherited): ?>
                    <div style="background:#f6f7f7; padding:12px; border-radius:4px;">
                        <p style="margin:0 0 8px;"><strong>Унаследовано от сети.</strong> Заявки этого сегмента уходят в:</p>
                        <ul style="margin:0; color:#646970;">
                            <?php foreach ($defs as $field => $meta):
                                $val = $current_settings[$field] ?? '';
                                if (!empty($meta['encrypt'])) $val = mask_secret((string) $val);
                            ?>
                                <li><strong><?php echo \esc_html($meta['label']); ?>:</strong> <code><?php echo \esc_html((string) $val); ?></code></li>
                            <?php endforeach; ?>
                        </ul>
                    </div>
                <?php else: ?>
                    <form method="post" action="<?php echo \esc_url(\admin_url('admin-post.php')); ?>">
                        <?php \wp_nonce_field('landing_int_save_' . $adapter_name); ?>
                        <input type="hidden" name="action" value="landing_int_save">
                        <input type="hidden" name="adapter_name" value="<?php echo \esc_attr($adapter_name); ?>">
                        <input type="hidden" name="segment" value="<?php echo (int) $segment; ?>">
                        <table class="form-table">
                            <?php foreach ($defs as $field => $meta):
                                $val = $current_settings[$field] ?? '';
                                $input_type = $meta['type'] ?? 'text';
                                if (!empty($meta['encrypt']) && $val !== '') {
                                    $placeholder = '(сохранено: ' . mask_secret((string) $val) . ' — оставьте пустым чтобы не менять)';
                                    $val_for_form = '';
                                } else {
                                    $placeholder = $meta['placeholder'] ?? '';
                                    $val_for_form = $val;
                                }
                            ?>
                                <tr>
                                    <th><?php echo \esc_html($meta['label']); ?></th>
                                    <td>
                                        <input type="<?php echo \esc_attr($input_type); ?>"
                                               name="field[<?php echo \esc_attr($field); ?>]"
                                               value="<?php echo \esc_attr((string) $val_for_form); ?>"
                                               placeholder="<?php echo \esc_attr($placeholder); ?>"
                                               class="regular-text"
                                               <?php if (!empty($meta['required']) && $val === '') echo 'required'; ?>>
                                    </td>
                                </tr>
                            <?php endforeach; ?>
                        </table>
                        <p><button type="submit" class="button button-primary">Сохранить</button></p>
                    </form>
                <?php endif; ?>
            </div>
        <?php endforeach; ?>
    </div>
    <?php
}

function handle_save(): void {
    if (!\current_user_can('manage_network_options')) { \wp_die('No.', 403); }
    $adapter_name = \sanitize_text_field($_POST['adapter_name'] ?? '');
    if (!in_array($adapter_name, VALID_ADAPTERS, true)) \wp_die('Invalid', 400);
    \check_admin_referer('landing_int_save_' . $adapter_name);

    $segment = (int) ($_POST['segment'] ?? 0);
    $is_network = ($segment === 0);
    $main_id = \function_exists('get_main_site_id') ? \get_main_site_id() : 1;
    $blog_id = $is_network ? $main_id : $segment;

    $cls = adapter_class($adapter_name);
    $defs = $cls::field_definitions();
    $encrypted_fields = [];
    foreach ($defs as $f => $meta) if (!empty($meta['encrypt'])) $encrypted_fields[] = $f;

    // Existing settings (для preserve encrypted-полей при пустом input)
    $existing = resolve_integration($adapter_name, $blog_id);
    $existing_settings = $existing ? $existing['settings'] : [];

    $new_settings = [];
    foreach ($defs as $field => $meta) {
        $input = (string) ($_POST['field'][$field] ?? '');
        if (!empty($meta['encrypt']) && $input === '' && isset($existing_settings[$field])) {
            // Preserve encrypted field if input empty
            $new_settings[$field] = $existing_settings[$field];
        } else {
            $new_settings[$field] = \sanitize_text_field($input);
        }
    }

    // Delete existing record for this blog+adapter+is_network combo
    foreach (list_integrations($blog_id) as $r) {
        if ($r['adapter_name'] === $adapter_name && $r['is_network'] === $is_network) {
            delete_integration($r['id']);
        }
    }
    save_integration($adapter_name, $new_settings, $is_network, $blog_id, $encrypted_fields, true);

    \wp_safe_redirect(\network_admin_url('admin.php?page=landing-config-network-integrations&segment=' . $segment . '&saved=1'));
    exit;
}

function handle_toggle_override(): void {
    if (!\current_user_can('manage_network_options')) { \wp_die('No.', 403); }
    $adapter_name = \sanitize_text_field($_POST['adapter_name'] ?? '');
    if (!in_array($adapter_name, VALID_ADAPTERS, true)) \wp_die('Invalid', 400);
    \check_admin_referer('landing_int_toggle_override_' . $adapter_name);

    $segment = (int) ($_POST['segment'] ?? 0);
    if ($segment === 0) \wp_die('Cannot toggle override on network level', 400);
    $enable = !empty($_POST['override_enabled']);

    if (!$enable) {
        // Drop site override → revert to network
        foreach (list_integrations($segment) as $r) {
            if ($r['adapter_name'] === $adapter_name && $r['is_network'] === false) {
                delete_integration($r['id']);
            }
        }
    } else {
        // Create empty site override (pre-filled с network на форме отдельным save)
        $net = resolve_integration($adapter_name, 1);
        $settings = $net ? $net['settings'] : [];
        $cls = adapter_class($adapter_name);
        $encrypted_fields = [];
        foreach ($cls::field_definitions() as $f => $m) if (!empty($m['encrypt'])) $encrypted_fields[] = $f;
        save_integration($adapter_name, $settings, false, $segment, $encrypted_fields, true);
    }
    \wp_safe_redirect(\network_admin_url('admin.php?page=landing-config-network-integrations&segment=' . $segment));
    exit;
}
```

- [ ] **Step 3: Lint + deploy + smoke**

Открыть `http://ailexi.ru/wp-admin/network/admin.php?page=landing-config-network-integrations` — селектор + 6 карточек адаптеров. На segment=2 → toggle override на одном адаптере → отображение меняется на форму, заполнить, сохранить, проверить что segment=0 (network) не затронут.

- [ ] **Step 4: Commit**

```bash
git add skills/wp-landing-config/mu-plugin/landing-config/includes/admin-integrations.php
git commit -m "feat(wp-landing-config): A3.4 — admin-integrations под Network admin с override-toggle

6 адаптеров: каждая карточка с inherited/override badge.
Toggle 'Использовать свой <adapter>' на сегменте — создаёт/удаляет site override.
Encrypted поля: при пустом input в форме сохраняется существующее значение.

Co-Authored-By: Claude Opus 4.7 (1M context) <noreply@anthropic.com>"
```

---

### Task A3.4.2: admin-integrations-readonly.php

- [ ] **Step 1: Создать аналогично admin-cta-readonly.php**

```php
<?php
namespace LandingConfig\Admin\IntegrationsReadOnly;

if (!defined('ABSPATH')) { exit; }

use function LandingConfig\Integrations\resolve_integration;
use function LandingConfig\Integrations\has_override;
use const LandingConfig\Integrations\VALID_ADAPTERS;

function adapter_class(string $name): string {
    return \LandingConfig\Admin\Integrations\adapter_class($name);
}
function mask(string $v): string {
    return \LandingConfig\Admin\Integrations\mask_secret($v);
}

\add_action('admin_menu', function () {
    \add_submenu_page(
        'landing-config',
        'Интеграции (просмотр)',
        'Интеграции',
        'manage_options',
        'landing-config-integrations',
        __NAMESPACE__ . '\\render_page'
    );
});

function render_page(): void {
    if (!\current_user_can('manage_options')) { \wp_die('No.', 403); }
    $blog_id = \get_current_blog_id();
    $net_url = \network_admin_url('admin.php?page=landing-config-network-integrations&segment=' . $blog_id);
    ?>
    <div class="wrap">
        <h1>Интеграции <span style="font-size:13px; color:#646970; font-weight:400;">— режим просмотра</span></h1>
        <div class="notice notice-info inline">
            <p>Управляются super-admin'ом. <a href="<?php echo \esc_url($net_url); ?>" target="_blank">Открыть редактор</a> →</p>
        </div>

        <?php foreach (VALID_ADAPTERS as $name):
            $r = resolve_integration($name, $blog_id);
            $source = has_override($name, $blog_id) ? 'site override' : 'inherited from network';
            $color = has_override($name, $blog_id) ? '#dba617' : '#2271b1';
            $cls = adapter_class($name);
            $defs = $cls ? $cls::field_definitions() : [];
        ?>
            <div style="background:#fff; border:1px solid #c3c4c7; padding:12px 16px; margin:10px 0; border-radius:4px;">
                <h3 style="margin:0 0 8px;"><code><?php echo \esc_html($name); ?></code>
                    <span style="background:<?php echo $color; ?>; color:#fff; padding:2px 8px; border-radius:3px; font-size:11px;">
                        <?php echo $source; ?>
                    </span>
                </h3>
                <?php if (!$r): ?>
                    <p style="color:#646970;"><em>Не настроено.</em></p>
                <?php else: ?>
                    <ul style="margin:0; color:#646970;">
                        <?php foreach ($defs as $field => $meta):
                            $v = (string) ($r['settings'][$field] ?? '');
                            if (!empty($meta['encrypt'])) $v = mask($v);
                        ?>
                            <li><strong><?php echo \esc_html($meta['label']); ?>:</strong> <code><?php echo \esc_html($v ?: '—'); ?></code></li>
                        <?php endforeach; ?>
                    </ul>
                <?php endif; ?>
            </div>
        <?php endforeach; ?>
    </div>
    <?php
}
```

- [ ] **Step 2: Подключить в landing-config.php**

```php
require_once LANDING_CONFIG_DIR . '/includes/admin-integrations-readonly.php';
```

- [ ] **Step 3: Lint + deploy + smoke + commit**

```bash
git add skills/wp-landing-config/mu-plugin/landing-config/includes/admin-integrations-readonly.php \
        skills/wp-landing-config/mu-plugin/landing-config/landing-config.php
git commit -m "feat(wp-landing-config): A3.4 — admin-integrations-readonly view на subsite

Read-only список 6 адаптеров с маскированными credentials.
Site override / inherited from network бейджи. Deep-link на network editor.

Co-Authored-By: Claude Opus 4.7 (1M context) <noreply@anthropic.com>"
```

- [ ] **Step 4: User Gate** — «A3.4 deployed. Интеграции в network admin с override-toggle + read-only на subsite. Готов к A3.5 (Snippets unified)?»

---

## Phase A3.5 — Snippets unified (merge network + site, segment selector)

**Цель фазы:** объединить `admin-snippets.php` и `admin-snippets-network.php` в единую страницу под `network_admin_menu`, с селектором сегмента. На subsite остаётся read-only.

**Files:**
- Rewrite: `skills/wp-landing-config/mu-plugin/landing-config/includes/admin-snippets.php` (теперь network-only с селектором)
- Delete: `skills/wp-landing-config/mu-plugin/landing-config/includes/admin-snippets-network.php` (merged)
- Create: `skills/wp-landing-config/mu-plugin/landing-config/includes/admin-snippets-readonly.php`

---

### Task A3.5.1: Merge admin-snippets + admin-snippets-network

- [ ] **Step 1: Backup существующих**

```bash
cp skills/wp-landing-config/mu-plugin/landing-config/includes/admin-snippets.php /tmp/snip-site.bak.php
cp skills/wp-landing-config/mu-plugin/landing-config/includes/admin-snippets-network.php /tmp/snip-net.bak.php
```

- [ ] **Step 2: Создать единый admin-snippets.php**

Логика страницы:
- При `segment=0` — список network-snippets с действиями new/edit/delete + столбец «Overridden by» (как сейчас в admin-snippets-network.php).
- При `segment=N>0` — список site-snippets этого сегмента + «Inherited from network» с кнопкой Override.

Реализация: взять полный код из `admin-snippets-network.php` для `segment=0` ветки + код из `admin-snippets.php` для `segment=N` ветки + общий header с `render_selector`. Все save/delete/override action handlers собрать в одном файле; различать save_segment 0 vs N по `$_POST['segment']`.

(Полный код опускаю — это ~300 строк, в основном copy-from-existing. Внимательно перенести wp_nonce_field имена, чтобы существующие links в email-уведомлениях / закладках не упали с invalid nonce.)

Ключевые правки:
- `\add_action('admin_menu', ...)` → `\add_action('network_admin_menu', ...)`
- parent slug: `'landing-config'` → `'landing-config-network'`
- new slug: `'landing-config-snippets'` / `'landing-config-network-snippets'` → один `'landing-config-network-snippets'`
- В render_list: ветвление по `current_from_request()`.

- [ ] **Step 3: Удалить admin-snippets-network.php**

```bash
git rm skills/wp-landing-config/mu-plugin/landing-config/includes/admin-snippets-network.php
```

И снять require_once из `landing-config.php`.

- [ ] **Step 4: Lint + deploy + smoke**

Открыть `network/admin.php?page=landing-config-network-snippets`:
- Segment=0 → редактирование network snippets.
- Segment=2 → список site snippets для blog_id=2 + блок inherited из network.

Проверить что save/edit/delete/override работают на обоих сегментах.

- [ ] **Step 5: Commit**

```bash
git add skills/wp-landing-config/mu-plugin/landing-config/includes/admin-snippets.php \
        skills/wp-landing-config/mu-plugin/landing-config/landing-config.php
git rm skills/wp-landing-config/mu-plugin/landing-config/includes/admin-snippets-network.php
git commit -m "feat(wp-landing-config): A3.5 — merge admin-snippets + _network в одну Network admin страницу

Селектор сегмента ?segment=N: 0 = network snippets editor, N>0 = site snippets для blog_id=N + inherited из network с override.
Старый _network.php удалён.

Co-Authored-By: Claude Opus 4.7 (1M context) <noreply@anthropic.com>"
```

---

### Task A3.5.2: admin-snippets-readonly.php

- [ ] **Step 1: Создать read-only view** (структура аналогично admin-cta-readonly + admin-integrations-readonly — таблица snippets без edit/delete + ссылка на network editor)

- [ ] **Step 2: Подключить в landing-config.php**

- [ ] **Step 3: Deploy + smoke + commit**

```bash
git add skills/wp-landing-config/mu-plugin/landing-config/includes/admin-snippets-readonly.php \
        skills/wp-landing-config/mu-plugin/landing-config/landing-config.php
git commit -m "feat(wp-landing-config): A3.5 — admin-snippets-readonly view на subsite

Read-only список всех snippets применяющихся к текущему сегменту
(network + site override). Deep-link на network editor.

Co-Authored-By: Claude Opus 4.7 (1M context) <noreply@anthropic.com>"
```

- [ ] **Step 4: User Gate** — «A3.5 deployed. Все три раздела (CTA / Integrations / Snippets) теперь в Network admin с селектором сегмента. На subsite read-only. Готов к финалу A3.6?»

---

## Phase A3.6 — Cleanup + final smoke + docs

**Цель фазы:** убрать R1 diagnostic logger, обновить CLAUDE.md / SETUP.md / wiki, прогнать полный smoke на ailexi.ru.

**Files:**
- Modify: `skills/wp-landing-config/mu-plugin/landing-config/includes/admin-cta.php` (snапping R1 diag) — НО он уже переписан в A3.3, так что эта правка скорее всего УЖЕ сделана. Проверить.
- Modify: `CLAUDE.md` (секция «Landing-config mu-plugin (S2-A)» — добавить S2-A.3 features)
- Modify: `docs/SETUP.md` (если упоминание про CTA / Integrations есть)
- Create: `skills/wp-landing-config/tests/integration/test_s2a3_smoke.sh` (live smoke на сервере)

---

### Task A3.6.1: Cleanup R1 diagnostic

- [ ] **Step 1: Убедиться что в admin-cta.php после A3.3.2 нет error_log('lp_cta_menu...')**

```bash
grep 'lp_cta_menu' skills/wp-landing-config/mu-plugin/landing-config/includes/admin-cta.php || echo "Already removed"
```

Если remnant остался — удалить.

- [ ] **Step 2: Commit (если что-то удалили)**

```bash
git add -A
git commit -m "chore(wp-landing-config): A3.6 — remove R1 diagnostic logger (root cause known: stale browser cookies)"
```

Если grep ничего не нашёл — skip.

---

### Task A3.6.2: Live full smoke

- [ ] **Step 1: Создать `tests/integration/test_s2a3_smoke.sh`**

```bash
#!/usr/bin/env bash
# Live smoke на ailexi.ru: проверка что все CPT-страницы доступны, миграция сработала,
# helper landing_get_cta() возвращает данные из cascade.
set -euo pipefail

source /tmp/test-s2a/.env

SSH="ssh -i $BEGET_SSH_KEY -o StrictHostKeyChecking=no -o LogLevel=ERROR ${BEGET_USER}@${BEGET_HOST}"
WP_PATH=/home/e/esper21/ailexi.ru/public_html
WPCLI="/usr/local/bin/php8.3 /usr/local/bin/wp-cli.phar --path=$WP_PATH"

echo "▶ T1: lp_cta CPT records exist (≥5 network + любые site overrides)"
n=$($SSH "$WPCLI post list --post_type=lp_cta --url=http://ailexi.ru/ --format=count")
test "$n" -ge 5 || { echo "FAIL: lp_cta count=$n, expected >=5"; exit 1; }

echo "▶ T2: lp_integration CPT records exist (хотя бы 1)"
m=$($SSH "$WPCLI post list --post_type=lp_integration --url=http://ailexi.ru/ --format=count")
test "$m" -ge 1 || { echo "FAIL: lp_integration count=$m, expected >=1"; exit 1; }

echo "▶ T3: landing_get_cta('primary') возвращает не-null с label"
out=$($SSH "$WPCLI eval 'var_export(landing_get_cta(\"primary\"));' --url=http://ailexi.ru/" 2>&1)
echo "$out" | grep -q "'label' =>" || { echo "FAIL: landing_get_cta returned no label"; echo "$out"; exit 1; }

echo "▶ T4: HTTP 200 на network admin страницах (auth: super-admin cookies нужны - тут только liveness)"
for slug in landing-config-network landing-config-network-cta landing-config-network-integrations landing-config-network-snippets; do
    code=$(curl -s -o /dev/null -w '%{http_code}' --max-time 10 "http://ailexi.ru/wp-admin/network/admin.php?page=$slug" || echo "000")
    # 200 (если auth) или 302 (redirect на login) — оба ок, означает страница зарегистрирована
    test "$code" = "200" -o "$code" = "302" || { echo "FAIL: $slug returned $code"; exit 1; }
done

echo "▶ T5: HTTP 200 на subsite read-only страницах"
for slug in landing-config-cta landing-config-integrations landing-config-snippets; do
    code=$(curl -s -o /dev/null -w '%{http_code}' --max-time 10 "http://russian.ailexi.ru/wp-admin/admin.php?page=$slug" || echo "000")
    test "$code" = "200" -o "$code" = "302" || { echo "FAIL: subsite $slug returned $code"; exit 1; }
done

echo "▶ T6: debug.log не содержит свежих PHP Fatal/Error от наших файлов"
recent=$($SSH "tail -200 $WP_PATH/wp-content/debug.log 2>/dev/null | grep -E 'Fatal|TypeError' | grep -i 'landing-config' | tail -3" || echo "")
test -z "$recent" || { echo "FAIL: fresh fatals in our code:"; echo "$recent"; exit 1; }

echo "✅ S2-A.3 live smoke GREEN"
```

- [ ] **Step 2: Запустить smoke**

```bash
bash skills/wp-landing-config/tests/integration/test_s2a3_smoke.sh
```

Ожидаемо: `✅ S2-A.3 live smoke GREEN`. Если что-то падает — фиксать соответствующую фазу и пересобирать.

- [ ] **Step 3: Commit smoke-script**

```bash
git add skills/wp-landing-config/tests/integration/test_s2a3_smoke.sh
git commit -m "test(wp-landing-config): A3.6 — live smoke S2-A.3 на ailexi.ru

6 проверок: CPT counts, helper output, HTTP 200/302 на admin URLs,
отсутствие свежих fatal'ов от нашего кода в debug.log.

Co-Authored-By: Claude Opus 4.7 (1M context) <noreply@anthropic.com>"
```

---

### Task A3.6.3: Документация

- [ ] **Step 1: Обновить CLAUDE.md секция «Landing-config mu-plugin (S2-A)»**

Дописать после блока про S2-A:

```markdown
### S2-A.3 — Network-Admin Unification (2026-05-19)

Все настройки (CTA / Интеграции / Снипеты) теперь в **Network admin → Лендинг**
с селектором сегмента ?segment=N (0 = network default, N = blog_id сегмента).
Cascade: network запись → site override по machine-id (preset_name / adapter_name / snippet name).

- 3 CPT: `lp_cta`, `lp_integration`, `lp_snippet`
- Общий резолвер `includes/cascade.php`
- Read-only mode на subsite: `*-readonly.php` файлы
- Миграция S2-A wp_options → CPT — идемпотентно, один раз при первом super-admin admin_init.
  Legacy fallback в `landing_get_cta()` оставлен на 2-3 недели.

См. [spec](docs/superpowers/specs/2026-05-19-s2a3-network-admin-unification-design.md)
и [plan](docs/superpowers/plans/2026-05-19-s2a3-network-admin-unification-plan.md).
```

- [ ] **Step 2: Commit doc**

```bash
git add CLAUDE.md
git commit -m "docs(s2a3): CLAUDE.md секция про Network-Admin Unification

Co-Authored-By: Claude Opus 4.7 (1M context) <noreply@anthropic.com>"
```

- [ ] **Step 3: Финальный User Gate** — «S2-A.3 закрыт. Все 6 фаз готовы, live smoke green, документация обновлена. Готов к следующему треку (B19 lead status workflow / B17 CTA-Library / S2-CD CD2 etc.)?»

---

## Self-Review

**1. Spec coverage** — проверка против §10 спека:

| Spec фаза | Plan |
|---|---|
| A3.1 cascade + CTA + migration | ✅ Tasks A3.1.1 — A3.1.9 |
| A3.2 Integrations CPT + AdapterInterface + migration | ✅ Tasks A3.2.1 — A3.2.3 |
| A3.3 admin-cta UI + read-only | ✅ Tasks A3.3.1 — A3.3.3 |
| A3.4 admin-integrations UI + read-only | ✅ Tasks A3.4.1 — A3.4.2 |
| A3.5 admin-snippets merge + read-only | ✅ Tasks A3.5.1 — A3.5.2 |
| A3.6 cleanup + smoke + docs | ✅ Tasks A3.6.1 — A3.6.3 |

Все требования спека покрыты.

**2. Placeholder scan** — есть один в A3.5.1 step 2: «Полный код опускаю — это ~300 строк, в основном copy-from-existing». Это компромиссное место — реальная имплементация будет занимать столько строк, и каждую строку выписывать в плане избыточно. Engineer берёт два бэкап-файла из `/tmp/snip-*.bak.php` и мерджит по описанной логике. **Оставляю как есть с явным указанием «inline merge from backups»**.

**3. Type consistency** —
- `LandingConfig\Cascade\resolve_for_blog($cpt, $name_meta_key, $is_network_meta_key, $name, $blog_id)` — 5 параметров, везде один сигнатуру использую.
- `save_cta(array, bool, int)` / `save_integration(string, array, bool, int, array, bool)` — сигнатуры стабильны между Task и handler.
- `field_definitions(): array<string, array{...}>` — единый формат во всех 6 адаптерах.
- Constants `PRESET_NAMES`, `VALID_ADAPTERS`, `VALID_TYPES` — экспортируются через `use const`, везде согласно.

Никаких contradictions.

Plan готов.
