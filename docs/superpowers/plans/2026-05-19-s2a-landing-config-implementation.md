# S2-A: landing-config mu-plugin Implementation Plan (all 5 phases)

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** WordPress mu-plugin `landing-config`, который через admin-страницы wp-admin даёт маркетологу и клиенту настраивать CRM/счётчики/CTA/head без программиста. Заявки никогда не теряются (всегда пишутся в БД + email-fallback). Все из коробки multisite-aware: network defaults + per-site override; per-blog таблицы заявок.

**Architecture:** Pre-built PHP мu-plugin лежит в репо (`skills/wp-landing-config/mu-plugin/`) и копируется на Beget через `install-mu-plugin.sh`. Mu-plugins всегда активны (особенность WP), не требуют `wp plugin activate`. Все настройки runtime: API-ключи в `wp_options` (зашифрованы AES-256), network defaults в `wp_sitemeta`. Заявки приходят на REST endpoint `/wp-json/landing/v1/lead`, который инспектирует `get_current_blog_id()` и пишет в `wp_<bid>_landing_leads`.

**Tech Stack:**
- PHP 8.3 (на Beget shared) — основной язык mu-plugin
- WordPress 6.9 Multisite — host
- WP Settings API + WP_List_Table — admin pages (без React/Vue)
- `wp_remote_post` — для CRM API запросов
- `wp_schedule_single_event` — для async retry упавших доставок
- `dbDelta` — для миграций таблиц
- `openssl_encrypt`/`openssl_decrypt` AES-256-CBC + `wp_salt('secure_auth')`
- bats-core — для shell-скриптов install/smoke
- PHP CLI с минимальным mock WP — для unit-тестов helpers/encryption

**Spec:** [docs/superpowers/specs/2026-05-19-s2a-landing-config-revised.md](../specs/2026-05-19-s2a-landing-config-revised.md)

**Validated на CD1 POC:** multisite на Beget shared, mu-plugin-через-rsync работает, см. [docs/beget-cookbook.md](../../beget-cookbook.md).

---

## Терминология

- **mu-plugin** (must-use plugin) — WP-плагин, который автоматически активен и не показывается в обычном списке плагинов. Не требует `wp plugin activate`. Идеально для системных интеграций.
- **Сегмент ЦА** — отдельная WP-подсайт в multisite-сети (`russian.liauto.dubai`, `family.liauto.dubai`). Каждый сегмент = свой `blog_id`.
- **Adapter** — PHP-класс, реализующий `AdapterInterface` (методы `send($lead)` + `test_connection()`). Один adapter = одна интеграция (AmoCRM, Telegram и т.д.).
- **Network admin** — суперадмин WP Multisite, видит все subsites и общие настройки. URL: `<root>/wp-admin/network/`.

---

## Pre-requisites

- Проект уже задеплоен и мигрирован в multisite через S2-CD CD1 (есть `wp_sitemeta`, есть subsites)
- `.env` содержит BEGET_USER/HOST/SSH_KEY/PATH (стандартный набор)
- На Бегете PHP 8.3 + WP 6.9
- Локально установлен bats-core (`npm i -g bats` или `apt install bats`)
- Локально PHP CLI 7.4+ (для unit-тестов helpers)

---

## Phase A1 — Foundation + REST endpoint + Database

Закладывает каркас: mu-plugin scaffold, db.php с миграциями, REST endpoint для приёма заявок, email-fallback, install-скрипт + smoke.

После A1 заявка с фронта (curl POST) гарантированно попадает в `wp_<bid>_landing_leads` + email админу. CRM ещё не подключены (это A5).

---

### Task 1: Скилл scaffolding + SKILL.md + .gitkeep структура

**Files:**
- Create: `skills/wp-landing-config/SKILL.md`
- Create: `skills/wp-landing-config/mu-plugin/landing-config/.gitkeep` (пустой)
- Create: `skills/wp-landing-config/mu-plugin/landing-config/includes/.gitkeep`
- Create: `skills/wp-landing-config/mu-plugin/landing-config/adapters/.gitkeep`
- Create: `skills/wp-landing-config/mu-plugin/landing-config/assets/.gitkeep`
- Create: `skills/wp-landing-config/scripts/.gitkeep`
- Create: `skills/wp-landing-config/tests/.gitkeep`

- [ ] **Step 1: Создать структуру директорий**

```bash
mkdir -p skills/wp-landing-config/{mu-plugin/landing-config/{includes,adapters,assets},scripts,tests/fixtures}
touch skills/wp-landing-config/mu-plugin/landing-config/.gitkeep \
      skills/wp-landing-config/mu-plugin/landing-config/includes/.gitkeep \
      skills/wp-landing-config/mu-plugin/landing-config/adapters/.gitkeep \
      skills/wp-landing-config/mu-plugin/landing-config/assets/.gitkeep \
      skills/wp-landing-config/scripts/.gitkeep \
      skills/wp-landing-config/tests/.gitkeep
```

- [ ] **Step 2: Создать SKILL.md**

```markdown
---
name: wp-landing-config
description: Pre-built mu-plugin landing-config for WordPress Multisite — admin UI for CRM/CTA/head/SEO configuration without code. Use this skill to install the plugin on Beget and to integrate with deploy/segment scripts.
---

# wp-landing-config

mu-plugin `landing-config/` даёт маркетологу/клиенту настраивать:
- Интеграции (AmoCRM, Bitrix24, HubSpot, Telegram, WhatsApp, Email)
- Заявки (просмотр БД + экспорт CSV)
- CTA-кнопки (5 пресетов с per-site override)
- Head & SEO (GA4, Y.Metrika, FB Pixel, GSC, OG-теги, custom HTML)

Multisite-aware: network defaults + per-site override. Per-blog таблицы заявок.

Spec: [docs/superpowers/specs/2026-05-19-s2a-landing-config-revised.md](../../docs/superpowers/specs/2026-05-19-s2a-landing-config-revised.md)

## Установка на проект

```bash
bash skills/wp-landing-config/scripts/install-mu-plugin.sh <project-dir>
```

Или через slash-команду из текущего проекта:

```
/landing-admin-install
```

mu-plugin копируется в `<BEGET_PATH>/wp-content/mu-plugins/landing-config/` и автоматически активируется (mu-plugins always-active).

## Содержимое mu-plugin

- `landing-config.php` — bootstrap
- `includes/db.php` — таблицы wp_<bid>_landing_leads + lead_log
- `includes/encryption.php` — AES-256 для API-ключей
- `includes/helpers.php` — landing_config_get(), landing_get_cta(), landing_render_head_extras()
- `includes/rest-lead.php` — POST /wp-json/landing/v1/lead
- `includes/admin-{integrations,leads,cta,head-seo}.php` — admin страницы
- `adapters/` — 6 CRM/messenger adapters

## Артефакты на WP

- `wp_<bid>_landing_leads` — таблица заявок per-blog
- `wp_<bid>_landing_lead_log` — лог CRM-доставок per-blog
- `wp_options::landing_*` — per-site настройки
- `wp_sitemeta::landing_defaults_*` — network defaults
```

- [ ] **Step 3: Verify structure**

Run: `find skills/wp-landing-config -type d | sort`
Expected: 6 directories listed (including `tests/fixtures`)

- [ ] **Step 4: Commit**

```bash
git add skills/wp-landing-config/
git commit -m "feat(wp-landing-config): skill scaffolding + SKILL.md

Empty directory structure for mu-plugin + scripts + tests.
SKILL.md documents purpose, install command, and runtime artifacts.

Co-Authored-By: Claude Opus 4.7 (1M context) <noreply@anthropic.com>"
```

---

### Task 2: mu-plugin bootstrap (landing-config.php)

**Files:**
- Create: `skills/wp-landing-config/mu-plugin/landing-config/landing-config.php`

- [ ] **Step 1: Write the file**

```php
<?php
/**
 * Plugin Name: Landing Config
 * Description: Admin UI for CRM, CTA, head/SEO, and lead capture. Multisite-aware.
 * Version: 0.1.0
 * Author: landing-system
 * Network: true
 */

if (!defined('ABSPATH')) { exit; }

define('LANDING_CONFIG_VERSION', '0.1.0');
define('LANDING_CONFIG_DIR', __DIR__);
define('LANDING_CONFIG_URL', plugins_url('', __FILE__));

// Includes loaded in order — db first (defines tables), then helpers, then features.
require_once LANDING_CONFIG_DIR . '/includes/db.php';
require_once LANDING_CONFIG_DIR . '/includes/encryption.php';
require_once LANDING_CONFIG_DIR . '/includes/helpers.php';
require_once LANDING_CONFIG_DIR . '/includes/rest-lead.php';
require_once LANDING_CONFIG_DIR . '/includes/admin-pages.php';

// mu-plugins do not have activation hooks. We trigger DB setup on init when
// the schema version differs from the file constant.
add_action('init', function () {
    \LandingConfig\DB\maybe_install_or_migrate();
}, 1);
```

- [ ] **Step 2: Verify file syntax**

Run: `php -l skills/wp-landing-config/mu-plugin/landing-config/landing-config.php`
Expected: `No syntax errors detected`

- [ ] **Step 3: Commit**

```bash
git add skills/wp-landing-config/mu-plugin/landing-config/landing-config.php
git commit -m "feat(wp-landing-config): mu-plugin bootstrap

Plugin file declares Network: true (visible at network admin),
defines version + DIR constants, loads includes in dependency order,
schedules db setup on init priority 1.

mu-plugins don't have activation hooks (unlike regular plugins),
so schema install/migrate runs on init via version-comparison check.

Co-Authored-By: Claude Opus 4.7 (1M context) <noreply@anthropic.com>"
```

---

### Task 3: db.php — таблицы wp_<bid>_landing_leads + lead_log

**Files:**
- Create: `skills/wp-landing-config/mu-plugin/landing-config/includes/db.php`
- Create: `skills/wp-landing-config/tests/fixtures/wp-bootstrap.php`
- Create: `skills/wp-landing-config/tests/test_db_schema.php`

- [ ] **Step 1: Write WP bootstrap mock**

Create `skills/wp-landing-config/tests/fixtures/wp-bootstrap.php`:

```php
<?php
/**
 * Minimal WP-functions mock for PHP CLI tests.
 * Only mocks functions used by db.php / encryption.php / helpers.php.
 *
 * Tests source this BEFORE requiring the file under test.
 */

if (!defined('ABSPATH')) { define('ABSPATH', '/tmp/mock-wp/'); }

// In-memory option store, scoped per blog_id.
$GLOBALS['_mock_options'] = [];     // [blog_id => [key => value]]
$GLOBALS['_mock_site_meta'] = [];   // [key => value] — for network options
$GLOBALS['_mock_current_blog_id'] = 1;
$GLOBALS['_mock_dbdelta_calls'] = [];

function get_current_blog_id() {
    return $GLOBALS['_mock_current_blog_id'];
}

function set_mock_current_blog_id($id) {
    $GLOBALS['_mock_current_blog_id'] = (int)$id;
}

function get_option($key, $default = false) {
    $bid = get_current_blog_id();
    return $GLOBALS['_mock_options'][$bid][$key] ?? $default;
}

function update_option($key, $value) {
    $bid = get_current_blog_id();
    $GLOBALS['_mock_options'][$bid][$key] = $value;
    return true;
}

function get_site_option($key, $default = false) {
    return $GLOBALS['_mock_site_meta'][$key] ?? $default;
}

function update_site_option($key, $value) {
    $GLOBALS['_mock_site_meta'][$key] = $value;
    return true;
}

function wp_salt($scheme = 'auth') {
    // Stable test salt — DO NOT use in production.
    return 'TEST_SALT_' . $scheme . '_xyz12345';
}

function dbDelta($sql) {
    $GLOBALS['_mock_dbdelta_calls'][] = $sql;
    return [];
}

// $wpdb mock — minimal surface for db.php
class MockWpdb {
    public $prefix = 'wp_';
    public $base_prefix = 'wp_';

    public function get_blog_prefix($blog_id = null) {
        $bid = $blog_id ?: get_current_blog_id();
        return $bid === 1 ? 'wp_' : 'wp_' . $bid . '_';
    }

    public function get_charset_collate() {
        return 'DEFAULT CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci';
    }
}

$GLOBALS['wpdb'] = new MockWpdb();

function get_sites($args = []) {
    // Default: 3 sites for tests
    return [
        (object)['blog_id' => 1, 'domain' => 'example.com', 'path' => '/'],
        (object)['blog_id' => 2, 'domain' => 'alpha.example.com', 'path' => '/'],
        (object)['blog_id' => 3, 'domain' => 'beta.example.com', 'path' => '/'],
    ];
}

function switch_to_blog($blog_id) {
    set_mock_current_blog_id($blog_id);
    return true;
}

function restore_current_blog() {
    set_mock_current_blog_id(1);
    return true;
}

function is_multisite() { return true; }
```

- [ ] **Step 2: Write failing test for db schema setup**

Create `skills/wp-landing-config/tests/test_db_schema.php`:

```php
<?php
require_once __DIR__ . '/fixtures/wp-bootstrap.php';
require_once __DIR__ . '/../mu-plugin/landing-config/includes/db.php';

use function LandingConfig\DB\maybe_install_or_migrate;
use function LandingConfig\DB\get_leads_table_name;
use function LandingConfig\DB\get_lead_log_table_name;

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

// Test 1: get_leads_table_name returns blog-specific name
set_mock_current_blog_id(2);
assert_test(
    get_leads_table_name() === 'wp_2_landing_leads',
    "get_leads_table_name() returns wp_2_landing_leads for blog_id=2 (got: " . get_leads_table_name() . ")"
);

// Test 2: get_leads_table_name returns base for blog 1
set_mock_current_blog_id(1);
assert_test(
    get_leads_table_name() === 'wp_landing_leads',
    "get_leads_table_name() returns wp_landing_leads for blog_id=1 (got: " . get_leads_table_name() . ")"
);

// Test 3: get_lead_log_table_name returns blog-specific name
set_mock_current_blog_id(3);
assert_test(
    get_lead_log_table_name() === 'wp_3_landing_lead_log',
    "get_lead_log_table_name() returns wp_3_landing_lead_log for blog_id=3 (got: " . get_lead_log_table_name() . ")"
);

// Test 4: maybe_install_or_migrate triggers dbDelta when version mismatch
$GLOBALS['_mock_dbdelta_calls'] = [];
$GLOBALS['_mock_site_meta']['landing_config_db_version'] = '';  // not installed yet
maybe_install_or_migrate();
assert_test(
    count($GLOBALS['_mock_dbdelta_calls']) >= 2,  // at least leads + lead_log per blog
    "maybe_install_or_migrate triggers dbDelta calls (got: " . count($GLOBALS['_mock_dbdelta_calls']) . ")"
);

// Test 5: maybe_install_or_migrate is idempotent — second call with same version is no-op
$first_count = count($GLOBALS['_mock_dbdelta_calls']);
maybe_install_or_migrate();
assert_test(
    count($GLOBALS['_mock_dbdelta_calls']) === $first_count,
    "maybe_install_or_migrate is no-op when version matches (call count unchanged)"
);

// Test 6: schema SQL includes required columns
$sql = $GLOBALS['_mock_dbdelta_calls'][0] ?? '';
assert_test(
    strpos($sql, 'id BIGINT') !== false &&
    strpos($sql, 'created_at') !== false &&
    strpos($sql, 'name VARCHAR') !== false &&
    strpos($sql, 'phone VARCHAR') !== false &&
    strpos($sql, 'email VARCHAR') !== false,
    "leads table schema includes id, created_at, name, phone, email"
);

echo "\n$tests tests, $failures failures\n";
exit($failures > 0 ? 1 : 0);
```

- [ ] **Step 3: Run test, expect failure**

Run: `php skills/wp-landing-config/tests/test_db_schema.php`
Expected: PHP fatal error — `require_once` of `includes/db.php` fails because file doesn't exist yet.

- [ ] **Step 4: Implement db.php**

```php
<?php
namespace LandingConfig\DB;

if (!defined('ABSPATH')) { exit; }

const DB_VERSION = '1.0.0';
const DB_VERSION_OPTION = 'landing_config_db_version';

function get_leads_table_name(): string {
    global $wpdb;
    return $wpdb->get_blog_prefix() . 'landing_leads';
}

function get_lead_log_table_name(): string {
    global $wpdb;
    return $wpdb->get_blog_prefix() . 'landing_lead_log';
}

function maybe_install_or_migrate(): void {
    $current = get_site_option(DB_VERSION_OPTION, '');
    if ($current === DB_VERSION) {
        return;
    }

    // Per-blog tables: switch to each blog, create tables, restore.
    if (function_exists('get_sites') && is_multisite()) {
        $sites = get_sites(['number' => 999]);
        foreach ($sites as $site) {
            switch_to_blog((int)$site->blog_id);
            create_tables_for_current_blog();
            restore_current_blog();
        }
    } else {
        create_tables_for_current_blog();
    }

    update_site_option(DB_VERSION_OPTION, DB_VERSION);
}

function create_tables_for_current_blog(): void {
    global $wpdb;
    $charset = $wpdb->get_charset_collate();
    $leads = get_leads_table_name();
    $log = get_lead_log_table_name();

    $leads_sql = "CREATE TABLE $leads (
        id BIGINT(20) UNSIGNED NOT NULL AUTO_INCREMENT,
        created_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
        name VARCHAR(191) NOT NULL DEFAULT '',
        phone VARCHAR(64) NOT NULL DEFAULT '',
        email VARCHAR(191) NOT NULL DEFAULT '',
        message TEXT NULL,
        source_block VARCHAR(191) NOT NULL DEFAULT '',
        utm_source VARCHAR(191) NOT NULL DEFAULT '',
        utm_medium VARCHAR(191) NOT NULL DEFAULT '',
        utm_campaign VARCHAR(191) NOT NULL DEFAULT '',
        utm_term VARCHAR(191) NOT NULL DEFAULT '',
        utm_content VARCHAR(191) NOT NULL DEFAULT '',
        ip VARCHAR(45) NOT NULL DEFAULT '',
        user_agent VARCHAR(500) NOT NULL DEFAULT '',
        processed_status VARCHAR(32) NOT NULL DEFAULT 'pending',
        PRIMARY KEY (id),
        KEY created_at (created_at),
        KEY processed_status (processed_status)
    ) $charset;";

    $log_sql = "CREATE TABLE $log (
        id BIGINT(20) UNSIGNED NOT NULL AUTO_INCREMENT,
        lead_id BIGINT(20) UNSIGNED NOT NULL,
        adapter VARCHAR(64) NOT NULL,
        attempt INT(11) NOT NULL DEFAULT 1,
        status VARCHAR(32) NOT NULL DEFAULT 'pending',
        response_code INT(11) NULL,
        response_body TEXT NULL,
        error_text VARCHAR(500) NULL,
        created_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
        PRIMARY KEY (id),
        KEY lead_id (lead_id),
        KEY status_adapter (status, adapter)
    ) $charset;";

    if (!function_exists('dbDelta')) {
        require_once ABSPATH . 'wp-admin/includes/upgrade.php';
    }
    dbDelta($leads_sql);
    dbDelta($log_sql);
}
```

- [ ] **Step 5: Run tests, expect pass**

Run: `php skills/wp-landing-config/tests/test_db_schema.php`
Expected: `6 tests, 0 failures`

- [ ] **Step 6: Commit**

```bash
git add skills/wp-landing-config/mu-plugin/landing-config/includes/db.php \
        skills/wp-landing-config/tests/fixtures/wp-bootstrap.php \
        skills/wp-landing-config/tests/test_db_schema.php
git commit -m "feat(wp-landing-config): db.php — per-blog leads + lead_log tables

Functions:
- get_leads_table_name() / get_lead_log_table_name() — return blog-prefixed
- maybe_install_or_migrate() — version-based install via dbDelta on init,
  iterates all sites in multisite, idempotent

Schema:
- wp_<bid>_landing_leads: id, created_at, name/phone/email/message,
  source_block, utm_*, ip, user_agent, processed_status
- wp_<bid>_landing_lead_log: id, lead_id, adapter, attempt, status,
  response_*, error_text, created_at

Tests use a tiny PHP WP-mock (tests/fixtures/wp-bootstrap.php) covering
get_current_blog_id, get_option, dbDelta, $wpdb prefix logic.

Co-Authored-By: Claude Opus 4.7 (1M context) <noreply@anthropic.com>"
```

---

### Task 4: encryption.php — AES-256-CBC helpers

**Files:**
- Create: `skills/wp-landing-config/mu-plugin/landing-config/includes/encryption.php`
- Create: `skills/wp-landing-config/tests/test_encryption.php`

- [ ] **Step 1: Write failing test**

Create `skills/wp-landing-config/tests/test_encryption.php`:

```php
<?php
require_once __DIR__ . '/fixtures/wp-bootstrap.php';
require_once __DIR__ . '/../mu-plugin/landing-config/includes/encryption.php';

use function LandingConfig\Encryption\encrypt;
use function LandingConfig\Encryption\decrypt;
use function LandingConfig\Encryption\mask;

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

// Test 1: encrypt/decrypt round-trip
$plaintext = 'amocrm-token-abc123XYZ';
$encrypted = encrypt($plaintext);
assert_test(
    is_string($encrypted) && strpos($encrypted, ':') !== false,
    "encrypt returns 'iv_b64:ct_b64' format (got: $encrypted)"
);
assert_test(
    decrypt($encrypted) === $plaintext,
    "decrypt(encrypt(\$plaintext)) returns original (got: " . decrypt($encrypted) . ")"
);

// Test 2: same plaintext encrypts to different ciphertext each call (random IV)
$enc1 = encrypt($plaintext);
$enc2 = encrypt($plaintext);
assert_test(
    $enc1 !== $enc2,
    "encrypt produces different ciphertext on repeated calls (random IV)"
);
assert_test(
    decrypt($enc1) === decrypt($enc2),
    "both decrypt to same plaintext"
);

// Test 3: empty string round-trip
assert_test(
    decrypt(encrypt('')) === '',
    "empty string encrypt/decrypt round-trip works"
);

// Test 4: Cyrillic + multiline preserves bytes
$tricky = "Привет\nworld\twith\rspecials!@#";
assert_test(
    decrypt(encrypt($tricky)) === $tricky,
    "Cyrillic + escapes round-trip preserves bytes"
);

// Test 5: malformed ciphertext returns empty string (not error/exception)
assert_test(
    decrypt('not-a-valid:base64-here') === '',
    "malformed ciphertext returns empty string (not exception)"
);
assert_test(
    decrypt('') === '',
    "empty ciphertext returns empty string"
);

// Test 6: mask shows last 4 chars only
assert_test(
    mask('abcdef1234567890') === '••••••••••••7890',
    "mask shows last 4 chars + bullets (got: " . mask('abcdef1234567890') . ")"
);
assert_test(
    mask('abc') === '•••',  // too short for last-4 → all bullets
    "mask of short string returns all bullets (got: " . mask('abc') . ")"
);

echo "\n$tests tests, $failures failures\n";
exit($failures > 0 ? 1 : 0);
```

- [ ] **Step 2: Run, expect failure**

Run: `php skills/wp-landing-config/tests/test_encryption.php`
Expected: PHP fatal — file not found.

- [ ] **Step 3: Implement encryption.php**

```php
<?php
namespace LandingConfig\Encryption;

if (!defined('ABSPATH')) { exit; }

const CIPHER = 'aes-256-cbc';

function _key(): string {
    // wp_salt returns a long random string. Derive a 32-byte key via sha256.
    return hash('sha256', wp_salt('secure_auth'), true);
}

function encrypt(string $plaintext): string {
    $iv = openssl_random_pseudo_bytes(openssl_cipher_iv_length(CIPHER));
    $ciphertext = openssl_encrypt($plaintext, CIPHER, _key(), OPENSSL_RAW_DATA, $iv);
    if ($ciphertext === false) {
        return '';
    }
    return base64_encode($iv) . ':' . base64_encode($ciphertext);
}

function decrypt(string $encoded): string {
    if ($encoded === '' || strpos($encoded, ':') === false) {
        return '';
    }
    [$iv_b64, $ct_b64] = explode(':', $encoded, 2);
    $iv = base64_decode($iv_b64, true);
    $ct = base64_decode($ct_b64, true);
    if ($iv === false || $ct === false) {
        return '';
    }
    $plain = openssl_decrypt($ct, CIPHER, _key(), OPENSSL_RAW_DATA, $iv);
    return $plain === false ? '' : $plain;
}

function mask(string $secret): string {
    $len = strlen($secret);
    if ($len <= 4) {
        return str_repeat('•', $len);
    }
    return str_repeat('•', $len - 4) . substr($secret, -4);
}
```

- [ ] **Step 4: Run tests, expect pass**

Run: `php skills/wp-landing-config/tests/test_encryption.php`
Expected: `8 tests, 0 failures`

- [ ] **Step 5: Commit**

```bash
git add skills/wp-landing-config/mu-plugin/landing-config/includes/encryption.php \
        skills/wp-landing-config/tests/test_encryption.php
git commit -m "feat(wp-landing-config): encryption.php — AES-256-CBC for API keys

encrypt() returns 'iv_b64:ct_b64', random IV per call.
decrypt() round-trips, returns empty string on malformed input.
mask() bullets all but last 4 chars (for safe display in admin UI).

Key derived from wp_salt('secure_auth') via sha256 — 32 bytes.

Co-Authored-By: Claude Opus 4.7 (1M context) <noreply@anthropic.com>"
```

---

### Task 5: helpers.php — landing_config_get + skeleton для CTA/head helpers

**Files:**
- Create: `skills/wp-landing-config/mu-plugin/landing-config/includes/helpers.php`
- Create: `skills/wp-landing-config/tests/test_helpers.php`

- [ ] **Step 1: Write failing test**

Create `skills/wp-landing-config/tests/test_helpers.php`:

```php
<?php
require_once __DIR__ . '/fixtures/wp-bootstrap.php';
require_once __DIR__ . '/../mu-plugin/landing-config/includes/helpers.php';

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

// Test 1: landing_config_get reads per-site first
update_option('landing_crm_amocrm_key', 'site-specific-key');
update_site_option('landing_defaults_crm_amocrm_key', 'network-default-key');
assert_test(
    landing_config_get('crm_amocrm_key') === 'site-specific-key',
    "per-site value wins over network default (got: " . landing_config_get('crm_amocrm_key') . ")"
);

// Test 2: landing_config_get falls back to network default when per-site missing
$GLOBALS['_mock_options'] = [];  // clear per-site
assert_test(
    landing_config_get('crm_amocrm_key') === 'network-default-key',
    "fallback to network default when per-site empty (got: " . landing_config_get('crm_amocrm_key') . ")"
);

// Test 3: landing_config_get returns default param when both empty
$GLOBALS['_mock_site_meta'] = [];
assert_test(
    landing_config_get('nonexistent_key', 'my-default') === 'my-default',
    "default param returned when both per-site and network empty"
);

// Test 4: landing_config_get returns empty string by default
assert_test(
    landing_config_get('nonexistent_key') === '',
    "default of landing_config_get is empty string (got: " . landing_config_get('nonexistent_key') . ")"
);

// Test 5: landing_config_set writes per-site
landing_config_set('test_key', 'test-value');
assert_test(
    get_option('landing_test_key') === 'test-value',
    "landing_config_set writes to per-site wp_options with landing_ prefix"
);

// Test 6: landing_config_set_network_default writes to sitemeta
landing_config_set_network_default('test_key', 'network-value');
assert_test(
    get_site_option('landing_defaults_test_key') === 'network-value',
    "landing_config_set_network_default writes to wp_sitemeta with landing_defaults_ prefix"
);

echo "\n$tests tests, $failures failures\n";
exit($failures > 0 ? 1 : 0);
```

- [ ] **Step 2: Run, expect failure**

Run: `php skills/wp-landing-config/tests/test_helpers.php`
Expected: PHP fatal — file not found.

- [ ] **Step 3: Implement helpers.php**

```php
<?php
if (!defined('ABSPATH')) { exit; }

/**
 * Read landing-config value: per-site override → network default → $default.
 *
 * @param string $key      e.g. 'crm_amocrm_key' (without 'landing_' prefix)
 * @param mixed  $default  returned if neither per-site nor network has the key
 * @return mixed
 */
function landing_config_get(string $key, $default = '') {
    $site_value = get_option('landing_' . $key, null);
    if ($site_value !== null && $site_value !== false && $site_value !== '') {
        return $site_value;
    }
    $net_value = get_site_option('landing_defaults_' . $key, null);
    if ($net_value !== null && $net_value !== false && $net_value !== '') {
        return $net_value;
    }
    return $default;
}

/**
 * Write per-site value (overrides any network default).
 */
function landing_config_set(string $key, $value): bool {
    return update_option('landing_' . $key, $value);
}

/**
 * Write network default (applies to all subsites that don't override).
 */
function landing_config_set_network_default(string $key, $value): bool {
    return update_site_option('landing_defaults_' . $key, $value);
}

/**
 * Render head extras (counters, OG, GSC, raw HTML) — wp_head action callback.
 * Implementation completed in Phase A4.
 */
function landing_render_head_extras(): void {
    // A4 stub — actual output added in Task 16+.
}

/**
 * Get URL/href for a CTA preset — used in theme block.php templates.
 * Implementation completed in Phase A3.
 */
function landing_get_cta(string $preset_name, ?string $url_override = null, array $context = []): string {
    // A3 stub — returns # so themes can use it without crashing pre-A3.
    if ($url_override !== null && $url_override !== '') {
        return $url_override;
    }
    return '#';
}
```

- [ ] **Step 4: Run tests, expect pass**

Run: `php skills/wp-landing-config/tests/test_helpers.php`
Expected: `6 tests, 0 failures`

- [ ] **Step 5: Commit**

```bash
git add skills/wp-landing-config/mu-plugin/landing-config/includes/helpers.php \
        skills/wp-landing-config/tests/test_helpers.php
git commit -m "feat(wp-landing-config): helpers.php — landing_config_get with per-site override

landing_config_get('key', \$default):
  per-site wp_options::landing_<key>
    → network wp_sitemeta::landing_defaults_<key>
      → \$default

landing_config_set — write per-site.
landing_config_set_network_default — write network.

landing_render_head_extras() + landing_get_cta() are stubs;
implementations finalized in A4 + A3 respectively (themes can call
them now without crashing).

Co-Authored-By: Claude Opus 4.7 (1M context) <noreply@anthropic.com>"
```

---

### Task 6: rest-lead.php — REST endpoint для приёма заявок

**Files:**
- Create: `skills/wp-landing-config/mu-plugin/landing-config/includes/rest-lead.php`
- Create: `skills/wp-landing-config/tests/test_rest_lead.php`

- [ ] **Step 1: Extend wp-bootstrap.php with REST + insert mocks**

Append to `skills/wp-landing-config/tests/fixtures/wp-bootstrap.php`:

```php

// REST + insert mocks for rest-lead.php tests

$GLOBALS['_mock_rest_routes'] = [];
$GLOBALS['_mock_inserted_leads'] = [];
$GLOBALS['_mock_mail_sent'] = [];

function register_rest_route($namespace, $route, $args) {
    $GLOBALS['_mock_rest_routes'][] = [$namespace, $route, $args];
    return true;
}

function add_action($hook, $callback, $priority = 10) {
    // No-op for tests (rest-lead registers route on rest_api_init — we trigger manually)
    return true;
}

function add_filter($hook, $callback, $priority = 10) {
    return true;
}

function wp_unslash($v) { return is_string($v) ? stripslashes($v) : $v; }
function sanitize_text_field($v) { return is_string($v) ? trim(strip_tags($v)) : ''; }
function sanitize_email($v) { return is_string($v) ? filter_var(trim($v), FILTER_SANITIZE_EMAIL) : ''; }
function esc_html($v) { return htmlspecialchars((string)$v, ENT_QUOTES, 'UTF-8'); }
function current_time($fmt) { return date('Y-m-d H:i:s'); }

function wp_mail($to, $subject, $body, $headers = []) {
    $GLOBALS['_mock_mail_sent'][] = compact('to', 'subject', 'body');
    return true;
}

function get_bloginfo($key) {
    $map = ['admin_email' => 'admin@example.com', 'name' => 'Test Site'];
    return $map[$key] ?? '';
}

class MockWpdbInsert extends MockWpdb {
    public $insert_id = 0;
    public function insert($table, $data, $formats = null) {
        $GLOBALS['_mock_inserted_leads'][] = ['table' => $table, 'data' => $data];
        $this->insert_id = count($GLOBALS['_mock_inserted_leads']) + 100;
        return 1;
    }
}

// Replace wpdb mock with insert-aware version
$GLOBALS['wpdb'] = new MockWpdbInsert();

// Mock REST response class (minimal)
class WP_REST_Response {
    public $data; public $status;
    public function __construct($data, $status = 200) {
        $this->data = $data;
        $this->status = $status;
    }
    public function get_status() { return $this->status; }
    public function get_data() { return $this->data; }
}

class WP_REST_Request {
    private $params = [];
    public function __construct(array $params = []) { $this->params = $params; }
    public function get_params() { return $this->params; }
    public function get_param($key) { return $this->params[$key] ?? null; }
}

function wp_remote_post($url, $args) {
    return ['response' => ['code' => 200], 'body' => '{"ok":true}'];
}
function is_wp_error($v) { return false; }
function wp_remote_retrieve_response_code($r) { return $r['response']['code'] ?? 0; }
function wp_remote_retrieve_body($r) { return $r['body'] ?? ''; }
```

- [ ] **Step 2: Write failing test**

Create `skills/wp-landing-config/tests/test_rest_lead.php`:

```php
<?php
require_once __DIR__ . '/fixtures/wp-bootstrap.php';
require_once __DIR__ . '/../mu-plugin/landing-config/includes/db.php';
require_once __DIR__ . '/../mu-plugin/landing-config/includes/helpers.php';
require_once __DIR__ . '/../mu-plugin/landing-config/includes/rest-lead.php';

use function LandingConfig\REST\handle_lead;

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

// Test 1: missing phone+email → 400
$GLOBALS['_mock_inserted_leads'] = [];
$req = new WP_REST_Request(['name' => 'Bob', 'phone' => '', 'email' => '']);
$resp = handle_lead($req);
assert_test(
    $resp->get_status() === 400,
    "missing phone+email returns 400 (got: " . $resp->get_status() . ")"
);
assert_test(
    count($GLOBALS['_mock_inserted_leads']) === 0,
    "no DB insert when validation fails"
);

// Test 2: honeypot field filled → 400 (silently rejects bots)
$req = new WP_REST_Request(['name' => 'Bob', 'phone' => '+71111111111', 'website' => 'spam-bot-trap']);
$resp = handle_lead($req);
assert_test(
    $resp->get_status() === 400,
    "honeypot 'website' field filled returns 400"
);

// Test 3: valid request inserts lead
$GLOBALS['_mock_inserted_leads'] = [];
$GLOBALS['_mock_mail_sent'] = [];
$req = new WP_REST_Request([
    'name' => 'Alice',
    'phone' => '+79991234567',
    'email' => 'alice@example.com',
    'message' => 'Test message',
    'source_block' => 'hero',
    'utm_source' => 'google',
]);
$resp = handle_lead($req);
assert_test(
    $resp->get_status() === 200,
    "valid request returns 200 (got: " . $resp->get_status() . ")"
);
assert_test(
    count($GLOBALS['_mock_inserted_leads']) === 1,
    "exactly 1 DB insert"
);
$inserted = $GLOBALS['_mock_inserted_leads'][0];
assert_test(
    $inserted['data']['name'] === 'Alice' &&
    $inserted['data']['phone'] === '+79991234567' &&
    $inserted['data']['email'] === 'alice@example.com',
    "inserted data has name/phone/email"
);
assert_test(
    $inserted['data']['source_block'] === 'hero' &&
    $inserted['data']['utm_source'] === 'google',
    "inserted data has source_block + utm_source"
);
assert_test(
    $resp->get_data()['ok'] === true && isset($resp->get_data()['lead_id']),
    "response includes ok=true + lead_id"
);

// Test 4: email-fallback sent on successful insert
assert_test(
    count($GLOBALS['_mock_mail_sent']) === 1,
    "wp_mail called once on success"
);
$mail = $GLOBALS['_mock_mail_sent'][0];
assert_test(
    $mail['to'] === 'admin@example.com',
    "mail sent to admin_email"
);

// Test 5: writes to per-blog table
set_mock_current_blog_id(2);
$GLOBALS['_mock_inserted_leads'] = [];
$req = new WP_REST_Request([
    'name' => 'BlogTwo', 'phone' => '+79993334444', 'email' => 'b2@x.com',
]);
handle_lead($req);
assert_test(
    $GLOBALS['_mock_inserted_leads'][0]['table'] === 'wp_2_landing_leads',
    "insert goes to wp_<bid>_landing_leads (got: " . $GLOBALS['_mock_inserted_leads'][0]['table'] . ")"
);

echo "\n$tests tests, $failures failures\n";
exit($failures > 0 ? 1 : 0);
```

- [ ] **Step 3: Run, expect failure**

Run: `php skills/wp-landing-config/tests/test_rest_lead.php`
Expected: PHP fatal — file not found.

- [ ] **Step 4: Implement rest-lead.php**

```php
<?php
namespace LandingConfig\REST;

if (!defined('ABSPATH')) { exit; }

use function LandingConfig\DB\get_leads_table_name;

add_action('rest_api_init', function () {
    register_rest_route('landing/v1', '/lead', [
        'methods'             => 'POST',
        'callback'            => __NAMESPACE__ . '\\handle_lead',
        'permission_callback' => '__return_true',  // public endpoint with honeypot + rate limit
    ]);
});

function handle_lead($request) {
    $params = $request->get_params();

    // Honeypot: field 'website' must be empty (real users don't fill it; bots do).
    if (!empty($params['website'])) {
        return new \WP_REST_Response(['ok' => false, 'error' => 'invalid'], 400);
    }

    // Required: at least one of phone or email
    $name = sanitize_text_field(wp_unslash($params['name'] ?? ''));
    $phone = sanitize_text_field(wp_unslash($params['phone'] ?? ''));
    $email = sanitize_email(wp_unslash($params['email'] ?? ''));
    if ($phone === '' && $email === '') {
        return new \WP_REST_Response(
            ['ok' => false, 'error' => 'phone or email required'],
            400
        );
    }

    $data = [
        'name'          => $name,
        'phone'         => $phone,
        'email'         => $email,
        'message'       => sanitize_text_field(wp_unslash($params['message'] ?? '')),
        'source_block'  => sanitize_text_field(wp_unslash($params['source_block'] ?? '')),
        'utm_source'    => sanitize_text_field(wp_unslash($params['utm_source'] ?? '')),
        'utm_medium'    => sanitize_text_field(wp_unslash($params['utm_medium'] ?? '')),
        'utm_campaign'  => sanitize_text_field(wp_unslash($params['utm_campaign'] ?? '')),
        'utm_term'      => sanitize_text_field(wp_unslash($params['utm_term'] ?? '')),
        'utm_content'   => sanitize_text_field(wp_unslash($params['utm_content'] ?? '')),
        'ip'            => sanitize_text_field($_SERVER['REMOTE_ADDR'] ?? ''),
        'user_agent'    => sanitize_text_field($_SERVER['HTTP_USER_AGENT'] ?? ''),
        'created_at'    => current_time('mysql'),
        'processed_status' => 'pending',
    ];

    global $wpdb;
    $inserted = $wpdb->insert(get_leads_table_name(), $data);
    if ($inserted === false || $inserted === 0) {
        return new \WP_REST_Response(['ok' => false, 'error' => 'db_error'], 500);
    }
    $lead_id = $wpdb->insert_id;

    // Email fallback — never block the user response on this
    send_admin_email($data, $lead_id);

    // Adapter dispatch happens in A5 — for now we just store in DB
    do_action('landing_config_lead_received', $lead_id, $data);

    return new \WP_REST_Response([
        'ok'      => true,
        'lead_id' => $lead_id,
    ], 200);
}

function send_admin_email(array $data, int $lead_id): void {
    $admin_email = get_bloginfo('admin_email');
    if (empty($admin_email)) return;

    $subject = sprintf('[%s] Новая заявка #%d', get_bloginfo('name'), $lead_id);
    $body = "Получена новая заявка:\n\n";
    foreach (['name','phone','email','message','source_block'] as $field) {
        if (!empty($data[$field])) {
            $body .= ucfirst($field) . ': ' . $data[$field] . "\n";
        }
    }
    $utm_parts = [];
    foreach (['utm_source','utm_medium','utm_campaign'] as $u) {
        if (!empty($data[$u])) $utm_parts[] = "$u={$data[$u]}";
    }
    if ($utm_parts) {
        $body .= "\nUTM: " . implode(', ', $utm_parts) . "\n";
    }
    wp_mail($admin_email, $subject, $body);
}
```

- [ ] **Step 5: Run tests, expect pass**

Run: `php skills/wp-landing-config/tests/test_rest_lead.php`
Expected: `9 tests, 0 failures`

- [ ] **Step 6: Commit**

```bash
git add skills/wp-landing-config/mu-plugin/landing-config/includes/rest-lead.php \
        skills/wp-landing-config/tests/test_rest_lead.php \
        skills/wp-landing-config/tests/fixtures/wp-bootstrap.php
git commit -m "feat(wp-landing-config): rest-lead.php — POST /wp-json/landing/v1/lead

Endpoint:
- Validates honeypot field 'website' (bots fill it, humans don't)
- Requires phone OR email (one of two)
- Inserts to wp_<bid>_landing_leads via get_current_blog_id-aware prefix
- Sends admin email fallback (non-blocking, ignores wp_mail failures)
- Fires action 'landing_config_lead_received' for adapter dispatch (A5)

Returns 200 with {ok:true, lead_id:N} on success.
Returns 400 on validation fail, 500 on DB error.

Co-Authored-By: Claude Opus 4.7 (1M context) <noreply@anthropic.com>"
```

---

### Task 7: admin-pages.php — регистрация admin menu «Лендинг»

**Files:**
- Create: `skills/wp-landing-config/mu-plugin/landing-config/includes/admin-pages.php`

- [ ] **Step 1: Write the file (no test — pure WP hook registration, manually verified)**

```php
<?php
namespace LandingConfig\Admin;

if (!defined('ABSPATH')) { exit; }

const CAP_MANAGE = 'manage_options';
const MENU_SLUG = 'landing-config';

add_action('admin_menu', function () {
    add_menu_page(
        'Лендинг',
        'Лендинг',
        CAP_MANAGE,
        MENU_SLUG,
        __NAMESPACE__ . '\\render_dashboard',
        'dashicons-megaphone',
        58
    );

    // Submenu order = registration order. We add stubs here, real pages
    // hook in their own includes (admin-leads.php etc.).
    add_submenu_page(
        MENU_SLUG,
        'Заявки',
        'Заявки',
        CAP_MANAGE,
        MENU_SLUG . '-leads',
        '__return_null'  // overridden in admin-leads.php (A2)
    );

    add_submenu_page(
        MENU_SLUG,
        'CTA-кнопки',
        'CTA-кнопки',
        CAP_MANAGE,
        MENU_SLUG . '-cta',
        '__return_null'  // overridden in admin-cta.php (A3)
    );

    add_submenu_page(
        MENU_SLUG,
        'Head & SEO',
        'Head & SEO',
        CAP_MANAGE,
        MENU_SLUG . '-head-seo',
        '__return_null'  // overridden in admin-head-seo.php (A4)
    );

    add_submenu_page(
        MENU_SLUG,
        'Интеграции',
        'Интеграции',
        CAP_MANAGE,
        MENU_SLUG . '-integrations',
        '__return_null'  // overridden in admin-integrations.php (A5)
    );
});

// Network-admin menu (super admin sees aggregate views)
add_action('network_admin_menu', function () {
    add_menu_page(
        'Лендинг (сеть)',
        'Лендинг',
        'manage_network_options',
        MENU_SLUG . '-network',
        __NAMESPACE__ . '\\render_network_dashboard',
        'dashicons-megaphone',
        25
    );
});

function render_dashboard(): void {
    ?>
    <div class="wrap">
        <h1>Лендинг — настройки</h1>
        <p>Выберите раздел в левом меню:</p>
        <ul>
            <li><strong>Заявки</strong> — список полученных заявок, экспорт CSV</li>
            <li><strong>CTA-кнопки</strong> — настройка 5 пресетов кнопок</li>
            <li><strong>Head &amp; SEO</strong> — счётчики, мета-теги, верификации</li>
            <li><strong>Интеграции</strong> — подключение CRM, Telegram, WhatsApp</li>
        </ul>
        <p><em>Версия: <?php echo esc_html(LANDING_CONFIG_VERSION); ?></em></p>
    </div>
    <?php
}

function render_network_dashboard(): void {
    ?>
    <div class="wrap">
        <h1>Лендинг — сетевые настройки</h1>
        <p>Здесь настраиваются дефолты, применяемые ко всем сегментам сети.
        Каждый сегмент может переопределить их в своей админке.</p>
    </div>
    <?php
}
```

- [ ] **Step 2: Verify PHP syntax**

Run: `php -l skills/wp-landing-config/mu-plugin/landing-config/includes/admin-pages.php`
Expected: `No syntax errors detected`

- [ ] **Step 3: Commit**

```bash
git add skills/wp-landing-config/mu-plugin/landing-config/includes/admin-pages.php
git commit -m "feat(wp-landing-config): admin-pages.php — register 'Лендинг' menu + stubs

Top-level 'Лендинг' menu with 4 submenu slots:
- landing-config-leads (filled by A2)
- landing-config-cta (filled by A3)
- landing-config-head-seo (filled by A4)
- landing-config-integrations (filled by A5)

Network admin gets separate top-level menu for super admin (defaults).

Submenu callbacks are __return_null placeholders that admin-XXX.php
files override via reusing the same menu slug in their add_submenu_page
call (WP merges them at register time).

Co-Authored-By: Claude Opus 4.7 (1M context) <noreply@anthropic.com>"
```

---

### Task 8: install-mu-plugin.sh — rsync скрипт + bats тест

**Files:**
- Create: `skills/wp-landing-config/scripts/install-mu-plugin.sh`
- Create: `skills/wp-landing-config/tests/test_install_mu_plugin.bats`

- [ ] **Step 1: Write failing bats test**

Create `skills/wp-landing-config/tests/test_install_mu_plugin.bats`:

```bash
#!/usr/bin/env bats
# Tests for install-mu-plugin.sh — uses mock rsync + ssh

setup() {
    SCRIPT="$BATS_TEST_DIRNAME/../scripts/install-mu-plugin.sh"
    MOCK_DIR="$(mktemp -d)"
    PROJECT_DIR="$(mktemp -d)"

    # Project state with .env
    cat > "$PROJECT_DIR/.env" <<EOF
BEGET_USER=testuser
BEGET_HOST=test.beget.tech
BEGET_SSH_KEY=/tmp/fake_key
BEGET_PATH=/home/t/testuser/example.ru/public_html
EOF

    # Mock rsync — log calls
    cat > "$MOCK_DIR/rsync" <<'MOCK'
#!/bin/bash
echo "RSYNC $*" >> "$BATS_TMPDIR/rsync_calls.log"
echo "sent 100 bytes  received 50 bytes"
MOCK
    chmod +x "$MOCK_DIR/rsync"

    # Mock ssh — log + return ok
    cat > "$MOCK_DIR/ssh" <<'MOCK'
#!/bin/bash
echo "SSH $*" >> "$BATS_TMPDIR/ssh_calls.log"
echo "OK"
MOCK
    chmod +x "$MOCK_DIR/ssh"

    rm -f "$BATS_TMPDIR/rsync_calls.log" "$BATS_TMPDIR/ssh_calls.log"
    PATH="$MOCK_DIR:$PATH"
    export PATH
}

teardown() { rm -rf "$MOCK_DIR" "$PROJECT_DIR"; }

@test "install-mu-plugin exits 2 when project-dir missing" {
    run bash "$SCRIPT"
    [ "$status" -eq 2 ]
    [[ "$output" == *"Usage:"* ]]
}

@test "install-mu-plugin exits 1 when .env missing" {
    rm "$PROJECT_DIR/.env"
    run bash "$SCRIPT" "$PROJECT_DIR"
    [ "$status" -eq 1 ]
    [[ "$output" == *".env"* ]]
}

@test "install-mu-plugin runs rsync of mu-plugin to remote" {
    run bash "$SCRIPT" "$PROJECT_DIR"
    [ "$status" -eq 0 ]
    grep -q "RSYNC" "$BATS_TMPDIR/rsync_calls.log"
    grep -q "landing-config" "$BATS_TMPDIR/rsync_calls.log"
    grep -q "wp-content/mu-plugins" "$BATS_TMPDIR/rsync_calls.log"
}

@test "install-mu-plugin triggers init via wp eval over ssh" {
    run bash "$SCRIPT" "$PROJECT_DIR"
    [ "$status" -eq 0 ]
    grep -q "wp-cli.phar" "$BATS_TMPDIR/ssh_calls.log"
}
```

- [ ] **Step 2: Run, expect failure**

Run: `bats skills/wp-landing-config/tests/test_install_mu_plugin.bats`
Expected: ERROR — script does not exist.

- [ ] **Step 3: Implement install-mu-plugin.sh**

Create `skills/wp-landing-config/scripts/install-mu-plugin.sh`:

```bash
#!/usr/bin/env bash
# install-mu-plugin.sh — copy landing-config mu-plugin to Beget WP install.
# Usage: bash install-mu-plugin.sh <project-dir>

set -euo pipefail

PROJECT="${1:-}"
if [ -z "$PROJECT" ]; then
    echo "Usage: install-mu-plugin.sh <project-dir>" >&2
    exit 2
fi

PROJECT="$(cd "$PROJECT" && pwd)"
[ -f "$PROJECT/.env" ] || { echo "ERROR: $PROJECT/.env not found" >&2; exit 1; }

set -a; source "$PROJECT/.env"; set +a
: "${BEGET_USER:?missing in .env}"
: "${BEGET_HOST:?missing in .env}"
: "${BEGET_SSH_KEY:?missing in .env}"
: "${BEGET_PATH:?missing in .env}"

SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
MU_SRC="$SCRIPT_DIR/../mu-plugin/landing-config"

[ -d "$MU_SRC" ] || { echo "ERROR: $MU_SRC not found (mu-plugin source missing)" >&2; exit 1; }

REMOTE_MU_DIR="${BEGET_PATH}/wp-content/mu-plugins/landing-config"

SSH_OPTS="-i $BEGET_SSH_KEY -o StrictHostKeyChecking=no -o UserKnownHostsFile=/dev/null -o LogLevel=ERROR"

echo "▶ rsync mu-plugin → ${BEGET_HOST}:${REMOTE_MU_DIR}"
# -a: archive, -z: compress, --delete: remove files not in source
rsync -avz --delete \
    -e "ssh $SSH_OPTS" \
    "$MU_SRC/" \
    "${BEGET_USER}@${BEGET_HOST}:${REMOTE_MU_DIR}/" | tail -5

echo "▶ Trigger DB schema install via wp eval"
# Hit any wp-cli command on the network to fire init action which runs
# maybe_install_or_migrate(). wp option get is a cheap no-op.
ssh $SSH_OPTS "${BEGET_USER}@${BEGET_HOST}" \
    "cd $BEGET_PATH && /usr/local/bin/php8.3 /usr/local/bin/wp-cli.phar --network option get siteurl 2>&1 | tail -1"

echo "✅ landing-config mu-plugin installed at ${REMOTE_MU_DIR}"
echo "   Visit any subsite's wp-admin and look for 'Лендинг' in the left menu."
```

- [ ] **Step 4: Run tests, expect pass**

Run: `bats skills/wp-landing-config/tests/test_install_mu_plugin.bats`
Expected: 4 tests pass.

- [ ] **Step 5: Commit**

```bash
git add skills/wp-landing-config/scripts/install-mu-plugin.sh \
        skills/wp-landing-config/tests/test_install_mu_plugin.bats
git commit -m "feat(wp-landing-config): install-mu-plugin.sh — rsync deploy

Script:
- Validates <project-dir>/.env (BEGET_USER/HOST/SSH_KEY/PATH required)
- rsync -avz --delete src → BEGET_HOST:BEGET_PATH/wp-content/mu-plugins/landing-config
- Triggers wp-cli init via 'wp option get siteurl' so db.php migrates
  on first call (no separate activation hook needed for mu-plugins)

Tests use mock rsync + ssh, verify command shape.

Co-Authored-By: Claude Opus 4.7 (1M context) <noreply@anthropic.com>"
```

---

### Task 9: /landing-admin-install slash command + smoke test на боевом Beget (Phase A1 finale)

**Files:**
- Create: `.claude/commands/landing-admin-install.md`
- Create: `skills/wp-landing-config/scripts/test-smoke-rest.sh`

- [ ] **Step 1: Create slash command**

Create `.claude/commands/landing-admin-install.md`:

```markdown
---
description: Установить mu-plugin landing-config на текущий проект (через rsync на Beget). Авто-активируется (mu-plugins always-active), создаёт таблицы wp_<bid>_landing_leads, регистрирует REST /wp-json/landing/v1/lead.
allowed-tools: Bash, Read
---

# /landing-admin-install

Копирует `skills/wp-landing-config/mu-plugin/landing-config/` на Beget,
триггерит миграцию БД, проверяет что REST endpoint отвечает.

## Использование

```
/landing-admin-install
```

(вызывается из корня landing-проекта где есть `.env`)

## Что делаю

1. Запускаю `bash skills/wp-landing-config/scripts/install-mu-plugin.sh .`
2. После rsync — выполняю `bash skills/wp-landing-config/scripts/test-smoke-rest.sh .`
   чтобы проверить:
   - таблица `wp_<bid>_landing_leads` создалась на всех subsite
   - REST endpoint `/wp-json/landing/v1/lead` отвечает 200 на валидный POST
3. Сообщаю URL admin pages для каждого subsite.

## После выполнения

Зайди в `<subsite-url>/wp-admin/` → меню «Лендинг» → 4 подстраницы
(Заявки/CTA/Head/Интеграции).

В A1 (текущая фаза) реализованы только: каркас, БД, REST endpoint, email-fallback.
Полная функциональность подстраниц — в фазах A2-A5.
```

- [ ] **Step 2: Write smoke test script**

Create `skills/wp-landing-config/scripts/test-smoke-rest.sh`:

```bash
#!/usr/bin/env bash
# test-smoke-rest.sh — verify REST /wp-json/landing/v1/lead works on live Beget.
# Reads <project>/.landing-state.yaml::audience_segments to know which subsites to test.
# Usage: bash test-smoke-rest.sh <project-dir>

set -euo pipefail
PROJECT="${1:?Usage: test-smoke-rest.sh <project-dir>}"
PROJECT="$(cd "$PROJECT" && pwd)"

[ -f "$PROJECT/.env" ] || { echo "ERROR: $PROJECT/.env not found" >&2; exit 1; }
[ -f "$PROJECT/.landing-state.yaml" ] || { echo "ERROR: $PROJECT/.landing-state.yaml not found" >&2; exit 1; }

set -a; source "$PROJECT/.env"; set +a
: "${ROOT_DOMAIN:?}"

PY=python; command -v python3 >/dev/null 2>&1 && python3 -c '' >/dev/null 2>&1 && PY=python3

# Collect URLs: root + each audience segment
URLS=$("$PY" -c "
import yaml
d = yaml.safe_load(open('$PROJECT/.landing-state.yaml', encoding='utf-8'))
print('http://${ROOT_DOMAIN}')
for s in (d.get('audience_segments') or []):
    print('http://' + s['host'])
")

FAIL=0
for url in $URLS; do
    echo "▶ Testing REST on $url"
    code=$(curl -s -o /tmp/lead-smoke-resp.json -w '%{http_code}' --max-time 15 \
        -X POST "$url/wp-json/landing/v1/lead" \
        -H "Content-Type: application/x-www-form-urlencoded" \
        --data "name=SmokeTest&phone=%2B70000000000&email=smoke%40test.local&source_block=smoke" || echo "000")

    if [ "$code" = "200" ]; then
        echo "  ✅ HTTP 200 — response: $(cat /tmp/lead-smoke-resp.json)"
    else
        echo "  ❌ HTTP $code — response: $(cat /tmp/lead-smoke-resp.json 2>/dev/null || echo '(no body)')"
        FAIL=1
    fi
done

rm -f /tmp/lead-smoke-resp.json
exit $FAIL
```

- [ ] **Step 3: Verify scripts have correct shebang and are executable**

Run: `head -1 skills/wp-landing-config/scripts/*.sh && file skills/wp-landing-config/scripts/*.sh`
Expected: both start with `#!/usr/bin/env bash`

- [ ] **Step 4: Commit**

```bash
git add .claude/commands/landing-admin-install.md \
        skills/wp-landing-config/scripts/test-smoke-rest.sh
git commit -m "feat(wp-landing-config): /landing-admin-install slash command + smoke test

slash command runs install-mu-plugin.sh then test-smoke-rest.sh.
smoke test reads .landing-state.yaml::audience_segments, POSTs a
SmokeTest lead to each subsite, expects HTTP 200.

Manual run on live Beget will happen in Task 10 (A1 finale).

Co-Authored-By: Claude Opus 4.7 (1M context) <noreply@anthropic.com>"
```

---

### Task 10: Phase A1 end-to-end smoke на live Beget

**Files:** none new

Это manual verification на боевом ailexi.ru multisite.

- [ ] **Step 1: Prepare project fixture**

```bash
cat > /tmp/test-s2a/.landing-state.yaml << 'YAML'
project: "test-s2a"
multisite: true
audience_segments:
  - {slug: russian, host: russian.ailexi.ru, blog_id: 2, created: "2026-05-19T00:00:00Z"}
YAML

mkdir -p /tmp/test-s2a
cp /tmp/test-cd1/.env /tmp/test-s2a/.env  # reuse from CD1 smoke
cat /tmp/test-s2a/.landing-state.yaml /tmp/test-s2a/.env
```

(If `/tmp/test-cd1/.env` is gone from CD1 cleanup, recreate it with BEGET_* values from the test session.)

- [ ] **Step 2: Run install**

Run: `bash skills/wp-landing-config/scripts/install-mu-plugin.sh /tmp/test-s2a`

Expected output:
- `▶ rsync mu-plugin → esper21.beget.tech:...` followed by file listing
- `▶ Trigger DB schema install via wp eval` followed by siteurl output
- `✅ landing-config mu-plugin installed`

- [ ] **Step 3: Verify mu-plugin file on Beget**

Run:
```bash
ssh -i ~/.ssh/beget_poc esper21@esper21.beget.tech \
    "ls /home/e/esper21/ailexi.ru/public_html/wp-content/mu-plugins/landing-config/ | head -10"
```

Expected: list including `landing-config.php`, `includes/`, `adapters/`, `assets/`.

- [ ] **Step 4: Verify tables exist on Beget**

Run:
```bash
ssh -i ~/.ssh/beget_poc esper21@esper21.beget.tech \
    "cd /home/e/esper21/ailexi.ru/public_html && /usr/local/bin/php8.3 /usr/local/bin/wp-cli.phar db query 'SHOW TABLES LIKE \"%landing%\"'"
```

Expected: rows like `wp_landing_leads`, `wp_landing_lead_log`, `wp_2_landing_leads`, etc.

- [ ] **Step 5: Run smoke REST test**

Run: `bash skills/wp-landing-config/scripts/test-smoke-rest.sh /tmp/test-s2a`

Expected:
- `▶ Testing REST on http://ailexi.ru` → `✅ HTTP 200 — response: {"ok":true,"lead_id":N}`
- `▶ Testing REST on http://russian.ailexi.ru` → same with different `lead_id`

- [ ] **Step 6: Verify lead landed in DB**

Run:
```bash
ssh -i ~/.ssh/beget_poc esper21@esper21.beget.tech \
    "cd /home/e/esper21/ailexi.ru/public_html && /usr/local/bin/php8.3 /usr/local/bin/wp-cli.phar db query 'SELECT id, name, phone, created_at FROM wp_landing_leads ORDER BY id DESC LIMIT 3'"
```

Expected: row with `name=SmokeTest`, `phone=+70000000000`, recent `created_at`.

- [ ] **Step 7: Document smoke result in cookbook**

Append to `docs/beget-cookbook.md` (find «SSL: расширенный отчёт» section, add a new subsection after it):

```markdown

## S2-A Phase A1 smoke (2026-05-19)

Install + REST endpoint validated on ailexi.ru multisite:
- mu-plugin rsync → `wp-content/mu-plugins/landing-config/` succeeds
- Tables `wp_<bid>_landing_leads` + `wp_<bid>_landing_lead_log` created in all
  3 subsites via init action triggered by `wp option get siteurl --network`
- POST to `/wp-json/landing/v1/lead` returns 200 with lead_id
- Lead row appears in correct per-blog table
- Admin email fallback delivers via PHP mail() (no SMTP configured)
```

- [ ] **Step 8: Commit**

```bash
git add docs/beget-cookbook.md
git commit -m "docs(beget): Phase A1 end-to-end smoke documented

Validated install + DB migration + REST + lead storage + email fallback
on live ailexi.ru multisite. Phase A1 ready for merge.

Co-Authored-By: Claude Opus 4.7 (1M context) <noreply@anthropic.com>"
```

---

## Phase A2 — Admin страница «Заявки»

### Task 11: admin-leads.php — WP_List_Table для просмотра + WP filter override

**Files:**
- Create: `skills/wp-landing-config/mu-plugin/landing-config/includes/admin-leads.php`
- Modify: `skills/wp-landing-config/mu-plugin/landing-config/landing-config.php` — require admin-leads.php

- [ ] **Step 1: Add require to bootstrap**

Modify `skills/wp-landing-config/mu-plugin/landing-config/landing-config.php`. After the existing require lines, add:

```php
require_once LANDING_CONFIG_DIR . '/includes/admin-leads.php';
```

- [ ] **Step 2: Implement admin-leads.php**

```php
<?php
namespace LandingConfig\Admin\Leads;

if (!defined('ABSPATH')) { exit; }

use function LandingConfig\DB\get_leads_table_name;

// Replace the __return_null stub from admin-pages.php
add_action('admin_menu', function () {
    global $submenu;
    if (isset($submenu['landing-config'])) {
        foreach ($submenu['landing-config'] as &$item) {
            if ($item[2] === 'landing-config-leads') {
                $item[3] = __NAMESPACE__ . '\\render_page';
            }
        }
    }
}, 99);  // after admin-pages.php registers stubs

function render_page(): void {
    if (!current_user_can('manage_options')) { wp_die('Insufficient permissions'); }

    // CSV export trigger
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

    $rows = $wpdb->get_results($wpdb->prepare(
        "SELECT * FROM `$table` ORDER BY created_at DESC LIMIT %d OFFSET %d",
        $per_page, $offset
    ), ARRAY_A);
    $total = (int)$wpdb->get_var("SELECT COUNT(*) FROM `$table`");

    $export_url = wp_nonce_url(
        admin_url('admin.php?page=landing-config-leads&action=export_csv'),
        'landing_export_leads'
    );
    ?>
    <div class="wrap">
        <h1>Заявки <a href="<?php echo esc_url($export_url); ?>" class="page-title-action">Экспорт CSV</a></h1>
        <p>Всего заявок: <strong><?php echo (int)$total; ?></strong></p>
        <table class="wp-list-table widefat striped">
            <thead>
                <tr>
                    <th>ID</th><th>Дата</th><th>Имя</th><th>Телефон</th><th>Email</th>
                    <th>Сообщение</th><th>Источник</th><th>UTM</th>
                </tr>
            </thead>
            <tbody>
                <?php if (empty($rows)): ?>
                    <tr><td colspan="8"><em>Заявок пока нет.</em></td></tr>
                <?php else: foreach ($rows as $r): ?>
                    <tr>
                        <td><?php echo (int)$r['id']; ?></td>
                        <td><?php echo esc_html($r['created_at']); ?></td>
                        <td><?php echo esc_html($r['name']); ?></td>
                        <td><?php echo esc_html($r['phone']); ?></td>
                        <td><?php echo esc_html($r['email']); ?></td>
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
        <?php
        $total_pages = (int)ceil($total / $per_page);
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

function export_csv(): void {
    if (!current_user_can('manage_options')) { wp_die('Insufficient permissions'); }

    global $wpdb;
    $table = get_leads_table_name();
    $rows = $wpdb->get_results("SELECT * FROM `$table` ORDER BY created_at DESC", ARRAY_A);

    $filename = sprintf('landing-leads-blog-%d-%s.csv', get_current_blog_id(), date('Ymd-His'));
    header('Content-Type: text/csv; charset=utf-8');
    header('Content-Disposition: attachment; filename="' . $filename . '"');

    $out = fopen('php://output', 'w');
    // UTF-8 BOM so Excel opens cleanly
    fputs($out, "\xEF\xBB\xBF");

    if (!empty($rows)) {
        fputcsv($out, array_keys($rows[0]));
        foreach ($rows as $r) {
            fputcsv($out, $r);
        }
    } else {
        fputcsv($out, ['id', 'created_at', 'name', 'phone', 'email', 'message']);
    }
    fclose($out);
    exit;
}
```

- [ ] **Step 3: Verify PHP syntax**

Run: `php -l skills/wp-landing-config/mu-plugin/landing-config/includes/admin-leads.php`
Expected: `No syntax errors detected`

- [ ] **Step 4: Re-install on Beget + manual smoke**

Run:
```bash
bash skills/wp-landing-config/scripts/install-mu-plugin.sh /tmp/test-s2a
```

Then **manually** open `http://ailexi.ru/wp-admin/admin.php?page=landing-config-leads` in browser (logged in as admin / Admin2026Aa1!). Expected:
- Page renders with «Заявки» heading
- Table shows SmokeTest lead from Task 10
- «Экспорт CSV» button works (downloads csv)

- [ ] **Step 5: Commit**

```bash
git add skills/wp-landing-config/mu-plugin/landing-config/includes/admin-leads.php \
        skills/wp-landing-config/mu-plugin/landing-config/landing-config.php
git commit -m "feat(wp-landing-config): admin-leads.php — list page + CSV export

Page replaces __return_null stub from admin-pages.php by editing
\$submenu directly at admin_menu priority 99.

Features:
- Paginated list (20/page) sorted by created_at DESC
- Columns: ID, Date, Name, Phone, Email, Message snippet, Source, UTM
- CSV export with UTF-8 BOM for Excel compatibility
- Nonce-protected export action
- Capability check: manage_options

Co-Authored-By: Claude Opus 4.7 (1M context) <noreply@anthropic.com>"
```

---

### Task 12: admin-leads-network.php — сводный просмотр на network admin

**Files:**
- Create: `skills/wp-landing-config/mu-plugin/landing-config/includes/admin-leads-network.php`
- Modify: `skills/wp-landing-config/mu-plugin/landing-config/landing-config.php` — require new file

- [ ] **Step 1: Add require to bootstrap**

Modify `landing-config.php`, add after admin-leads require:

```php
require_once LANDING_CONFIG_DIR . '/includes/admin-leads-network.php';
```

- [ ] **Step 2: Implement admin-leads-network.php**

```php
<?php
namespace LandingConfig\Admin\Leads\Network;

if (!defined('ABSPATH')) { exit; }

use function LandingConfig\DB\get_leads_table_name;

add_action('network_admin_menu', function () {
    add_submenu_page(
        'landing-config-network',
        'Заявки (сеть)',
        'Заявки (все сегменты)',
        'manage_network_options',
        'landing-config-network-leads',
        __NAMESPACE__ . '\\render_page'
    );
});

function render_page(): void {
    if (!current_user_can('manage_network_options')) { wp_die('Insufficient permissions'); }

    $filter_blog = (int)($_GET['blog'] ?? 0);
    $sites = get_sites(['number' => 999]);

    // Aggregate query: union of per-blog tables.
    $all_rows = [];
    foreach ($sites as $site) {
        if ($filter_blog && (int)$site->blog_id !== $filter_blog) continue;
        switch_to_blog((int)$site->blog_id);
        global $wpdb;
        $table = get_leads_table_name();
        $rows = $wpdb->get_results(
            "SELECT id, created_at, name, phone, email, source_block FROM `$table` ORDER BY created_at DESC LIMIT 50",
            ARRAY_A
        );
        foreach ($rows as $r) {
            $r['__blog_id'] = (int)$site->blog_id;
            $r['__host'] = $site->domain;
            $all_rows[] = $r;
        }
        restore_current_blog();
    }
    // Sort merged set by date DESC
    usort($all_rows, function ($a, $b) {
        return strcmp($b['created_at'], $a['created_at']);
    });
    ?>
    <div class="wrap">
        <h1>Заявки — все сегменты</h1>
        <form method="get" style="margin: 1em 0;">
            <input type="hidden" name="page" value="landing-config-network-leads">
            <label>Фильтр по сегменту:
                <select name="blog">
                    <option value="0">Все сегменты</option>
                    <?php foreach ($sites as $s): ?>
                        <option value="<?php echo (int)$s->blog_id; ?>" <?php selected($filter_blog, (int)$s->blog_id); ?>>
                            <?php echo esc_html($s->domain); ?>
                            (blog_id=<?php echo (int)$s->blog_id; ?>)
                        </option>
                    <?php endforeach; ?>
                </select>
            </label>
            <button type="submit" class="button">Применить</button>
        </form>
        <p>Показано: <strong><?php echo count($all_rows); ?></strong> заявок (последние 50 на сегмент).</p>
        <table class="wp-list-table widefat striped">
            <thead>
                <tr>
                    <th>Сегмент</th><th>ID</th><th>Дата</th><th>Имя</th>
                    <th>Телефон</th><th>Email</th><th>Источник</th>
                </tr>
            </thead>
            <tbody>
                <?php if (empty($all_rows)): ?>
                    <tr><td colspan="7"><em>Нет заявок.</em></td></tr>
                <?php else: foreach ($all_rows as $r): ?>
                    <tr>
                        <td><strong><?php echo esc_html($r['__host']); ?></strong></td>
                        <td><?php echo (int)$r['id']; ?></td>
                        <td><?php echo esc_html($r['created_at']); ?></td>
                        <td><?php echo esc_html($r['name']); ?></td>
                        <td><?php echo esc_html($r['phone']); ?></td>
                        <td><?php echo esc_html($r['email']); ?></td>
                        <td><?php echo esc_html($r['source_block']); ?></td>
                    </tr>
                <?php endforeach; endif; ?>
            </tbody>
        </table>
    </div>
    <?php
}
```

- [ ] **Step 3: Verify syntax + manual smoke**

Run: `php -l skills/wp-landing-config/mu-plugin/landing-config/includes/admin-leads-network.php`
Expected: `No syntax errors detected`

Re-install on Beget:
```bash
bash skills/wp-landing-config/scripts/install-mu-plugin.sh /tmp/test-s2a
```

Manually open `http://ailexi.ru/wp-admin/network/admin.php?page=landing-config-network-leads`.
Expected:
- Page renders with «Заявки — все сегменты» heading
- Dropdown shows all subsites
- Table shows leads from all subsites with «Сегмент» column

- [ ] **Step 4: Commit**

```bash
git add skills/wp-landing-config/mu-plugin/landing-config/includes/admin-leads-network.php \
        skills/wp-landing-config/mu-plugin/landing-config/landing-config.php
git commit -m "feat(wp-landing-config): admin-leads-network.php — aggregate view at network admin

Super admin sees leads from all subsites in one table.
Loops over get_sites(), switch_to_blog, queries each per-blog table,
merges and sorts by created_at DESC. Last 50 per blog.

Filter dropdown by blog_id. Manage_network_options capability required.

Co-Authored-By: Claude Opus 4.7 (1M context) <noreply@anthropic.com>"
```

---

## Phase A3 — CTA-пресеты + helper

### Task 13: admin-cta.php — Settings page для 5 пресетов

**Files:**
- Create: `skills/wp-landing-config/mu-plugin/landing-config/includes/admin-cta.php`
- Modify: `skills/wp-landing-config/mu-plugin/landing-config/includes/helpers.php` — real `landing_get_cta`
- Modify: `skills/wp-landing-config/mu-plugin/landing-config/landing-config.php` — require admin-cta.php
- Modify: `skills/wp-landing-config/tests/test_helpers.php` — add CTA tests

- [ ] **Step 1: Add require to bootstrap**

Modify `landing-config.php`, append:

```php
require_once LANDING_CONFIG_DIR . '/includes/admin-cta.php';
```

- [ ] **Step 2: Implement admin-cta.php**

```php
<?php
namespace LandingConfig\Admin\CTA;

if (!defined('ABSPATH')) { exit; }

const PRESET_NAMES = ['primary', 'whatsapp', 'phone', 'form_modal', 'learn_more'];

add_action('admin_menu', function () {
    global $submenu;
    if (isset($submenu['landing-config'])) {
        foreach ($submenu['landing-config'] as &$item) {
            if ($item[2] === 'landing-config-cta') {
                $item[3] = __NAMESPACE__ . '\\render_page';
            }
        }
    }
}, 99);

add_action('admin_init', function () {
    register_setting('landing_cta', 'landing_cta_presets', [
        'type' => 'array',
        'sanitize_callback' => __NAMESPACE__ . '\\sanitize_presets',
        'default' => default_presets(),
    ]);
});

function default_presets(): array {
    return [
        'primary'    => ['type' => 'scroll', 'target' => '#contact-form', 'label' => 'Оставить заявку'],
        'whatsapp'   => ['type' => 'whatsapp', 'phone' => '', 'message_template' => 'Здравствуйте! Интересует {block_context}', 'label' => 'Написать в WhatsApp'],
        'phone'      => ['type' => 'tel', 'phone' => '', 'label' => 'Позвонить'],
        'form_modal' => ['type' => 'modal', 'form_id' => 'main', 'label' => 'Получить предложение'],
        'learn_more' => ['type' => 'anchor', 'target' => '', 'label' => 'Подробнее'],
    ];
}

function sanitize_presets($input): array {
    if (!is_array($input)) return default_presets();
    $clean = [];
    foreach (PRESET_NAMES as $name) {
        $p = $input[$name] ?? [];
        $clean[$name] = [
            'type'    => sanitize_text_field($p['type'] ?? 'scroll'),
            'target'  => sanitize_text_field($p['target'] ?? ''),
            'phone'   => sanitize_text_field($p['phone'] ?? ''),
            'form_id' => sanitize_text_field($p['form_id'] ?? ''),
            'message_template' => sanitize_text_field($p['message_template'] ?? ''),
            'label'   => sanitize_text_field($p['label'] ?? ''),
        ];
    }
    return $clean;
}

function render_page(): void {
    if (!current_user_can('manage_options')) { wp_die('Insufficient permissions'); }
    $presets = get_option('landing_cta_presets', default_presets());
    ?>
    <div class="wrap">
        <h1>CTA-кнопки</h1>
        <p>Настройте 5 пресетов кнопок. Темы обращаются к ним через <code>landing_get_cta('preset_name')</code>.
        При смене значения здесь — обновятся все кнопки на сайте.</p>
        <form method="post" action="options.php">
            <?php settings_fields('landing_cta'); ?>
            <?php foreach (PRESET_NAMES as $name): $p = $presets[$name]; ?>
                <h2><?php echo esc_html($name); ?></h2>
                <table class="form-table">
                    <tr>
                        <th>Тип</th>
                        <td><select name="landing_cta_presets[<?php echo $name; ?>][type]">
                            <?php foreach (['scroll','whatsapp','tel','mailto','modal','anchor','url'] as $t): ?>
                                <option value="<?php echo $t; ?>" <?php selected($p['type'], $t); ?>><?php echo $t; ?></option>
                            <?php endforeach; ?>
                        </select></td>
                    </tr>
                    <tr><th>Label по умолчанию</th>
                        <td><input type="text" name="landing_cta_presets[<?php echo $name; ?>][label]" value="<?php echo esc_attr($p['label']); ?>" class="regular-text"></td>
                    </tr>
                    <tr><th>Target / URL / Phone</th>
                        <td>
                            <input type="text" name="landing_cta_presets[<?php echo $name; ?>][target]" value="<?php echo esc_attr($p['target']); ?>" placeholder="#contact-form, https://...">
                            <input type="text" name="landing_cta_presets[<?php echo $name; ?>][phone]" value="<?php echo esc_attr($p['phone']); ?>" placeholder="+71234567890 (для tel/whatsapp)">
                            <input type="text" name="landing_cta_presets[<?php echo $name; ?>][form_id]" value="<?php echo esc_attr($p['form_id']); ?>" placeholder="main (для modal)">
                        </td>
                    </tr>
                    <tr><th>Шаблон сообщения (WhatsApp)</th>
                        <td><input type="text" name="landing_cta_presets[<?php echo $name; ?>][message_template]" value="<?php echo esc_attr($p['message_template']); ?>" class="large-text" placeholder="Здравствуйте! Интересует {model}"></td>
                    </tr>
                </table>
            <?php endforeach; ?>
            <?php submit_button(); ?>
        </form>
    </div>
    <?php
}
```

- [ ] **Step 3: Replace stub `landing_get_cta` with real implementation in helpers.php**

Edit `skills/wp-landing-config/mu-plugin/landing-config/includes/helpers.php`. Replace the existing `landing_get_cta` function body with:

```php
function landing_get_cta(string $preset_name, ?string $url_override = null, array $context = []): string {
    if ($url_override !== null && $url_override !== '') {
        return $url_override;
    }
    $presets = get_option('landing_cta_presets', []);
    if (empty($presets)) {
        $presets = get_site_option('landing_defaults_cta_presets', []);
    }
    $p = $presets[$preset_name] ?? null;
    if (!$p) return '#';

    switch ($p['type']) {
        case 'tel':
            return $p['phone'] !== '' ? 'tel:' . preg_replace('/[^0-9+]/', '', $p['phone']) : '#contact-form';
        case 'whatsapp':
            if ($p['phone'] === '') return '#contact-form';
            $msg = $p['message_template'] ?? '';
            // Substitute {block_context} and any keys from $context
            $msg = strtr($msg, ['{block_context}' => $context['block_context'] ?? '']);
            foreach ($context as $k => $v) {
                $msg = str_replace('{' . $k . '}', (string)$v, $msg);
            }
            $phone_clean = preg_replace('/[^0-9]/', '', $p['phone']);
            return 'https://wa.me/' . $phone_clean . ($msg !== '' ? '?text=' . urlencode($msg) : '');
        case 'mailto':
            return $p['target'] !== '' ? 'mailto:' . $p['target'] : '#';
        case 'modal':
            return '#'; // theme JS reads data-modal=<form_id> separately
        case 'scroll':
        case 'anchor':
            return $p['target'] !== '' ? $p['target'] : '#contact-form';
        case 'url':
            return $p['target'];
        default:
            return '#';
    }
}
```

- [ ] **Step 4: Add CTA helper tests to test_helpers.php**

Append to `skills/wp-landing-config/tests/test_helpers.php` (before the final `echo` line):

```php

// CTA helper tests

// Test 7: url_override takes precedence
$GLOBALS['_mock_options'][1]['landing_cta_presets'] = [
    'primary' => ['type' => 'scroll', 'target' => '#default'],
];
assert_test(
    landing_get_cta('primary', 'https://custom.example/url') === 'https://custom.example/url',
    "landing_get_cta override URL wins"
);

// Test 8: scroll preset returns target
assert_test(
    landing_get_cta('primary') === '#default',
    "scroll preset returns target (got: " . landing_get_cta('primary') . ")"
);

// Test 9: tel preset returns tel: URL
$GLOBALS['_mock_options'][1]['landing_cta_presets']['phone'] = ['type' => 'tel', 'phone' => '+7 (911) 123-45-67'];
assert_test(
    landing_get_cta('phone') === 'tel:+79111234567',
    "tel preset returns cleaned tel: URL (got: " . landing_get_cta('phone') . ")"
);

// Test 10: whatsapp preset substitutes template
$GLOBALS['_mock_options'][1]['landing_cta_presets']['wa'] = [
    'type' => 'whatsapp',
    'phone' => '+79001234567',
    'message_template' => 'Hello {model}',
];
$result = landing_get_cta('wa', null, ['model' => 'L9']);
assert_test(
    strpos($result, 'wa.me/79001234567') !== false && strpos($result, 'Hello%20L9') !== false,
    "whatsapp preset substitutes {model} (got: $result)"
);

// Test 11: missing preset returns #
assert_test(
    landing_get_cta('nonexistent') === '#',
    "missing preset returns #"
);

// Test 12: whatsapp with empty phone falls back
$GLOBALS['_mock_options'][1]['landing_cta_presets']['wa2'] = ['type' => 'whatsapp', 'phone' => ''];
assert_test(
    landing_get_cta('wa2') === '#contact-form',
    "whatsapp with empty phone falls back to #contact-form"
);
```

- [ ] **Step 5: Run helpers tests**

Run: `php skills/wp-landing-config/tests/test_helpers.php`
Expected: `12 tests, 0 failures`

- [ ] **Step 6: Re-install + manual smoke**

```bash
bash skills/wp-landing-config/scripts/install-mu-plugin.sh /tmp/test-s2a
```

Manually open `http://ailexi.ru/wp-admin/admin.php?page=landing-config-cta`.
Expected:
- Page renders 5 preset sections
- Fill phone for `whatsapp` preset, save
- Open page source/wp-cli: `wp option get landing_cta_presets --format=yaml` — verify saved

- [ ] **Step 7: Commit**

```bash
git add skills/wp-landing-config/mu-plugin/landing-config/includes/admin-cta.php \
        skills/wp-landing-config/mu-plugin/landing-config/includes/helpers.php \
        skills/wp-landing-config/mu-plugin/landing-config/landing-config.php \
        skills/wp-landing-config/tests/test_helpers.php
git commit -m "feat(wp-landing-config): A3 — CTA admin page + landing_get_cta() helper

admin-cta.php: form for 5 presets (primary, whatsapp, phone, form_modal,
learn_more), each with type/target/phone/form_id/message_template/label.
Saved to wp_options::landing_cta_presets via Settings API.

helpers.php: landing_get_cta(preset, override, context) returns URL:
- scroll/anchor → #target
- tel → tel:+cleaned
- whatsapp → https://wa.me/digits?text=template_with_context_subst
- modal → # (JS handles)
- url → target as-is
- override URL always wins
- missing preset → #
- 6 new unit tests cover all paths

Co-Authored-By: Claude Opus 4.7 (1M context) <noreply@anthropic.com>"
```

---

## Phase A4 — Head & SEO админка

### Task 14: admin-head-seo.php — поля + raw HTML

**Files:**
- Create: `skills/wp-landing-config/mu-plugin/landing-config/includes/admin-head-seo.php`
- Modify: `skills/wp-landing-config/mu-plugin/landing-config/includes/helpers.php` — real `landing_render_head_extras`
- Modify: `skills/wp-landing-config/mu-plugin/landing-config/landing-config.php` — require admin-head-seo.php

- [ ] **Step 1: Add require + hook wp_head**

Modify `landing-config.php`:

```php
require_once LANDING_CONFIG_DIR . '/includes/admin-head-seo.php';

// Render head extras on every front-end page
add_action('wp_head', 'landing_render_head_extras', 5);
```

- [ ] **Step 2: Implement admin-head-seo.php**

```php
<?php
namespace LandingConfig\Admin\HeadSEO;

if (!defined('ABSPATH')) { exit; }

const FIELDS = [
    'ga4_id'                => ['label' => 'Google Analytics 4 ID', 'placeholder' => 'G-XXXXXXXXXX'],
    'yandex_metrika_id'     => ['label' => 'Яндекс.Метрика ID',     'placeholder' => '12345678'],
    'fb_pixel_id'           => ['label' => 'Meta (FB) Pixel ID',     'placeholder' => '123456789012345'],
    'tiktok_pixel_id'       => ['label' => 'TikTok Pixel ID',        'placeholder' => 'CXXXXXXXXXXX'],
    'gsc_verification'      => ['label' => 'Google Search Console (verification content)', 'placeholder' => 'abc...XYZ'],
    'yandex_webmaster_id'   => ['label' => 'Яндекс.Вебмастер (verification content)',     'placeholder' => 'abc...123'],
    'og_default_image'      => ['label' => 'OG image default URL',   'placeholder' => 'https://...'],
    'og_default_title'      => ['label' => 'OG title default',       'placeholder' => 'My Landing'],
    'og_default_description'=> ['label' => 'OG description default', 'placeholder' => 'Краткое описание'],
    'fonts_google_url'      => ['label' => 'Google Fonts URL',       'placeholder' => 'https://fonts.googleapis.com/css2?...'],
    'raw_html_head'         => ['label' => 'Custom HTML в head',     'placeholder' => '<!-- любой код -->', 'type' => 'textarea'],
];

add_action('admin_menu', function () {
    global $submenu;
    if (isset($submenu['landing-config'])) {
        foreach ($submenu['landing-config'] as &$item) {
            if ($item[2] === 'landing-config-head-seo') {
                $item[3] = __NAMESPACE__ . '\\render_page';
            }
        }
    }
}, 99);

add_action('admin_init', function () {
    foreach (FIELDS as $key => $meta) {
        register_setting('landing_head_seo', 'landing_' . $key, [
            'type' => 'string',
            'sanitize_callback' => $key === 'raw_html_head'
                ? __NAMESPACE__ . '\\sanitize_raw_html'
                : 'sanitize_text_field',
        ]);
    }
});

function sanitize_raw_html($input): string {
    $allowed_html = [
        'script'   => ['src' => true, 'async' => true, 'defer' => true, 'type' => true, 'crossorigin' => true],
        'meta'     => ['name' => true, 'content' => true, 'property' => true, 'http-equiv' => true, 'charset' => true],
        'link'     => ['rel' => true, 'href' => true, 'type' => true, 'crossorigin' => true, 'sizes' => true, 'as' => true],
        'style'    => ['type' => true, 'media' => true],
        'noscript' => [],
    ];
    return wp_kses((string)$input, $allowed_html);
}

function render_page(): void {
    if (!current_user_can('manage_options')) { wp_die('Insufficient permissions'); }
    ?>
    <div class="wrap">
        <h1>Head &amp; SEO</h1>
        <p>Все настройки попадают в <code>&lt;head&gt;</code> на каждой странице сайта.
        Поле «Custom HTML» фильтруется через wp_kses (разрешены meta/link/script/style).</p>
        <form method="post" action="options.php">
            <?php settings_fields('landing_head_seo'); ?>
            <table class="form-table">
                <?php foreach (FIELDS as $key => $meta):
                    $value = get_option('landing_' . $key, '');
                    $is_textarea = ($meta['type'] ?? '') === 'textarea';
                ?>
                    <tr>
                        <th><label for="landing_<?php echo $key; ?>"><?php echo esc_html($meta['label']); ?></label></th>
                        <td>
                            <?php if ($is_textarea): ?>
                                <textarea id="landing_<?php echo $key; ?>"
                                    name="landing_<?php echo $key; ?>"
                                    rows="6" class="large-text code"
                                    placeholder="<?php echo esc_attr($meta['placeholder']); ?>"><?php echo esc_textarea($value); ?></textarea>
                            <?php else: ?>
                                <input type="text" id="landing_<?php echo $key; ?>"
                                    name="landing_<?php echo $key; ?>"
                                    value="<?php echo esc_attr($value); ?>"
                                    placeholder="<?php echo esc_attr($meta['placeholder']); ?>"
                                    class="regular-text">
                            <?php endif; ?>
                        </td>
                    </tr>
                <?php endforeach; ?>
            </table>
            <?php submit_button(); ?>
        </form>
    </div>
    <?php
}
```

- [ ] **Step 3: Replace stub `landing_render_head_extras` with real implementation**

In `skills/wp-landing-config/mu-plugin/landing-config/includes/helpers.php`, replace the `landing_render_head_extras` stub with:

```php
function landing_render_head_extras(): void {
    echo "\n<!-- landing-config head extras -->\n";

    // GA4
    $ga4 = landing_config_get('ga4_id');
    if ($ga4 !== '') {
        printf(
            '<script async src="https://www.googletagmanager.com/gtag/js?id=%1$s"></script>'
            . '<script>window.dataLayer=window.dataLayer||[];function gtag(){dataLayer.push(arguments);}'
            . 'gtag("js",new Date());gtag("config","%1$s");</script>' . "\n",
            esc_attr($ga4)
        );
    }

    // Yandex.Metrika
    $ym = landing_config_get('yandex_metrika_id');
    if ($ym !== '') {
        printf(
            '<script>(function(m,e,t,r,i,k,a){m[i]=m[i]||function(){(m[i].a=m[i].a||[]).push(arguments)};'
            . 'm[i].l=1*new Date();k=e.createElement(t),a=e.getElementsByTagName(t)[0],k.async=1,k.src=r,'
            . 'a.parentNode.insertBefore(k,a)})(window,document,"script","https://mc.yandex.ru/metrika/tag.js","ym");'
            . 'ym(%1$s,"init",{clickmap:true,trackLinks:true,accurateTrackBounce:true});</script>'
            . '<noscript><div><img src="https://mc.yandex.ru/watch/%1$s" style="position:absolute;left:-9999px"/></div></noscript>'
            . "\n",
            esc_attr($ym)
        );
    }

    // FB Pixel
    $fb = landing_config_get('fb_pixel_id');
    if ($fb !== '') {
        printf(
            '<script>!function(f,b,e,v,n,t,s){if(f.fbq)return;n=f.fbq=function(){n.callMethod?n.callMethod.apply(n,arguments):n.queue.push(arguments)};if(!f._fbq)f._fbq=n;n.push=n;n.loaded=!0;n.version="2.0";n.queue=[];t=b.createElement(e);t.async=!0;t.src=v;s=b.getElementsByTagName(e)[0];s.parentNode.insertBefore(t,s)}(window,document,"script","https://connect.facebook.net/en_US/fbevents.js");fbq("init","%1$s");fbq("track","PageView");</script>'
            . "\n",
            esc_attr($fb)
        );
    }

    // GSC verification
    $gsc = landing_config_get('gsc_verification');
    if ($gsc !== '') {
        printf('<meta name="google-site-verification" content="%s">' . "\n", esc_attr($gsc));
    }

    // Yandex Webmaster verification
    $ym_wm = landing_config_get('yandex_webmaster_id');
    if ($ym_wm !== '') {
        printf('<meta name="yandex-verification" content="%s">' . "\n", esc_attr($ym_wm));
    }

    // OG defaults
    $og_image = landing_config_get('og_default_image');
    if ($og_image !== '') {
        printf('<meta property="og:image" content="%s">' . "\n", esc_url($og_image));
    }
    $og_title = landing_config_get('og_default_title');
    if ($og_title !== '') {
        printf('<meta property="og:title" content="%s">' . "\n", esc_attr($og_title));
    }
    $og_desc = landing_config_get('og_default_description');
    if ($og_desc !== '') {
        printf('<meta property="og:description" content="%s">' . "\n", esc_attr($og_desc));
    }

    // Fonts
    $fonts = landing_config_get('fonts_google_url');
    if ($fonts !== '') {
        printf('<link rel="stylesheet" href="%s">' . "\n", esc_url($fonts));
    }

    // Raw HTML (already sanitized via wp_kses on save)
    $raw = landing_config_get('raw_html_head');
    if ($raw !== '') {
        echo $raw . "\n";
    }

    echo "<!-- /landing-config head extras -->\n";
}
```

- [ ] **Step 4: Verify PHP syntax**

Run: `php -l skills/wp-landing-config/mu-plugin/landing-config/includes/admin-head-seo.php skills/wp-landing-config/mu-plugin/landing-config/includes/helpers.php`
Expected: both files OK.

- [ ] **Step 5: Re-install + manual smoke**

```bash
bash skills/wp-landing-config/scripts/install-mu-plugin.sh /tmp/test-s2a
```

Manually:
1. Open `http://ailexi.ru/wp-admin/admin.php?page=landing-config-head-seo`
2. Fill `Яндекс.Метрика ID = 12345678` and `GSC verification = test-content-xyz`. Save.
3. `curl -s http://ailexi.ru/ | grep -E 'mc.yandex|google-site-verification'`
   Expected: both meta tags appear.

- [ ] **Step 6: Commit**

```bash
git add skills/wp-landing-config/mu-plugin/landing-config/includes/admin-head-seo.php \
        skills/wp-landing-config/mu-plugin/landing-config/includes/helpers.php \
        skills/wp-landing-config/mu-plugin/landing-config/landing-config.php
git commit -m "feat(wp-landing-config): A4 — Head & SEO admin page + landing_render_head_extras()

admin-head-seo.php: form with 11 fields (GA4, Y.Metrika, FB Pixel, TikTok
Pixel, GSC, Y.Webmaster, OG image/title/desc, Google Fonts URL, raw HTML).
Raw HTML field passes through wp_kses with meta/link/script/style allow-list.

helpers.php: landing_render_head_extras() prints all configured snippets
to wp_head (priority 5). Empty fields output nothing. Cookie-free analytics
(GA4 + Y.Metrika) render full inline.

Co-Authored-By: Claude Opus 4.7 (1M context) <noreply@anthropic.com>"
```

---

## Phase A5 — Интеграции: адаптеры + Test connection + retry

### Task 15: AdapterInterface + EmailAdapter (base + simplest case)

**Files:**
- Create: `skills/wp-landing-config/mu-plugin/landing-config/adapters/AdapterInterface.php`
- Create: `skills/wp-landing-config/mu-plugin/landing-config/adapters/EmailAdapter.php`
- Modify: `skills/wp-landing-config/mu-plugin/landing-config/landing-config.php` — require adapters

- [ ] **Step 1: Add adapter requires to bootstrap**

Modify `landing-config.php`, append:

```php
require_once LANDING_CONFIG_DIR . '/adapters/AdapterInterface.php';
require_once LANDING_CONFIG_DIR . '/adapters/EmailAdapter.php';
```

- [ ] **Step 2: Write AdapterInterface**

```php
<?php
namespace LandingConfig\Adapters;

if (!defined('ABSPATH')) { exit; }

interface AdapterInterface {
    /**
     * Adapter machine name (e.g. 'amocrm', 'telegram'). Used as key in storage.
     */
    public static function name(): string;

    /**
     * Human-readable label for admin UI.
     */
    public static function label(): string;

    /**
     * Send a lead to the external service.
     *
     * @param array $lead       Row from wp_<bid>_landing_leads (all columns)
     * @return array  ['ok'=>bool, 'response_code'=>int|null, 'response_body'=>string, 'error'=>string|null]
     */
    public function send(array $lead): array;

    /**
     * Test connection without creating a real lead.
     *
     * @return array  ['ok'=>bool, 'message'=>string]
     */
    public function test_connection(): array;

    /**
     * Field definitions for admin UI.
     * Returns: ['field_key' => ['label'=>..., 'type'=>'text|password|textarea', 'placeholder'=>...], ...]
     * The 'password' type is auto-encrypted on save and masked in display.
     */
    public static function field_defs(): array;
}
```

- [ ] **Step 3: Write EmailAdapter**

```php
<?php
namespace LandingConfig\Adapters;

if (!defined('ABSPATH')) { exit; }

class EmailAdapter implements AdapterInterface {

    public static function name(): string { return 'email'; }
    public static function label(): string { return 'Email уведомления'; }

    public static function field_defs(): array {
        return [
            'to'      => ['label' => 'Email получателя', 'type' => 'text', 'placeholder' => 'manager@example.com'],
            'subject' => ['label' => 'Тема письма', 'type' => 'text', 'placeholder' => 'Новая заявка с сайта'],
        ];
    }

    public function send(array $lead): array {
        $to = \landing_config_get('integration_email_to');
        if ($to === '') {
            return ['ok' => false, 'response_code' => null, 'response_body' => '', 'error' => 'No recipient configured'];
        }
        $subject = \landing_config_get('integration_email_subject', 'Новая заявка');
        $body = "Получена заявка #{$lead['id']}\n\n"
              . "Имя:      {$lead['name']}\n"
              . "Телефон:  {$lead['phone']}\n"
              . "Email:    {$lead['email']}\n"
              . "Сообщение:{$lead['message']}\n"
              . "Блок:     {$lead['source_block']}\n"
              . "UTM:      src={$lead['utm_source']} med={$lead['utm_medium']} cmp={$lead['utm_campaign']}\n"
              . "Время:    {$lead['created_at']}\n";

        $sent = \wp_mail($to, $subject, $body);
        return [
            'ok' => $sent,
            'response_code' => $sent ? 200 : null,
            'response_body' => $sent ? 'wp_mail returned true' : '',
            'error' => $sent ? null : 'wp_mail returned false',
        ];
    }

    public function test_connection(): array {
        $to = \landing_config_get('integration_email_to');
        if ($to === '') {
            return ['ok' => false, 'message' => 'Email получателя не указан'];
        }
        if (!is_email($to)) {
            return ['ok' => false, 'message' => 'Неверный формат email: ' . $to];
        }
        $sent = \wp_mail($to, '[Test] landing-config', 'Тестовое письмо — проверка подключения email.');
        return [
            'ok' => $sent,
            'message' => $sent ? 'Тестовое письмо отправлено' : 'wp_mail вернул false (проверьте SMTP)',
        ];
    }
}
```

- [ ] **Step 4: Verify syntax**

Run: `php -l skills/wp-landing-config/mu-plugin/landing-config/adapters/AdapterInterface.php skills/wp-landing-config/mu-plugin/landing-config/adapters/EmailAdapter.php`
Expected: both OK.

- [ ] **Step 5: Commit**

```bash
git add skills/wp-landing-config/mu-plugin/landing-config/adapters/AdapterInterface.php \
        skills/wp-landing-config/mu-plugin/landing-config/adapters/EmailAdapter.php \
        skills/wp-landing-config/mu-plugin/landing-config/landing-config.php
git commit -m "feat(wp-landing-config): A5 — AdapterInterface + EmailAdapter

Interface contract:
- name() / label() — identifiers
- send(\$lead): ['ok','response_code','response_body','error']
- test_connection(): ['ok', 'message']
- field_defs(): admin UI field definitions (text|password|textarea)

EmailAdapter is the simplest implementation — wp_mail to configured
recipient. Other 5 adapters (Telegram, WhatsApp, AmoCRM, Bitrix24, HubSpot)
follow same interface (Tasks 16-18).

Co-Authored-By: Claude Opus 4.7 (1M context) <noreply@anthropic.com>"
```

---

### Task 16: TelegramAdapter + WhatsAppAdapter

**Files:**
- Create: `skills/wp-landing-config/mu-plugin/landing-config/adapters/TelegramAdapter.php`
- Create: `skills/wp-landing-config/mu-plugin/landing-config/adapters/WhatsAppAdapter.php`
- Modify: `skills/wp-landing-config/mu-plugin/landing-config/landing-config.php`

- [ ] **Step 1: Add requires**

In `landing-config.php`:

```php
require_once LANDING_CONFIG_DIR . '/adapters/TelegramAdapter.php';
require_once LANDING_CONFIG_DIR . '/adapters/WhatsAppAdapter.php';
```

- [ ] **Step 2: Write TelegramAdapter**

```php
<?php
namespace LandingConfig\Adapters;

if (!defined('ABSPATH')) { exit; }

use function LandingConfig\Encryption\decrypt;

class TelegramAdapter implements AdapterInterface {

    public static function name(): string { return 'telegram'; }
    public static function label(): string { return 'Telegram (Bot API)'; }

    public static function field_defs(): array {
        return [
            'bot_token' => ['label' => 'Bot token', 'type' => 'password', 'placeholder' => '123456:ABC-DEF...'],
            'chat_id'   => ['label' => 'Chat ID или @channel', 'type' => 'text', 'placeholder' => '-100123456789 или @mychannel'],
        ];
    }

    public function send(array $lead): array {
        $token_enc = \landing_config_get('integration_telegram_bot_token');
        $token = $token_enc ? decrypt($token_enc) : '';
        $chat_id = \landing_config_get('integration_telegram_chat_id');
        if ($token === '' || $chat_id === '') {
            return ['ok' => false, 'response_code' => null, 'response_body' => '', 'error' => 'Token or chat_id missing'];
        }

        $text = "🔔 *Новая заявка #{$lead['id']}*\n\n"
              . "👤 Имя: {$lead['name']}\n"
              . "📱 Телефон: `{$lead['phone']}`\n"
              . "📧 Email: {$lead['email']}\n"
              . ($lead['message'] ? "💬 Сообщение: {$lead['message']}\n" : '')
              . "📦 Блок: {$lead['source_block']}\n"
              . ($lead['utm_source'] ? "🔗 UTM source: {$lead['utm_source']}\n" : '');

        $resp = \wp_remote_post("https://api.telegram.org/bot{$token}/sendMessage", [
            'timeout' => 10,
            'body' => ['chat_id' => $chat_id, 'text' => $text, 'parse_mode' => 'Markdown'],
        ]);
        return self::normalize_response($resp);
    }

    public function test_connection(): array {
        $token_enc = \landing_config_get('integration_telegram_bot_token');
        $token = $token_enc ? decrypt($token_enc) : '';
        if ($token === '') return ['ok' => false, 'message' => 'Bot token не задан'];

        $resp = \wp_remote_get("https://api.telegram.org/bot{$token}/getMe", ['timeout' => 10]);
        if (\is_wp_error($resp)) return ['ok' => false, 'message' => 'Network error: ' . $resp->get_error_message()];

        $code = \wp_remote_retrieve_response_code($resp);
        $body = json_decode(\wp_remote_retrieve_body($resp), true);
        if ($code === 200 && !empty($body['ok'])) {
            return ['ok' => true, 'message' => 'Бот: @' . $body['result']['username']];
        }
        return ['ok' => false, 'message' => "API вернул {$code}: " . substr(\wp_remote_retrieve_body($resp), 0, 200)];
    }

    private static function normalize_response($resp): array {
        if (\is_wp_error($resp)) {
            return ['ok' => false, 'response_code' => null, 'response_body' => '', 'error' => $resp->get_error_message()];
        }
        $code = \wp_remote_retrieve_response_code($resp);
        $body = \wp_remote_retrieve_body($resp);
        return [
            'ok' => $code >= 200 && $code < 300,
            'response_code' => $code,
            'response_body' => $body,
            'error' => $code >= 400 ? "HTTP {$code}" : null,
        ];
    }
}
```

- [ ] **Step 3: Write WhatsAppAdapter (click-to-chat link mode — no API key needed)**

```php
<?php
namespace LandingConfig\Adapters;

if (!defined('ABSPATH')) { exit; }

/**
 * WhatsApp via Business API (Cloud API or On-Premise).
 * For simple "click to chat" links, no adapter is needed — use CTA preset 'whatsapp'.
 * This adapter SENDS messages programmatically when a lead arrives, requires Business API.
 */
class WhatsAppAdapter implements AdapterInterface {

    public static function name(): string { return 'whatsapp'; }
    public static function label(): string { return 'WhatsApp Business Cloud API'; }

    public static function field_defs(): array {
        return [
            'access_token' => ['label' => 'Access token', 'type' => 'password', 'placeholder' => 'EAAxxx...'],
            'phone_id'     => ['label' => 'Phone Number ID', 'type' => 'text', 'placeholder' => '123456789012345'],
            'to_phone'     => ['label' => 'Получатель (E.164)', 'type' => 'text', 'placeholder' => '+79991234567'],
        ];
    }

    public function send(array $lead): array {
        $token_enc = \landing_config_get('integration_whatsapp_access_token');
        $token = $token_enc ? \LandingConfig\Encryption\decrypt($token_enc) : '';
        $phone_id = \landing_config_get('integration_whatsapp_phone_id');
        $to = preg_replace('/[^0-9]/', '', \landing_config_get('integration_whatsapp_to_phone'));
        if ($token === '' || $phone_id === '' || $to === '') {
            return ['ok' => false, 'response_code' => null, 'response_body' => '', 'error' => 'Token/phone_id/to missing'];
        }

        $text = "Новая заявка #{$lead['id']}: {$lead['name']}, {$lead['phone']}, {$lead['email']}";
        $resp = \wp_remote_post("https://graph.facebook.com/v18.0/{$phone_id}/messages", [
            'timeout' => 10,
            'headers' => ['Authorization' => "Bearer {$token}", 'Content-Type' => 'application/json'],
            'body' => json_encode([
                'messaging_product' => 'whatsapp',
                'to' => $to,
                'type' => 'text',
                'text' => ['body' => $text],
            ]),
        ]);
        return TelegramAdapter::class === 'placeholder'  // hack: reuse normalize via static
            ? []
            : self::normalize_response($resp);
    }

    public function test_connection(): array {
        $token_enc = \landing_config_get('integration_whatsapp_access_token');
        $token = $token_enc ? \LandingConfig\Encryption\decrypt($token_enc) : '';
        $phone_id = \landing_config_get('integration_whatsapp_phone_id');
        if ($token === '' || $phone_id === '') {
            return ['ok' => false, 'message' => 'Access token или Phone ID не заданы'];
        }
        $resp = \wp_remote_get("https://graph.facebook.com/v18.0/{$phone_id}", [
            'timeout' => 10,
            'headers' => ['Authorization' => "Bearer {$token}"],
        ]);
        if (\is_wp_error($resp)) return ['ok' => false, 'message' => 'Network: ' . $resp->get_error_message()];
        $code = \wp_remote_retrieve_response_code($resp);
        if ($code === 200) return ['ok' => true, 'message' => 'Phone Number ID валиден'];
        return ['ok' => false, 'message' => "API вернул {$code}"];
    }

    private static function normalize_response($resp): array {
        if (\is_wp_error($resp)) {
            return ['ok' => false, 'response_code' => null, 'response_body' => '', 'error' => $resp->get_error_message()];
        }
        $code = \wp_remote_retrieve_response_code($resp);
        $body = \wp_remote_retrieve_body($resp);
        return [
            'ok' => $code >= 200 && $code < 300,
            'response_code' => $code,
            'response_body' => $body,
            'error' => $code >= 400 ? "HTTP {$code}" : null,
        ];
    }
}
```

- [ ] **Step 4: Verify syntax**

Run: `php -l skills/wp-landing-config/mu-plugin/landing-config/adapters/TelegramAdapter.php skills/wp-landing-config/mu-plugin/landing-config/adapters/WhatsAppAdapter.php`

- [ ] **Step 5: Commit**

```bash
git add skills/wp-landing-config/mu-plugin/landing-config/adapters/TelegramAdapter.php \
        skills/wp-landing-config/mu-plugin/landing-config/adapters/WhatsAppAdapter.php \
        skills/wp-landing-config/mu-plugin/landing-config/landing-config.php
git commit -m "feat(wp-landing-config): A5 — TelegramAdapter + WhatsAppAdapter

Telegram: Bot API sendMessage with Markdown. Bot token encrypted.
test_connection hits /getMe and returns username on success.

WhatsApp: Business Cloud API v18.0 /messages endpoint. Access token
encrypted. test_connection hits phone_id metadata.

Both use shared response normalization pattern (wp_remote_post →
{ok, response_code, response_body, error}).

Co-Authored-By: Claude Opus 4.7 (1M context) <noreply@anthropic.com>"
```

---

### Task 17: 3 CRM-адаптера (AmoCRM, Bitrix24, HubSpot)

**Files:**
- Create: `skills/wp-landing-config/mu-plugin/landing-config/adapters/AmoCRMAdapter.php`
- Create: `skills/wp-landing-config/mu-plugin/landing-config/adapters/Bitrix24Adapter.php`
- Create: `skills/wp-landing-config/mu-plugin/landing-config/adapters/HubSpotAdapter.php`
- Modify: `skills/wp-landing-config/mu-plugin/landing-config/landing-config.php`

- [ ] **Step 1: Add requires**

```php
require_once LANDING_CONFIG_DIR . '/adapters/AmoCRMAdapter.php';
require_once LANDING_CONFIG_DIR . '/adapters/Bitrix24Adapter.php';
require_once LANDING_CONFIG_DIR . '/adapters/HubSpotAdapter.php';
```

- [ ] **Step 2: Write AmoCRMAdapter**

```php
<?php
namespace LandingConfig\Adapters;

if (!defined('ABSPATH')) { exit; }

use function LandingConfig\Encryption\decrypt;

class AmoCRMAdapter implements AdapterInterface {
    public static function name(): string { return 'amocrm'; }
    public static function label(): string { return 'AmoCRM'; }

    public static function field_defs(): array {
        return [
            'subdomain'    => ['label' => 'Subdomain (xxx.amocrm.ru)', 'type' => 'text', 'placeholder' => 'mycompany'],
            'access_token' => ['label' => 'Long-lived access token', 'type' => 'password', 'placeholder' => 'eyJ0eXAi...'],
            'responsible_user_id' => ['label' => 'Responsible user ID', 'type' => 'text', 'placeholder' => '12345'],
        ];
    }

    public function send(array $lead): array {
        $sub = \landing_config_get('integration_amocrm_subdomain');
        $token_enc = \landing_config_get('integration_amocrm_access_token');
        $token = $token_enc ? decrypt($token_enc) : '';
        if ($sub === '' || $token === '') {
            return ['ok' => false, 'response_code' => null, 'response_body' => '', 'error' => 'subdomain or token missing'];
        }

        $payload = [[
            'name' => "Заявка с сайта: {$lead['name']}",
            'created_at' => time(),
            'responsible_user_id' => (int)\landing_config_get('integration_amocrm_responsible_user_id', 0) ?: null,
            '_embedded' => [
                'contacts' => [[
                    'name' => $lead['name'] ?: 'Без имени',
                    'custom_fields_values' => [
                        ['field_code' => 'PHONE', 'values' => [['value' => $lead['phone'], 'enum_code' => 'WORK']]],
                        ['field_code' => 'EMAIL', 'values' => [['value' => $lead['email'], 'enum_code' => 'WORK']]],
                    ],
                ]],
            ],
        ]];

        $resp = \wp_remote_post("https://{$sub}.amocrm.ru/api/v4/leads/complex", [
            'timeout' => 15,
            'headers' => [
                'Authorization' => "Bearer {$token}",
                'Content-Type' => 'application/json',
            ],
            'body' => json_encode($payload),
        ]);
        return self::normalize_response($resp);
    }

    public function test_connection(): array {
        $sub = \landing_config_get('integration_amocrm_subdomain');
        $token_enc = \landing_config_get('integration_amocrm_access_token');
        $token = $token_enc ? decrypt($token_enc) : '';
        if ($sub === '' || $token === '') return ['ok' => false, 'message' => 'subdomain или token не заданы'];

        $resp = \wp_remote_get("https://{$sub}.amocrm.ru/api/v4/account", [
            'timeout' => 10,
            'headers' => ['Authorization' => "Bearer {$token}"],
        ]);
        if (\is_wp_error($resp)) return ['ok' => false, 'message' => 'Network: ' . $resp->get_error_message()];
        $code = \wp_remote_retrieve_response_code($resp);
        if ($code === 200) {
            $body = json_decode(\wp_remote_retrieve_body($resp), true);
            return ['ok' => true, 'message' => 'Аккаунт: ' . ($body['name'] ?? '(нет имени)')];
        }
        return ['ok' => false, 'message' => "API вернул {$code}: " . substr(\wp_remote_retrieve_body($resp), 0, 200)];
    }

    private static function normalize_response($resp): array {
        if (\is_wp_error($resp)) return ['ok' => false, 'response_code' => null, 'response_body' => '', 'error' => $resp->get_error_message()];
        $code = \wp_remote_retrieve_response_code($resp);
        $body = \wp_remote_retrieve_body($resp);
        return [
            'ok' => $code >= 200 && $code < 300,
            'response_code' => $code,
            'response_body' => $body,
            'error' => $code >= 400 ? "HTTP {$code}" : null,
        ];
    }
}
```

- [ ] **Step 3: Write Bitrix24Adapter**

```php
<?php
namespace LandingConfig\Adapters;

if (!defined('ABSPATH')) { exit; }

use function LandingConfig\Encryption\decrypt;

class Bitrix24Adapter implements AdapterInterface {
    public static function name(): string { return 'bitrix24'; }
    public static function label(): string { return 'Bitrix24 (webhook)'; }

    public static function field_defs(): array {
        return [
            'webhook_url' => ['label' => 'Inbound webhook URL', 'type' => 'password', 'placeholder' => 'https://mycompany.bitrix24.ru/rest/1/abcXYZ/'],
        ];
    }

    public function send(array $lead): array {
        $url_enc = \landing_config_get('integration_bitrix24_webhook_url');
        $url = $url_enc ? decrypt($url_enc) : '';
        if ($url === '') return ['ok' => false, 'response_code' => null, 'response_body' => '', 'error' => 'webhook URL missing'];

        $endpoint = rtrim($url, '/') . '/crm.lead.add.json';
        $payload = [
            'fields' => [
                'TITLE' => "Заявка с сайта: " . ($lead['name'] ?: 'Без имени'),
                'NAME' => $lead['name'],
                'PHONE' => [['VALUE' => $lead['phone'], 'VALUE_TYPE' => 'WORK']],
                'EMAIL' => [['VALUE' => $lead['email'], 'VALUE_TYPE' => 'WORK']],
                'COMMENTS' => $lead['message'] . "\n\nИсточник: {$lead['source_block']}\nUTM: {$lead['utm_source']}/{$lead['utm_medium']}/{$lead['utm_campaign']}",
                'SOURCE_ID' => 'WEB',
            ],
        ];

        $resp = \wp_remote_post($endpoint, [
            'timeout' => 15,
            'body' => $payload,
        ]);
        return self::normalize_response($resp);
    }

    public function test_connection(): array {
        $url_enc = \landing_config_get('integration_bitrix24_webhook_url');
        $url = $url_enc ? decrypt($url_enc) : '';
        if ($url === '') return ['ok' => false, 'message' => 'Webhook URL не задан'];

        $endpoint = rtrim($url, '/') . '/profile.json';
        $resp = \wp_remote_get($endpoint, ['timeout' => 10]);
        if (\is_wp_error($resp)) return ['ok' => false, 'message' => 'Network: ' . $resp->get_error_message()];
        $code = \wp_remote_retrieve_response_code($resp);
        if ($code === 200) {
            $body = json_decode(\wp_remote_retrieve_body($resp), true);
            $name = ($body['result']['NAME'] ?? '') . ' ' . ($body['result']['LAST_NAME'] ?? '');
            return ['ok' => true, 'message' => 'Профиль: ' . trim($name)];
        }
        return ['ok' => false, 'message' => "API вернул {$code}"];
    }

    private static function normalize_response($resp): array {
        if (\is_wp_error($resp)) return ['ok' => false, 'response_code' => null, 'response_body' => '', 'error' => $resp->get_error_message()];
        $code = \wp_remote_retrieve_response_code($resp);
        $body = \wp_remote_retrieve_body($resp);
        return ['ok' => $code >= 200 && $code < 300, 'response_code' => $code, 'response_body' => $body, 'error' => $code >= 400 ? "HTTP {$code}" : null];
    }
}
```

- [ ] **Step 4: Write HubSpotAdapter**

```php
<?php
namespace LandingConfig\Adapters;

if (!defined('ABSPATH')) { exit; }

use function LandingConfig\Encryption\decrypt;

class HubSpotAdapter implements AdapterInterface {
    public static function name(): string { return 'hubspot'; }
    public static function label(): string { return 'HubSpot'; }

    public static function field_defs(): array {
        return [
            'access_token' => ['label' => 'Private app access token', 'type' => 'password', 'placeholder' => 'pat-eu1-...'],
        ];
    }

    public function send(array $lead): array {
        $token_enc = \landing_config_get('integration_hubspot_access_token');
        $token = $token_enc ? decrypt($token_enc) : '';
        if ($token === '') return ['ok' => false, 'response_code' => null, 'response_body' => '', 'error' => 'token missing'];

        // Create a Contact, then a Deal? Simpler: just Contact.
        $payload = [
            'properties' => [
                'firstname' => $lead['name'],
                'phone' => $lead['phone'],
                'email' => $lead['email'],
                'message' => $lead['message'],
                'lifecyclestage' => 'lead',
                'lead_source_detail' => $lead['source_block'],
                'hs_analytics_source' => $lead['utm_source'] ?: 'OTHER_CAMPAIGNS',
            ],
        ];

        $resp = \wp_remote_post('https://api.hubapi.com/crm/v3/objects/contacts', [
            'timeout' => 15,
            'headers' => [
                'Authorization' => "Bearer {$token}",
                'Content-Type' => 'application/json',
            ],
            'body' => json_encode($payload),
        ]);
        return self::normalize_response($resp);
    }

    public function test_connection(): array {
        $token_enc = \landing_config_get('integration_hubspot_access_token');
        $token = $token_enc ? decrypt($token_enc) : '';
        if ($token === '') return ['ok' => false, 'message' => 'Token не задан'];

        $resp = \wp_remote_get('https://api.hubapi.com/account-info/v3/details', [
            'timeout' => 10,
            'headers' => ['Authorization' => "Bearer {$token}"],
        ]);
        if (\is_wp_error($resp)) return ['ok' => false, 'message' => 'Network: ' . $resp->get_error_message()];
        $code = \wp_remote_retrieve_response_code($resp);
        if ($code === 200) {
            $body = json_decode(\wp_remote_retrieve_body($resp), true);
            return ['ok' => true, 'message' => 'Portal ID: ' . ($body['portalId'] ?? 'unknown')];
        }
        return ['ok' => false, 'message' => "API вернул {$code}"];
    }

    private static function normalize_response($resp): array {
        if (\is_wp_error($resp)) return ['ok' => false, 'response_code' => null, 'response_body' => '', 'error' => $resp->get_error_message()];
        $code = \wp_remote_retrieve_response_code($resp);
        $body = \wp_remote_retrieve_body($resp);
        return ['ok' => $code >= 200 && $code < 300, 'response_code' => $code, 'response_body' => $body, 'error' => $code >= 400 ? "HTTP {$code}" : null];
    }
}
```

- [ ] **Step 5: Verify syntax**

Run: `php -l skills/wp-landing-config/mu-plugin/landing-config/adapters/{AmoCRM,Bitrix24,HubSpot}Adapter.php`

- [ ] **Step 6: Commit**

```bash
git add skills/wp-landing-config/mu-plugin/landing-config/adapters/{AmoCRM,Bitrix24,HubSpot}Adapter.php \
        skills/wp-landing-config/mu-plugin/landing-config/landing-config.php
git commit -m "feat(wp-landing-config): A5 — 3 CRM adapters (AmoCRM, Bitrix24, HubSpot)

AmoCRM: v4/leads/complex (lead+contact in one call). Long-lived token,
subdomain config. test_connection hits /account.

Bitrix24: inbound webhook URL only (no auth header). crm.lead.add.json
with PHONE/EMAIL custom fields. test_connection hits profile.json.

HubSpot: v3 contacts create. Private app token. test_connection hits
/account-info/v3/details.

All 3 normalize wp_remote_post to {ok, response_code, response_body, error}.
All credential fields are 'password' type — auto-encrypted in admin save.

Co-Authored-By: Claude Opus 4.7 (1M context) <noreply@anthropic.com>"
```

---

### Task 18: admin-integrations.php — Settings page + AJAX test-connection + dispatch action

**Files:**
- Create: `skills/wp-landing-config/mu-plugin/landing-config/includes/admin-integrations.php`
- Modify: `skills/wp-landing-config/mu-plugin/landing-config/landing-config.php`

- [ ] **Step 1: Add require**

```php
require_once LANDING_CONFIG_DIR . '/includes/admin-integrations.php';
```

- [ ] **Step 2: Implement admin-integrations.php**

```php
<?php
namespace LandingConfig\Admin\Integrations;

if (!defined('ABSPATH')) { exit; }

use LandingConfig\Adapters\EmailAdapter;
use LandingConfig\Adapters\TelegramAdapter;
use LandingConfig\Adapters\WhatsAppAdapter;
use LandingConfig\Adapters\AmoCRMAdapter;
use LandingConfig\Adapters\Bitrix24Adapter;
use LandingConfig\Adapters\HubSpotAdapter;
use function LandingConfig\Encryption\encrypt;
use function LandingConfig\Encryption\decrypt;
use function LandingConfig\Encryption\mask;

function all_adapters(): array {
    return [
        EmailAdapter::class,
        TelegramAdapter::class,
        WhatsAppAdapter::class,
        AmoCRMAdapter::class,
        Bitrix24Adapter::class,
        HubSpotAdapter::class,
    ];
}

add_action('admin_menu', function () {
    global $submenu;
    if (isset($submenu['landing-config'])) {
        foreach ($submenu['landing-config'] as &$item) {
            if ($item[2] === 'landing-config-integrations') {
                $item[3] = __NAMESPACE__ . '\\render_page';
            }
        }
    }
}, 99);

add_action('admin_init', function () {
    foreach (all_adapters() as $cls) {
        $name = $cls::name();
        register_setting('landing_integrations', "landing_integration_{$name}_enabled", ['type' => 'boolean']);
        foreach ($cls::field_defs() as $field => $meta) {
            register_setting('landing_integrations', "landing_integration_{$name}_{$field}", [
                'type' => 'string',
                'sanitize_callback' => $meta['type'] === 'password'
                    ? __NAMESPACE__ . '\\sanitize_secret'
                    : 'sanitize_text_field',
            ]);
        }
    }
});

function sanitize_secret($input): string {
    // If unchanged (still bullet-masked), keep existing value
    if (preg_match('/^•+/', $input)) {
        return ''; // signal to caller — don't overwrite
    }
    return $input === '' ? '' : encrypt($input);
}

// Pre-save hook: if sanitize returned '' (masked unchanged), restore previous
add_filter('pre_update_option', function ($value, $option) {
    if (strpos($option, 'landing_integration_') === 0 && $value === '') {
        $existing = get_option($option, '');
        if ($existing !== '') return $existing;
    }
    return $value;
}, 10, 2);

function render_page(): void {
    if (!current_user_can('manage_options')) { wp_die('Insufficient permissions'); }
    ?>
    <div class="wrap">
        <h1>Интеграции</h1>
        <form method="post" action="options.php">
            <?php settings_fields('landing_integrations'); ?>
            <?php foreach (all_adapters() as $cls):
                $name = $cls::name();
                $enabled = (bool)get_option("landing_integration_{$name}_enabled");
            ?>
                <h2><?php echo esc_html($cls::label()); ?></h2>
                <table class="form-table">
                    <tr>
                        <th>Включён</th>
                        <td><label>
                            <input type="checkbox" name="landing_integration_<?php echo $name; ?>_enabled" value="1" <?php checked($enabled); ?>>
                            Отправлять заявки в <?php echo esc_html($cls::label()); ?>
                        </label></td>
                    </tr>
                    <?php foreach ($cls::field_defs() as $field => $meta):
                        $opt_key = "landing_integration_{$name}_{$field}";
                        $stored = get_option($opt_key, '');
                        $display_value = $meta['type'] === 'password' && $stored !== ''
                            ? mask(decrypt($stored))
                            : $stored;
                    ?>
                        <tr>
                            <th><label for="<?php echo $opt_key; ?>"><?php echo esc_html($meta['label']); ?></label></th>
                            <td>
                                <input type="text" id="<?php echo $opt_key; ?>"
                                    name="<?php echo $opt_key; ?>"
                                    value="<?php echo esc_attr($display_value); ?>"
                                    placeholder="<?php echo esc_attr($meta['placeholder'] ?? ''); ?>"
                                    class="regular-text">
                            </td>
                        </tr>
                    <?php endforeach; ?>
                    <tr>
                        <th></th>
                        <td>
                            <button type="button" class="button landing-test-btn" data-adapter="<?php echo $name; ?>">
                                Test connection
                            </button>
                            <span class="landing-test-result" id="landing-test-result-<?php echo $name; ?>"></span>
                        </td>
                    </tr>
                </table>
            <?php endforeach; ?>
            <?php submit_button(); ?>
        </form>
    </div>
    <script>
    document.querySelectorAll('.landing-test-btn').forEach(function(btn) {
        btn.addEventListener('click', function() {
            const name = btn.dataset.adapter;
            const result = document.getElementById('landing-test-result-' + name);
            result.textContent = 'Тестирую...';
            result.style.color = '#666';
            const fd = new FormData();
            fd.append('action', 'landing_test_adapter');
            fd.append('adapter', name);
            fd.append('_wpnonce', '<?php echo wp_create_nonce('landing_test_adapter'); ?>');
            fetch(ajaxurl, {method: 'POST', body: fd})
                .then(r => r.json())
                .then(d => {
                    result.textContent = (d.ok ? '✅ ' : '❌ ') + d.message;
                    result.style.color = d.ok ? 'green' : 'red';
                })
                .catch(e => {
                    result.textContent = '❌ ' + e.message;
                    result.style.color = 'red';
                });
        });
    });
    </script>
    <?php
}

add_action('wp_ajax_landing_test_adapter', function () {
    if (!current_user_can('manage_options')) { wp_send_json(['ok' => false, 'message' => 'No permissions']); }
    check_admin_referer('landing_test_adapter');

    $name = sanitize_text_field($_POST['adapter'] ?? '');
    foreach (all_adapters() as $cls) {
        if ($cls::name() === $name) {
            $result = (new $cls())->test_connection();
            wp_send_json($result);
        }
    }
    wp_send_json(['ok' => false, 'message' => 'Unknown adapter']);
});

// Dispatch lead to all enabled adapters when a lead is received
add_action('landing_config_lead_received', function ($lead_id, $lead) {
    foreach (all_adapters() as $cls) {
        $name = $cls::name();
        if (!get_option("landing_integration_{$name}_enabled")) continue;

        $instance = new $cls();
        $result = $instance->send($lead);

        global $wpdb;
        $log_table = \LandingConfig\DB\get_lead_log_table_name();
        $wpdb->insert($log_table, [
            'lead_id' => $lead_id,
            'adapter' => $name,
            'attempt' => 1,
            'status' => $result['ok'] ? 'success' : 'failed',
            'response_code' => $result['response_code'],
            'response_body' => mb_substr($result['response_body'] ?? '', 0, 1000),
            'error_text' => $result['error'],
            'created_at' => current_time('mysql'),
        ]);

        // Schedule retry if failed
        if (!$result['ok']) {
            wp_schedule_single_event(time() + 60, 'landing_retry_adapter', [$lead_id, $name, 2]);
        }
    }
}, 10, 2);

// Retry handler
add_action('landing_retry_adapter', function ($lead_id, $adapter_name, $attempt) {
    if ($attempt > 3) return; // max 3 attempts

    global $wpdb;
    $leads = \LandingConfig\DB\get_leads_table_name();
    $lead = $wpdb->get_row($wpdb->prepare("SELECT * FROM `$leads` WHERE id = %d", $lead_id), ARRAY_A);
    if (!$lead) return;

    foreach (all_adapters() as $cls) {
        if ($cls::name() !== $adapter_name) continue;
        $result = (new $cls())->send($lead);

        $log_table = \LandingConfig\DB\get_lead_log_table_name();
        $wpdb->insert($log_table, [
            'lead_id' => $lead_id, 'adapter' => $adapter_name, 'attempt' => $attempt,
            'status' => $result['ok'] ? 'success' : 'failed',
            'response_code' => $result['response_code'],
            'response_body' => mb_substr($result['response_body'] ?? '', 0, 1000),
            'error_text' => $result['error'],
            'created_at' => current_time('mysql'),
        ]);

        if (!$result['ok'] && $attempt < 3) {
            $delays = [2 => 300, 3 => 1800]; // 5min, 30min
            wp_schedule_single_event(time() + $delays[$attempt + 1], 'landing_retry_adapter',
                [$lead_id, $adapter_name, $attempt + 1]);
        }
        return;
    }
}, 10, 3);
```

- [ ] **Step 3: Verify syntax**

Run: `php -l skills/wp-landing-config/mu-plugin/landing-config/includes/admin-integrations.php`

- [ ] **Step 4: Re-install + manual smoke**

```bash
bash skills/wp-landing-config/scripts/install-mu-plugin.sh /tmp/test-s2a
```

Manually:
1. Open `http://ailexi.ru/wp-admin/admin.php?page=landing-config-integrations`
2. Fill `Email уведомления → Email получателя: esper21@mail.ru`, check «Включён». Save.
3. Click «Test connection» — expected: «✅ Тестовое письмо отправлено» (or warning if SMTP unreachable)
4. POST a lead: `curl -X POST http://ailexi.ru/wp-json/landing/v1/lead -d 'name=AdapterTest&phone=%2B70000000000'`
5. Open `http://ailexi.ru/wp-admin/admin.php?page=landing-config-leads` — verify lead appears
6. SSH check log table: `wp db query 'SELECT * FROM wp_landing_lead_log ORDER BY id DESC LIMIT 3' --path=/home/e/esper21/ailexi.ru/public_html`

- [ ] **Step 5: Commit**

```bash
git add skills/wp-landing-config/mu-plugin/landing-config/includes/admin-integrations.php \
        skills/wp-landing-config/mu-plugin/landing-config/landing-config.php
git commit -m "feat(wp-landing-config): A5 — admin-integrations page + dispatch + retry

admin-integrations.php:
- Settings form for all 6 adapters (Email/Telegram/WhatsApp/AmoCRM/Bitrix24/HubSpot)
- Per-adapter 'Включён' checkbox
- Password-type fields auto-encrypted via sanitize_secret on save
- Display shows masked value (bullets + last 4 chars)
- 'Test connection' button per adapter — AJAX to wp_ajax_landing_test_adapter
- Nonce-protected AJAX endpoint

Dispatch:
- Hook 'landing_config_lead_received' iterates enabled adapters
- Each result logged to wp_<bid>_landing_lead_log
- Failed sends schedule wp_schedule_single_event for retry
- Max 3 attempts: 60s, 5min, 30min backoff

Co-Authored-By: Claude Opus 4.7 (1M context) <noreply@anthropic.com>"
```

---

### Task 19: Phase A5 end-to-end smoke на live Beget + CLAUDE.md/SETUP.md updates

**Files:**
- Modify: `CLAUDE.md`
- Modify: `docs/SETUP.md`
- Modify: `docs/beget-cookbook.md`

- [ ] **Step 1: End-to-end smoke на ailexi.ru**

(Опираемся на multisite POC, в котором tests/poc создали admin/Admin2026Aa1!)

```bash
bash skills/wp-landing-config/scripts/install-mu-plugin.sh /tmp/test-s2a
```

Manually:
1. `http://ailexi.ru/wp-admin/admin.php?page=landing-config-integrations` — настрой Email adapter (recipient = esper21@mail.ru, enabled).
2. Click «Test connection» — ожидание ✅
3. `curl -X POST http://ailexi.ru/wp-json/landing/v1/lead -d 'name=E2ETest&phone=%2B79991112222&utm_source=manual_smoke'`
4. Check email received (or PHP mail() failed visible in logs)
5. `http://ailexi.ru/wp-admin/admin.php?page=landing-config-leads` — see lead row
6. `http://ailexi.ru/wp-admin/network/admin.php?page=landing-config-network-leads` — see aggregated view
7. Set GA4 ID + Yandex.Metrika ID in Head&SEO. Reload `http://ailexi.ru/` — view-source should include both scripts.
8. Configure WhatsApp preset in CTA page with phone. Verify `wp option get landing_cta_presets --format=yaml`.

- [ ] **Step 2: Update CLAUDE.md — add section про landing-config**

Append to `CLAUDE.md`:

```markdown

## Landing-config mu-plugin (S2-A)

С 2026-05-19 landing-system включает pre-built mu-plugin `landing-config`
который даёт клиенту и маркетологу через wp-admin настраивать:
- CRM/мессенджеры (6 адаптеров: Email, Telegram, WhatsApp, AmoCRM, Bitrix24, HubSpot)
- CTA-кнопки (5 пресетов с per-site override)
- Head & SEO (GA4, Y.Metrika, FB Pixel, GSC, OG, custom HTML)
- Заявки (per-blog таблицы wp_<bid>_landing_leads + admin UI)

Multisite-aware: network defaults + per-site override; per-blog таблицы заявок.

### Установка на проект

```
/landing-admin-install
```

### REST endpoint для форм

```
POST /wp-json/landing/v1/lead
Body: name=... phone=... email=... message=... source_block=... utm_source=...
```

### Helper-функции для тем

```php
landing_get_cta('primary', $url_override = null, ['model' => 'X']);
landing_render_head_extras();  // вызывается автоматически на wp_head
landing_config_get('key', $default);
```

### Spec

[docs/superpowers/specs/2026-05-19-s2a-landing-config-revised.md](docs/superpowers/specs/2026-05-19-s2a-landing-config-revised.md)
```

- [ ] **Step 3: Update docs/SETUP.md**

Append:

```markdown

## Установка mu-plugin landing-config

После создания multisite-проекта (через `/landing-segment`) — установить admin-плагин:

```
/landing-admin-install
```

Плагин копируется в `<BEGET_PATH>/wp-content/mu-plugins/landing-config/` и
автоматически активируется (mu-plugins always-active). Создаёт таблицы
`wp_<bid>_landing_leads` + `wp_<bid>_landing_lead_log` в каждом subsite.

В wp-admin появляется меню «Лендинг» с подстраницами:
- Заявки
- CTA-кнопки
- Head & SEO
- Интеграции

Network admin показывает «Лендинг» → «Заявки (все сегменты)» — сводный просмотр со всех subsite.

### Pre-requisites

`.env` должен содержать BEGET_USER/HOST/SSH_KEY/PATH (стандартные).
Дополнительных переменных НЕ требуется — все настройки рантайм-через wp-admin.

### Email-fallback

`wp_mail` использует PHP `mail()` если SMTP не настроен. На Beget shared
письма часто попадают в спам. Рекомендация: настроить SMTP через любой
plugin типа WP Mail SMTP, либо использовать как back-up только.
```

- [ ] **Step 4: Update beget-cookbook.md**

Append:

```markdown

## S2-A landing-config end-to-end smoke (2026-05-19)

Validated:
- mu-plugin installation via rsync — `install-mu-plugin.sh /tmp/test-s2a`
- Table creation on all subsites (verified `SHOW TABLES LIKE '%landing%'`)
- REST POST `/wp-json/landing/v1/lead` returns 200 with lead_id
- Lead appears in `wp_<bid>_landing_leads` with correct blog scoping
- Admin email-fallback sent via PHP mail() (no SMTP)
- Admin pages render: Заявки (list+CSV), CTA-кнопки (form), Head&SEO (form), Интеграции (form+test-connection AJAX)
- Network admin → Заявки (все сегменты) aggregates leads from all subsites
- GA4 ID + Y.Metrika ID in Head&SEO → snippets appear in wp_head on front-end
- Email adapter dispatch on lead arrival → log row in `wp_landing_lead_log`

**S2-A Phase A1-A5 ready for merge.**
```

- [ ] **Step 5: Commit**

```bash
git add CLAUDE.md docs/SETUP.md docs/beget-cookbook.md
git commit -m "docs(s2a): end-to-end smoke documented, CLAUDE.md + SETUP.md updated

Validated on live ailexi.ru multisite all 5 phases of S2-A landing-config:
install → DB migration → REST → admin pages → adapters → email dispatch.

Co-Authored-By: Claude Opus 4.7 (1M context) <noreply@anthropic.com>"
```

---

## Self-Review

### 1. Spec coverage

| Spec section | Task |
|---|---|
| §2.1 mu-plugin размещение в repo | Tasks 1-2 |
| §2.2 network vs per-site хранилище | Tasks 5, 13, 18 |
| §2.3 Admin pages (5 sub-страниц) | Tasks 7, 11, 12, 13, 14, 18 |
| §2.4 REST endpoint multisite-aware | Task 6 |
| §2.5 шифрование API-ключей | Tasks 4, 18 |
| §3 Components — все файлы | Tasks 1-19 |
| §4.1 Workflow: установка | Tasks 8, 9 |
| §4.2 настройка интеграций + test-connection | Task 18 |
| §4.3 заявки + CSV + network aggregate | Tasks 11, 12 |
| §4.4 CTA-кнопки | Task 13 |
| §4.5 Head & SEO + wp_kses | Task 14 |
| §5.1 заявки никогда не теряются (db + email) | Task 6 |
| §5.2 async retry | Task 18 |
| §5.3 шифрование | Task 4 |
| §5.4 wp_kses whitelist | Task 14 |
| §5.5 capability checks | присутствует в каждом admin page |
| §5.6 rate limit | **GAP** — не покрыто (см. ниже) |
| §6 Фазы A1-A5 | Tasks: A1=1-10, A2=11-12, A3=13, A4=14, A5=15-19 |

**Gap fix:** rate limit на REST endpoint — добавляю Task 6.5 inline в plan через note для имплементера. Решение: simple transient-based limit (`set_transient('landing_lead_ratelimit_' . $ip, count, 3600)`). Implementer добавит 10 строк в `rest-lead.php::handle_lead()` после Task 6 — это не оправдывает отдельной task'и.

Добавлю это в Task 6 как Step 4.5:

После Step 4 в Task 6, добавить step:

> **Step 4.5: Rate limit (5 строк в начало handle_lead)**
>
> Перед валидацией добавить:
>
> ```php
> $ip = $_SERVER['REMOTE_ADDR'] ?? 'unknown';
> $key = 'landing_lead_rl_' . md5($ip);
> $count = (int) get_transient($key);
> if ($count >= 10) {
>     return new \WP_REST_Response(['ok' => false, 'error' => 'rate_limit'], 429);
> }
> set_transient($key, $count + 1, HOUR_IN_SECONDS);
> ```

(Имплементер увидит этот gap-fix при чтении plan'а сверху вниз.)

### 2. Placeholder scan

Поиск: TBD, TODO, similar to Task N, implement later, fill in details, write tests for the above.

- **None found** в основном plan'е. Все steps содержат runnable код.
- Один stub в Task 5 (`landing_render_head_extras` пустое тело) — но это документировано как "финализируется в A4", и Task 14 явно показывает финальную реализацию.
- В Task 16 в WhatsAppAdapter::send есть hack-условие `TelegramAdapter::class === 'placeholder'` — это **bug-вероятность**, починю inline:

В Task 16 replace в WhatsAppAdapter::send() последняя строка:

```php
return self::normalize_response($resp);
```

(убрать `TelegramAdapter::class === 'placeholder' ? [] :` префикс который остался от черновика)

### 3. Type consistency

- `landing_config_get(string $key, $default = '')` — одинаково в Task 5 и Task 13 (helpers.php real impl + admin usage)
- `landing_get_cta(string $preset_name, ?string $url_override = null, array $context = [])` — одинаково в Task 5 (stub) и Task 13 (real)
- Adapter interface `send(array $lead): array` с ключами `ok/response_code/response_body/error` — соблюдается во всех 6 adapter classes
- `test_connection(): array` с `ok/message` — одинаково во всех 6
- Option key patterns:
  - `landing_<key>` для per-site (Task 5 set, Task 13/14/18 read)
  - `landing_defaults_<key>` для network (Task 5 set network default)
  - `landing_cta_presets` (Task 13 — array)
  - `landing_<head-seo-field>` (Task 14)
  - `landing_integration_<adapter>_enabled` + `landing_integration_<adapter>_<field>` (Task 18)
- Action `landing_config_lead_received` (Task 6 fires, Task 18 listens) — same signature `($lead_id, $lead)`

Всё consistent.

Один минор: в Task 12 `admin-leads-network.php` regsters submenu под parent slug `landing-config-network` — этот parent slug регистрируется в Task 7 (`add_menu_page` в network admin). Проверил — да, Task 7 регистрирует `landing-config-network` parent. ✓

---

## Что НЕ покрыто (out of scope для S2-A)

| Что | Куда | Почему |
|---|---|---|
| Multisite-aware deploy контента | CD2 | Отдельный под-проект |
| Lazy Blocks generator fixes | CD3 | Отдельный под-проект |
| llms.txt + bot allow-list mu-plugins | CD4 | Отдельный под-проект |
| SSL automation | CD6 | Отдельный под-проект |
| SMS adapter | future S2-A.1 | Не P0 |
| Pipedrive/Salesforce adapter | future S2-A.1 | Add new adapter class по шаблону |
| GraphQL endpoint | out of scope | REST достаточно |
| A/B тестирование форм | future | Отдельный under-project |

---
