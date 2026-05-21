# B19 Lead Status Workflow — Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Дать маркетологу UI для управления статусами заявок: редактируемый словарь статусов (4-я ось cascade S2-A.3), карточка заявки с timeline истории, табы-фильтры и bulk-action в списке заявок.

**Architecture:** Новый CPT `lp_lead_status` через тот же резолвер что CTA/Integrations/Snippets из S2-A.3. Отдельная per-blog таблица `landing_lead_status_log` для истории изменений. Network admin + subsite readonly для словаря. Расширения существующего `admin-leads.php` (табы, колонка, checkbox, ссылка на карточку). Новая карточка заявки с модальным окном смены статуса. Bulk-action с транзакциями.

**Tech Stack:** PHP 8.3, WordPress multisite, mu-plugin, dbDelta, `$wpdb` prepared statements, BATS-style PHP-тесты с моками в `tests/fixtures/wp-bootstrap.php`.

---

## Phase B19.1 — lp_lead_status CPT + CRUD + cascade

**Цель:** базовый слой данных. Регистрация CPT, save/get/list/resolve/delete/has_override через cascade-резолвер. Полное покрытие unit-тестами по образцу `tests/test_cta.php`.

**Files:**
- Create: `skills/wp-landing-config/mu-plugin/landing-config/includes/lead-statuses.php`
- Modify: `skills/wp-landing-config/mu-plugin/landing-config/landing-config.php` (добавить require)
- Test: `skills/wp-landing-config/tests/test_lead_statuses.php`

---

### Task B19.1.1: Создать failing test для CPT + CRUD

**Files:**
- Test: `skills/wp-landing-config/tests/test_lead_statuses.php`

- [ ] **Step 1: Создать файл теста**

```php
<?php
require_once __DIR__ . '/fixtures/wp-bootstrap.php';
require_once __DIR__ . '/../mu-plugin/landing-config/includes/cascade.php';
require_once __DIR__ . '/../mu-plugin/landing-config/includes/lead-statuses.php';

use function LandingConfig\LeadStatuses\save_lead_status;
use function LandingConfig\LeadStatuses\get_lead_status;
use function LandingConfig\LeadStatuses\list_lead_statuses;
use function LandingConfig\LeadStatuses\resolve_lead_status;
use function LandingConfig\LeadStatuses\delete_lead_status;
use function LandingConfig\LeadStatuses\has_override;

$failures = 0; $tests = 0;
function assert_test($c, $m) { global $failures, $tests; $tests++; if (!$c) { echo "FAIL: $m\n"; $failures++; } }

function reset_ls() {
    $GLOBALS['_mock_posts'] = [];
    $GLOBALS['_mock_post_meta'] = [];
    $GLOBALS['_mock_next_post_id'] = 1;
    $GLOBALS['_mock_current_blog_id'] = 1;
}

// T1: save+get round-trip
reset_ls();
$id = save_lead_status([
    'slug'  => 'pending',
    'label' => 'Новая',
    'color' => '#2271b1',
    'order' => 10,
], true, 1);
assert_test($id > 0, 'T1a save_lead_status returned id');
$row = get_lead_status($id);
assert_test($row['slug'] === 'pending', 'T1b slug round-trip');
assert_test($row['label'] === 'Новая', 'T1c label round-trip');
assert_test($row['color'] === '#2271b1', 'T1d color round-trip');
assert_test($row['order'] === 10, 'T1e order round-trip');
assert_test($row['is_network'] === true, 'T1f is_network round-trip');

// T2: cascade site override wins
reset_ls();
save_lead_status(['slug' => 'pending', 'label' => 'Net label', 'color' => '#000', 'order' => 10], true, 1);
$GLOBALS['_mock_current_blog_id'] = 2;
save_lead_status(['slug' => 'pending', 'label' => 'Site label', 'color' => '#fff', 'order' => 10], false, 2);
$r = resolve_lead_status('pending', 2);
assert_test($r['label'] === 'Site label', 'T2 site override wins');

// T3: cascade network fallback
$r = resolve_lead_status('pending', 1);
assert_test($r['label'] === 'Net label', 'T3 network fallback for main blog');

// T4: list sorted by order asc
reset_ls();
save_lead_status(['slug' => 'won', 'label' => 'Won', 'color' => '#0a0', 'order' => 30], true, 1);
save_lead_status(['slug' => 'pending', 'label' => 'Pending', 'color' => '#00f', 'order' => 10], true, 1);
save_lead_status(['slug' => 'in_progress', 'label' => 'In progress', 'color' => '#fa0', 'order' => 20], true, 1);
$list = list_lead_statuses(1);
assert_test(count($list) === 3, 'T4a list count == 3');
assert_test($list[0]['slug'] === 'pending', 'T4b first by order is pending');
assert_test($list[1]['slug'] === 'in_progress', 'T4c second is in_progress');
assert_test($list[2]['slug'] === 'won', 'T4d third is won');

// T5: has_override
reset_ls();
save_lead_status(['slug' => 'pending', 'label' => 'Net', 'color' => '#000', 'order' => 10], true, 1);
assert_test(has_override('pending', 2) === false, 'T5a no override yet');
$GLOBALS['_mock_current_blog_id'] = 2;
save_lead_status(['slug' => 'pending', 'label' => 'Site', 'color' => '#fff', 'order' => 10], false, 2);
assert_test(has_override('pending', 2) === true, 'T5b override registered');

// T6: delete removes
reset_ls();
$id = save_lead_status(['slug' => 'spam', 'label' => 'Spam', 'color' => '#999', 'order' => 50], true, 1);
assert_test(delete_lead_status($id) === true, 'T6a delete returns true');
assert_test(get_lead_status($id) === null, 'T6b row gone after delete');

// T7: invalid slug → 0
reset_ls();
$id = save_lead_status(['slug' => 'BAD SLUG!', 'label' => 'X', 'color' => '#000', 'order' => 10], true, 1);
assert_test($id === 0, 'T7 invalid slug rejected');

// T8: update path (post_id передан → wp_update_post, не дубль)
reset_ls();
$id1 = save_lead_status(['slug' => 'pending', 'label' => 'Old', 'color' => '#000', 'order' => 10], true, 1);
$id2 = save_lead_status(['slug' => 'pending', 'label' => 'New', 'color' => '#000', 'order' => 10], true, 1, $id1);
assert_test($id1 === $id2, 'T8a update reuses post id');
$list = list_lead_statuses(1);
assert_test(count($list) === 1, 'T8b no duplicate row');
assert_test($list[0]['label'] === 'New', 'T8c updated label persists');

echo "$tests tests, $failures failures\n";
exit($failures > 0 ? 1 : 0);
```

- [ ] **Step 2: Запустить тест — должен упасть**

```bash
php skills/wp-landing-config/tests/test_lead_statuses.php
```

Ожидаемо: `Fatal error: require_once(...lead-statuses.php) failed`.

---

### Task B19.1.2: Реализовать lead-statuses.php — RED → GREEN

**Files:**
- Create: `skills/wp-landing-config/mu-plugin/landing-config/includes/lead-statuses.php`

- [ ] **Step 1: Создать includes/lead-statuses.php**

```php
<?php
namespace LandingConfig\LeadStatuses;

if (!defined('ABSPATH')) { exit; }

use function LandingConfig\Cascade\resolve_for_blog;
use function LandingConfig\Cascade\list_for_blog;
use function LandingConfig\Cascade\has_site_override;
use function LandingConfig\Cascade\_with_blog;

const POST_TYPE = 'lp_lead_status';
const SLUG_META = '_lp_status_slug';
const LABEL_META = '_lp_status_label';
const COLOR_META = '_lp_status_color';
const ORDER_META = '_lp_status_order';
const NETWORK_META = '_lp_is_network';

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

function _is_valid_slug(string $slug): bool {
    return $slug !== '' && (bool) preg_match('/^[a-z0-9_-]+$/', $slug);
}

function _is_valid_color(string $color): bool {
    return (bool) preg_match('/^#[0-9a-fA-F]{6}$/', $color);
}

function save_lead_status(array $args, bool $is_network, int $blog_id, int $post_id = 0): int {
    return _with_blog($blog_id, function () use ($args, $is_network, $post_id) {
        $slug = \sanitize_key($args['slug'] ?? '');
        if (!_is_valid_slug($slug)) return 0;

        $label = \sanitize_text_field($args['label'] ?? '');
        $color = (string) ($args['color'] ?? '#2271b1');
        if (!_is_valid_color($color)) $color = '#2271b1';
        $order = (int) ($args['order'] ?? 10);

        $post = ['post_type' => POST_TYPE, 'post_status' => 'publish', 'post_title' => $slug];
        if ($post_id > 0) {
            $post['ID'] = $post_id;
            $id = \wp_update_post($post);
        } else {
            $id = \wp_insert_post($post);
        }
        \update_post_meta($id, SLUG_META, $slug);
        \update_post_meta($id, LABEL_META, $label);
        \update_post_meta($id, COLOR_META, $color);
        \update_post_meta($id, ORDER_META, $order);
        \update_post_meta($id, NETWORK_META, $is_network ? '1' : '0');
        return (int) $id;
    });
}

function get_lead_status(int $id): ?array {
    $p = \get_post($id);
    if (!$p || ($p->post_type ?? '') !== POST_TYPE) return null;
    return [
        'id'         => $id,
        'slug'       => (string) \get_post_meta($id, SLUG_META, true),
        'label'      => (string) \get_post_meta($id, LABEL_META, true),
        'color'      => (string) \get_post_meta($id, COLOR_META, true),
        'order'      => (int) \get_post_meta($id, ORDER_META, true),
        'is_network' => (string) \get_post_meta($id, NETWORK_META, true) === '1',
    ];
}

function delete_lead_status(int $id): bool {
    return (bool) \wp_delete_post($id, true);
}

function list_lead_statuses(int $blog_id): array {
    $raw = list_for_blog(POST_TYPE, SLUG_META, NETWORK_META, $blog_id);
    $out = [];
    foreach ($raw as $row) {
        $out[] = [
            'id'         => (int) ($row['__post_id'] ?? 0),
            'slug'       => $row[SLUG_META] ?? '',
            'label'      => $row[LABEL_META] ?? '',
            'color'      => $row[COLOR_META] ?? '#2271b1',
            'order'      => (int) ($row[ORDER_META] ?? 10),
            'is_network' => ($row[NETWORK_META] ?? '0') === '1',
        ];
    }
    usort($out, fn($a, $b) => $a['order'] <=> $b['order']);
    return $out;
}

function resolve_lead_status(string $slug, int $blog_id): ?array {
    $row = resolve_for_blog(POST_TYPE, SLUG_META, NETWORK_META, $slug, $blog_id);
    if (!$row) return null;
    return [
        'slug'       => $row[SLUG_META] ?? $slug,
        'label'      => $row[LABEL_META] ?? '',
        'color'      => $row[COLOR_META] ?? '#2271b1',
        'order'      => (int) ($row[ORDER_META] ?? 10),
        'is_network' => ($row[NETWORK_META] ?? '0') === '1',
    ];
}

function has_override(string $slug, int $blog_id): bool {
    return has_site_override(POST_TYPE, SLUG_META, NETWORK_META, $slug, $blog_id);
}
```

- [ ] **Step 2: Подключить require в landing-config.php**

В файле `skills/wp-landing-config/mu-plugin/landing-config/landing-config.php` найди строку:

```php
require_once LANDING_CONFIG_DIR . '/includes/integrations.php';
```

И добавь сразу после неё:

```php
require_once LANDING_CONFIG_DIR . '/includes/lead-statuses.php';
```

- [ ] **Step 3: Запустить тест — должен пройти**

```bash
php skills/wp-landing-config/tests/test_lead_statuses.php
```

Ожидаемо: `12 tests, 0 failures`.

- [ ] **Step 4: Regression — все PHP-тесты**

```bash
for t in skills/wp-landing-config/tests/test_*.php; do echo "=== $t ==="; php "$t" 2>&1 | tail -2; done
```

Ожидаемо: никаких новых failures сверх pre-existing openssl (5 в test_encryption, 2 в test_integrations, 2 в test_adapter_settings_cascade).

- [ ] **Step 5: Commit**

```bash
git add skills/wp-landing-config/tests/test_lead_statuses.php \
        skills/wp-landing-config/mu-plugin/landing-config/includes/lead-statuses.php \
        skills/wp-landing-config/mu-plugin/landing-config/landing-config.php
git commit -m "feat(wp-landing-config): B19.1 — lp_lead_status CPT + CRUD + cascade

12/12 tests: save+get round-trip с slug/label/color/order, cascade
override+fallback, sort by order, has_override, delete, invalid-slug rejection,
update path.

Co-Authored-By: Claude Opus 4.7 (1M context) <noreply@anthropic.com>"
```

---

## Phase B19.2 — landing_lead_status_log таблица + helpers

**Цель:** per-blog таблица истории изменений + защищённые helpers с whitelist валидацией статусов.

**Files:**
- Modify: `skills/wp-landing-config/mu-plugin/landing-config/includes/db.php` (CREATE TABLE)
- Create: `skills/wp-landing-config/mu-plugin/landing-config/includes/lead-status-log.php`
- Modify: `skills/wp-landing-config/mu-plugin/landing-config/landing-config.php` (require)
- Test: `skills/wp-landing-config/tests/test_lead_status_log.php`

---

### Task B19.2.1: Добавить таблицу в db.php

**Files:**
- Modify: `skills/wp-landing-config/mu-plugin/landing-config/includes/db.php`

- [ ] **Step 1: Прочитать существующий db.php (для контекста)**

```bash
cat skills/wp-landing-config/mu-plugin/landing-config/includes/db.php | head -110
```

Найди функцию `get_lead_log_table_name()` — выше неё добавим аналогичную для status_log.

- [ ] **Step 2: Добавить getter для имени таблицы**

В `skills/wp-landing-config/mu-plugin/landing-config/includes/db.php` найди:

```php
function get_lead_log_table_name(): string {
    global $wpdb;
    return $wpdb->prefix . 'landing_lead_log';
}
```

Сразу после неё добавь:

```php
function get_lead_status_log_table_name(): string {
    global $wpdb;
    return $wpdb->prefix . 'landing_lead_status_log';
}
```

- [ ] **Step 3: Добавить CREATE TABLE в install_schema()**

В той же `db.php`, в функции `install_schema()`, найди блок:

```php
$leads = get_leads_table_name();
$log = get_lead_log_table_name();
```

Добавь сразу после:

```php
$status_log = get_lead_status_log_table_name();
```

Затем после блока `$log_sql = "CREATE TABLE $log ..."` (заканчивается на `) $charset;";`) добавь:

```php
$status_log_sql = "CREATE TABLE $status_log (
    id BIGINT(20) UNSIGNED NOT NULL AUTO_INCREMENT,
    lead_id BIGINT(20) UNSIGNED NOT NULL,
    user_id BIGINT(20) UNSIGNED NULL,
    from_status VARCHAR(64) NULL,
    to_status VARCHAR(64) NOT NULL,
    comment TEXT NULL,
    created_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
    PRIMARY KEY (id),
    KEY lead_id (lead_id),
    KEY created_at (created_at)
) $charset;";
```

И в конце функции, после `dbDelta($log_sql);` добавь:

```php
dbDelta($status_log_sql);
```

- [ ] **Step 4: Lint**

```bash
php -l skills/wp-landing-config/mu-plugin/landing-config/includes/db.php
```

Ожидаемо: `No syntax errors detected`.

- [ ] **Step 5: Прогнать существующий test_db_schema.php**

```bash
php skills/wp-landing-config/tests/test_db_schema.php
```

Ожидаемо: `8 tests, 0 failures` (не должны сломаться существующие проверки). Если падает — значит мок dbDelta не справляется с третьим вызовом, в этом случае посмотри tests/fixtures/wp-bootstrap.php и пробрось.

---

### Task B19.2.2: Failing test для lead-status-log

**Files:**
- Test: `skills/wp-landing-config/tests/test_lead_status_log.php`

- [ ] **Step 1: Создать файл теста**

```php
<?php
require_once __DIR__ . '/fixtures/wp-bootstrap.php';
require_once __DIR__ . '/../mu-plugin/landing-config/includes/cascade.php';
require_once __DIR__ . '/../mu-plugin/landing-config/includes/lead-statuses.php';
require_once __DIR__ . '/../mu-plugin/landing-config/includes/lead-status-log.php';

use function LandingConfig\LeadStatuses\save_lead_status;
use function LandingConfig\LeadStatusLog\log_status_change;
use function LandingConfig\LeadStatusLog\get_status_history;

$failures = 0; $tests = 0;
function assert_test($c, $m) { global $failures, $tests; $tests++; if (!$c) { echo "FAIL: $m\n"; $failures++; } }

function reset_lsl() {
    $GLOBALS['_mock_posts'] = [];
    $GLOBALS['_mock_post_meta'] = [];
    $GLOBALS['_mock_next_post_id'] = 1;
    $GLOBALS['_mock_current_blog_id'] = 1;
    $GLOBALS['_mock_status_log'] = [];
    $GLOBALS['_mock_next_status_log_id'] = 1;
}

// Seed vocab — нужно для whitelist валидации
function seed_vocab(int $blog_id = 1): void {
    save_lead_status(['slug' => 'pending', 'label' => 'Pending', 'color' => '#2271b1', 'order' => 10], true, $blog_id);
    save_lead_status(['slug' => 'in_progress', 'label' => 'In progress', 'color' => '#dba617', 'order' => 20], true, $blog_id);
    save_lead_status(['slug' => 'won', 'label' => 'Won', 'color' => '#00a32a', 'order' => 30], true, $blog_id);
}

// T1: log+get round-trip
reset_lsl();
seed_vocab();
$id = log_status_change(42, null, 'pending', 1, 'Заявка создана');
assert_test($id > 0, 'T1a log_status_change returned id');
$h = get_status_history(42);
assert_test(count($h) === 1, 'T1b history count == 1');
assert_test($h[0]['from_status'] === null, 'T1c from is null');
assert_test($h[0]['to_status'] === 'pending', 'T1d to is pending');
assert_test($h[0]['comment'] === 'Заявка создана', 'T1e comment round-trip');
assert_test($h[0]['user_id'] === 1, 'T1f user_id round-trip');

// T2: get_status_history sorted desc
reset_lsl();
seed_vocab();
log_status_change(7, null, 'pending', 1, 'a');
log_status_change(7, 'pending', 'in_progress', 1, 'b');
log_status_change(7, 'in_progress', 'won', 1, 'c');
$h = get_status_history(7);
assert_test(count($h) === 3, 'T2a 3 entries');
assert_test($h[0]['to_status'] === 'won', 'T2b newest first');
assert_test($h[1]['to_status'] === 'in_progress', 'T2c middle');
assert_test($h[2]['to_status'] === 'pending', 'T2d oldest last');

// T3: invalid to_status (not in vocab) → 0
reset_lsl();
seed_vocab();
$id = log_status_change(8, null, 'unknown_status', 1, 'should fail');
assert_test($id === 0, 'T3a invalid to_status rejected');
assert_test(count(get_status_history(8)) === 0, 'T3b nothing written');

// T4: empty comment → NULL
reset_lsl();
seed_vocab();
log_status_change(9, null, 'pending', 1, '');
$h = get_status_history(9);
assert_test($h[0]['comment'] === null, 'T4 empty comment stored as null');

// T5: user_id null (системное изменение)
reset_lsl();
seed_vocab();
log_status_change(10, null, 'pending', null, 'system seed');
$h = get_status_history(10);
assert_test($h[0]['user_id'] === null, 'T5 null user_id stored');

echo "$tests tests, $failures failures\n";
exit($failures > 0 ? 1 : 0);
```

- [ ] **Step 2: Запустить тест — должен упасть**

```bash
php skills/wp-landing-config/tests/test_lead_status_log.php
```

Ожидаемо: `Fatal error: require_once(...lead-status-log.php) failed`.

---

### Task B19.2.3: Реализовать lead-status-log.php + мок таблицы

**Files:**
- Create: `skills/wp-landing-config/mu-plugin/landing-config/includes/lead-status-log.php`
- Modify: `skills/wp-landing-config/tests/fixtures/wp-bootstrap.php` (мок $wpdb методов для status_log)

- [ ] **Step 1: Создать includes/lead-status-log.php**

```php
<?php
namespace LandingConfig\LeadStatusLog;

if (!defined('ABSPATH')) { exit; }

use function LandingConfig\DB\get_lead_status_log_table_name;
use function LandingConfig\LeadStatuses\resolve_lead_status;

/**
 * Записать изменение статуса в лог.
 * Возвращает id новой записи или 0 если to_status не валиден (нет в vocab).
 */
function log_status_change(int $lead_id, ?string $from_status, string $to_status, ?int $user_id, ?string $comment): int {
    global $wpdb;

    // Whitelist: to_status должен существовать в vocab текущего blog
    $vocab_match = resolve_lead_status($to_status, \get_current_blog_id());
    if ($vocab_match === null) {
        \error_log("[landing-config] log_status_change: invalid to_status='{$to_status}' for lead_id={$lead_id}");
        return 0;
    }

    $table = get_lead_status_log_table_name();
    $comment_value = ($comment === null || $comment === '') ? null : $comment;

    $data = [
        'lead_id'     => $lead_id,
        'user_id'     => $user_id,
        'from_status' => $from_status,
        'to_status'   => $to_status,
        'comment'     => $comment_value,
    ];
    $format = ['%d', $user_id === null ? null : '%d', $from_status === null ? null : '%s', '%s', $comment_value === null ? null : '%s'];

    $wpdb->insert($table, $data, $format);
    return (int) $wpdb->insert_id;
}

/** Получить историю изменений статуса заявки, отсортирована created_at desc. */
function get_status_history(int $lead_id): array {
    global $wpdb;
    $table = get_lead_status_log_table_name();
    $rows = $wpdb->get_results(
        $wpdb->prepare("SELECT * FROM `$table` WHERE lead_id = %d ORDER BY created_at DESC, id DESC", $lead_id),
        ARRAY_A
    );
    return is_array($rows) ? $rows : [];
}
```

- [ ] **Step 2: Расширить мок в wp-bootstrap.php**

Найди в `skills/wp-landing-config/tests/fixtures/wp-bootstrap.php` определение мок-класса `$wpdb` (поищи `class MockWpdb` или похожее). Добавь поддержку методов `insert($table, $data, $format)` и `get_results($sql, $output)` для таблицы status_log через массив `$GLOBALS['_mock_status_log']`.

Если мок уже умеет insert/get_results общим путём через массив-по-таблице — ничего не делать, твой тест уже работает.

Если нет — добавь минимальный мок только для нашей таблицы. Шаблон (адаптируй под существующий MockWpdb):

```php
// В MockWpdb::insert():
public function insert($table, $data, $format = null) {
    if (strpos($table, 'landing_lead_status_log') !== false) {
        $id = $GLOBALS['_mock_next_status_log_id']++;
        $data['id'] = $id;
        $data['created_at'] = $data['created_at'] ?? date('Y-m-d H:i:s');
        $GLOBALS['_mock_status_log'][] = $data;
        $this->insert_id = $id;
        return 1;
    }
    // ... существующая логика для других таблиц
}

// В MockWpdb::get_results():
public function get_results($sql, $output = OBJECT) {
    if (strpos($sql, 'landing_lead_status_log') !== false) {
        // Простой парсер: ищем WHERE lead_id = N через preg
        if (preg_match('/WHERE\s+lead_id\s*=\s*(\d+)/i', $sql, $m)) {
            $lead_id = (int) $m[1];
            $rows = array_values(array_filter($GLOBALS['_mock_status_log'] ?? [], fn($r) => (int) $r['lead_id'] === $lead_id));
        } else {
            $rows = $GLOBALS['_mock_status_log'] ?? [];
        }
        // Sort by created_at desc, id desc
        usort($rows, fn($a, $b) => ($b['created_at'] ?? '') <=> ($a['created_at'] ?? '') ?: ($b['id'] ?? 0) <=> ($a['id'] ?? 0));
        return $output === ARRAY_A ? $rows : array_map(fn($r) => (object) $r, $rows);
    }
    // ... существующая логика
}

// В MockWpdb::prepare():
public function prepare($sql, ...$args) {
    // Простая подстановка %d/%s/%f для теста
    $i = 0;
    return preg_replace_callback('/%[dsf]/', function($m) use (&$i, $args) {
        $v = $args[$i++] ?? '';
        return $m[0] === '%d' ? (int) $v : ($m[0] === '%f' ? (float) $v : "'" . addslashes($v) . "'");
    }, $sql);
}
```

**ВАЖНО:** если в bootstrap.php уже есть похожие методы, не дублируй — расширь существующие switch'и. Тест-таргет — `12 tests, 0 failures` через `php skills/wp-landing-config/tests/test_lead_status_log.php`.

- [ ] **Step 3: Подключить require в landing-config.php**

Найди строку:

```php
require_once LANDING_CONFIG_DIR . '/includes/lead-statuses.php';
```

Добавь сразу после:

```php
require_once LANDING_CONFIG_DIR . '/includes/lead-status-log.php';
```

- [ ] **Step 4: Запустить тест — должен пройти**

```bash
php skills/wp-landing-config/tests/test_lead_status_log.php
```

Ожидаемо: `12 tests, 0 failures`.

- [ ] **Step 5: Regression**

```bash
for t in skills/wp-landing-config/tests/test_*.php; do echo "=== $t ==="; php "$t" 2>&1 | tail -2; done
```

- [ ] **Step 6: Commit**

```bash
git add skills/wp-landing-config/tests/test_lead_status_log.php \
        skills/wp-landing-config/mu-plugin/landing-config/includes/lead-status-log.php \
        skills/wp-landing-config/mu-plugin/landing-config/includes/db.php \
        skills/wp-landing-config/mu-plugin/landing-config/landing-config.php \
        skills/wp-landing-config/tests/fixtures/wp-bootstrap.php
git commit -m "feat(wp-landing-config): B19.2 — landing_lead_status_log таблица + helpers

dbDelta создаёт per-blog wp_<bid>_landing_lead_status_log.
log_status_change валидирует to_status через resolve_lead_status (whitelist
из vocab). Пустой comment → NULL. user_id nullable для системных изменений.
get_status_history сортирует created_at desc.

12/12 tests: round-trip, sort, invalid status reject, null comment, null user.

Co-Authored-By: Claude Opus 4.7 (1M context) <noreply@anthropic.com>"
```

---

## Phase B19.3 — Network admin UI для словаря + readonly

**Цель:** Network admin страница редактирования словаря с селектором сегмента + readonly на subsite. Шаблон точно как `admin-cta.php` / `admin-integrations.php` из S2-A.3.

**Files:**
- Create: `skills/wp-landing-config/mu-plugin/landing-config/includes/admin-lead-statuses.php`
- Create: `skills/wp-landing-config/mu-plugin/landing-config/includes/admin-lead-statuses-readonly.php`
- Modify: `skills/wp-landing-config/mu-plugin/landing-config/landing-config.php` (2 require)

---

### Task B19.3.1: admin-lead-statuses.php (network admin)

**Files:**
- Create: `skills/wp-landing-config/mu-plugin/landing-config/includes/admin-lead-statuses.php`

- [ ] **Step 1: Создать файл**

```php
<?php
namespace LandingConfig\Admin\LeadStatuses;

if (!defined('ABSPATH')) { exit; }

use function LandingConfig\LeadStatuses\list_lead_statuses;
use function LandingConfig\LeadStatuses\resolve_lead_status;
use function LandingConfig\LeadStatuses\save_lead_status;
use function LandingConfig\LeadStatuses\delete_lead_status;
use function LandingConfig\LeadStatuses\get_lead_status;
use function LandingConfig\LeadStatuses\has_override;
use function LandingConfig\SegmentSelector\render as render_selector;
use function LandingConfig\SegmentSelector\current_from_request;

\add_action('network_admin_menu', function () {
    \add_submenu_page(
        'landing-config-network',
        'Статусы заявок',
        'Статусы заявок',
        'manage_network_options',
        'landing-config-network-lead-statuses',
        __NAMESPACE__ . '\\dispatch'
    );
});

\add_action('admin_post_landing_lead_status_save', __NAMESPACE__ . '\\handle_save');
\add_action('admin_post_landing_lead_status_delete', __NAMESPACE__ . '\\handle_delete');
\add_action('admin_post_landing_lead_status_delete_override', __NAMESPACE__ . '\\handle_delete_override');

function dispatch(): void {
    if (!\current_user_can('manage_network_options')) { \wp_die('Insufficient permissions', 403); }
    $segment = current_from_request();
    render_page($segment);
}

function render_page(int $segment): void {
    $main_id = \function_exists('get_main_site_id') ? \get_main_site_id() : 1;
    $blog_id = $segment === 0 ? $main_id : $segment;
    $list = list_lead_statuses($blog_id);
    ?>
    <div class="wrap">
        <h1>Статусы заявок</h1>
        <p>Словарь статусов для админки «Заявки». Сетевые статусы видны на всех сегментах;
        сегмент может переопределить статус по slug или добавить свой.</p>
        <?php render_selector('landing-config-network-lead-statuses', $segment); ?>

        <h2>Текущие статусы (отсортированы по order)</h2>
        <table class="wp-list-table widefat striped">
            <thead>
                <tr>
                    <th style="width:60px;">Цвет</th>
                    <th>Slug</th>
                    <th>Label</th>
                    <th style="width:80px;">Order</th>
                    <th style="width:120px;">Источник</th>
                    <th style="width:180px;">Действия</th>
                </tr>
            </thead>
            <tbody>
                <?php if (empty($list)): ?>
                    <tr><td colspan="6"><em>Нет статусов. Добавьте первый ниже.</em></td></tr>
                <?php else: foreach ($list as $s):
                    $is_site_row = !$s['is_network'];
                    $can_override = ($segment !== 0) && $s['is_network'] && !has_override($s['slug'], $segment);
                ?>
                    <tr>
                        <td><span style="display:inline-block; width:24px; height:24px; background:<?php echo \esc_attr($s['color']); ?>; border-radius:3px; border:1px solid #c3c4c7;"></span></td>
                        <td><code><?php echo \esc_html($s['slug']); ?></code></td>
                        <td><?php echo \esc_html($s['label']); ?></td>
                        <td><?php echo (int) $s['order']; ?></td>
                        <td>
                            <?php if ($s['is_network']): ?>
                                <span style="background:#2271b1; color:#fff; padding:2px 8px; border-radius:3px; font-size:11px;">NETWORK</span>
                            <?php else: ?>
                                <span style="background:#dba617; color:#fff; padding:2px 8px; border-radius:3px; font-size:11px;">SITE OVERRIDE</span>
                            <?php endif; ?>
                        </td>
                        <td>
                            <?php if (($segment === 0 && $s['is_network']) || ($segment !== 0 && $is_site_row)): ?>
                                <a href="#edit-<?php echo (int) $s['id']; ?>" class="button button-small" onclick="document.getElementById('edit-form-<?php echo (int) $s['id']; ?>').style.display='block'; return false;">Изменить</a>
                                <a href="<?php echo \esc_url(\wp_nonce_url(
                                    \network_admin_url('admin-post.php?action=landing_lead_status_delete&id=' . $s['id'] . '&segment=' . $segment),
                                    'landing_lead_status_delete_' . $s['id']
                                )); ?>" class="button button-small" onclick="return confirm('Удалить статус? Существующие заявки сохранят значение slug, но потеряют label/color.');">Удалить</a>
                            <?php elseif ($can_override): ?>
                                <a href="#override-<?php echo \esc_attr($s['slug']); ?>" class="button button-small" onclick="document.getElementById('override-form-<?php echo \esc_attr($s['slug']); ?>').style.display='block'; return false;">Override</a>
                            <?php endif; ?>
                        </td>
                    </tr>
                    <?php if (($segment === 0 && $s['is_network']) || ($segment !== 0 && $is_site_row)): ?>
                        <tr id="edit-form-<?php echo (int) $s['id']; ?>" style="display:none; background:#f6f7f7;">
                            <td colspan="6">
                                <?php render_edit_form($s, $segment); ?>
                            </td>
                        </tr>
                    <?php elseif ($can_override): ?>
                        <tr id="override-form-<?php echo \esc_attr($s['slug']); ?>" style="display:none; background:#fff8e5;">
                            <td colspan="6">
                                <p><strong>Создать site override для slug «<?php echo \esc_html($s['slug']); ?>».</strong> Изменения применятся только к этому сегменту.</p>
                                <?php render_edit_form(['id' => 0, 'slug' => $s['slug'], 'label' => $s['label'], 'color' => $s['color'], 'order' => $s['order']], $segment); ?>
                            </td>
                        </tr>
                    <?php endif; ?>
                <?php endforeach; endif; ?>
            </tbody>
        </table>

        <h2 style="margin-top:32px;">Добавить новый статус</h2>
        <?php render_edit_form(['id' => 0, 'slug' => '', 'label' => '', 'color' => '#2271b1', 'order' => 10], $segment); ?>
    </div>
    <?php
}

function render_edit_form(array $s, int $segment): void {
    ?>
    <form method="post" action="<?php echo \esc_url(\network_admin_url('admin-post.php')); ?>" style="background:#fff; padding:12px; border-radius:4px; border:1px solid #c3c4c7;">
        <?php \wp_nonce_field('landing_lead_status_save'); ?>
        <input type="hidden" name="action" value="landing_lead_status_save">
        <input type="hidden" name="id" value="<?php echo (int) $s['id']; ?>">
        <input type="hidden" name="segment" value="<?php echo (int) $segment; ?>">
        <table class="form-table">
            <tr><th>Slug</th><td><input type="text" name="slug" value="<?php echo \esc_attr($s['slug']); ?>" pattern="[a-z0-9_-]+" required class="regular-text"> <span class="description">a-z, 0-9, _, -. Например: <code>contacted</code>.</span></td></tr>
            <tr><th>Label</th><td><input type="text" name="label" value="<?php echo \esc_attr($s['label']); ?>" required class="regular-text"> <span class="description">Отображаемое название.</span></td></tr>
            <tr><th>Color</th><td><input type="color" name="color" value="<?php echo \esc_attr($s['color']); ?>"></td></tr>
            <tr><th>Order</th><td><input type="number" name="order" value="<?php echo (int) $s['order']; ?>" min="0" step="10" class="small-text"> <span class="description">Меньше = выше в списке.</span></td></tr>
        </table>
        <p><button type="submit" class="button button-primary">Сохранить</button></p>
    </form>
    <?php
}

function handle_save(): void {
    if (!\current_user_can('manage_network_options')) { \wp_die('No.', 403); }
    \check_admin_referer('landing_lead_status_save');

    $segment = (int) ($_POST['segment'] ?? 0);
    $is_network = ($segment === 0);
    $main_id = \function_exists('get_main_site_id') ? \get_main_site_id() : 1;
    $blog_id = $is_network ? $main_id : $segment;

    $id = save_lead_status([
        'slug'  => \sanitize_key($_POST['slug'] ?? ''),
        'label' => \sanitize_text_field($_POST['label'] ?? ''),
        'color' => (string) ($_POST['color'] ?? '#2271b1'),
        'order' => (int) ($_POST['order'] ?? 10),
    ], $is_network, $blog_id, (int) ($_POST['id'] ?? 0));

    if ($id === 0) {
        \wp_die('Не удалось сохранить статус. Проверь slug (a-z, 0-9, _, -).', 400);
    }

    \wp_safe_redirect(\network_admin_url('admin.php?page=landing-config-network-lead-statuses&segment=' . $segment . '&saved=1'));
    exit;
}

function handle_delete(): void {
    if (!\current_user_can('manage_network_options')) { \wp_die('No.', 403); }
    $id = (int) ($_GET['id'] ?? 0);
    if ($id <= 0) \wp_die('Invalid id', 400);
    \check_admin_referer('landing_lead_status_delete_' . $id);

    $segment = (int) ($_GET['segment'] ?? 0);
    delete_lead_status($id);

    \wp_safe_redirect(\network_admin_url('admin.php?page=landing-config-network-lead-statuses&segment=' . $segment . '&deleted=1'));
    exit;
}

function handle_delete_override(): void {
    if (!\current_user_can('manage_network_options')) { \wp_die('No.', 403); }
    \check_admin_referer('landing_lead_status_delete_override');

    $slug = \sanitize_key($_GET['slug'] ?? '');
    $segment = (int) ($_GET['segment'] ?? 0);
    if ($slug === '' || $segment === 0) \wp_die('Invalid', 400);

    foreach (list_lead_statuses($segment) as $s) {
        if ($s['slug'] === $slug && !$s['is_network']) {
            delete_lead_status($s['id']);
        }
    }
    \wp_safe_redirect(\network_admin_url('admin.php?page=landing-config-network-lead-statuses&segment=' . $segment));
    exit;
}
```

- [ ] **Step 2: Lint**

```bash
php -l skills/wp-landing-config/mu-plugin/landing-config/includes/admin-lead-statuses.php
```

---

### Task B19.3.2: admin-lead-statuses-readonly.php (subsite)

**Files:**
- Create: `skills/wp-landing-config/mu-plugin/landing-config/includes/admin-lead-statuses-readonly.php`

- [ ] **Step 1: Создать файл**

```php
<?php
namespace LandingConfig\Admin\LeadStatusesReadOnly;

if (!defined('ABSPATH')) { exit; }

use function LandingConfig\LeadStatuses\list_lead_statuses;
use function LandingConfig\LeadStatuses\has_override;

\add_action('admin_menu', function () {
    \add_submenu_page(
        'landing-config',
        'Статусы заявок (просмотр)',
        'Статусы заявок',
        'manage_options',
        'landing-config-lead-statuses',
        __NAMESPACE__ . '\\render_page'
    );
});

function render_page(): void {
    if (!\current_user_can('manage_options')) { \wp_die('No.', 403); }
    $blog_id = \get_current_blog_id();
    $net_url = \network_admin_url('admin.php?page=landing-config-network-lead-statuses&segment=' . $blog_id);
    $list = list_lead_statuses($blog_id);
    ?>
    <div class="wrap">
        <h1>Статусы заявок <span style="font-size:13px; color:#646970; font-weight:400;">— режим просмотра</span></h1>
        <div class="notice notice-info inline">
            <p>Словарь управляется super-admin'ом из network admin.
            <a href="<?php echo \esc_url($net_url); ?>" target="_blank">Открыть редактор</a> →</p>
        </div>

        <table class="wp-list-table widefat striped" style="margin-top:16px;">
            <thead>
                <tr><th style="width:60px;">Цвет</th><th>Slug</th><th>Label</th><th style="width:80px;">Order</th><th style="width:180px;">Источник</th></tr>
            </thead>
            <tbody>
                <?php if (empty($list)): ?>
                    <tr><td colspan="5"><em>Нет статусов. Попроси super-admin'а добавить.</em></td></tr>
                <?php else: foreach ($list as $s):
                    $is_override = !$s['is_network'];
                    $source = $is_override ? 'site override' : 'inherited from network';
                    $color = $is_override ? '#dba617' : '#2271b1';
                ?>
                    <tr>
                        <td><span style="display:inline-block; width:24px; height:24px; background:<?php echo \esc_attr($s['color']); ?>; border-radius:3px; border:1px solid #c3c4c7;"></span></td>
                        <td><code><?php echo \esc_html($s['slug']); ?></code></td>
                        <td><?php echo \esc_html($s['label']); ?></td>
                        <td><?php echo (int) $s['order']; ?></td>
                        <td><span style="background:<?php echo \esc_attr($color); ?>; color:#fff; padding:2px 8px; border-radius:3px; font-size:11px;"><?php echo \esc_html($source); ?></span></td>
                    </tr>
                <?php endforeach; endif; ?>
            </tbody>
        </table>
    </div>
    <?php
}
```

- [ ] **Step 2: Lint**

```bash
php -l skills/wp-landing-config/mu-plugin/landing-config/includes/admin-lead-statuses-readonly.php
```

- [ ] **Step 3: Подключить оба файла в landing-config.php**

В `skills/wp-landing-config/mu-plugin/landing-config/landing-config.php` найди:

```php
require_once LANDING_CONFIG_DIR . '/includes/admin-snippets-readonly.php';
```

Добавь сразу после:

```php
require_once LANDING_CONFIG_DIR . '/includes/admin-lead-statuses.php';
require_once LANDING_CONFIG_DIR . '/includes/admin-lead-statuses-readonly.php';
```

- [ ] **Step 4: Regression тестов**

```bash
for t in skills/wp-landing-config/tests/test_*.php; do echo "=== $t ==="; php "$t" 2>&1 | tail -2; done
```

- [ ] **Step 5: Commit**

```bash
git add skills/wp-landing-config/mu-plugin/landing-config/includes/admin-lead-statuses.php \
        skills/wp-landing-config/mu-plugin/landing-config/includes/admin-lead-statuses-readonly.php \
        skills/wp-landing-config/mu-plugin/landing-config/landing-config.php
git commit -m "feat(wp-landing-config): B19.3 — admin UI для словаря статусов (network + readonly)

Network admin: список статусов с цветным swatch, форма add/edit (slug/label/
color/order), кнопки delete и override-toggle. Form actions на network_admin_url.
3 admin_post handlers: save, delete, delete_override.

Subsite readonly: таблица эффективных статусов с источником inherited/site override
+ deep-link на network editor.

Co-Authored-By: Claude Opus 4.7 (1M context) <noreply@anthropic.com>"
```

- [ ] **Step 6: Deploy для liveness check**

```bash
bash skills/wp-landing-config/scripts/install-mu-plugin.sh /tmp/test-s2a
```

- [ ] **Step 7: Smoke — никаких фаталов**

```bash
ssh -i /c/Users/esper21/.ssh/beget_poc -o StrictHostKeyChecking=no esper21@esper21.beget.tech \
  "tail -30 /home/e/esper21/ailexi.ru/public_html/wp-content/debug.log 2>/dev/null | grep -E 'Fatal|TypeError' | tail -5 || echo 'no fatals'"
```

Ожидаемо: `no fatals` либо пусто. Если есть фатал — исправить и пересобрать.

---

## Phase B19.4 — Расширения admin-leads.php (табы + статус-колонка + checkbox + ссылка)

**Цель:** обновить существующий список заявок: subsubsub-табы, колонка статуса с бейджем, checkbox-колонка для bulk-action, кликабельная ссылка на карточку. Bulk-action handler — следующая фаза B19.6.

**Files:**
- Modify: `skills/wp-landing-config/mu-plugin/landing-config/includes/admin-leads.php`

---

### Task B19.4.1: Обновить render_page() в admin-leads.php

**Files:**
- Modify: `skills/wp-landing-config/mu-plugin/landing-config/includes/admin-leads.php`

- [ ] **Step 1: Backup**

```bash
cp skills/wp-landing-config/mu-plugin/landing-config/includes/admin-leads.php /tmp/admin-leads.bak.php
```

- [ ] **Step 2: Перепиши render_page() полностью**

Замени **содержимое** функции `render_page()` (от `function render_page(): void {` до закрывающей `}` функции, **не** трогая саму подпись) на это:

```php
function render_page(): void {
    if (!current_user_can('manage_options')) { wp_die('Insufficient permissions'); }

    if (isset($_GET['action']) && $_GET['action'] === 'export_csv'
        && check_admin_referer('landing_export_leads')) {
        export_csv();
        return;
    }

    global $wpdb;
    $table = get_leads_table_name();
    $per_page = 20;
    $page = max(1, (int)($_GET['paged'] ?? 1));
    $offset = ($page - 1) * $per_page;
    $blog_id = get_current_blog_id();

    // Filter: ?status=<slug> или ?status=all (default)
    $active_status = sanitize_key($_GET['status'] ?? 'all');

    // Counts по статусам — один SQL
    $count_rows = $wpdb->get_results("SELECT processed_status AS s, COUNT(*) AS n FROM `$table` GROUP BY processed_status", ARRAY_A);
    $counts_by_slug = [];
    $total = 0;
    foreach ($count_rows as $cr) {
        $counts_by_slug[(string) $cr['s']] = (int) $cr['n'];
        $total += (int) $cr['n'];
    }

    // WHERE clause для основной выборки
    if ($active_status === 'all') {
        $rows = $wpdb->get_results($wpdb->prepare(
            "SELECT * FROM `$table` ORDER BY created_at DESC LIMIT %d OFFSET %d",
            $per_page, $offset
        ), ARRAY_A);
        $filtered_total = $total;
    } else {
        $rows = $wpdb->get_results($wpdb->prepare(
            "SELECT * FROM `$table` WHERE processed_status = %s ORDER BY created_at DESC LIMIT %d OFFSET %d",
            $active_status, $per_page, $offset
        ), ARRAY_A);
        $filtered_total = $counts_by_slug[$active_status] ?? 0;
    }

    $vocab = \LandingConfig\LeadStatuses\list_lead_statuses($blog_id);
    $vocab_by_slug = [];
    foreach ($vocab as $v) $vocab_by_slug[$v['slug']] = $v;

    $export_url = wp_nonce_url(
        admin_url('admin.php?page=landing-config-leads&action=export_csv'),
        'landing_export_leads'
    );
    $base_url = admin_url('admin.php?page=landing-config-leads');
    ?>
    <div class="wrap">
        <h1>Заявки <a href="<?php echo esc_url($export_url); ?>" class="page-title-action">Экспорт CSV</a></h1>

        <ul class="subsubsub">
            <li>
                <a href="<?php echo esc_url(add_query_arg('status', 'all', $base_url)); ?>" class="<?php echo $active_status === 'all' ? 'current' : ''; ?>">
                    Все <span class="count">(<?php echo (int) $total; ?>)</span>
                </a>
            </li>
            <?php foreach ($vocab as $v):
                $n = (int) ($counts_by_slug[$v['slug']] ?? 0);
                $is_active = $active_status === $v['slug'];
            ?>
                | <li>
                    <a href="<?php echo esc_url(add_query_arg('status', $v['slug'], $base_url)); ?>" class="<?php echo $is_active ? 'current' : ''; ?>">
                        <?php echo esc_html($v['label']); ?> <span class="count">(<?php echo $n; ?>)</span>
                    </a>
                </li>
            <?php endforeach; ?>
        </ul>
        <div style="clear:both;"></div>

        <form method="post" action="<?php echo esc_url(admin_url('admin-post.php')); ?>">
            <?php wp_nonce_field('landing_leads_bulk_intent'); ?>
            <input type="hidden" name="action" value="landing_leads_bulk_intent">
            <input type="hidden" name="status" value="<?php echo esc_attr($active_status); ?>">

            <div class="tablenav top">
                <div class="alignleft actions bulkactions">
                    <select name="bulk_action">
                        <option value="">— Действие —</option>
                        <option value="change_status">Изменить статус…</option>
                    </select>
                    <button type="submit" class="button action">Применить</button>
                </div>
            </div>

            <table class="wp-list-table widefat striped">
                <thead>
                    <tr>
                        <td class="check-column"><input type="checkbox" id="cb-select-all"></td>
                        <th>ID</th><th>Дата</th><th>Имя</th><th>Телефон</th><th>Email</th>
                        <th>Статус</th>
                        <th>Сообщение</th><th>Источник</th><th>UTM</th>
                    </tr>
                </thead>
                <tbody>
                    <?php if (empty($rows)): ?>
                        <tr><td colspan="10"><em>Заявок нет.</em></td></tr>
                    <?php else: foreach ($rows as $r):
                        $status_slug = (string) ($r['processed_status'] ?? '');
                        $v = $vocab_by_slug[$status_slug] ?? null;
                        $badge_label = $v ? $v['label'] : ($status_slug !== '' ? $status_slug : '—');
                        $badge_color = $v ? $v['color'] : '#646970';
                        $badge_warn = $v ? '' : ' title="Статус не найден в vocab"';
                        $detail_url = admin_url('admin.php?page=landing-config-lead-detail&id=' . (int) $r['id']);
                    ?>
                        <tr>
                            <th scope="row" class="check-column"><input type="checkbox" name="lead_ids[]" value="<?php echo (int) $r['id']; ?>"></th>
                            <td><?php echo (int) $r['id']; ?></td>
                            <td><?php echo esc_html($r['created_at']); ?></td>
                            <td><a href="<?php echo esc_url($detail_url); ?>"><?php echo esc_html($r['name'] ?: '— без имени —'); ?></a></td>
                            <td><?php echo esc_html($r['phone']); ?></td>
                            <td><?php echo esc_html($r['email']); ?></td>
                            <td><span<?php echo $badge_warn; ?> style="background:<?php echo esc_attr($badge_color); ?>; color:#fff; padding:3px 10px; border-radius:3px; font-size:12px;"><?php echo esc_html($badge_label); ?></span></td>
                            <td><?php echo esc_html(mb_substr($r['message'] ?? '', 0, 60)); ?></td>
                            <td><?php echo esc_html($r['source_block']); ?></td>
                            <td><?php
                                $utm = array_filter([
                                    $r['utm_source'] ? "src={$r['utm_source']}" : '',
                                    $r['utm_medium'] ? "med={$r['utm_medium']}" : '',
                                    $r['utm_campaign'] ? "cmp={$r['utm_campaign']}" : '',
                                ]);
                                echo esc_html(implode(' ', $utm));
                            ?></td>
                        </tr>
                    <?php endforeach; endif; ?>
                </tbody>
            </table>

            <script>
            document.getElementById('cb-select-all')?.addEventListener('change', function() {
                document.querySelectorAll('input[name="lead_ids[]"]').forEach(cb => cb.checked = this.checked);
            });
            </script>
        </form>

        <?php
        $total_pages = (int) ceil($filtered_total / $per_page);
        if ($total_pages > 1) {
            echo '<div class="tablenav"><div class="tablenav-pages">';
            echo paginate_links([
                'base'      => add_query_arg('paged', '%#%'),
                'format'    => '',
                'total'     => $total_pages,
                'current'   => $page,
                'prev_text' => '‹',
                'next_text' => '›',
            ]);
            echo '</div></div>';
        }
        ?>
    </div>
    <?php
}
```

**Замечание:** добавил namespace-prefix `\LandingConfig\LeadStatuses\list_lead_statuses(...)` без `use function`, чтобы не возиться с импортами наверху файла (старый `admin-leads.php` импортирует только `get_leads_table_name`).

- [ ] **Step 3: Lint**

```bash
php -l skills/wp-landing-config/mu-plugin/landing-config/includes/admin-leads.php
```

- [ ] **Step 4: Regression тестов**

```bash
for t in skills/wp-landing-config/tests/test_*.php; do echo "=== $t ==="; php "$t" 2>&1 | tail -2; done
```

Ожидаемо: без изменений в pre-existing failures.

- [ ] **Step 5: Commit**

```bash
git add skills/wp-landing-config/mu-plugin/landing-config/includes/admin-leads.php
git commit -m "feat(wp-landing-config): B19.4 — admin-leads с табами по статусу и колонкой статуса

- Subsubsub-табы Все/<status_label>(N) сверху, фильтр через ?status=<slug>
- Один GROUP BY запрос для counts всех статусов
- Колонка 'Статус' с цветным бейджем из vocab (warning-стиль если slug
  не найден в vocab — например после удаления статуса)
- Колонка checkbox (через <th class=check-column>) + 'select all' toggle
- Колонка 'Имя' стала ссылкой на карточку заявки
- bulk-action form с dropdown 'Изменить статус...' + handler-intent
  (сам обработчик в B19.6)

Co-Authored-By: Claude Opus 4.7 (1M context) <noreply@anthropic.com>"
```

---

## Phase B19.5 — Карточка заявки + handler смены статуса

**Цель:** новая admin-страница `landing-config-lead-detail?id=N` с timeline истории, формой смены статуса в модалке, handler `landing_lead_change_status` с транзакцией.

**Files:**
- Create: `skills/wp-landing-config/mu-plugin/landing-config/includes/admin-lead-detail.php`
- Modify: `skills/wp-landing-config/mu-plugin/landing-config/landing-config.php`

---

### Task B19.5.1: admin-lead-detail.php (карточка + handler)

**Files:**
- Create: `skills/wp-landing-config/mu-plugin/landing-config/includes/admin-lead-detail.php`

- [ ] **Step 1: Создать файл**

```php
<?php
namespace LandingConfig\Admin\LeadDetail;

if (!defined('ABSPATH')) { exit; }

use function LandingConfig\DB\get_leads_table_name;
use function LandingConfig\LeadStatuses\list_lead_statuses;
use function LandingConfig\LeadStatuses\resolve_lead_status;
use function LandingConfig\LeadStatusLog\log_status_change;
use function LandingConfig\LeadStatusLog\get_status_history;

\add_action('admin_menu', function () {
    // parent=null + hidden slug — страница доступна по прямой ссылке, в меню не показываем
    \add_submenu_page(
        null,
        'Карточка заявки',
        'Карточка заявки',
        'manage_options',
        'landing-config-lead-detail',
        __NAMESPACE__ . '\\render_page'
    );
});

\add_action('admin_post_landing_lead_change_status', __NAMESPACE__ . '\\handle_change_status');

function render_page(): void {
    if (!\current_user_can('manage_options')) { \wp_die('No.', 403); }
    $lead_id = (int) ($_GET['id'] ?? 0);
    if ($lead_id <= 0) { \wp_die('Не указан id заявки.', 400); }

    global $wpdb;
    $table = get_leads_table_name();
    $lead = $wpdb->get_row($wpdb->prepare("SELECT * FROM `$table` WHERE id = %d", $lead_id), ARRAY_A);
    if (!$lead) { \wp_die('Заявка не найдена.', 404); }

    $blog_id = \get_current_blog_id();
    $current_slug = (string) ($lead['processed_status'] ?? '');
    $current_status = resolve_lead_status($current_slug, $blog_id);
    $vocab = list_lead_statuses($blog_id);
    $history = get_status_history($lead_id);
    $back_url = \admin_url('admin.php?page=landing-config-leads');
    ?>
    <div class="wrap">
        <h1>
            <a href="<?php echo \esc_url($back_url); ?>" class="page-title-action">← Назад к списку</a>
            Заявка #<?php echo (int) $lead_id; ?>
        </h1>

        <p style="margin:16px 0;">
            <strong>Текущий статус:</strong>
            <?php if ($current_status): ?>
                <span style="background:<?php echo \esc_attr($current_status['color']); ?>; color:#fff; padding:4px 14px; border-radius:3px; font-size:14px;">
                    <?php echo \esc_html($current_status['label']); ?>
                </span>
            <?php else: ?>
                <span style="background:#646970; color:#fff; padding:4px 14px; border-radius:3px; font-size:14px;" title="Статус не найден в vocab">
                    <?php echo \esc_html($current_slug ?: '—'); ?>
                </span>
            <?php endif; ?>
            <button type="button" class="button button-primary" style="margin-left:12px;" onclick="document.getElementById('change-status-modal').style.display='block'">
                Сменить статус
            </button>
        </p>

        <?php if (isset($_GET['saved'])): ?>
            <div class="notice notice-success is-dismissible"><p>Статус обновлён.</p></div>
        <?php endif; ?>

        <h2>Данные заявки</h2>
        <table class="form-table">
            <tr><th>Дата</th><td><?php echo \esc_html($lead['created_at']); ?></td></tr>
            <tr><th>Имя</th><td><?php echo \esc_html($lead['name'] ?: '—'); ?></td></tr>
            <tr><th>Телефон</th><td><?php echo \esc_html($lead['phone'] ?: '—'); ?></td></tr>
            <tr><th>Email</th><td><?php echo \esc_html($lead['email'] ?: '—'); ?></td></tr>
            <tr><th>Сообщение</th><td><?php echo nl2br(\esc_html($lead['message'] ?? '')); ?></td></tr>
            <tr><th>Источник</th><td><?php echo \esc_html($lead['source_block'] ?: '—'); ?></td></tr>
            <tr><th>UTM source</th><td><?php echo \esc_html($lead['utm_source'] ?: '—'); ?></td></tr>
            <tr><th>UTM medium</th><td><?php echo \esc_html($lead['utm_medium'] ?: '—'); ?></td></tr>
            <tr><th>UTM campaign</th><td><?php echo \esc_html($lead['utm_campaign'] ?: '—'); ?></td></tr>
            <tr><th>UTM term</th><td><?php echo \esc_html($lead['utm_term'] ?: '—'); ?></td></tr>
            <tr><th>UTM content</th><td><?php echo \esc_html($lead['utm_content'] ?: '—'); ?></td></tr>
            <tr><th>IP</th><td><code><?php echo \esc_html($lead['ip']); ?></code></td></tr>
            <tr><th>User agent</th><td><code style="font-size:11px;"><?php echo \esc_html($lead['user_agent'] ?? ''); ?></code></td></tr>
        </table>

        <h2 style="margin-top:32px;">История изменений</h2>
        <?php if (empty($history)): ?>
            <p style="color:#646970;"><em>Нет записей. Первая запись появится после первой смены статуса.</em></p>
        <?php else: ?>
            <table class="wp-list-table widefat striped">
                <thead>
                    <tr><th style="width:160px;">Когда</th><th style="width:180px;">Кто</th><th>Переход</th><th>Комментарий</th></tr>
                </thead>
                <tbody>
                    <?php foreach ($history as $h):
                        $user_label = $h['user_id'] ? (function() use ($h) {
                            $u = \get_userdata((int) $h['user_id']);
                            return $u ? $u->display_name : 'user#' . (int) $h['user_id'];
                        })() : '— системное —';
                        $from_v = $h['from_status'] ? resolve_lead_status((string) $h['from_status'], $blog_id) : null;
                        $to_v = resolve_lead_status((string) $h['to_status'], $blog_id);
                    ?>
                        <tr>
                            <td><?php echo \esc_html($h['created_at']); ?></td>
                            <td><?php echo \esc_html($user_label); ?></td>
                            <td>
                                <?php if ($from_v): ?>
                                    <span style="background:<?php echo \esc_attr($from_v['color']); ?>; color:#fff; padding:2px 8px; border-radius:3px; font-size:11px;"><?php echo \esc_html($from_v['label']); ?></span>
                                <?php elseif ($h['from_status']): ?>
                                    <code><?php echo \esc_html($h['from_status']); ?></code>
                                <?php else: ?>
                                    <em>— создана —</em>
                                <?php endif; ?>
                                →
                                <?php if ($to_v): ?>
                                    <span style="background:<?php echo \esc_attr($to_v['color']); ?>; color:#fff; padding:2px 8px; border-radius:3px; font-size:11px;"><?php echo \esc_html($to_v['label']); ?></span>
                                <?php else: ?>
                                    <code><?php echo \esc_html($h['to_status']); ?></code>
                                <?php endif; ?>
                            </td>
                            <td><?php echo nl2br(\esc_html($h['comment'] ?? '')); ?></td>
                        </tr>
                    <?php endforeach; ?>
                </tbody>
            </table>
        <?php endif; ?>

        <!-- Modal: смена статуса -->
        <div id="change-status-modal" style="display:none; position:fixed; top:0; left:0; right:0; bottom:0; background:rgba(0,0,0,0.5); z-index:9999;" onclick="if(event.target===this)this.style.display='none'">
            <div style="background:#fff; max-width:520px; margin:80px auto; padding:24px; border-radius:6px;">
                <h2 style="margin-top:0;">Сменить статус</h2>
                <form method="post" action="<?php echo \esc_url(\admin_url('admin-post.php')); ?>">
                    <?php \wp_nonce_field('landing_lead_change_status_' . $lead_id); ?>
                    <input type="hidden" name="action" value="landing_lead_change_status">
                    <input type="hidden" name="lead_id" value="<?php echo (int) $lead_id; ?>">
                    <p>
                        <label><strong>Новый статус:</strong></label><br>
                        <select name="to_status" required style="width:100%;">
                            <?php foreach ($vocab as $v): ?>
                                <option value="<?php echo \esc_attr($v['slug']); ?>" <?php \selected($v['slug'], $current_slug); ?>>
                                    <?php echo \esc_html($v['label']); ?>
                                </option>
                            <?php endforeach; ?>
                        </select>
                    </p>
                    <p>
                        <label><strong>Комментарий (опционально):</strong></label><br>
                        <textarea name="comment" rows="4" style="width:100%;" placeholder="Перезвонил, договорились на встречу в среду."></textarea>
                    </p>
                    <p>
                        <button type="submit" class="button button-primary">Сохранить</button>
                        <button type="button" class="button" onclick="document.getElementById('change-status-modal').style.display='none'">Отмена</button>
                    </p>
                </form>
            </div>
        </div>
    </div>
    <?php
}

function handle_change_status(): void {
    if (!\current_user_can('manage_options')) { \wp_die('No.', 403); }
    $lead_id = (int) ($_POST['lead_id'] ?? 0);
    if ($lead_id <= 0) \wp_die('Invalid lead_id', 400);
    \check_admin_referer('landing_lead_change_status_' . $lead_id);

    $to_status = \sanitize_key($_POST['to_status'] ?? '');
    $comment = \sanitize_textarea_field($_POST['comment'] ?? '');
    $blog_id = \get_current_blog_id();

    // Whitelist
    if (resolve_lead_status($to_status, $blog_id) === null) {
        \wp_die('Статус не существует в словаре.', 400);
    }

    global $wpdb;
    $table = get_leads_table_name();
    $current = $wpdb->get_var($wpdb->prepare("SELECT processed_status FROM `$table` WHERE id = %d", $lead_id));
    if ($current === null) \wp_die('Заявка не найдена.', 404);
    $from_status = (string) $current;

    // Транзакция: log + UPDATE
    $wpdb->query('START TRANSACTION');
    try {
        $log_id = log_status_change($lead_id, $from_status !== '' ? $from_status : null, $to_status, \get_current_user_id() ?: null, $comment !== '' ? $comment : null);
        if ($log_id === 0) {
            $wpdb->query('ROLLBACK');
            \wp_die('Не удалось записать историю.', 500);
        }
        $wpdb->update($table, ['processed_status' => $to_status], ['id' => $lead_id], ['%s'], ['%d']);
        $wpdb->query('COMMIT');
    } catch (\Throwable $e) {
        $wpdb->query('ROLLBACK');
        \error_log('[landing-config] handle_change_status failed: ' . $e->getMessage());
        \wp_die('Ошибка сохранения. Подробности в debug.log.', 500);
    }

    \wp_safe_redirect(\admin_url('admin.php?page=landing-config-lead-detail&id=' . $lead_id . '&saved=1'));
    exit;
}
```

- [ ] **Step 2: Lint**

```bash
php -l skills/wp-landing-config/mu-plugin/landing-config/includes/admin-lead-detail.php
```

- [ ] **Step 3: Подключить require в landing-config.php**

В `skills/wp-landing-config/mu-plugin/landing-config/landing-config.php` найди строку:

```php
require_once LANDING_CONFIG_DIR . '/includes/admin-lead-statuses-readonly.php';
```

Добавь сразу после:

```php
require_once LANDING_CONFIG_DIR . '/includes/admin-lead-detail.php';
```

- [ ] **Step 4: Regression**

```bash
for t in skills/wp-landing-config/tests/test_*.php; do echo "=== $t ==="; php "$t" 2>&1 | tail -2; done
```

- [ ] **Step 5: Commit**

```bash
git add skills/wp-landing-config/mu-plugin/landing-config/includes/admin-lead-detail.php \
        skills/wp-landing-config/mu-plugin/landing-config/landing-config.php
git commit -m "feat(wp-landing-config): B19.5 — карточка заявки + handler смены статуса

Скрытая admin-страница landing-config-lead-detail?id=N (доступ по прямой
ссылке из списка). Показывает: все поля заявки, текущий статус большим
бейджем, кнопку 'Сменить статус' открывающую модальное окно (select+
textarea), timeline истории с цветными бейджами from→to + комментариями.

handler landing_lead_change_status: cap → nonce → sanitize → whitelist
через resolve_lead_status → транзакция (log_status_change + UPDATE
landing_leads.processed_status) → redirect на ту же страницу с saved=1.

ROLLBACK в Throwable, fail-fast в wp_die при невалидном to_status.

Co-Authored-By: Claude Opus 4.7 (1M context) <noreply@anthropic.com>"
```

- [ ] **Step 6: Deploy и smoke**

```bash
bash skills/wp-landing-config/scripts/install-mu-plugin.sh /tmp/test-s2a
ssh -i /c/Users/esper21/.ssh/beget_poc -o StrictHostKeyChecking=no esper21@esper21.beget.tech \
  "tail -30 /home/e/esper21/ailexi.ru/public_html/wp-content/debug.log 2>/dev/null | grep -E 'Fatal|TypeError' | tail -5 || echo 'no fatals'"
```

Ожидаемо: `no fatals`. Файлы зарегистрированы на сервере.

---

## Phase B19.6 — Bulk-action handler

**Цель:** обработчики двух admin_post actions: `landing_leads_bulk_intent` (показ модалки выбора) и `landing_leads_bulk_status` (применение). Транзакции per-lead.

**Files:**
- Modify: `skills/wp-landing-config/mu-plugin/landing-config/includes/admin-leads.php` (добавить handlers + intent page)

---

### Task B19.6.1: Bulk intent + bulk apply handlers

**Files:**
- Modify: `skills/wp-landing-config/mu-plugin/landing-config/includes/admin-leads.php`

- [ ] **Step 1: Добавить use-импорт сверху файла**

В `skills/wp-landing-config/mu-plugin/landing-config/includes/admin-leads.php` найди:

```php
use function LandingConfig\DB\get_leads_table_name;
```

Замени на:

```php
use function LandingConfig\DB\get_leads_table_name;
use function LandingConfig\LeadStatuses\list_lead_statuses;
use function LandingConfig\LeadStatuses\resolve_lead_status;
use function LandingConfig\LeadStatusLog\log_status_change;
```

И **убери** namespace-prefix `\LandingConfig\LeadStatuses\list_lead_statuses` в `render_page()` если он там был — теперь имя импортировано.

- [ ] **Step 2: Зарегистрировать admin_post handlers**

После `add_action('admin_menu', ...)` блока добавь:

```php
add_action('admin_post_landing_leads_bulk_intent', __NAMESPACE__ . '\\handle_bulk_intent');
add_action('admin_post_landing_leads_bulk_status', __NAMESPACE__ . '\\handle_bulk_status');
```

- [ ] **Step 3: Реализовать handle_bulk_intent — показывает модалку выбора**

В конец того же файла (после `export_csv()`) добавь:

```php
function handle_bulk_intent(): void {
    if (!current_user_can('manage_options')) { wp_die('No.', 403); }
    check_admin_referer('landing_leads_bulk_intent');

    $bulk_action = sanitize_key($_POST['bulk_action'] ?? '');
    $lead_ids = array_map('intval', (array) ($_POST['lead_ids'] ?? []));
    $lead_ids = array_filter($lead_ids, fn($i) => $i > 0);
    $return_status = sanitize_key($_POST['status'] ?? 'all');

    if ($bulk_action !== 'change_status') {
        wp_safe_redirect(admin_url('admin.php?page=landing-config-leads&status=' . $return_status));
        exit;
    }
    if (empty($lead_ids)) {
        wp_safe_redirect(admin_url('admin.php?page=landing-config-leads&status=' . $return_status . '&bulk_error=no_selection'));
        exit;
    }

    $blog_id = get_current_blog_id();
    $vocab = list_lead_statuses($blog_id);
    $back_url = admin_url('admin.php?page=landing-config-leads&status=' . $return_status);
    ?>
    <div class="wrap">
        <h1>Массовая смена статуса</h1>
        <p>Выбрано заявок: <strong><?php echo count($lead_ids); ?></strong>. Выберите целевой статус и комментарий (опционально). Комментарий будет одинаковым у всех выбранных заявок в истории.</p>

        <form method="post" action="<?php echo esc_url(admin_url('admin-post.php')); ?>" style="background:#fff; padding:20px; border:1px solid #c3c4c7; border-radius:4px; max-width:600px;">
            <?php wp_nonce_field('landing_leads_bulk_status'); ?>
            <input type="hidden" name="action" value="landing_leads_bulk_status">
            <input type="hidden" name="return_status" value="<?php echo esc_attr($return_status); ?>">
            <?php foreach ($lead_ids as $id): ?>
                <input type="hidden" name="lead_ids[]" value="<?php echo (int) $id; ?>">
            <?php endforeach; ?>

            <p>
                <label><strong>Новый статус:</strong></label><br>
                <select name="to_status" required style="width:100%;">
                    <option value="">— Выберите —</option>
                    <?php foreach ($vocab as $v): ?>
                        <option value="<?php echo esc_attr($v['slug']); ?>"><?php echo esc_html($v['label']); ?></option>
                    <?php endforeach; ?>
                </select>
            </p>
            <p>
                <label><strong>Комментарий (опционально):</strong></label><br>
                <textarea name="comment" rows="3" style="width:100%;" placeholder="Массовая обработка ботов / повторных заявок / ..."></textarea>
            </p>
            <p>
                <button type="submit" class="button button-primary">Применить ко всем выбранным</button>
                <a href="<?php echo esc_url($back_url); ?>" class="button" style="margin-left:8px;">Отмена</a>
            </p>
        </form>
    </div>
    <?php
}

function handle_bulk_status(): void {
    if (!current_user_can('manage_options')) { wp_die('No.', 403); }
    check_admin_referer('landing_leads_bulk_status');

    $lead_ids = array_map('intval', (array) ($_POST['lead_ids'] ?? []));
    $lead_ids = array_filter($lead_ids, fn($i) => $i > 0);
    $to_status = sanitize_key($_POST['to_status'] ?? '');
    $comment = sanitize_textarea_field($_POST['comment'] ?? '');
    $return_status = sanitize_key($_POST['return_status'] ?? 'all');
    $blog_id = get_current_blog_id();

    if (empty($lead_ids) || $to_status === '') {
        wp_safe_redirect(admin_url('admin.php?page=landing-config-leads&status=' . $return_status . '&bulk_error=missing_params'));
        exit;
    }
    if (resolve_lead_status($to_status, $blog_id) === null) {
        wp_die('Статус не существует в словаре.', 400);
    }

    global $wpdb;
    $table = get_leads_table_name();
    $user_id = get_current_user_id() ?: null;
    $comment_value = $comment !== '' ? $comment : null;

    $updated = 0;
    $failed = 0;
    foreach ($lead_ids as $lid) {
        $current = $wpdb->get_var($wpdb->prepare("SELECT processed_status FROM `$table` WHERE id = %d", $lid));
        if ($current === null) { $failed++; continue; }
        $from_status = (string) $current;

        $wpdb->query('START TRANSACTION');
        try {
            $log_id = log_status_change($lid, $from_status !== '' ? $from_status : null, $to_status, $user_id, $comment_value);
            if ($log_id === 0) {
                $wpdb->query('ROLLBACK');
                $failed++;
                continue;
            }
            $wpdb->update($table, ['processed_status' => $to_status], ['id' => $lid], ['%s'], ['%d']);
            $wpdb->query('COMMIT');
            $updated++;
        } catch (\Throwable $e) {
            $wpdb->query('ROLLBACK');
            error_log('[landing-config] bulk_status lead_id=' . $lid . ' failed: ' . $e->getMessage());
            $failed++;
        }
    }

    $redirect = admin_url('admin.php?page=landing-config-leads&status=' . $return_status . '&bulk_updated=' . $updated . ($failed > 0 ? '&bulk_failed=' . $failed : ''));
    wp_safe_redirect($redirect);
    exit;
}
```

- [ ] **Step 4: Добавить отображение notice результата bulk в render_page**

В `render_page()` сразу после открывающего `<div class="wrap">` и перед `<h1>` добавь:

```php
<?php if (isset($_GET['bulk_updated'])): $updated = (int) $_GET['bulk_updated']; $failed = (int) ($_GET['bulk_failed'] ?? 0); ?>
    <div class="notice notice-success is-dismissible"><p>Обновлено заявок: <strong><?php echo $updated; ?></strong>. <?php if ($failed > 0): ?>Не удалось: <strong><?php echo $failed; ?></strong> (см. debug.log).<?php endif; ?></p></div>
<?php elseif (isset($_GET['bulk_error'])): ?>
    <div class="notice notice-error is-dismissible"><p>Ошибка: <code><?php echo esc_html((string) $_GET['bulk_error']); ?></code>. Проверь выбор заявок и параметры.</p></div>
<?php endif; ?>
```

- [ ] **Step 5: Lint**

```bash
php -l skills/wp-landing-config/mu-plugin/landing-config/includes/admin-leads.php
```

- [ ] **Step 6: Regression**

```bash
for t in skills/wp-landing-config/tests/test_*.php; do echo "=== $t ==="; php "$t" 2>&1 | tail -2; done
```

- [ ] **Step 7: Commit**

```bash
git add skills/wp-landing-config/mu-plugin/landing-config/includes/admin-leads.php
git commit -m "feat(wp-landing-config): B19.6 — bulk-action для смены статуса заявок

Два admin_post handler'а:
- landing_leads_bulk_intent: показывает страницу-форму с select статуса +
  textarea для общего комментария + hidden inputs со списком lead_ids
- landing_leads_bulk_status: применяет статус ко всем выбранным заявкам
  в цикле с per-lead START TRANSACTION/COMMIT/ROLLBACK. Один и тот же
  комментарий пишется в history каждой заявки.

Notice о результате (updated/failed) показывается в admin-leads после
redirect. Ошибки одной заявки не блокируют остальные.

Co-Authored-By: Claude Opus 4.7 (1M context) <noreply@anthropic.com>"
```

---

## Phase B19.7 — Seed-миграция, smoke, docs

**Цель:** на свежем сайте сразу видны 5 default-статусов в vocab; smoke-script расширен новыми проверками; CLAUDE.md обновлён.

**Files:**
- Modify: `skills/wp-landing-config/mu-plugin/landing-config/includes/migrate-to-s2a3.php`
- Modify: `skills/wp-landing-config/tests/test_migrate_to_s2a3.php`
- Modify: `skills/wp-landing-config/tests/integration/test_s2a3_smoke.sh`
- Modify: `CLAUDE.md`

---

### Task B19.7.1: Seed-функция + тест

**Files:**
- Modify: `skills/wp-landing-config/mu-plugin/landing-config/includes/migrate-to-s2a3.php`
- Modify: `skills/wp-landing-config/tests/test_migrate_to_s2a3.php`

- [ ] **Step 1: Добавить failing test**

В `skills/wp-landing-config/tests/test_migrate_to_s2a3.php` сразу перед `echo "$tests tests, $failures failures\n";` (последняя строка вывода) добавь:

```php
// T_SEED_1..3: seed_default_lead_statuses создаёт 5 default-статусов
require_once __DIR__ . '/../mu-plugin/landing-config/includes/lead-statuses.php';
use function LandingConfig\LeadStatuses\list_lead_statuses;
use function LandingConfig\Migrate\seed_default_lead_statuses;

reset_mig();
$seeded = seed_default_lead_statuses(1);
assert_test($seeded === 5, "T_SEED_1 seeded 5 statuses (got $seeded)");
$list = list_lead_statuses(1);
assert_test(count($list) === 5, 'T_SEED_2 5 records in vocab');
$slugs = array_column($list, 'slug');
assert_test(in_array('pending', $slugs) && in_array('won', $slugs) && in_array('spam', $slugs), 'T_SEED_3 contains pending/won/spam');

// T_SEED_4: idempotent — второй запуск 0
$again = seed_default_lead_statuses(1);
assert_test($again === 0, "T_SEED_4 idempotent (got $again)");
```

**Замечание:** `use function ...` нельзя писать в середине файла в PHP — поэтому перенеси оба `use function` в начало файла, где уже сгруппированы другие импорты.

- [ ] **Step 2: Запустить — упадёт**

```bash
php skills/wp-landing-config/tests/test_migrate_to_s2a3.php
```

Ожидаемо: `Fatal error: ... seed_default_lead_statuses not defined`.

- [ ] **Step 3: Добавить функцию в migrate-to-s2a3.php**

В `skills/wp-landing-config/mu-plugin/landing-config/includes/migrate-to-s2a3.php` найди конец файла, перед закрывающим `?>` (если есть) или просто в конец namespace-блока добавь:

```php
/**
 * Создать 5 default-статусов для свежего сайта (B19). Идемпотентно:
 * если хоть один статус уже есть — возвращает 0 без действий.
 */
function seed_default_lead_statuses(int $network_blog_id): int {
    $existing = \LandingConfig\LeadStatuses\list_lead_statuses($network_blog_id);
    if (!empty($existing)) return 0;

    $defaults = [
        ['slug' => 'pending',     'label' => 'Новая',            'color' => '#2271b1', 'order' => 10],
        ['slug' => 'in_progress', 'label' => 'В работе',         'color' => '#dba617', 'order' => 20],
        ['slug' => 'won',         'label' => 'Закрыта успешно',  'color' => '#00a32a', 'order' => 30],
        ['slug' => 'lost',        'label' => 'Отказ',            'color' => '#d63638', 'order' => 40],
        ['slug' => 'spam',        'label' => 'Спам',             'color' => '#646970', 'order' => 50],
    ];

    $count = 0;
    foreach ($defaults as $d) {
        $id = \LandingConfig\LeadStatuses\save_lead_status($d, true, $network_blog_id);
        if ($id > 0) $count++;
    }
    return $count;
}
```

- [ ] **Step 4: Вызвать seed в maybe_run()**

В той же `migrate-to-s2a3.php` найди функцию `maybe_run()`. Найди строку с `migrate_integrations_from_options($main);` (есть после A3.2.3) и добавь сразу после неё:

```php
    seed_default_lead_statuses($main);
```

- [ ] **Step 5: Запустить тест — должен пройти**

```bash
php skills/wp-landing-config/tests/test_migrate_to_s2a3.php
```

Ожидаемо: `17 tests, 0 failures` (13 предыдущих + 4 новых).

- [ ] **Step 6: Regression**

```bash
for t in skills/wp-landing-config/tests/test_*.php; do echo "=== $t ==="; php "$t" 2>&1 | tail -2; done
```

- [ ] **Step 7: Commit**

```bash
git add skills/wp-landing-config/tests/test_migrate_to_s2a3.php \
        skills/wp-landing-config/mu-plugin/landing-config/includes/migrate-to-s2a3.php
git commit -m "feat(wp-landing-config): B19.7 — seed 5 default-статусов в maybe_run

Идемпотентно. На свежем сайте админка 'Заявки' сразу получает рабочие
табы и dropdown. Маркетолог может переименовать/добавить/удалить — seed
повторно не сработает (проверка по непустому списку).

+4 теста (T_SEED_1..4) в test_migrate_to_s2a3.

Co-Authored-By: Claude Opus 4.7 (1M context) <noreply@anthropic.com>"
```

---

### Task B19.7.2: Расширить smoke-script + deploy + run

**Files:**
- Modify: `skills/wp-landing-config/tests/integration/test_s2a3_smoke.sh`

- [ ] **Step 1: Добавить новые ассерты в smoke**

В `skills/wp-landing-config/tests/integration/test_s2a3_smoke.sh` найди блок T4 (HTTP code на network admin страницах). В массив `for slug in ...` добавь `landing-config-network-lead-statuses`:

```bash
for slug in landing-config-network landing-config-network-cta landing-config-network-integrations landing-config-network-snippets landing-config-network-lead-statuses; do
```

Аналогично в блоке T5 (subsite) добавь `landing-config-lead-statuses`:

```bash
for slug in landing-config-cta landing-config-integrations landing-config-snippets landing-config-lead-statuses; do
```

И перед блоком T6 (debug.log) добавь новый блок T7:

```bash
echo "▶ T7: lp_lead_status CPT — seeded (count >= 5)"
ls=$($SSH "$WPCLI post list --post_type=lp_lead_status --url=http://ailexi.ru/ --format=count")
test "$ls" -ge 5 || { echo "FAIL: lp_lead_status count=$ls, expected >=5 (seed-migration)"; exit 1; }
echo "  OK ($ls records)"

echo "▶ T8: lead-detail URL liveness (id=1)"
code=$(curl -s -o /dev/null -w '%{http_code}' --max-time 10 "http://russian.ailexi.ru/wp-admin/admin.php?page=landing-config-lead-detail&id=1" || echo "000")
test "$code" = "200" -o "$code" = "302" -o "$code" = "404" || { echo "FAIL: lead-detail returned $code"; exit 1; }
echo "  OK lead-detail → $code (200/302/404 все ок — 404 если такого id нет)"
```

- [ ] **Step 2: Deploy на ailexi.ru**

```bash
bash skills/wp-landing-config/scripts/install-mu-plugin.sh /tmp/test-s2a
```

- [ ] **Step 3: Запустить smoke**

```bash
bash skills/wp-landing-config/tests/integration/test_s2a3_smoke.sh
```

Ожидаемо: `✅ S2-A.3 live smoke GREEN`. Все новые ассерты тоже GREEN. Если T7 падает с count=0 — значит `maybe_run()` не вызвался ещё (нужно открыть любой admin URL чтобы триггернуть init), либо marker уже стоит из A3.1.9 (тогда `seed_default_lead_statuses` НЕ вызовется — это known: на ailexi.ru `landing_config_migration_s2a3_cta` уже выставлен в '1'). В этом случае ручной триггер:

```bash
ssh -i /c/Users/esper21/.ssh/beget_poc -o StrictHostKeyChecking=no esper21@esper21.beget.tech \
  '/usr/local/bin/php8.3 /usr/local/bin/wp-cli.phar --path=/home/e/esper21/ailexi.ru/public_html eval "LandingConfig\\Migrate\\seed_default_lead_statuses(1);" --url=http://ailexi.ru/'
```

Это разовый ручной seed на уже-мигрированном сайте. На свежих установках seed сработает автоматически.

- [ ] **Step 4: Commit smoke-script**

```bash
git add skills/wp-landing-config/tests/integration/test_s2a3_smoke.sh
git commit -m "test(wp-landing-config): B19.7 — расширение smoke для lead-status

+T7 lp_lead_status CPT count >= 5 (после seed-миграции)
+T8 lead-detail URL liveness
Расширены T4/T5 двумя новыми admin slug'ами (network + readonly).

Co-Authored-By: Claude Opus 4.7 (1M context) <noreply@anthropic.com>"
```

---

### Task B19.7.3: Обновить CLAUDE.md

**Files:**
- Modify: `CLAUDE.md`

- [ ] **Step 1: Найти секцию S2-A.3**

В `CLAUDE.md` найди заголовок `### S2-A.3 — Network-Admin Unification (2026-05-20)`. После этого блока (там есть ссылки на spec и plan в конце) добавь:

```markdown

### S2-A.4 — Lead Status Workflow MVP (2026-05-20)

Маркетолог управляет статусами заявок через wp-admin:

- 4-я ось cascade S2-A.3: CPT `lp_lead_status` (slug/label/color/order) с network→site override
- Network admin → Статусы заявок: редактирование словаря с селектором сегмента
- На subsite: `Лендинг → Статусы заявок` — read-only список с deep-link на network editor
- Карточка заявки: `Лендинг → Заявки → клик по имени` → детальная страница с
  timeline истории и модальным окном смены статуса (select + textarea для комментария)
- Список заявок расширен: subsubsub-табы по статусу со счётчиками, колонка
  «Статус» с цветным бейджем, checkbox-колонка, bulk-action «Изменить статус»
- Per-blog таблица `wp_<bid>_landing_lead_status_log` (lead_id/user_id/from/to/
  comment/created_at) — полная история изменений с записью пользователя
- Транзакции per-lead в bulk-action: ошибка одной не блокирует остальные
- Seed 5 default-статусов в `maybe_run()`: pending/in_progress/won/lost/spam.
  Идемпотентно — если хоть один статус есть, не трогает.
- Whitelist валидации в двух местах: handler и `log_status_change` (через
  `resolve_lead_status` в vocab)

CRM sync (двусторонняя — webhook из CRM в админку и push из админки в CRM)
явно отложен на отдельный трек. Требует расширения AdapterInterface::update_status()
и тестов с реальными credentials всех 5 адаптеров.

См. [spec](docs/superpowers/specs/2026-05-20-b19-lead-status-workflow-design.md)
и [plan](docs/superpowers/plans/2026-05-20-b19-lead-status-workflow-plan.md).
```

- [ ] **Step 2: Commit**

```bash
git add CLAUDE.md
git commit -m "docs(b19): CLAUDE.md секция про Lead Status Workflow MVP (S2-A.4)

Зафиксирован 4-й CPT в cascade-архитектуре, карточка заявки с timeline,
расширения списка заявок (табы/колонка/bulk), per-blog таблица истории,
seed дефолтных статусов, deferred CRM sync.

Co-Authored-By: Claude Opus 4.7 (1M context) <noreply@anthropic.com>"
```

---

## Финальный шаг — финальный code review

После завершения всех 7 фаз — диспатч финального review по всему B19 (как было в S2-A.3). Проверки: cross-cutting consistency между файлами, security audit handlers, multisite correctness (хотя B19 — per-blog, не multisite в смысле switch_to_blog, но cascade vocab — multisite), backward compat (admin-leads.php старая логика сохранена для не-vocab statuses через warning-бейдж), test health, plan adherence.

После review — отчитаться пользователю что B19 готов, branch ready to merge.

---

## Self-Review плана

**1. Spec coverage** — каждый раздел спеки покрыт:
- §3.1 CPT — Phase B19.1
- §3.2 status_log таблица — Phase B19.2
- §4.1 Network admin UI — Phase B19.3
- §4.2 Subsite readonly — Phase B19.3
- §4.3 Карточка заявки — Phase B19.5
- §4.4 Расширения admin-leads — Phase B19.4 (списочные) + B19.6 (bulk handler)
- §4.5 Seed-миграция — Phase B19.7
- §5 Файлы — все 5 новых + 4 модификации присутствуют
- §6 Безопасность — cap/nonce/sanitize/whitelist во всех handlers
- §7 Тестирование — unit (B19.1, B19.2, B19.7.1) + smoke (B19.7.2)
- §8 Out-of-scope — не делаем CRM sync, FSM, кастомные статусы; явно прописано

**2. Placeholder scan** — TBD/TODO нет. Все шаги имеют точный код или точные команды.

**3. Type consistency:**
- `save_lead_status(array, bool, int, int=0): int` — одинаково в lead-statuses.php и handle_save в admin-lead-statuses.php
- `log_status_change(int, ?string, string, ?int, ?string): int` — одинаково в lead-status-log.php и в admin-lead-detail/admin-leads.php handlers
- `resolve_lead_status(string, int): ?array` — одинаково
- `list_lead_statuses(int): array` — одинаково
- Все константы slug/meta-keys из lead-statuses.php соответствуют сами себе

**4. Известный риск:** seed-миграция на ailexi.ru не сработает автоматически потому что marker `landing_config_migration_s2a3_cta` уже выставлен. План явно описывает ручной триггер через wp-cli в B19.7.2 Step 3 как fallback.

**5. Один граничный момент в B19.2 Step 2 (мок MockWpdb):** план говорит «найди MockWpdb в bootstrap.php и расширь». Если в bootstrap нет такого класса вообще (всё захардкожено через функции), implementer должен будет добавить базовый класс. Это нормальный escalation case, описан как «адаптируй под существующий MockWpdb» и тестируется через прогон test_lead_status_log.php — если падает, implementer чинит мок до зелёного.

План готов.
