# HybridAutos WordPress Monitoring Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Make WordPress idempotently save each submitted lead, detect missing leads and delivery failures, and send privacy-safe technical alerts to the existing HybridCars Telegram chat without ever changing a successful lead response.

**Architecture:** The existing `POST /landing/v1/lead` remains primary and returns immediately after the lead and audit rows are durable. Email, Telegram, and Roistat run asynchronously from an exactly-once-per-integration reservation queue; monitoring has a separate incident/Telegram queue. WordPress also issues uncached 12-hour fallback tokens, exposes unsigned public no-PII health plus signed submission-status/external-observation routes, and reconciles five-minute-old form events with the independent delayed Vercel receipt.

**Tech Stack:** PHP 8.3, WordPress MU-plugin and REST API, MySQL/MariaDB `dbDelta`, WP-Cron plus Beget system cron, WordPress HTTP API, Telegram Bot API, standalone PHP CLI tests.

## Global Constraints

- Keep `POST /wp-json/landing/v1/lead` and `/?rest_route=/landing/v1/lead` backward compatible; a missing or invalid `submission_id` follows the existing insert path.
- A valid UUID v4 is the idempotency key; replay returns the original positive `lead_id` and never redispatches Email, Telegram, Roistat, or another adapter.
- A named MySQL lock serializes concurrent requests for the same valid UUID; lock failure returns HTTP 503 after the early contact audit, never inserts a duplicate.
- After a positive lead insert and linked audit, the primary request schedules delivery and returns the positive `lead_id` without waiting for Email, Telegram, Roistat, monitoring, Vercel, or WP-Cron HTTP loopback.
- WordPress never calls Vercel from the normal lead request. After an eligible primary failure, the browser sends the fallback POST immediately with its own 15-second timeout; Vercel stores it immediately and schedules only the reconciliation worker for 45 seconds later.
- Monitoring, receipt checking, alert-table writes, and Telegram alert delivery are best-effort and must never change a safely stored lead's HTTP success response.
- The five-minute missing-lead grace is exactly `300` seconds; scan and queue hooks run once per minute; public health is degraded when the heartbeat is absent, older than `180` seconds, or the previous scheduled run failed.
- The incident table, health output, technical Telegram messages, options, and logs must never contain names, phones, emails, messages, raw IPs, User-Agent values, provider bodies, raw SQL errors, webhook URLs, bot tokens, or signing secrets.
- `form_started`, ordinary abandonment, `validation_failed`, consent rejection, and honeypot traffic never create immediate incidents.
- External receipt states are exactly `pending|delivered|unknown|expired`. `pending,stored=true` is a non-terminal watch, `unknown,stored=true` immediately alerts uncertainty, only `delivered,stored=true` or a WordPress lead is terminal recovery, and `expired,stored=false` reopens/creates missing-lead. A pending watch older than 10 minutes alerts stuck delivery while the contact is still recoverable.
- Monitoring Telegram uses the existing HybridCars bot/chat through an independent client; it must not call `dispatch_all_integrations()`, `_send_telegram()`, or `TelegramAdapter::send()`.
- No reCAPTCHA, Turnstile, or other third-party challenge is introduced.
- Deploy code with `LP_MONITOR_ENABLED=false`; enable only after backup, migration, cron, unsigned public health, signed submission-status/external-observation, and `[TEST — DO NOT CONTACT]` alert checks pass.
- WordPress constants are the exact union: `LP_MONITOR_ENABLED`, `LP_FALLBACK_ENABLED`, `LP_FALLBACK_URL`, `LP_FALLBACK_SIGNING_SECRET`, `LP_FALLBACK_STATUS_URL`, `LP_FALLBACK_STATUS_SECRET`, `LP_FALLBACK_SITE_ID`, `LP_FALLBACK_TEST_MODE`, `LP_MONITOR_TELEGRAM_INTEGRATION_ID`.
- `LP_FALLBACK_SIGNING_SECRET` and `LP_FALLBACK_STATUS_SECRET` are different literal HMAC keys, each matching `^[a-f0-9]{64}$`; neither may come from WordPress salts, appear in cached HTML, logs, admin output, browser storage, or Git.
- The fallback-token route is always same-origin/no-store and rate-limited to 60 successful bundles per HMAC-IP per hour under a named lock. Public requests receive `mode=live` only when `LP_FALLBACK_ENABLED===true`. `LP_FALLBACK_TEST_MODE===true` never makes the route public: `mode=test` additionally requires a logged-in `manage_options` administrator and a valid `X-WP-Nonce` for action `wp_rest`; while live fallback is false, every ordinary, unauthenticated, non-admin, missing-nonce, or bad-nonce request returns the same 404.
- No catch block hashes or logs raw exception text. Logs and incidents use fixed safe categories from an allow-list only.
- Before every production-file edit, including `landing-config.php`, first run the focused new test and record the expected failing assertion. A test that is already green does not authorize that edit; strengthen it until it observes the missing behavior.
- `landing_leads.processed_status` remains exclusively the business/CRM status. Delivery queue state exists only in `landing_lead_log` and cron state.
- Status HMAC is lowercase hex `HMAC-SHA256("GET\n<path>\n<unix timestamp>\nhybridautos-ae", hex2bin(LP_FALLBACK_STATUS_SECRET))` with a maximum clock skew of `300` seconds; strict decoding must yield exactly 32 bytes.
- Production release requires an exact server-side integration inventory: precisely one enabled lead Email recipient equal to `elapova00@gmail.com`, every prior Neuroboost Email/integration disabled, and the recorded Telegram plus Roistat/CRM integrations enabled. Admin/health evidence exposes booleans and IDs only, never the address or credentials; a mismatch blocks release.
- A missing-lead Telegram alert contains no contact, but reports whether an exact private audit row exists, its numeric ID, and an authenticated admin URL using a prepared exact UUID filter. No audit row means the alert explicitly directs recovery to the independent fallback.
- Manual audit promotion requires `pd_consent=1` and at least one phone/email, uses a named lock, reuses an existing valid submission UUID, and after a new insert reserves/schedules every exact enabled integration. Consentless, contactless, and repeated rows are skipped without delivery.
- Status live-smoke is available only while `LP_FALLBACK_TEST_MODE===true`: nonce-protected `manage_options` POST body arms one exact UUID for at most 180 seconds. The first correctly HMAC-signed status request atomically returns generic no-store 503; the second follows the normal lookup. No public control route/query, raw UUID log/notification, or UUID-bearing redirect is allowed.

---

## File Map and Stable Interfaces

| File | Change | Responsibility |
|---|---|---|
| `skills/wp-landing-config/mu-plugin/landing-config/includes/db.php` | Modify | DB version `1.1.0`, `integration_id` delivery column, per-blog `landing_monitor_alerts` schema. |
| `skills/wp-landing-config/mu-plugin/landing-config/includes/rest-lead.php` | Modify | Primary UUID lock/replay, exact integration IDs in delivery logs, non-blocking monitoring observation. |
| `skills/wp-landing-config/mu-plugin/landing-config/includes/lead-delivery-worker.php` | Create | Exact integration reservations, asynchronous delivery, named lead lock, stale-sending classification. |
| `skills/wp-landing-config/mu-plugin/landing-config/includes/monitoring-alerts.php` | Create | Incident allow-lists/upsert, missing-lead scan, Vercel receipt lookup, Telegram client/queue, cron/heartbeat. |
| `skills/wp-landing-config/mu-plugin/landing-config/includes/rest-fallback-token.php` | Create | Uncached same-origin 12-hour fallback token bundle and safe rate limit. |
| `skills/wp-landing-config/mu-plugin/landing-config/includes/rest-health.php` | Create | Public health, signed submission-status lookup, and signed Redis-health observation fallback. |
| `skills/wp-landing-config/mu-plugin/landing-config/includes/admin-monitoring.php` | Create | Read-only Monitoring page and nonce-protected safe test-alert action. |
| `skills/wp-landing-config/mu-plugin/landing-config/includes/admin-lead-audit.php` | Modify | Prepared exact UUID filter, safe audit pointer target, consent/contact-gated idempotent promotion and exact async integration reservations. |
| `skills/wp-landing-config/mu-plugin/landing-config/landing-config.php` | Modify | Load modules in deterministic order. |
| `skills/wp-landing-config/tests/fixtures/wp-bootstrap.php` | Modify | Header-aware REST request/response, GET HTTP mock, lock/query support. |
| `skills/wp-landing-config/tests/fixtures/lead-reliability-bootstrap.php` | Modify | In-memory UUID lookup, alert rows, atomic claim controls. |
| `skills/wp-landing-config/tests/test_db_schema.php` | Modify | Migration, isolation, integration-ID and privacy assertions. |
| `skills/wp-landing-config/tests/test_rest_lead_idempotency.php` | Create | Replay, concurrency, legacy request and no-redelivery tests. |
| `skills/wp-landing-config/tests/test_rest_fallback_token.php` | Create | Exact token bundle/HMAC, flags, same-origin, no-store and rate limit. |
| `skills/wp-landing-config/tests/test_lead_delivery_worker.php` | Create | Async response, unique reservation, named lock, stale sending and no blind resend. |
| `skills/wp-landing-config/tests/test_monitoring_incidents.php` | Create | Delivery observation, strict safe incident contract and deduplication. |
| `skills/wp-landing-config/tests/test_monitoring_detector.php` | Create | Five-minute classification and external-receipt suppression. |
| `skills/wp-landing-config/tests/test_monitoring_queue.php` | Create | Atomic claim, non-recursive Telegram, exact confirmation, retry/failure state. |
| `skills/wp-landing-config/tests/test_rest_health.php` | Create | Health states, signature validation and no-secret output. |
| `skills/wp-landing-config/tests/test_admin_monitoring.php` | Create | Capability, nonce, read-only safe output and test prefix. |
| `skills/wp-landing-config/tests/test_monitoring_privacy.php` | Create | Cross-module PII/credential storage and message regression gate. |

Stable PHP interfaces used across tasks:

```php
namespace LandingConfig\Monitoring;

function is_enabled(): bool;
function record_incident(string $kind, string $severity, ?string $submission_id,
    ?int $lead_id, ?int $integration_id, string $adapter, string $safe_status,
    string $safe_category, ?int $provider_response_code = null,
    string $resolution = '', ?int $now = null): int;
function observe_delivery_result(int $lead_id, int $integration_id, string $adapter,
    string $status, string $safe_category, ?int $response_code): void;
function classify_timeline(array $events): ?array;
function fetch_external_receipt_status(string $submission_id, ?int $now = null): array;
function run_missing_lead_scan(int $limit = 100, ?int $now = null): array;
function claim_next_alert(?int $now = null): ?array;
function run_alert_queue(int $limit = 10, ?int $now = null): array;
function touch_heartbeat(bool $ok, ?int $now = null): void;
function configuration_status(): array;
function cleanup_expired_alerts(?int $now = null): array;
function record_external_incident(string $kind, string $safe_category,
    int $episode_generation, ?int $now = null): int;
function check_external_monitor_stale(?int $now = null): array;

namespace LandingConfig\REST;
function acquire_submission_lock(string $submission_id): bool;
function release_submission_lock(string $submission_id): void;
function find_lead_id_by_submission(string $submission_id): int;

namespace LandingConfig\LeadDelivery;
function reserve_integrations(int $lead_id): int;
function run_delivery_worker(int $limit = 20, ?int $now = null): array;
function mark_stale_sending_unknown(?int $now = null): int;

namespace LandingConfig\FallbackToken;
function resolve_token_mode($request): ?string;
function build_token_bundle(string $mode, ?int $now = null): ?array;
function handle_token($request);

namespace LandingConfig\Health;
function build_health_payload(?int $now = null): array;
function handle_health($request);
function handle_submission_status($request);
```

The Vercel receipt response consumed by WordPress is exactly:

```json
{"ok":true,"submission_id":"11111111-1111-4111-8111-111111111111","exists":true,"stored":true,"delivery_state":"pending"}
```

`delivery_state` is exactly one of `pending`, `delivered`, `unknown`, or `expired`. Only `stored=true` suppresses a missing-lead alert. `expired` with `stored=false` is not recovery. The signed WordPress reconciliation response is exactly `{"ok":true,"site_id":"hybridautos-ae","submission_id":"<uuid>","exists":true}` and contains no lead ID or contact. The public WordPress health response is exactly:

```json
{"ok":true,"site_id":"hybridautos-ae","site":"ok","lead_endpoint":"ok","database":"ok","monitor_heartbeat":"ok","heartbeat_age_seconds":42,"checked_at":1784190000}
```

The uncached fallback-token response is exactly:

```json
{"ok":true,"site_id":"hybridautos-ae","protocol_version":"1","privacy_policy_version":"2026-07-16","mode":"live","issued_at":1784190000,"expires_at":1784233200,"nonce":"0123456789abcdef0123456789abcdef","token":"v1.1784190000.1784233200.0123456789abcdef0123456789abcdef.live.<64-lowercase-hex-hmac>"}
```

The token HMAC canonical bytes are `v1\nhybridautos-ae\n<issued_at>\n<expires_at>\n<nonce>\n<mode>` and expiry is exactly 43,200 seconds. Every shared 64-lowercase-hex HMAC secret is strictly decoded with `hex2bin` to 32 binary bytes before `hash_hmac`; the hex text itself is never used as the HMAC key. `mode=test` is issued only when `LP_FALLBACK_TEST_MODE===true`, the request belongs to a logged-in `manage_options` administrator, and `X-WP-Nonce` passes `wp_verify_nonce($nonce, 'wp_rest')`; a browser primary-failure simulation is invalid without that signed test claim. The nonce used to authorize this test-token request is exposed only as admin-only `testRestNonce` in the no-store monitoring/test bootstrap and is never part of cached public HTML, browser persistence, or the signed intake token.

## Task 1: Extend the Test Harness and Add the Safe Schema

**Files:**
- Modify: `skills/wp-landing-config/tests/fixtures/wp-bootstrap.php`
- Modify: `skills/wp-landing-config/tests/fixtures/lead-reliability-bootstrap.php`
- Modify: `skills/wp-landing-config/tests/test_lead_reliability_fixture.php`
- Modify: `skills/wp-landing-config/tests/test_db_schema.php`
- Modify: `skills/wp-landing-config/mu-plugin/landing-config/includes/db.php`

**Interfaces:**
- Consumes: existing blog-prefix helpers and `dbDelta()` migration flow.
- Produces: `DB_VERSION='1.1.0'`, `DB\get_monitor_alerts_table_name(): string`, six per-blog tables, and mocks required by every later task.

- [ ] **Step 1: Add failing schema and fixture assertions**

Append concrete assertions to `test_db_schema.php`:

```php
use function LandingConfig\DB\get_monitor_alerts_table_name;

set_mock_current_blog_id(2);
assert_test(get_monitor_alerts_table_name() === 'wp_2_landing_monitor_alerts', 'monitor incidents are isolated per blog');
assert_test(\LandingConfig\DB\DB_VERSION === '1.1.0', 'monitoring migration has version 1.1.0');

$schema_sql = implode("\n", $GLOBALS['_mock_dbdelta_calls']);
assert_test(str_contains($schema_sql, 'integration_id BIGINT(20) UNSIGNED NOT NULL DEFAULT 0'), 'delivery rows store exact integration id');
assert_test(str_contains($schema_sql, 'next_attempt_at DATETIME NULL'), 'delivery rows carry queue due time');
assert_test(str_contains(implode("\n", $GLOBALS['wpdb']->query_log), 'UNIQUE KEY delivery_attempt (lead_id,integration_id,attempt)'), 'migration installs exact reservation key');
assert_test(str_contains($schema_sql, 'UNIQUE KEY fingerprint (fingerprint)'), 'incident fingerprint is unique');
assert_test(str_contains($schema_sql, 'fingerprint_scope BIGINT(20) UNSIGNED NOT NULL DEFAULT 0'), 'incident stores privacy-safe external generation');
preg_match('/CREATE TABLE wp_landing_monitor_alerts \((.*?)\) DEFAULT CHARACTER SET/s', $schema_sql, $monitor_match);
$monitor_sql = $monitor_match[1] ?? '';
foreach (['name','phone','email','message','ip ','user_agent','response_body','error_text','token','webhook'] as $forbidden) {
    assert_test(!preg_match('/\\b' . preg_quote(trim($forbidden), '/') . '\\b/i', $monitor_sql), "monitor schema excludes {$forbidden}");
}
```

Change the single-site expected `dbDelta` count from `5` to `6`, and the total schema `submission_id CHAR(36)` count from `3` to `4`.

Extend `test_lead_reliability_fixture.php` with header and HTTP-GET controls:

```php
$request = new WP_REST_Request([], '', ['X-LP-Timestamp' => '1784190000']);
$assert($request->get_header('x-lp-timestamp') === '1784190000', 'REST mock reads headers case-insensitively');
lr_set_http(['response' => ['code' => 404], 'body' => '{"ok":true,"exists":false,"stored":false}', 'headers' => []]);
$http = wp_remote_get('https://fallback.invalid/api/v1/receipts/uuid', []);
$assert(wp_remote_retrieve_response_code($http) === 404, 'HTTP GET mock is controllable');
```

- [ ] **Step 2: Run the red tests**

Run:

```bash
php skills/wp-landing-config/tests/test_lead_reliability_fixture.php
php skills/wp-landing-config/tests/test_db_schema.php
```

Expected: both exit `1`; failures name missing header/GET support, missing alert table, missing `integration_id`, and DB version `1.1.0`.

- [ ] **Step 3: Upgrade the test doubles**

Change `WP_REST_Request` and `WP_REST_Response` in `wp-bootstrap.php` to the exact behavior below, and route GET requests through the existing HTTP capture:

```php
class WP_REST_Response {
    public $data; public $status; public array $headers = [];
    public function __construct($data, $status = 200) { $this->data = $data; $this->status = $status; }
    public function get_status() { return $this->status; }
    public function get_data() { return $this->data; }
    public function header($key, $value) { $this->headers[strtolower((string)$key)] = (string)$value; }
}

class WP_REST_Request {
    private array $params; private string $body; private array $headers;
    public function __construct(array $params = [], string $body = '', array $headers = []) {
        $this->params = $params; $this->body = $body;
        $this->headers = array_change_key_case($headers, CASE_LOWER);
    }
    public function get_params() { return $this->params; }
    public function get_param($key) { return $this->params[$key] ?? null; }
    public function get_body() { return $this->body; }
    public function get_header($key) { return $this->headers[strtolower((string)$key)] ?? ''; }
}

function wp_remote_get($url, $args = []) {
    $GLOBALS['_lr_http_requests'][] = ['method' => 'GET', 'url' => $url, 'args' => $args];
    return $GLOBALS['_lr_http'];
}
```

Make `wp_remote_post()` capture `'method' => 'POST'`. Add controllable `_lr_force_lock_failure`, row queues, and `query_log` to `MockWpdbInsert`; preserve the richer overrides already present in `LeadReliabilityWpdb`.

- [ ] **Step 4: Implement schema `1.1.0`**

In `db.php`, set `const DB_VERSION = '1.1.0';`, add:

```php
function get_monitor_alerts_table_name(): string {
    global $wpdb;
    return $wpdb->get_blog_prefix() . 'landing_monitor_alerts';
}
```

Add `integration_id BIGINT(20) UNSIGNED NOT NULL DEFAULT 0` after `adapter`, change status default to `queued`, and add `next_attempt_at DATETIME NULL`, `locked_at DATETIME NULL`, `finished_at DATETIME NULL`, `provider_id BIGINT(20) UNSIGNED NULL`, `KEY delivery_queue (status,next_attempt_at)`, and `KEY lead_integration (lead_id,integration_id)` to `$log_sql`. Do not read or write `landing_leads.processed_status` for queue decisions. In `create_tables_for_current_blog()`, declare `$alerts = get_monitor_alerts_table_name();` and the exact privacy-safe schema:

```php
$alerts_sql = "CREATE TABLE $alerts (
    id BIGINT(20) UNSIGNED NOT NULL AUTO_INCREMENT,
    fingerprint CHAR(64) NOT NULL,
    incident_kind VARCHAR(32) NOT NULL,
    severity VARCHAR(16) NOT NULL,
    submission_id CHAR(36) NULL,
    lead_id BIGINT(20) UNSIGNED NULL,
    integration_id BIGINT(20) UNSIGNED NULL,
    fingerprint_scope BIGINT(20) UNSIGNED NOT NULL DEFAULT 0,
    adapter VARCHAR(64) NOT NULL DEFAULT '',
    safe_status VARCHAR(32) NOT NULL DEFAULT '',
    safe_category VARCHAR(64) NOT NULL DEFAULT '',
    provider_response_code SMALLINT UNSIGNED NULL,
    occurrence_count INT UNSIGNED NOT NULL DEFAULT 1,
    first_seen_at DATETIME NOT NULL,
    last_seen_at DATETIME NOT NULL,
    due_at DATETIME NOT NULL,
    locked_at DATETIME NULL,
    lock_token CHAR(36) NULL,
    sent_at DATETIME NULL,
    resolved_at DATETIME NULL,
    resolution VARCHAR(32) NOT NULL DEFAULT '',
    telegram_status VARCHAR(32) NOT NULL DEFAULT 'pending',
    send_attempts SMALLINT UNSIGNED NOT NULL DEFAULT 0,
    last_response_at DATETIME NULL,
    telegram_response_code SMALLINT UNSIGNED NULL,
    telegram_message_id BIGINT(20) UNSIGNED NULL,
    PRIMARY KEY (id),
    UNIQUE KEY fingerprint (fingerprint),
    KEY queue_due (telegram_status,resolved_at,due_at),
    KEY submission_id (submission_id),
    KEY lead_integration (lead_id,integration_id)
) $charset;";
```

Call `dbDelta($alerts_sql);` after the five existing calls. Then run explicit idempotent `ensure_delivery_reservation_index()`: after new columns exist, set `attempt=id` only on historical `integration_id=0` rows, inspect `SHOW INDEX`, and add `UNIQUE KEY delivery_attempt (lead_id,integration_id,attempt)` only when absent. New reservations always have a positive integration ID and start at attempt 1. Tests cover two legacy `integration_id=0,attempt=1` rows and prove migration preserves both rows and installs the key.

- [ ] **Step 5: Run the green tests and commit**

Run:

```bash
php skills/wp-landing-config/tests/test_lead_reliability_fixture.php
php skills/wp-landing-config/tests/test_db_schema.php
php -l skills/wp-landing-config/mu-plugin/landing-config/includes/db.php
```

Expected: both test files print `PASS`/`0 failures`; lint prints `No syntax errors detected`.

```bash
git add skills/wp-landing-config/mu-plugin/landing-config/includes/db.php skills/wp-landing-config/tests/fixtures skills/wp-landing-config/tests/test_db_schema.php skills/wp-landing-config/tests/test_lead_reliability_fixture.php
git commit -m "feat: add privacy-safe monitoring schema"
```

## Task 2: Make Primary Submission Idempotent

**Files:**
- Create: `skills/wp-landing-config/tests/test_rest_lead_idempotency.php`
- Create: `skills/wp-landing-config/tests/test_lead_delivery_worker.php`
- Create: `skills/wp-landing-config/mu-plugin/landing-config/includes/lead-delivery-worker.php`
- Modify: `skills/wp-landing-config/mu-plugin/landing-config/includes/rest-lead.php`

**Interfaces:**
- Consumes: valid UUID, early audit, enabled integration records and existing adapters.
- Produces: UUID replay plus durable per-integration reservations and asynchronous worker; the primary response never waits for an adapter.

- [ ] **Step 1: Write the failing replay and concurrency tests**

Create `test_rest_lead_idempotency.php` with these scenarios: first request durably saves lead/audit and one `queued` attempt-1 reservation per enabled integration but performs zero HTTP/mail adapter calls; replay returns the same ID without another lead/reservation/schedule; forced UUID-lock contention returns 503 after one audit and no lead; no/invalid UUID remains backward compatible. Use integration ID 7, UUID `11111111-1111-4111-8111-111111111111`, phone `+971501111111`, and prove lock SQL contains no phone.

Create `test_lead_delivery_worker.php` before creating the worker. Required RED observations: unique `(lead_id,integration_id,attempt)` rejects a second reservation; worker loads contact from `landing_leads`, named-locks by lead ID, conditionally changes one due `queued→sending` before the first external call, then records the confirmed result; two workers send once; stale `sending` becomes `unknown` and is never sent. A definite HTTP 429 terminally marks attempt N `retry_wait`, inserts exactly one separate `queued` attempt N+1 with its due time, and never reclaims attempt N; a concurrent duplicate insertion loses to the unique key. Attempts are capped at three total calls; the third 429 becomes `failed_permanent` with no attempt 4. The delay is a valid normalized `Retry-After` clamped to 1..3600 seconds, otherwise exactly 60 seconds. 5xx, timeout, malformed response, and adapter exception become `unknown` with no blind retry; a lead lacking delivery rows is reconciled into reservations and a cron event; no code reads/writes `processed_status`.

Core assertions:

```php
$first = handle_lead(idempotent_request());
$lead_id = (int)$first->get_data()['lead_id'];
$lead_count = count(lr_rows(\LandingConfig\DB\get_leads_table_name()));
$delivery_count = count(lr_rows(\LandingConfig\DB\get_lead_log_table_name()));
$assert(count($GLOBALS['_lr_http_requests']) === 0 && count($GLOBALS['_mock_mail_sent']) === 0, 'primary response waits for no adapter');
lr_queue_row(['id' => $lead_id]);
$replay = handle_lead(idempotent_request());
$assert($replay->get_status() === 200, 'replay succeeds');
$assert($replay->get_data() === ['ok' => true, 'lead_id' => $lead_id, 'replayed' => true], 'replay returns original lead');
$assert(count(lr_rows(\LandingConfig\DB\get_leads_table_name())) === $lead_count, 'replay inserts no lead');
$assert(count(lr_rows(\LandingConfig\DB\get_lead_log_table_name())) === $delivery_count, 'replay redelivers nothing');

lr_reset_state();
$GLOBALS['_lr_force_lock_failure'] = true;
$busy = handle_lead(idempotent_request());
$assert($busy->get_status() === 503, 'contended UUID returns retryable 503');
$assert(lr_rows(\LandingConfig\DB\get_leads_table_name()) === [], 'contended UUID creates no duplicate');
$assert(count(lr_rows(\LandingConfig\DB\get_lead_audit_table_name())) === 1, 'early recoverable audit survives contention');
```

- [ ] **Step 2: Verify RED**

Run `php skills/wp-landing-config/tests/test_rest_lead_idempotency.php`.

Expected: exit `1`; replay/idempotency is absent and the primary path still calls adapters synchronously. Also run `php skills/wp-landing-config/tests/test_lead_delivery_worker.php`; expected exit 1 because the worker is absent. Record both RED outputs before editing either production file.

- [ ] **Step 3: Implement the named lock and replay lookup**

Add to `rest-lead.php`:

```php
const SUBMISSION_LOCK_WAIT_SECONDS = 3;

function submission_lock_name(string $submission_id): string {
    return 'lpl_' . get_current_blog_id() . '_' . substr(hash('sha256', $submission_id), 0, 32);
}

function acquire_submission_lock(string $submission_id): bool {
    global $wpdb;
    return (int)$wpdb->get_var($wpdb->prepare(
        'SELECT GET_LOCK(%s, %d)', submission_lock_name($submission_id), SUBMISSION_LOCK_WAIT_SECONDS
    )) === 1;
}

function release_submission_lock(string $submission_id): void {
    global $wpdb;
    $wpdb->get_var($wpdb->prepare('SELECT RELEASE_LOCK(%s)', submission_lock_name($submission_id)));
}

function find_lead_id_by_submission(string $submission_id): int {
    global $wpdb;
    $row = $wpdb->get_row($wpdb->prepare(
        'SELECT id FROM `' . get_leads_table_name() . '` WHERE submission_id=%s ORDER BY id ASC LIMIT 1',
        $submission_id
    ), ARRAY_A);
    return is_array($row) ? max(0, (int)($row['id'] ?? 0)) : 0;
}
```

After honeypot and exact consent checks but before the rate-limit counter, use this exact branch:

```php
$submission_id = $normalized['submission_id'];
if ($submission_id !== null) {
    if (!acquire_submission_lock($submission_id)) {
        audit_log_block($audit_id, 'idempotency_busy', 'submission lock busy');
        return new \WP_REST_Response(['ok' => false, 'error' => 'temporarily_unavailable'], 503);
    }
    try {
        $existing_lead_id = find_lead_id_by_submission($submission_id);
        if ($existing_lead_id > 0) {
            audit_log_success($audit_id, $existing_lead_id);
            return new \WP_REST_Response([
                'ok' => true,
                'lead_id' => $existing_lead_id,
                'replayed' => true,
            ], 200);
        }
        return store_new_lead($params, $normalized, $audit_id, (string)$ip);
    } finally {
        release_submission_lock($submission_id);
    }
}
return store_new_lead($params, $normalized, $audit_id, (string)$ip);
```

Create `store_new_lead(...)` by moving the existing rate limit, validation, data construction, INSERT/fallback INSERT, positive-ID check and audit-success code. Replace synchronous `dispatch_all_integrations()` with a best-effort `LeadDelivery\reserve_integrations($lead_id)` followed by `wp_schedule_single_event(time(), 'landing_config_deliver_lead', [$lead_id])` and guarded nonblocking `spawn_cron()`. Catch failures with fixed category `delivery_schedule_failed` only; never log exception text. Fire the existing action and return the existing `{ok:true,lead_id}` immediately. Reservation/cron failure cannot change that response because the monitor reconciles saved leads lacking delivery rows.

- [ ] **Step 4: Implement the delivery worker after its RED result**

`reserve_integrations()` inserts `queued` attempt 1 rows using exact positive integration IDs and the unique reservation key. `run_delivery_worker()` loads the lead server-side, acquires named lock `lpd_<blog>_<lead>`, atomically claims only one due `queued` row by changing it to `sending` with `locked_at` before any external call, loads that exact enabled integration, and calls its adapter. Confirmed Email is `accepted`; confirmed Telegram/Roistat is `success`. On a definite HTTP 429, within the same named lock/transaction mark attempt N `retry_wait` as terminal for that attempt and `INSERT IGNORE` exactly one `queued` attempt N+1 due after normalized `Retry-After` clamped to 1..3600 seconds (default 60); schedule one worker event. Never claim `retry_wait` itself. Maximum attempt is 3; a 429 on attempt 3 becomes `failed_permanent` and creates no successor. Timeout, 5xx, malformed response, adapter exception, missing integration, and stale sending become terminal `unknown`/`failed_permanent` without resend. `mark_stale_sending_unknown()` uses five minutes. The hook and one-minute system cron are backups for each other.

- [ ] **Step 5: Run focused and regression tests**

Run:

```bash
php skills/wp-landing-config/tests/test_rest_lead_idempotency.php
php skills/wp-landing-config/tests/test_rest_lead.php
php skills/wp-landing-config/tests/test_rest_lead_field_limits.php
php skills/wp-landing-config/tests/test_urgent_delivery_log.php
php skills/wp-landing-config/tests/test_lead_delivery_worker.php
```

Expected: all five exit 0; primary makes no adapter call, worker delivers once, replay adds no reservation, legacy requests remain green.

- [ ] **Step 6: Commit**

```bash
git add skills/wp-landing-config/mu-plugin/landing-config/includes/rest-lead.php skills/wp-landing-config/mu-plugin/landing-config/includes/lead-delivery-worker.php skills/wp-landing-config/tests/test_rest_lead_idempotency.php skills/wp-landing-config/tests/test_lead_delivery_worker.php
git commit -m "feat: save immediately and deliver leads asynchronously"
```

## Task 3: Observe Asynchronous Delivery Reservations and Safe Incidents

**Files:**
- Create: `skills/wp-landing-config/mu-plugin/landing-config/includes/monitoring-alerts.php`
- Create: `skills/wp-landing-config/tests/test_monitoring_incidents.php`
- Modify: `skills/wp-landing-config/mu-plugin/landing-config/includes/lead-delivery-worker.php`
- Modify: `skills/wp-landing-config/tests/test_urgent_delivery_log.php`

**Interfaces:**
- Consumes: worker-owned delivery rows already tied to exact integration IDs.
- Produces: strict incident upsert, delivery failure/recovery observation, and queued/stuck reconciliation without touching lead business status.

- [ ] **Step 1: Write failing integration and privacy tests**

Test two exact integration reservations IDs 11/12; accepted/success resolve/no-alert; unknown/failed_permanent create one fingerprint per `(site,lead,integration)`; a `retry_wait` attempt with its valid queued successor does not alert, while a missing or overdue successor creates the one safe stuck fingerprint; duplicate observation increments only occurrence count. Add RED cases for a lead older than one minute with no delivery rows (recreate reservations+cron), queued older than five minutes (safe `delivery_stuck` incident), and stale sending (worker changes to unknown, monitor alerts, never resends). Assert `processed_status` is unchanged and raw contact/provider/exception markers appear nowhere.

- [ ] **Step 2: Verify RED**

Run:

```bash
php skills/wp-landing-config/tests/test_monitoring_incidents.php
php skills/wp-landing-config/tests/test_urgent_delivery_log.php
```

Expected: missing incident core and delivery reconciliation assertions fail. Record RED before creating `monitoring-alerts.php` or editing the worker.

- [ ] **Step 3: Create the strict incident core**

Start `monitoring-alerts.php` with exact constants and allow-lists:

```php
<?php
namespace LandingConfig\Monitoring;
if (!defined('ABSPATH')) { exit; }

use function LandingConfig\DB\get_monitor_alerts_table_name;

const ENABLED_OPTION = 'landing_monitor_enabled';
const HEARTBEAT_OPTION = 'landing_monitor_last_heartbeat';
const RUN_STATUS_OPTION = 'landing_monitor_last_run_status';
const EXTERNAL_HEALTH_OPTION = 'landing_monitor_last_external_health_result';
const SCAN_HOOK = 'landing_config_monitor_scan';
const QUEUE_HOOK = 'landing_config_monitor_queue';
const GRACE_SECONDS = 300;
const HEARTBEAT_STALE_SECONDS = 180;
const LOCK_TTL_SECONDS = 120;
const MAX_SEND_ATTEMPTS = 3;

function is_enabled(): bool {
    if (defined('LP_MONITOR_ENABLED')) return LP_MONITOR_ENABLED === true;
    return (string)get_option(ENABLED_OPTION, '0') === '1';
}

function allowed_incident_kinds(): array {
    return ['missing_lead','javascript_stall','integration_failure','delivery_stuck',
        'fallback_receipt_watch','fallback_delivery_stuck','fallback_delivery_uncertain',
        'external_outage','external_recovery','external_monitor_stale','external_monitor_recovery',
        'monitor_internal_failure','test_alert'];
}
function allowed_severities(): array { return ['info','warning','critical']; }
function allowed_statuses(): array {
    return ['request_started','request_failed','submit_attempt','pending','delivered','unknown','expired',
        'ok','failed','retry_wait','failed_permanent','watching','test'];
}
function allowed_categories(): array {
    return ['missing_wordpress_lead','browser_javascript_stall','external_receipt_confirmed',
        'configuration_missing','unsupported_adapter','adapter_exception','invalid_adapter_result',
        'transport_error','provider_4xx','provider_5xx','rate_limited','invalid_response',
        'delivery_rows_missing','delivery_queued_stuck','delivery_sending_stale',
        'fallback_receipt_watch','fallback_delivery_stuck','fallback_delivery_uncertain',
        'redis_outage','redis_recovery','external_monitor_stale','external_monitor_recovery',
        'monitor_scan_failed','monitor_queue_failed','test'];
}
function allowed_resolutions(): array { return ['','external_recovered','wordpress_lead_saved','delivery_recovered']; }
function utc_mysql(int $timestamp): string { return gmdate('Y-m-d H:i:s', $timestamp); }
```

Implement `record_incident()` as one prepared `INSERT ... ON DUPLICATE KEY UPDATE` using fingerprint:

```php
$fingerprint = hash('sha256', implode('|', [get_current_blog_id(), $kind,
    $submission_id ?? '', $lead_id ?? 0, $integration_id ?? 0, $adapter, 0]));
```

Keep the public `record_incident()` signature stable. It calls one private prepared `record_incident_scoped(..., int $fingerprint_scope, ?int $now)` with scope `0`. Add dedicated `record_external_incident($kind,$safe_category,$episode_generation,$now)`: it accepts only `external_outage|external_recovery|external_monitor_stale|external_monitor_recovery`, matching fixed categories, and a positive integer generation; it passes no submission/lead/integration/free-text adapter, stores the integer in `fingerprint_scope`, and includes it in the hash. Generic callers cannot set a non-zero scope, and generation is never encoded in `adapter`. Tests require rejection for an external generation on any other incident kind, one row/message for repeats inside an episode, and a new row/message for a later generation.

Reject any value outside the exact allow-lists, invalid UUID, non-positive IDs, adapter not matching `/^[a-z0-9_-]{0,64}$/`, or response code outside `100..599`. Store only the schema fields from Task 1. On duplicate update only `occurrence_count=occurrence_count+1`, `last_seen_at`, safe status/category/code, and a non-empty resolution; never reset `sent_at`, `telegram_status`, or a prior resolution.

Implement delivery observation:

```php
function observe_delivery_result(int $lead_id, int $integration_id, string $adapter,
    string $status, string $safe_category, ?int $response_code): void {
    if (!is_enabled() || $lead_id <= 0 || $integration_id <= 0) return;
    if (in_array($status, ['success','accepted'], true)) {
        resolve_integration_incident($lead_id, $integration_id, $adapter, 'delivery_recovered');
        return;
    }
    // A definite 429 is not an incident while its one bounded successor is
    // correctly queued. Reconciliation below owns the missing/overdue case.
    if (!in_array($status, ['unknown','failed_permanent'], true)) return;
    record_incident('integration_failure', 'critical', null, $lead_id, $integration_id,
        $adapter, $status, $safe_category, $response_code);
}
```

- [ ] **Step 4: Observe worker results and reconcile missing/stuck queue rows**

The worker calls the observer only after it has updated the reservation row. It passes only fixed safe category, exact IDs, adapter, status, and numeric code:

```php
function observe_worker_result(int $lead_id, int $integration_id, string $adapter,
    string $status, string $safe_category, ?int $response_code): void {
    try {
        \LandingConfig\Monitoring\observe_delivery_result(
            $lead_id, $integration_id, sanitize_key($adapter), $status,
            $safe_category, $response_code
        );
    } catch (\Throwable $ignored) {
        error_log('[landing-config] monitor_observe_failed');
    }
}
```

Normalize adapter output inside the worker before persistence. It may inspect raw adapter output in memory but returns/stores only this safe category:

```php
function safe_delivery_error_category(array $result, ?int $code): string {
    $known = ['configuration_missing','unsupported_adapter','adapter_exception','invalid_adapter_result','transport_error'];
    $raw = is_string($result['error'] ?? null) ? $result['error'] : '';
    if (in_array($raw, $known, true)) return $raw;
    if ($code === 429) return 'rate_limited';
    if ($code !== null && $code >= 500) return 'provider_5xx';
    if ($code !== null && $code >= 400) return 'provider_4xx';
    if ($code === null) return 'transport_error';
    return 'invalid_response';
}
```

Add `reconcile_delivery_rows()`: select saved leads older than one minute that have no `landing_lead_log` rows, call `LeadDelivery\reserve_integrations($lead_id)`, and schedule the delivery hook; select queued rows older than five minutes into one deduplicated `delivery_stuck/delivery_queued_stuck` incident. Separately inspect each terminal `retry_wait` row: while its one `attempt+1` successor exists and is queued with a future `next_attempt_at`, do not alert; if that exact successor is absent or its due time is older than five minutes, create the same one deduplicated stuck incident. Never reclaim or resend the old `retry_wait` row. Never use `processed_status`. Stale sending is classified by the worker as unknown before monitoring observes it.

- [ ] **Step 5: Run tests and commit**

Run:

```bash
php skills/wp-landing-config/tests/test_monitoring_incidents.php
php skills/wp-landing-config/tests/test_urgent_delivery_log.php
php skills/wp-landing-config/tests/test_rest_lead_idempotency.php
php -l skills/wp-landing-config/mu-plugin/landing-config/includes/monitoring-alerts.php
```

Expected: all exit 0; exact integration reservations remain unique, missing/stuck queue conditions are visible, and incident failure cannot alter the earlier saved-lead response.

```bash
git add skills/wp-landing-config/mu-plugin/landing-config/includes/monitoring-alerts.php skills/wp-landing-config/mu-plugin/landing-config/includes/lead-delivery-worker.php skills/wp-landing-config/tests
git commit -m "feat: monitor asynchronous lead delivery"
```

## Task 4: Issue an Uncached Same-origin Fallback Token with Admin-only Test Mode

**Files:**
- Create: `skills/wp-landing-config/tests/test_rest_fallback_token.php`
- Create: `skills/wp-landing-config/mu-plugin/landing-config/includes/rest-fallback-token.php`

**Interfaces:** Produces GET `/landing/v1/fallback-token`, public live mode only while live fallback is enabled, authenticated admin-only test mode, `resolve_token_mode($request): ?string`, `build_token_bundle(string,?int): ?array`, and no cached-HTML token or REST nonce injection.

- [ ] **Step 1: Write the failing endpoint tests before creating the production file**

Test the exact 43,200-second bundle/HMAC shown above with a deterministic nonce and a shared known vector also asserted by the Vercel tests. Require strict `decode_hmac_hex_secret()` to return exactly 32 binary bytes; reject missing/uppercase/short/non-hex keys and equal signing/status keys, and prove signing with the undecoded 64-byte hex text does not match the expected vector. Cover the complete authorization matrix: both flags false returns 404; test true/live false returns 404 for an ordinary visitor, a logged-out request, a non-admin, a missing nonce, and a bad nonce, but returns signed `mode=test` for a logged-in `manage_options` administrator with a valid `X-WP-Nonce`; live true/test false returns signed `mode=live` to a same-origin public request; both true still return live to an ordinary request and test only to the valid administrator request. `Origin` mismatch or `Sec-Fetch-Site: cross-site` returns 403; same-origin succeeds; the 61st HMAC-IP request in one hour returns 429; a parallel counter lock has one winner; raw IP never enters option/transient/lock/log; every response has `Cache-Control: no-store, private, max-age=0`, no CORS wildcard, and no secret. Static cached theme/functions output contains only the endpoint URL and never a bundle, token, `testRestNonce`, or secret.

- [ ] **Step 2: Run RED**

Run: `php skills/wp-landing-config/tests/test_rest_fallback_token.php`

Expected: exit 1 because the route/module does not exist. Save this output before creating `rest-fallback-token.php`.

- [ ] **Step 3: Implement exact token and safe rate limit**

Resolve mode in this exact order: return `test` only when `LP_FALLBACK_TEST_MODE===true`, `is_user_logged_in()`, `current_user_can('manage_options')`, and the `X-WP-Nonce` header passes `wp_verify_nonce($nonce, 'wp_rest')`; otherwise return `live` only when `LP_FALLBACK_ENABLED===true`; otherwise return null and the same generic 404. Thus the test flag alone never exposes a public token, and when both flags are true an ordinary request remains live while a correctly authorized admin request is test. Require `LP_FALLBACK_SIGNING_SECRET` and `LP_FALLBACK_STATUS_SECRET` to be distinct lowercase 64-hex strings. In `rest-fallback-token.php` provide shared `LandingConfig\FallbackSecurity\decode_hmac_hex_secret(string): ?string`: regex-check lowercase 64-hex, call `hex2bin`, and return only an exact 32-byte result. Every token, receipt-status, submission-status, and signed external-observation `hash_hmac` call must use this decoded binary result; public health never uses HMAC. Use `bin2hex(random_bytes(16))`; canonical HMAC bytes and response fields are exactly those above. Rate key is `hash_hmac('sha256', REMOTE_ADDR, wp_salt('auth'))`, truncated only after hashing; serialize count under a non-waiting named lock; limit 60 successful bundles/hour. Never persist either authorization nonce or intake nonce/token. Validate optional `Origin` equals the exact home origin and optional fetch-site equals `same-origin`; send no access-control wildcard. Return disabled/unauthorized 404, origin 403, limited 429, or exact 200 bundle, all no-store.

- [ ] **Step 4: Run GREEN and commit**

Run: `php skills/wp-landing-config/tests/test_rest_fallback_token.php && php -l skills/wp-landing-config/mu-plugin/landing-config/includes/rest-fallback-token.php`

Expected: test exits 0 and lint is clean.

```bash
git add skills/wp-landing-config/mu-plugin/landing-config/includes/rest-fallback-token.php skills/wp-landing-config/tests/test_rest_fallback_token.php
git commit -m "feat: issue uncached fallback intake tokens"
```

## Task 5: Five-minute Missing-lead Detector and External Receipt Check

**Files:**
- Create: skills/wp-landing-config/tests/test_monitoring_detector.php
- Modify: skills/wp-landing-config/mu-plugin/landing-config/includes/monitoring-alerts.php

**Interfaces:** Consumes anonymous form events and lead UUIDs. Produces `classify_timeline(array): ?array`, normalized receipt `{lookup,exists,stored,delivery_state}`, a contact-free due watch, and `run_missing_lead_scan(int,?int): array`.

- [ ] **Step 1: Write failing tests**

Test: form_started only → null; validation_failed without request → null; submit_attempt without request/validation → warning javascript_stall; request_started/request_failed without lead → critical missing_lead; age 299 seconds → none; age 300 → incident; matching WordPress lead → terminal wordpress_lead_saved. Exercise the complete receipt lifecycle: `pending,stored=true` creates/updates only a `fallback_receipt_watch` with `telegram_status=watching` and `due_at=now+300`, does not terminally resolve, and is not re-polled before due; pending at 9:59 has no alert, at 10:00 creates one `fallback_delivery_stuck` and continues watching; `unknown,stored=true` immediately creates one `fallback_delivery_uncertain` while continuing to watch; transition to `delivered,stored=true` terminally resolves watch/stuck/uncertain/missing and stops polling; transition `pending→unknown→expired,stored=false` reopens/creates the missing-lead incident. Missing, disabled, transport failure, malformed fields, or expired/stored-false never receives terminal external-recovered resolution. Every watch/incident contains only UUID/public state/due time and no contact.

- [ ] **Step 2: Run RED**

Run: php skills/wp-landing-config/tests/test_monitoring_detector.php

Expected: exit 1 because detector functions are absent.

- [ ] **Step 3: Implement classification and queries**

classify_timeline returns only kind,severity,safe_status,safe_category. Candidate SQL selects UUID/timestamps only, groups events, requires MAX(created_at) no newer than UTC now minus exactly 300 seconds, excludes a matching lead and only terminal `wordpress_lead_saved|external_recovered` resolution. An unresolved receipt watch with future `due_at` throttles lookup; when due it is included again. Never exclude a UUID merely because a prior receipt was pending/unknown or a non-terminal alert was sent. Timeline SQL selects only id,event_sequence,event_name,event_detail.

- [ ] **Step 4: Implement receipt HMAC**

Canonical path is `/api/v1/receipts/{uuid}`. Signature is lowercase hex HMAC-SHA256 of GET, path, Unix timestamp and site ID separated by newline, using only the 32-byte result of `FallbackSecurity\decode_hmac_hex_secret()`. GET timeout is 4, redirects 0, and headers are only the three status headers. Return a normalized safe array with `lookup=ok|missing|unknown|disabled`, booleans `exists/stored`, and `delivery_state=pending|delivered|unknown|expired|null`. Validate exact keys, matching UUID and allowed state. Apply the lifecycle/watch decisions from Step 1; do not terminally suppress solely because `stored===true`. Never persist provider body. Add the shared cross-runtime known-vector assertion here as well.

- [ ] **Step 5: Run GREEN and commit**

Run: php skills/wp-landing-config/tests/test_monitoring_detector.php && php skills/wp-landing-config/tests/test_form_events.php

Expected: both exit 0; recovered receipt creates no pending alert.

Commit: git commit -am "feat: detect missing WordPress leads"

## Task 6: Atomic, Non-recursive Telegram Technical Alerts

**Files:**
- Create: skills/wp-landing-config/tests/test_monitoring_queue.php
- Modify: skills/wp-landing-config/mu-plugin/landing-config/includes/monitoring-alerts.php

**Interfaces:** Produces claim_next_alert(?int): ?array, build_alert_text(array,array): string, run_alert_queue(int,?int): array.

- [ ] **Step 1: Write failing tests**

Prove two workers yield one conditional UPDATE winner and one HTTP POST; the row is durably `sending` and `send_attempts` is incremented before the HTTP capture; success requires HTTP 200, ok=true and positive message_id. Only a definite 429 changes that same alert row to `retry_wait`, sets the existing alert-table `due_at` from valid Telegram `parameters.retry_after` clamped to 1..3600 seconds (default 60), and permits another claim; assert no alert SQL references nonexistent `next_attempt_at`. Cap at three total HTTP calls, after which another 429 becomes terminal `failed`. 5xx, timeout, malformed/empty 2xx and stale sending become terminal unknown with no resend; permanent non-429 4xx becomes failed. Assert all messages/rows exclude PII/secret/exception markers and source never calls normal lead dispatch/Telegram adapter.

- [ ] **Step 2: Run RED**

Run: php skills/wp-landing-config/tests/test_monitoring_queue.php

Expected: exit 1.

- [ ] **Step 3: Implement exact credentials and claim**

Use LP_MONITOR_TELEGRAM_INTEGRATION_ID when positive; otherwise require exactly one enabled Telegram integration. Credentials stay in memory. Claim by one conditional UPDATE that changes `pending|retry_wait→sending` only when alert-table `due_at <= UTC_TIMESTAMP()`, stores lock/time, and increments `send_attempts` before any HTTP call; ownership requires `rows_affected===1` and `send_attempts < MAX_SEND_ATTEMPTS` before the increment. A separate sweep changes `sending` older than 120 seconds to `unknown` and never makes it claimable again.

- [ ] **Step 4: Implement messages/client**

Exact headings include “🚨 Заявка не появилась”, “⚠️ Форма остановилась до запроса”, “⚠️ Ошибка доставки заявки #<id>”, “⚠️ Резервная заявка ожидает доставку”, “🚨 Доставка резервной заявки неопределённа”, “🚨 Резервное хранилище недоступно”, “✅ Резервное хранилище восстановлено”, and “[TEST — DO NOT CONTACT]”. Load only page/form/CTA from form events, escape HTML, timeout 8, redirects 0. Store only status, code, positive message ID and timestamps. Confirmed response becomes `sent`; definite 429 becomes `retry_wait` only while fewer than three calls have occurred and otherwise `failed`; 5xx/timeout/malformed/empty 2xx becomes terminal `unknown`; other 4xx becomes `failed`. No raw body or exception-derived value is stored/logged.

- [ ] **Step 5: Run GREEN and commit**

Run: php skills/wp-landing-config/tests/test_monitoring_queue.php && php skills/wp-landing-config/tests/test_monitoring_incidents.php

Expected: exit 0 and exactly one captured Telegram POST.

Commit: git commit -am "feat: send deduplicated monitoring alerts"

## Task 7: One-minute Cron, Retention, and Privacy-safe Heartbeat

**Files:**
- Create: skills/wp-landing-config/tests/test_monitoring_cron.php
- Modify: skills/wp-landing-config/mu-plugin/landing-config/includes/monitoring-alerts.php

**Interfaces:** Produces recurrence `landing_every_minute`, scan/incident-queue/delivery hooks, retention hook, integer heartbeat and fixed safe run status.

- [ ] **Step 1: Test scheduling idempotency, disable/clear, heartbeat, fixed exception categories, delivery hook, and retention boundaries**
- [ ] **Step 2: Run RED:** php skills/wp-landing-config/tests/test_monitoring_cron.php; expected exit 1.
- [ ] **Step 3: Implement:** schedule delivery at +5, scan at +10 and incident queue at +40 each minute; schedule retention daily. Each wrapper catches Throwable, writes only literal `delivery_worker_failed`, `monitor_scan_failed`, `monitor_queue_failed`, or `monitor_cleanup_failed`, updates safe run status, and never logs/hashes exception text or rethrows. Scan may enqueue only fixed `monitor_scan_failed`; incident queue never recursively alerts itself.

`cleanup_expired_alerts()` deletes in batches of 1,000: resolved or confirmed-sent incidents with their terminal timestamp older than exactly 30 days; terminal `unknown|failed` incidents older than exactly 90 days. It never deletes pending, retry_wait, or sending rows regardless of age. Tests cover boundary timestamps at one second before/equal/after each cutoff and verify no contact/secret-bearing query values.
- [ ] **Step 4: Run GREEN:** same test exits 0; minute hooks and one daily cleanup exist exactly once; retention counts match fixtures.
- [ ] **Step 5: Commit:** git commit -am "feat: schedule WordPress lead monitoring"

## Task 8: Public Health, Signed External Poll, and Submission Reconciliation

**Files:**
- Create: skills/wp-landing-config/mu-plugin/landing-config/includes/rest-health.php
- Create: skills/wp-landing-config/tests/test_rest_health.php

**Interfaces:** Produces public `GET /landing/v1/health`, signed `GET /landing/v1/submission-status/(?P<submission_id>UUID)`, signed `POST /landing/v1/external-health-observation`, and safe external-health state.

- [ ] **Step 1: Test heartbeat ages 179/180/181, DB failure, handler absence, and exact no-secret public unsigned health JSON. Separately test submission-status invalid UUID; absent/duplicate/bad/expired/correct `X-LP-Site-Id`, `X-LP-Timestamp`, and `X-LP-Signature`; exists true/false; constant-time signature comparison; and exact four response keys with no lead ID/contact. Test the external-observation POST exact body/keys, body-digest HMAC, five-minute slot replay, first Redis failure no incident, second one deduplicated `external_outage/redis_outage`, repeated failure no duplicate, first ok one `external_recovery/redis_recovery`, and no contact/provider text. Run two complete fail/fail/recovery cycles and require four messages total; the repeated same slot adds none, and a delayed lower slot after the second recovery cannot reopen an outage. Test monitor-cadence boundaries 899/900/901 seconds, scheduler-never-started after enablement, repeat deduplication, and first-valid-observation recovery.**
- [ ] **Step 2: Run RED:** php skills/wp-landing-config/tests/test_rest_health.php; expected exit 1.
- [ ] **Step 3: Implement health after RED:** exact unsigned public response keys are ok, site_id, site, lead_endpoint, database, monitor_heartbeat, heartbeat_age_seconds, checked_at. Database check is SELECT 1. Heartbeat is healthy only if enabled, age <=180 and last run status is ok. Add no-store. The unsigned public health read and signed submission-status read never mutate the Redis-observation ledger; only the signed exact POST route in Step 4 does. Authentication failures use literal safe categories only.

- [ ] **Step 4: Run submission-status RED, then implement it**

Run the focused submission-status test selector first and record failure. The route canonical path is exactly `/wp-json/landing/v1/submission-status/{lowercase-uuid}`. Require exactly one `X-LP-Site-Id: hybridautos-ae`, one decimal `X-LP-Timestamp`, and one lowercase 64-hex `X-LP-Signature`; validate a lowercase 64-hex `LP_FALLBACK_STATUS_SECRET`, decode it through `FallbackSecurity\decode_hmac_hex_secret()` to exactly 32 binary bytes, enforce clock skew <=300, and compare in constant time with `HMAC-SHA256("GET\n<exact path>\n<timestamp>\nhybridautos-ae", decoded_secret)`. Reuse the same known vector as Vercel. Query only `SELECT 1 ... WHERE submission_id=%s LIMIT 1`, and return exactly `{ok:true,site_id,submission_id,exists:<bool>}` with no-store. Invalid auth returns a generic 401 with no existence signal; invalid UUID returns 400. Never return lead ID, timestamps, status, contact, audit data, delivery rows, raw hashes, or exception-derived values.

For `POST /wp-json/landing/v1/external-health-observation`, accept only exact JSON `{v:1,site_id:"hybridautos-ae",target:"redis",status:"ok|failed",checked_at_slot:<integer>}` and require `checked_at_slot === floor(X-LP-Timestamp/300)`. Canonical authentication is `POST\n/wp-json/landing/v1/external-health-observation\n<timestamp>\nhybridautos-ae\n<lowercase sha256 of exact raw body bytes>` with the same decoded status key and <=300-second skew. A named lock serializes the small option/incident transition. Any slot `<= last_processed_slot` returns the exact duplicate success and cannot mutate state; consecutive failures mean distinct adjacent increasing slots `N,N+1`, while a gap starts a new count at one. Store a privacy-safe episode generation equal to the first accepted failure slot after healthy/recovered state, and call only `record_external_incident()` for outage/recovery. Two consecutive failed slots create one external-outage incident for that episode; repeated/older slots do nothing; first later ok creates one recovery and closes that generation; a later failure starts a new generation. Every newly accepted observation also closes an open `external_monitor_stale` episode through `external_monitor_recovery`. Return exactly no-store `{ok:true,site_id:"hybridautos-ae",accepted:true,duplicate:<bool>}` for new or stale/duplicate authenticated observations. The endpoint never sends Telegram inline, accepts contact/free text, or depends on browser fallback/test flags. Generic auth failure reveals no state.

Persist only numeric `last_processed_slot`, accepted-at time, external episode state/generation, monitoring-enabled-at, and monitor-stale generation. `check_external_monitor_stale()` runs from the existing one-minute monitor scan. It does nothing until monitoring has been enabled for more than 900 seconds. When the last accepted observation—or enable start if none—is strictly older than 900 seconds, it records one `external_monitor_stale` generation equal to the first stale check slot; repeats deduplicate. The first later valid increasing-slot observation records `external_monitor_recovery` for that same generation and closes it.
- [ ] **Step 5: Run GREEN and lint:** all health/submission tests exit 0; php -l reports no syntax errors.
- [ ] **Step 6: Commit:** git commit -am "feat: expose WordPress health and signed status"

## Task 9: Read-only Monitoring Admin and Safe Test Button

**Files:**
- Create: skills/wp-landing-config/mu-plugin/landing-config/includes/admin-monitoring.php
- Create: skills/wp-landing-config/tests/test_admin_monitoring.php

- [ ] **Step 1: Test manage_options, POST-only action nonce, escaped safe columns, no free-text input and no secret values. Fixture the exact integration inventory and require safe booleans for exactly one enabled Email equal to `elapova00@gmail.com`, old Neuroboost disabled, Telegram enabled, and Roistat/CRM enabled; add mismatch cases while asserting rendered output never contains either email address or credentials. Test that only a logged-in `manage_options` user while `LP_FALLBACK_TEST_MODE===true` receives a POST form to `admin-post.php` with action `lp_fallback_arm_controlled_failure`; valid POST sets exact user transient `lp_fallback_controlled_failure_<user_id>` to `armed` for 60 seconds and returns HTTP 303 to exact `home_url('/')` with no query, no-store, and `Referrer-Policy:no-referrer`. GET, bad/missing nonce, non-admin, or disabled mode sets no transient. Assert the nonce appears only in the admin POST body/form, never in redirect URL, logs, analytics, or frontend HTML. The companion frontend consumes/deletes the transient once under a named lock and emits `testRestNonce` only in that clean no-store response.**
- [ ] **Step 2: Run RED:** php skills/wp-landing-config/tests/test_admin_monitoring.php; expected exit 1.
- [ ] **Step 3: Implement:** show monitor/fallback/test flags, heartbeat, last signed external result, incident counts, delivery queued/sending/unknown counts, recent safe incidents, configured/valid/distinct yes/no for fallback URL/signing/status/Telegram, and safe `email_binding_ok|neuroboost_disabled|roistat_crm_enabled` booleans. Never show recipient values. Button text is “Отправить [TEST — DO NOT CONTACT]”; its existing alert action remains capability+nonce protected. Separately, while test mode is true render a POST form for `admin_post_lp_fallback_arm_controlled_failure`. Its handler requires method POST, capability, test flag, and `check_admin_referer('lp_fallback_arm_controlled_failure')`; it sets the exact user transient to literal `armed` for 60 seconds, sends no-store plus `Referrer-Policy:no-referrer`, and `wp_safe_redirect(home_url('/'),303)` with no query. The frontend gate consumes it once and emits `testMode:true`, `forcePrimaryFailure:true`, and `testRestNonce:wp_create_nonce('wp_rest')` only in that authenticated clean response. The browser sends `testRestNonce` only in `X-WP-Nonce`; neither nonce is persisted or included in cached/ordinary output.
- [ ] **Step 4: Run GREEN/lint and commit:** test exits 0, lint clean, commit message “feat: add safe WordPress monitoring dashboard”.

## Task 10: Bootstrap and Full Privacy Regression

**Files:**
- Modify: skills/wp-landing-config/mu-plugin/landing-config/landing-config.php
- Create: skills/wp-landing-config/tests/test_monitoring_privacy.php

- [ ] **Step 1: Before editing plugin bootstrap, add/run a failing bootstrap test for every new module. Also test incidents, fallback token, health/submission/admin payloads, delivery/Telegram bodies, options and logs with PII/secret/exception markers; force delivery/monitor failures and still require the already saved lead HTTP 200. Assert that the REST token module consumes an authorized `testRestNonce` only as a header and that the companion frontend owns its authorized no-store emission; cached/public output has none.**
- [ ] **Step 2: After recorded RED, preserve every existing include exactly once and enforce this dependency order:** foundational `admin-mode → db → encryption → helpers → cascade → cta → integrations → lead-statuses → lead-status-log → migrations/selector/snippets`; then `AdapterInterface` and every existing adapter; then `rest-fallback-token` (which defines the shared strict HMAC decoder) → `monitoring-alerts → lead-delivery-worker → rest-lead → rest-form-events → rest-health`; then existing admin modules with `admin-pages` before `admin-monitoring`; then the unchanged cookie-banner/SEO modules. `db` must load before monitoring, the HMAC decoder before receipt/health signing, integrations/adapters before the worker, monitoring/worker before `rest-lead`, and monitoring before health/admin. Assert cached HTML never contains an intake token or either secret.
- [ ] **Step 3: Run all gates**

Run:
    set -euo pipefail
    for file in skills/wp-landing-config/tests/test_*.php; do
      php "$file"
    done
    find skills/wp-landing-config/mu-plugin/landing-config -type f -name '*.php' -print0 | xargs -0 -n1 php -l
    git diff --check

Expected: all tests exit 0, all PHP files lint, diff check silent.

- [ ] **Step 4: Commit and push**

Run:
    git add skills/wp-landing-config/mu-plugin/landing-config skills/wp-landing-config/tests
    git commit -m "feat: complete WordPress lead monitoring"
    git push origin hotfix/urgent-ad-launch-2026-07-15

## Task 11: Backup, Disabled-first Deployment, Enablement and Rollback Proof

**Files:** The production mutation allow-list is exactly ten paths: protected `/public_html/wp-config.php` plus nine plugin files: `landing-config.php`, `includes/db.php`, `includes/rest-lead.php`, `includes/lead-delivery-worker.php`, `includes/monitoring-alerts.php`, `includes/rest-fallback-token.php`, `includes/rest-health.php`, `includes/admin-monitoring.php`, `includes/admin-lead-audit.php`. The upload tool handles only the nine plugin files; `wp-config.php` is edited separately through the protected configuration step and is never downloaded or printed as plaintext.

- [ ] **Step 1: Tag rollback point**

Run: git tag -a backup/pre-wordpress-monitoring-2026-07-16 06a269c -m "Backup before WordPress monitoring" && git push origin backup/pre-wordpress-monitoring-2026-07-16

Expected: GitHub tag targets 06a269c.

- [ ] **Step 2: Validate the one authoritative fresh encrypted rollback backup**

Do not create a second WordPress-specific backup or a second key. The authoritative pre-change artifact is exactly Task 6 of the browser release plan:

- directory `/Users/kirillbezikov/Documents/Сайт Дубай /backups/2026-07-16_before_independent_fallback` mode `0700`;
- Keychain service `hybridautos-fallback-backup-20260716` for the current macOS user;
- `database.sql.gz.enc` and `public_html.tar.gz.enc`, each mode `0600`;
- ciphertext hashes/sizes and restore evidence recorded without contact data;
- retention through `2026-10-14`, review on/after `2026-10-15` only after a newer verified backup exists.

If Task 6 has not completed, execute it exactly once and stop this WordPress rollout until it does. If it has completed, retrieve that same key, re-run streaming integrity checks (`gzip -t` for the database and complete tar traversal proving `wp-config.php`, active theme, and MU-plugin), compare the recorded ciphertext SHA-256 values and modes, and confirm no plaintext `.sql`, `.sql.gz`, `.tar`, `.tar.gz`, `wp-config.php`, or extracted contact artifact exists in backup/temp paths. A Beget snapshot may be additional protection but never substitutes for this one encrypted-at-creation pair. Any missing key/artifact/hash/restore proof stops with `ENCRYPTED_BACKUP_GATE_BLOCKED` before production edits.

- [ ] **Step 3: Configure disabled-first**

Through Beget's protected editor, add the exact constant union from Global Constraints to `wp-config.php` before the “stop editing” line, without replacing or downloading the file. Deploy with monitor/fallback/test mode all false. `LP_FALLBACK_URL` is the full Vercel fallback POST URL; status URL is the Vercel base origin; site ID is `hybridautos-ae`; signing/status values are distinct literal lowercase 64-hex keys; Telegram ID is exact positive ID (use 0 only when exactly one enabled Telegram record exists). Record only the pre/post file hashes. Validate via WP-CLI checks that print only `CONFIG_OK`, never values; duplicate constants, wrong placement, regex failure, or role equality blocks deployment.

- [ ] **Step 4: Deploy the nine allow-listed plugin files in a mixed-version-safe order**

First install and enable the once-per-minute Beget system cron under `flock` for `wp cron event run --due-now`; before hooks exist it is harmless. Then upload additive `db.php` plus the new worker/monitor/token/health/admin modules and `admin-lead-audit.php`, but leave both the old synchronous `rest-lead.php` and old entrypoint active. Run the additive migration. `admin-lead-audit.php` must therefore be present while all flags are still false and before monitoring is enabled. Next upload the new `landing-config.php` entrypoint so it loads the worker/monitor modules while the old synchronous lead handler remains compatible; verify no fatal and prove one labeled synthetic due delivery row drains through cron. Only then upload the new asynchronous `rest-lead.php` last. This order guarantees it never calls an unloaded `LeadDelivery` function. Use `upload_allowlist_ftp.py`/atomic per-file replacement and verify every hash.

Expected: nine plugin remote paths/hashes plus the separately recorded protected `wp-config.php` hash; no other theme/content/upload/config changes. Keep monitor/fallback/test flags false, but keep the system cron active. During and for two minutes after the final handler switch, require queued due rows to fall rather than grow and no saved lead to remain without reservation beyond the one-minute reconciliation window.

- [ ] **Step 5: Run migration and disabled health**

Run `maybe_install_or_migrate`; verify version 1.1.0, alerts table, delivery queue columns, and exact unique reservation key. Health is 503 only for disabled/stale monitor while database/lead endpoint are ok. Token route is 404 while both fallback/test flags are false; with only test mode true it remains 404 for every ordinary/non-admin/bad-nonce request. Signed submission-status returns exists true/false correctly and no PII.

- [ ] **Step 6: Production idempotency control**

POST the same labeled test UUID twice. Expected: same positive lead ID, replayed=true, one lead, one queued attempt-1 reservation per exact integration, and zero external adapter calls before response. Run delivery cron; each reservation becomes confirmed exactly once. Force a stale sending fixture; expected unknown and no resend. Confirm lead `processed_status` is unchanged.

- [ ] **Step 7: Enable monitor on the already-proven Beget cron**

Confirm the already-active exact one-minute WP-CLI cron under flock marker hybridautos-monitor still drains delivery rows, then set LP_MONITOR_ENABLED=true. Expected: delivery queue does not grow, heartbeat advances within 90 seconds, and health becomes HTTP 200 with age <=180.

- [ ] **Step 8: Live acceptance**

Send one admin test alert; prove the alert row is `sending` before the Telegram call and confirmed afterward. Age one anonymous submit event five minutes and verify one missing/stall alert; rerun without duplicate. Exercise terminal 5xx/timeout/malformed alert responses as unknown/no resend and only definite 429 as retry. Force one delivery failure/stuck queue and verify safe alert/recovery. Verify 30/90-day cleanup boundaries. Have Vercel fetch unsigned public health with strict schema/TLS/redirect rejection, call signed submission-status GET, and POST signed external observations; bad/301-second-old signatures on the signed routes must not reveal/update anything.

- [ ] **Step 9: Enable independent fallback only after Vercel/frontend controlled failure passes**

First keep `LP_FALLBACK_ENABLED=false` and set only `LP_FALLBACK_TEST_MODE=true`. Prove an ordinary same-origin request still receives 404. Then log in as a `manage_options` administrator, obtain `testRestNonce` only from the no-store admin test bootstrap, send it only in `X-WP-Nonce`, and prove the token route returns a no-store signed `mode=test`; after the controlled primary failure the browser stores with Vercel immediately, and Vercel calls signed WordPress submission status about 45 seconds later before Telegram. Next enable live fallback and disable test mode. Expected: a normal primary success never reaches Vercel; a normal same-origin token request is signed `mode=live`; controlled primary absence produces one durable receipt/message; all normalized receipt states and watches work; only delivered/WordPress terminal recovery stops polling, while pending>10m, unknown, and expired/stored-false create the appropriate safe incident.

For the mandatory live status smoke, while test mode is still true use only the nonce-protected admin POST body to arm the synthetic submission UUID. The first valid signed status request must return generic no-store 503, and the second must return the normal missing response. Prove the arm expires at 180 seconds, another UUID is unaffected, and two concurrent requests cannot both receive the injected 503. Disable test mode after the controlled checks.

- [ ] **Step 10: Hash and rollback proof**

Download the nine live plugin files and match reviewed hashes; verify `wp-config.php` only by its remote hash and `CONFIG_OK`, never by downloading/printing it. Inspect logs for no fatal/raw/exception hashes. On isolated staging, rehearse the safe reverse order: restore old synchronous `rest-lead.php` first while the new worker is still loaded, drain any queued/sending/retry-wait rows, then restore the old entrypoint and remaining modules while leaving additive DB schema. Submit an old-format request without UUID and require a positive lead ID. Production rollback restores only the ten allow-listed paths from the verified backup and never restores the database unless a separately approved data rollback is required. Record encrypted-backup hashes/retention date, all nine plugin hashes plus the protected config hash, IDs, heartbeat, receipt states, Telegram message IDs and rollback result in README without PII/secrets.

## Final Acceptance Gate

- [ ] Replay creates one lead and no repeated integrations.
- [ ] Primary success barrier is the durable lead plus linked audit. Reservation and cron scheduling are attempted before response but their failure never revokes success; the monitor recreates missing reservations, and successful reservations contain exact integration IDs and unique `(lead,integration,attempt)` rows.
- [ ] Delivery worker writes sending before call; two workers send once; stale/ambiguous results become unknown without blind resend; only definite 429 retries; `processed_status` is untouched.
- [ ] Uncached same-origin token is an exact 12h HMAC bundle and secrets are distinct 64 lowercase hex; public live, disabled, and admin-only test authorization matrices pass; the test flag alone never opens the route publicly; cached/public HTML has neither token nor `testRestNonce`.
- [ ] Signed submission-status reveals only UUID existence; Vercel stores the fallback first, then its delayed 45-second worker reconciles before Telegram delivery.
- [ ] Five-minute missing lead creates one safe alert; pending external receipt stays on a five-minute watch, pending>10m/unknown alert before expiry, WordPress lead or delivered receipt resolves terminally, and expired/stored-false reopens missing.
- [ ] Technical Telegram persists sending before call; two workers cannot send twice; 5xx/timeout/malformed/stale sending are unknown/no resend.
- [ ] Monitoring failures never alter stored-lead success.
- [ ] Cron/heartbeat, delivery reconciliation, unsigned public health, signed submission-status/external-observation, and 30/90-day retention behave exactly as specified.
- [ ] Monitoring rows/messages/options/admin/logs contain no contacts or credentials.
- [ ] No raw exception text or its hash appears in logs/rows/messages.
- [ ] Fresh encrypted full-site/DB backup (0700 directory/0600 files, no plaintext, dated retention), Git tag, nine plugin hashes plus protected `wp-config.php` hash, and additive-schema rollback are verified.

## Known Boundary

Telegram cannot report its own outage through Telegram. Such incidents remain unknown/failed in WordPress/admin and external health; fallback contacts remain encrypted in Upstash under the Vercel plan. A contact that reaches neither WordPress nor the independent fallback cannot be reconstructed; anonymous telemetry intentionally identifies only the stopping stage and contains no draft contact.
