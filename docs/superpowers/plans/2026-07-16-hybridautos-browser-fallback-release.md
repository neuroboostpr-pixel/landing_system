# HybridAutos Browser Fallback Release Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Add a consent-gated, primary-first browser fallback that protects a submitted HybridAutos contact outside Beget, disclose that processing in the live Privacy Policy, and release the complete WordPress/Vercel system with verified backups and rollback.

**Architecture:** The browser creates one immutable in-memory submission snapshot, prefetches a no-store 12-hour token into memory after real form interaction, and gives WordPress one 20-second primary window across both REST variants. Only an eligible unconfirmed primary failure starts a new, independent 15-second Vercel request with the same UUID; cached HTML contains no token, strict endpoint/receipt validation is fail-closed, and production enablement happens only after an admin-only controlled failure test.

**Tech Stack:** WordPress/PHP 8.1, vanilla ES5-compatible browser JavaScript with an explicit surrogate-pair-safe Unicode splitter, Node.js `node:test`, Python `unittest`, Vercel TypeScript service, Upstash Redis/QStash, Telegram Bot API, Git/GitHub, Beget FTP/WP-CLI, SHA-256.

## Global Constraints

- Production site is exactly `https://hybridautos.ae`; allowed fallback browser origin is exactly `https://hybridautos.ae`.
- Existing WordPress remains the normal receiver; never send every lead to WordPress and Vercel in parallel.
- Vercel Hobby is forbidden for this commercial lead receiver. Require an existing Pro/Enterprise plan, effective DPA coverage, reviewed/disabled customer-data model-training use where applicable, and confirmed included/free Upstash Redis/QStash; otherwise stop with `COMMERCIAL_PLAN_GATE_BLOCKED`. Never incur a new charge without explicit user authorization.
- Primary deadline is exactly `20_000` milliseconds across both WordPress route variants.
- Fallback deadline is a separate exact `15_000` milliseconds with a new `AbortController`; the exhausted primary timer/signal is never reused.
- Intake token lifetime is exactly `43_200` seconds (12 hours), with at most 300 seconds of clock skew before `iat`.
- Cached HTML/public config never contains an intake token. `GET /wp-json/landing/v1/fallback-token` returns it with `Cache-Control: no-store`; browser memory is the only client-side token store.
- Fallback request is `application/x-www-form-urlencoded`, encoded body is at most `16_384` bytes, `credentials: 'omit'`, and `referrerPolicy: 'no-referrer'`.
- Fallback reasons are exactly `primary_timeout`, `primary_network`, `primary_5xx`, and `primary_invalid_response`.
- HTTP `400`, `401`, `403`, `409`, `422`, and `429`, consent rejection, validation errors, and honeypot detection never bypass WordPress.
- Fallback success requires HTTP success plus `ok === true`, exact matching `submission_id`, `receipt_id` matching `/^rct_[0-9a-f]{32}$/`, and `stored === true`; the initial service response state is `pending`.
- A valid fallback may have an empty name; canonical phone is exact `+971` followed immediately by nine digits and `pd_consent=1` is mandatory. This preserves the production phone-only form contract.
- Optional Unicode values are byte-truncated deterministically and lower-priority attribution is dropped as needed; long message/UTM values never discard the mandatory contact or make the browser reject an otherwise recoverable lead.
- A retry with the same contact/UUID but a refreshed token or a different observed failure reason replays the same receipt, not `409`; Vercel's idempotency fingerprint excludes `intake_token` and `fallback_reason`.
- Contact data must never enter `localStorage`, `sessionStorage`, IndexedDB, cookies, console output, analytics, form-event telemetry, technical alert rows, or source control.
- The browser never receives Telegram, Roistat, encryption, signing, or receipt-status secrets. The intake token is public and short-lived; `LP_FALLBACK_STATUS_SECRET` is never public.
- Monitoring or analytics failure must never block or change a confirmed primary or fallback success.
- No reCAPTCHA, Turnstile, or third-party challenge is added.
- Privacy Policy version is exactly `2026-07-16`; it must be published before `LP_FALLBACK_ENABLED` becomes `true`.
- Undelivered/uncertain encrypted fallback contact retention is at most seven days; confirmed Telegram delivery deletes encrypted contact immediately; a pseudonymous keyed duplicate-prevention receipt/fingerprint containing no direct contact values remains for 30 days.
- Fallback storage is immediate, but its Telegram message is intentionally delayed about 45 seconds for WordPress reconciliation and up to about 75 seconds when a second status check is needed. A theoretical duplicate remains only if WordPress completes after reconciliation while its signed status endpoint is unreachable; the shared UUID makes that case identifiable.
- The six advertising routes are `/`, `/li-auto/`, `/zeekr/`, `/xiaomi/`, `/lynk-co/`, and `/rox/`.
- Production upload is allow-listed and atomic. Never deploy the entire theme, use `rsync --delete`, or upload an uncommitted worktree.
- Every hard-gate failure stops the release; do not continue with an assumption.

---

## Repository and Interface Map

**Site repository:** `/Users/kirillbezikov/Documents/Сайт Дубай /hybridautos-ae-lead-reliability-2026-07-15`

- `08_КОД/wp-theme/includes/fallback-config.php` — exact public endpoint/config validation and admin-only controlled-test flag; no token signing or contact handling.
- `08_КОД/wp-theme/functions.php` — injects the same public config into the WordPress home page and five standalone brand pages.
- `08_КОД/wp-theme/assets/js/lead-form.js` — immutable snapshot, primary deadline, fallback matrix, strict receipt, analytics, and user retry state.
- `08_КОД/legal-pages/privacy-policy-hybridautos-en.md` — tracked canonical legal copy.
- `08_КОД/legal-pages/privacy-policy-hybridautos-en.html` — exact body published to WordPress.
- `tests/php/fallback-config.test.php` — HMAC/config contract.
- `tests/node/lead-delivery-protocol.test.cjs` — browser delivery protocol.
- `tests/node/urgent-lead-form.test.cjs` — existing reliability and privacy regression suite.
- `tests/python/test_urgent_launch_contract.py` — six-route/config/policy source contract.

**WordPress repository:** `/Users/kirillbezikov/Documents/Сайт Дубай /landing_system/.worktrees/urgent-ad-launch-2026-07-15`

- Consumed interfaces: idempotent `POST /wp-json/landing/v1/lead`, alternate `/?rest_route=/landing/v1/lead`, no-store `GET /wp-json/landing/v1/fallback-token`, signed `GET /wp-json/landing/v1/submission-status/{uuid}`, monitoring/health, and `LP_MONITOR_ENABLED` from the companion WordPress plan.

**Vercel repository:** `/Users/kirillbezikov/Documents/Сайт Дубай /hybridautos-lead-fallback`

- Consumed interfaces: `POST https://hybridautos-lead-fallback.vercel.app/api/v1/fallback-leads`, `GET /api/v1/receipts/{uuid}`, `GET /api/v1/health`, and internal `/api/internal/fallback-delivery`, `/api/internal/telegram-cleanup`, `/api/internal/health-check` from the companion Vercel plan.

**Exact public configuration:**

```js
window.lpLeadFallbackConfig = {
  enabled: false,
  endpoint: 'https://hybridautos-lead-fallback.vercel.app/api/v1/fallback-leads',
  tokenEndpoint: '/wp-json/landing/v1/fallback-token',
  siteId: 'hybridautos-ae',
  protocolVersion: '1',
  privacyPolicyVersion: '2026-07-16',
  testMode: false
};
```

This is the exact cacheable value. It contains no token and always has `testMode:false`, even while the server-side test constant is on. An admin-only, no-cache response may change `testMode` to `true` and additionally contain boolean `forcePrimaryFailure` equal to `true` and string `testRestNonce` equal to the current `wp_create_nonce('wp_rest')` result only when all checks pass: authenticated user, `manage_options`, `LP_FALLBACK_TEST_MODE === true`, and one still-live user-scoped transient armed by the companion admin module's nonce-protected POST. The POST returns `303` to the exact clean homepage URL; the theme consumes/deletes the transient once under a named lock before output. `testRestNonce` is sent only as `X-WP-Nonce` to the token endpoint and is never persisted. Ordinary users, ordinary requests, and arbitrary query strings receive `testMode:false` and neither optional property.

The browser accepts only the exact endpoint string above. Any other scheme, hostname, port, credentials, query, fragment, or path is rejected; the token path must equal `/wp-json/landing/v1/fallback-token` exactly.

**Exact no-store token response:**

```json
{
  "ok": true,
  "site_id": "hybridautos-ae",
  "protocol_version": "1",
  "privacy_policy_version": "2026-07-16",
  "mode": "live",
  "issued_at": 1784188800,
  "expires_at": 1784232000,
  "nonce": "0123456789abcdef0123456789abcdef",
  "token": "v1.1784188800.1784232000.0123456789abcdef0123456789abcdef.live.0123456789abcdef0123456789abcdef0123456789abcdef0123456789abcdef"
}
```

Token HMAC canonical bytes are exactly `v1\nhybridautos-ae\n<iat>\n<exp>\n<nonce>\n<mode>` and the signing secret is exactly 64 lowercase hex characters. `mode` is `live` or `test`; controlled primary failure additionally requires a valid in-memory `mode:'test'` bundle. Public same-origin GET receives `mode:'live'` only while `LP_FALLBACK_ENABLED === true`. Test mode requires `LP_FALLBACK_TEST_MODE === true`, authenticated `manage_options`, and a valid `X-WP-Nonce` for `wp_rest`. If live fallback is false, every ordinary, anonymous, missing-nonce, or bad-nonce request returns `404`, even when the test constant is true. If both flags are true, ordinary traffic still gets `live` and only the valid admin request gets `test`.

**Exact fallback request keys:**

```text
protocol_version, site_id, submission_id, fallback_reason,
pd_consent, privacy_policy_version, intake_token,
name, phone, email, message, model, form_id, brand, cta_key,
cta_label, cta_placement, source_path, source_label,
utm_source, utm_medium, utm_campaign, utm_term, utm_content,
roistat_visit, gclid, gbraid, wbraid, yclid, fbclid, msclkid, website
```

Every key occurs at most once; unknown keys are forbidden. `name` may be empty; phone is canonical `+971` plus exactly nine digits.

**Exact accepted fallback response:**

```json
{
  "ok": true,
  "site_id": "hybridautos-ae",
  "submission_id": "2189b544-1204-4ad9-89d2-dbf00d780d9e",
  "receipt_id": "rct_0123456789abcdef0123456789abcdef",
  "stored": true,
  "delivery_state": "pending"
}
```

The browser gates only on HTTP success, `ok`, matching UUID, receipt regex, and `stored`; Telegram state is not a browser success prerequisite.

---

### Task 1: Create and Inject the Exact Token-Free Public Configuration

**Files:**
- Create: `/Users/kirillbezikov/Documents/Сайт Дубай /hybridautos-ae-lead-reliability-2026-07-15/08_КОД/wp-theme/includes/fallback-config.php`
- Modify: `/Users/kirillbezikov/Documents/Сайт Дубай /hybridautos-ae-lead-reliability-2026-07-15/08_КОД/wp-theme/functions.php:7-20,99-145`
- Create: `/Users/kirillbezikov/Documents/Сайт Дубай /hybridautos-ae-lead-reliability-2026-07-15/tests/php/fallback-config.test.php`
- Modify: `/Users/kirillbezikov/Documents/Сайт Дубай /hybridautos-ae-lead-reliability-2026-07-15/tests/python/test_urgent_launch_contract.py`

**Interfaces:**
- Consumes: `LP_FALLBACK_ENABLED`, exact `LP_FALLBACK_URL`, `LP_FALLBACK_TEST_MODE`, WordPress authentication/capability, and a WordPress nonce; never consumes or renders the signing secret.
- Produces: `lp_fallback_public_config_from_settings(array $settings): array`, `lp_fallback_public_config(): array`, and token-free `window.lpLeadFallbackConfig` with the seven cacheable keys documented above plus optional admin-only, no-cache `forcePrimaryFailure:true` and `testRestNonce`.

- [ ] **Step 1: Write the failing exact-endpoint/config test**

Create `tests/php/fallback-config.test.php` with these executable assertions:

```php
<?php
require dirname(__DIR__, 2) . '/08_КОД/wp-theme/includes/fallback-config.php';

function check($condition, string $message): void {
    if (!$condition) { fwrite(STDERR, "FAIL: {$message}\n"); exit(1); }
}
$config = lp_fallback_public_config_from_settings([
    'enabled' => true,
    'endpoint' => 'https://hybridautos-lead-fallback.vercel.app/api/v1/fallback-leads',
    'test_mode' => false,
    'force_primary_failure' => false,
]);

check(array_keys($config) === [
    'enabled', 'endpoint', 'tokenEndpoint', 'siteId',
    'protocolVersion', 'privacyPolicyVersion', 'testMode'
], 'public allow-list changed');
check($config['enabled'] === true, 'valid settings must enable fallback');
check($config['endpoint'] === 'https://hybridautos-lead-fallback.vercel.app/api/v1/fallback-leads', 'endpoint changed');
check($config['tokenEndpoint'] === '/wp-json/landing/v1/fallback-token', 'token endpoint changed');
check(!array_key_exists('token', $config), 'cached HTML must not contain a token');
check(!array_key_exists('intakeToken', $config), 'cached HTML must not contain a token');
check(!array_key_exists('testRestNonce', $config), 'ordinary response exposed admin REST nonce');
check(!array_key_exists('forcePrimaryFailure', $config), 'ordinary response exposed test switch');

$invalid = [
    'http://hybridautos-lead-fallback.vercel.app/api/v1/fallback-leads',
    'https://evil.hybridautos-lead-fallback.vercel.app/api/v1/fallback-leads',
    'https://hybridautos-lead-fallback.vercel.app:444/api/v1/fallback-leads',
    'https://user@hybridautos-lead-fallback.vercel.app/api/v1/fallback-leads',
    'https://hybridautos-lead-fallback.vercel.app/api/v1/fallback-leads?x=1',
    'https://hybridautos-lead-fallback.vercel.app/api/v1/fallback-leads#x',
    'https://hybridautos-lead-fallback.vercel.app/api/v1/other',
];
foreach ($invalid as $endpoint) {
    $bad = lp_fallback_public_config_from_settings([
        'enabled' => true, 'endpoint' => $endpoint, 'test_mode' => false,
    ]);
    check($bad['enabled'] === false, "unsafe endpoint enabled: {$endpoint}");
    check($bad['endpoint'] === LP_FALLBACK_APPROVED_ENDPOINT, 'public endpoint must remain exact');
}

$admin = lp_fallback_public_config_from_settings([
    'enabled' => false,
    'endpoint' => LP_FALLBACK_APPROVED_ENDPOINT,
    'test_mode' => true,
    'force_primary_failure' => true,
    'test_rest_nonce' => '0123456789',
]);
check($admin['forcePrimaryFailure'] === true, 'authorized controlled test missing');
check($admin['testRestNonce'] === '0123456789', 'admin REST nonce missing');
check($admin['enabled'] === false && $admin['testMode'] === true, 'test must not silently enable live traffic');
echo "fallback-config: PASS\n";
```

- [ ] **Step 2: Run the test and verify the intended failure**

Run:

```bash
cd "/Users/kirillbezikov/Documents/Сайт Дубай /hybridautos-ae-lead-reliability-2026-07-15"
php tests/php/fallback-config.test.php
```

Expected: failure because `08_КОД/wp-theme/includes/fallback-config.php` does not exist.

- [ ] **Step 3: Implement the pure exact config builder and admin-only gate**

Create `includes/fallback-config.php` with these exact public boundaries:

```php
<?php
const LP_FALLBACK_APPROVED_ENDPOINT = 'https://hybridautos-lead-fallback.vercel.app/api/v1/fallback-leads';
const LP_FALLBACK_TOKEN_ENDPOINT = '/wp-json/landing/v1/fallback-token';

function lp_fallback_public_config_from_settings(array $settings): array {
    $endpoint = isset($settings['endpoint']) ? (string) $settings['endpoint'] : '';
    $endpoint_is_exact = hash_equals(LP_FALLBACK_APPROVED_ENDPOINT, $endpoint);
    $config = [
        'enabled' => !empty($settings['enabled']) && $endpoint_is_exact,
        'endpoint' => LP_FALLBACK_APPROVED_ENDPOINT,
        'tokenEndpoint' => LP_FALLBACK_TOKEN_ENDPOINT,
        'siteId' => 'hybridautos-ae',
        'protocolVersion' => '1',
        'privacyPolicyVersion' => '2026-07-16',
        'testMode' => !empty($settings['test_mode']),
    ];
    if ($config['testMode'] && !empty($settings['force_primary_failure'])
        && !empty($settings['test_rest_nonce'])) {
        $config['forcePrimaryFailure'] = true;
        $config['testRestNonce'] = (string) $settings['test_rest_nonce'];
    }
    return $config;
}

function lp_fallback_controlled_failure_allowed(): bool {
    if (!defined('LP_FALLBACK_TEST_MODE') || LP_FALLBACK_TEST_MODE !== true) { return false; }
    if (!is_user_logged_in() || !current_user_can('manage_options')) { return false; }
    $user_id = get_current_user_id();
    if ($user_id <= 0) { return false; }
    global $wpdb;
    $lock = 'lpft_' . get_current_blog_id() . '_' . $user_id;
    if ((int) $wpdb->get_var($wpdb->prepare('SELECT GET_LOCK(%s,0)', $lock)) !== 1) { return false; }
    try {
        $key = 'lp_fallback_controlled_failure_' . $user_id;
        if (get_transient($key) !== 'armed') { return false; }
        delete_transient($key);
        return true;
    } finally {
        $wpdb->get_var($wpdb->prepare('SELECT RELEASE_LOCK(%s)', $lock));
    }
}

function lp_fallback_public_config(): array {
    $force = lp_fallback_controlled_failure_allowed();
    if ($force) {
        if (!defined('DONOTCACHEPAGE')) { define('DONOTCACHEPAGE', true); }
        nocache_headers();
        header('Cache-Control: no-store, no-cache, must-revalidate, max-age=0', true);
        header('Referrer-Policy: no-referrer', true);
        header('X-Robots-Tag: noindex, nofollow', true);
    }
    return lp_fallback_public_config_from_settings([
        'enabled' => defined('LP_FALLBACK_ENABLED') && LP_FALLBACK_ENABLED === true,
        'endpoint' => defined('LP_FALLBACK_URL') ? LP_FALLBACK_URL : '',
        'test_mode' => $force,
        'force_primary_failure' => $force,
        'test_rest_nonce' => $force ? wp_create_nonce('wp_rest') : '',
    ]);
}

function lp_fallback_config_script(): string {
    return 'window.lpLeadFallbackConfig=' . wp_json_encode(
        lp_fallback_public_config(),
        JSON_HEX_TAG | JSON_HEX_AMP | JSON_HEX_APOS | JSON_HEX_QUOT
    ) . ';';
}
```

- [ ] **Step 4: Inject the config before `lead-form.js` on all six routes**

In `functions.php`, require the file once, add `wp_add_inline_script('lp-lead-form', lp_fallback_config_script(), 'before')` after enqueueing `lp-lead-form`, and concatenate the same token-free script with the existing `lpRestBase` script inside `lp_render_subpage()`. Do not inject `LP_FALLBACK_SIGNING_SECRET`, `LP_FALLBACK_STATUS_SECRET`, or any token. The authorized controlled-test response must execute `nocache_headers()` before output for both normal and standalone routes.

Use this exact subpage construction:

```php
$public_scripts = '<script>window.lpRestBase=' . wp_json_encode(rtrim(rest_url(), '/')) . ';'
    . lp_fallback_config_script()
    . '</script>';
```

- [ ] **Step 5: Add six-route/static secret-leak assertions**

Extend `test_urgent_launch_contract.py` to assert `fallback-config.php` is required, `wp_add_inline_script` precedes the shared handler, subpages use `$public_scripts`, policy version is `2026-07-16`, and cacheable config contains only the seven documented keys with no token and `testMode:false`. Test every rejected URL mutation and prove arbitrary query strings never arm test mode. Require `testMode:true`, `forcePrimaryFailure`, and `testRestNonce` only when test constant, authenticated `manage_options`, and exact user transient `armed` pass; two concurrent consumers under the named lock yield exactly one success, the winner deletes the transient before output, a second page is ordinary, and an expired transient rejects. Authorized output must have no-store, `Referrer-Policy:no-referrer`, and noindex headers on the clean URL. Separately cover token REST authorization: live enabled/ordinary request returns `live`; live disabled/ordinary or missing/bad REST nonce returns `404` even when test mode is on; valid admin `X-WP-Nonce` returns `test`; with both flags on, ordinary remains `live` and valid admin remains `test`.

- [ ] **Step 6: Run the focused and regression tests**

Run:

```bash
php tests/php/fallback-config.test.php
node --test tests/node/urgent-lead-form.test.cjs
python3 -m unittest tests/python/test_urgent_launch_contract.py -v
php -l 08_КОД/wp-theme/includes/fallback-config.php
php -l 08_КОД/wp-theme/functions.php
```

Expected: all tests pass and both PHP files report `No syntax errors detected`.

- [ ] **Step 7: Commit the isolated public-config unit**

```bash
git add 08_КОД/wp-theme/includes/fallback-config.php 08_КОД/wp-theme/functions.php tests/php/fallback-config.test.php tests/python/test_urgent_launch_contract.py
git commit -m "feat(theme): expose exact token-free fallback config"
```

---

### Task 2: Implement the Immutable Browser Snapshot and Delivery Protocol

**Files:**
- Modify: `/Users/kirillbezikov/Documents/Сайт Дубай /hybridautos-ae-lead-reliability-2026-07-15/08_КОД/wp-theme/assets/js/lead-form.js:22-53,163-213,222-254,526-688`
- Create: `/Users/kirillbezikov/Documents/Сайт Дубай /hybridautos-ae-lead-reliability-2026-07-15/tests/node/lead-delivery-protocol.test.cjs`
- Modify: `/Users/kirillbezikov/Documents/Сайт Дубай /hybridautos-ae-lead-reliability-2026-07-15/tests/node/urgent-lead-form.test.cjs`

**Interfaces:**
- Consumes: token-free `window.lpLeadFallbackConfig`, in-memory no-store token bundle, exact Vercel request/response contract, and WordPress strict `{ok:true,lead_id:<positive integer>}`.
- Produces: `prefetchFallbackToken(form, config, environment)`, `getOrCreateSubmissionSnapshot(form, fields)`, `freezeFallbackReason(form, snapshot, reason)`, `classifyPrimaryFailure(failure)`, `isConfirmedFallback(httpOk, data, submissionId)`, `buildFallbackBody(snapshot, tokenBundle)`, and `deliverSubmission(snapshot, environment)` exported under `window.lpLeadFormReliability` for focused tests.

- [ ] **Step 1: Write failing protocol tests for the complete fallback matrix**

Create `tests/node/lead-delivery-protocol.test.cjs`. Load `lead-form.js` with the same `vm` harness as the existing test and cover these exact cases:

```js
test('primary success never calls Vercel', async () => {
  const calls = [];
  const result = await helper.deliverSubmission(snapshot(), env(calls, [reply(201, {ok:true, lead_id:77})]));
  assert.deepEqual(result, {channel:'primary', lead_id:77});
  assert.equal(calls.length, 1);
});

test('any pretty-route 404, including HTML, tries legacy before Vercel', async () => {
  const calls = [];
  const result = await helper.deliverSubmission(snapshot(), env(calls, [
    replyText(404, '<html>proxy not found</html>'), reply(200, {ok:true, lead_id:78})
  ]));
  assert.equal(result.channel, 'primary');
  assert.equal(calls.length, 2);
  assert.match(calls[1].url, /rest_route=\/landing\/v1\/lead/);
});

test('two generic 404 routes call fallback exactly once', async () => {
  const calls = [];
  const result = await helper.deliverSubmission(snapshot(), env(calls, [
    replyText(404, '<html>not found</html>'), reply(404, {error:'not found'}), fallbackReply()
  ]));
  assert.equal(result.channel, 'fallback');
  assert.equal(calls.filter(c => c.url.includes('vercel.app')).length, 1);
});

for (const scenario of [
  ['network', networkError(), 'primary_network'],
  ['5xx', reply(503, {ok:false}), 'primary_5xx'],
  ['malformed', replyText(200, '<html>bad gateway</html>'), 'primary_invalid_response'],
  ['unconfirmed', reply(200, {ok:true, lead_id:0}), 'primary_invalid_response'],
]) {
  test(`${scenario[0]} calls Vercel once`, async () => {
    const calls = [];
    const id = snapshot().submission_id;
    const result = await helper.deliverSubmission(snapshot(id), env(calls, [
      scenario[1], reply(201, receipt(id))
    ]));
    assert.equal(result.channel, 'fallback');
    assert.equal(result.fallback_reason, scenario[2]);
    assert.equal(calls.filter(c => c.url.includes('vercel.app')).length, 1);
  });
}

for (const status of [400, 401, 403, 409, 422, 429]) {
  test(`HTTP ${status} never bypasses WordPress`, async () => {
    const calls = [];
    await assert.rejects(helper.deliverSubmission(snapshot(), env(calls, [reply(status, {ok:false})])));
    assert.equal(calls.length, 1);
  });
}
```

Also test: a never-resolving primary fetch calls fallback at a test primary deadline of 10 ms; both missing WordPress route variants call fallback once; fallback receives a newly constructed controller and an independent test timeout of 10 ms; a never-resolving fallback rejects at that deadline and re-enables the form rather than hanging. Wrong UUID, receipt outside `/^rct_[0-9a-f]{32}$/`, or `stored:false` remains failure; fallback `409`, `413`, `429`, or `503` never redirects; and fallback uses `credentials:'omit'`, `referrerPolicy:'no-referrer'`, and no primary signal.

Add token tests proving: cached config has no token; real `focusin`/`form_started` sends a PII-free same-origin GET with `cache:'no-store'`; token lives only at `form._lpFallbackTokenBundle`; submit starts a refresh while primary is reachable; if WordPress later becomes unavailable the last unexpired prefetched token is used; an expired/malformed bundle is never sent. Controlled failure requires `forcePrimaryFailure === true` and bundle `mode === 'test'`, then routes both primary variants to `/landing/v1/__controlled-fallback-test-no-route`; neither an ordinary query nor public `testMode` alone can do that.

- [ ] **Step 2: Run the protocol suite and verify it fails for missing exports**

Run:

```bash
node --test tests/node/lead-delivery-protocol.test.cjs
```

Expected: FAIL because `deliverSubmission`, `isConfirmedFallback`, and snapshot helpers are undefined.

- [ ] **Step 3: Add typed failure classification and the one-deadline primary chain**

Implement exact decision rules:

```js
var PRIMARY_TIMEOUT_MS = 20000;
var FALLBACK_TIMEOUT_MS = 15000;
var PROTECTED_PRIMARY_STATUS = {400:true,401:true,403:true,409:true,422:true,429:true};

function classifyPrimaryFailure(failure) {
  if (failure.kind === 'timeout') return {eligible:true, reason:'primary_timeout'};
  if (failure.kind === 'network') return {eligible:true, reason:'primary_network'};
  if (failure.kind === 'http' && failure.status >= 500 && failure.status <= 599) {
    return {eligible:true, reason:'primary_5xx'};
  }
  if (failure.kind === 'invalid_response' || failure.kind === 'routes_unavailable') {
    return {eligible:true, reason:'primary_invalid_response'};
  }
  return {eligible:false, reason:''};
}

function isConfirmedFallback(httpOk, data, submissionId) {
  var keys = data && typeof data === 'object' ? Object.keys(data).sort().join(',') : '';
  return httpOk === true && !!data &&
    keys === 'delivery_state,ok,receipt_id,site_id,stored,submission_id' &&
    data.ok === true && data.site_id === 'hybridautos-ae' &&
    data.stored === true && data.delivery_state === 'pending' &&
    data.submission_id === submissionId && typeof data.receipt_id === 'string' &&
    /^rct_[0-9a-f]{32}$/.test(data.receipt_id);
}
```

`deliverSubmission(snapshot, environment)` must start one primary deadline at `environment.now() + 20000`, pass the remaining milliseconds to the first and optional legacy WordPress request, and abort/race the active request when the shared deadline expires. A late WordPress result is ignored. Any HTTP 404 from the first lead POST selects the legacy route, including non-JSON proxy/hosting 404; the lead endpoint has no business-level 404. Only a second 404 becomes `routes_unavailable` and one fallback attempt. When fallback becomes eligible, create a new `AbortController`, start a new 15,000-ms timer, and never reuse the primary controller, signal, deadline, or remaining time.

- [ ] **Step 4: Prefetch and validate a no-store token without contact data**

Call `prefetchFallbackToken` from a `focusin` listener and from the existing real `form_started` path; programmatic focus may prefetch a token but must still not emit `form_started`. On validated submit, start one refresh in parallel with the primary request while WordPress is still reachable. A refresh failure leaves a previously prefetched, unexpired bundle intact.

The request is exact and contains no body, form values, query attribution, or referrer override. Build the headers without modern-only collection helpers: ordinary live traffic sends only `Accept`; an authorized controlled test adds `X-WP-Nonce` only when the server issued both `forcePrimaryFailure:true` and a non-empty `testRestNonce` in the same no-cache response:

```js
var tokenHeaders = {'Accept': 'application/json'};
if (config.forcePrimaryFailure === true && typeof config.testRestNonce === 'string' &&
    config.testRestNonce !== '') {
  tokenHeaders['X-WP-Nonce'] = config.testRestNonce;
}
fetch(config.tokenEndpoint, {
  method: 'GET',
  credentials: 'same-origin',
  cache: 'no-store',
  headers: tokenHeaders
});
```

Accept only the exact token response contract in the Interface Map, `expires_at === issued_at + 43200`, unexpired time with the defined skew, nonce `/^[0-9a-f]{32}$/`, token `/^v1\.[0-9]+\.[0-9]+\.[0-9a-f]{32}\.(live|test)\.[0-9a-f]{64}$/`, and fields matching config. The server may issue `mode:'test'` only when `LP_FALLBACK_TEST_MODE === true`, the caller is authenticated with `manage_options`, and that `X-WP-Nonce` passes `wp_verify_nonce(..., 'wp_rest')`; otherwise an enabled public same-origin request receives `mode:'live'`, and a disabled non-test endpoint returns `404`. Store the frozen bundle only as `form._lpFallbackTokenBundle`; reset/success deletes it. Never put it in HTML cache, Web Storage, cookies, analytics, telemetry, URL, or console.

- [ ] **Step 5: Build one deterministic budgeted fallback body without sacrificing contact**

First validate the config endpoint by exact string equality; do not follow a configured alternate URL. Canonicalize phone to `+971` plus exactly nine digits with no spaces or punctuation. Append all required service fields, UUID, frozen reason, consent, token, phone, and empty honeypot first. These mandatory fields are never truncated or dropped.

Then append optional values in this exact priority order: `name`, `email`, `message`; `model`, `form_id`, `brand`, `cta_key`, `cta_label`, `cta_placement`, `source_path`, `source_label`; then UTM values, `roistat_visit`, and click IDs. For every optional value, apply its field limit, split with an ES5-compatible surrogate-pair-safe helper so Unicode code points are never cut, and binary-search the largest prefix for which `new URLSearchParams(candidate).toString().length <= 16384`. Because the encoded result is ASCII, this length is the exact transmitted byte count. Append the non-empty prefix or drop that optional field; continue to lower priorities only while bytes remain. Never throw or cancel fallback because message/UTM/click data was shortened. Do not use `Array.from`, because the production handler supports older browsers.

Use this core algorithm:

```js
function unicodeCodePoints(value) {
  var input = String(value || '');
  var points = [];
  var index = 0;
  var first;
  var second;
  while (index < input.length) {
    first = input.charCodeAt(index);
    if (first >= 0xD800 && first <= 0xDBFF && index + 1 < input.length) {
      second = input.charCodeAt(index + 1);
      if (second >= 0xDC00 && second <= 0xDFFF) {
        points.push(input.slice(index, index + 2));
        index += 2;
        continue;
      }
    }
    points.push(input.charAt(index));
    index += 1;
  }
  return points;
}

function appendOptionalWithinBudget(body, key, value, charLimit) {
  var chars = unicodeCodePoints(value).slice(0, charLimit);
  var low = 0;
  var high = chars.length;
  var best = '';
  while (low <= high) {
    var middle = Math.floor((low + high) / 2);
    var candidateValue = chars.slice(0, middle).join('');
    var candidate = new URLSearchParams(body.toString());
    if (candidateValue) candidate.append(key, candidateValue);
    if (candidate.toString().length <= 16384) {
      best = candidateValue;
      low = middle + 1;
    } else {
      high = middle - 1;
    }
  }
  if (best) body.append(key, best);
}
```

The fetch options must be exactly:

```js
{
  method: 'POST',
  headers: {'Content-Type': 'application/x-www-form-urlencoded'},
  body: fallbackBody,
  credentials: 'omit',
  referrerPolicy: 'no-referrer',
  redirect: 'error',
  signal: fallbackAbortController.signal
}
```

Add a RED test for an HTTP 301/302/307/308 response and require the browser request to fail locally without following it or resending the contact to any redirected origin.

- [ ] **Step 6: Create the immutable snapshot and freeze the first fallback reason**

On the first validated submit, freeze one snapshot containing `submission_id`, canonical contact fields, form context, bounded attribution, `primaryBody`, a contact comparison key, and an initially empty `fallback_reason`. Token is never part of the snapshot. On the first eligible primary failure, replace it once with a frozen copy whose `fallback_reason` is that first reason; later unchanged retries keep it even if the newly observed primary failure category or token differs.

Use these rules:

```js
function clearSubmissionId(form) {
  delete form._lpSubmissionId;
  delete form._lpEventSequence;
  delete form._lpSubmissionSnapshot;
}

function getOrCreateSubmissionSnapshot(form, fields) {
  var contactKey = JSON.stringify([fields.name, fields.phone, fields.email, fields.message]);
  var copiedFields = {};
  var fieldName;
  if (form._lpSubmissionSnapshot && form._lpSubmissionSnapshot.contactKey !== contactKey) {
    clearSubmissionId(form);
  }
  for (fieldName in fields) {
    if (Object.prototype.hasOwnProperty.call(fields, fieldName)) {
      copiedFields[fieldName] = fields[fieldName];
    }
  }
  if (!form._lpSubmissionSnapshot) {
    form._lpSubmissionSnapshot = Object.freeze({
      submission_id: submissionIdFor(form),
      contactKey: contactKey,
      fields: Object.freeze(copiedFields),
      fallback_reason: ''
    });
  }
  return form._lpSubmissionSnapshot;
}

function freezeFallbackReason(form, snapshot, reason) {
  if (snapshot.fallback_reason) return snapshot;
  var frozen = Object.freeze({
    submission_id: snapshot.submission_id,
    contactKey: snapshot.contactKey,
    fields: snapshot.fields,
    fallback_reason: reason
  });
  form._lpSubmissionSnapshot = frozen;
  return frozen;
}
```

Before `submit_attempt`, compare current name/phone/email/message against an existing failed snapshot so an edited contact gets a new UUID. An unchanged retry reuses the exact frozen snapshot, UUID, and first fallback reason while it may use a fresh valid token. Reset and confirmed success clear snapshot and token bundle.

- [ ] **Step 7: Prove the budget, replay, timeout, and privacy guarantees**

Add tests that:

- unchanged retry returns the same frozen object and UUID;
- editing name, phone, email, or message produces a different UUID before the next request;
- attribution changes alone do not mutate an existing snapshot;
- first fallback reason remains stable across retries;
- changing only token or newly observed failure reason does not change the Vercel idempotency payload and replays rather than returning `409`;
- no active source contains `localStorage`, `sessionStorage`, `indexedDB`, contact cookies, or contact-bearing `dataLayer.push`;
- mandatory phone/consent/UUID/token remain in a body no larger than 16,384 bytes with 100,000 emoji in message/UTMs; truncation is deterministic and never splits a code point;
- empty name plus valid phone and consent remains a valid fallback request.
- a never-resolving primary uses 20 seconds, then a never-resolving fallback uses no more than its independent additional 15 seconds; neither can hang indefinitely.

- [ ] **Step 8: Run protocol and existing regression tests**

```bash
node --test tests/node/lead-delivery-protocol.test.cjs tests/node/urgent-lead-form.test.cjs
python3 -m unittest tests/python/test_urgent_launch_contract.py -v
```

Expected: all tests pass; no skipped tests.

- [ ] **Step 9: Commit the delivery protocol**

```bash
git add 08_КОД/wp-theme/assets/js/lead-form.js tests/node/lead-delivery-protocol.test.cjs tests/node/urgent-lead-form.test.cjs tests/python/test_urgent_launch_contract.py
git commit -m "feat(forms): add passive independent lead fallback"
```

---

### Task 3: Wire the Form UI, Analytics, and Failure Telemetry to the Protocol

**Files:**
- Modify: `/Users/kirillbezikov/Documents/Сайт Дубай /hybridautos-ae-lead-reliability-2026-07-15/08_КОД/wp-theme/assets/js/lead-form.js:526-688`
- Modify: `/Users/kirillbezikov/Documents/Сайт Дубай /hybridautos-ae-lead-reliability-2026-07-15/tests/node/lead-delivery-protocol.test.cjs`
- Modify: `/Users/kirillbezikov/Documents/Сайт Дубай /hybridautos-ae-lead-reliability-2026-07-15/tests/python/test_urgent_launch_contract.py`

**Interfaces:**
- Consumes: Task 2 `deliverSubmission` result `{channel:'primary',lead_id}` or `{channel:'fallback',receipt_id,fallback_reason}`.
- Produces: redirect only after strict storage confirmation; `lead_success` for WordPress or `lead_fallback_success` for Vercel, with no contact, UUID, or receipt in analytics.

- [ ] **Step 1: Write failing UI/analytics assertions**

Add tests proving:

```js
assert.deepEqual(primaryAnalytics, {
  event:'lead_success', lead_id:77,
  form_id:'rox-test-drive', brand:'rox', model:'ROX 01', cta_key:'hero-test-drive'
});
assert.deepEqual(fallbackAnalytics, {
  event:'lead_fallback_success', fallback_reason:'primary_timeout',
  form_id:'rox-test-drive', brand:'rox', model:'ROX 01', cta_key:'hero-test-drive'
});
```

Assert neither event contains name, phone, email, message, submission ID, receipt ID, token, full URL, or click ID. Assert both-path failure, including a 15-second fallback timeout, leaves values in the form, re-enables the button, shows the retry/WhatsApp message, does not push a conversion event, and does not assign `/thank-you/`.

- [ ] **Step 2: Run and verify the failure**

```bash
node --test tests/node/lead-delivery-protocol.test.cjs
```

Expected: FAIL because the current submit handler calls its local `send()` and only emits `lead_success`.

- [ ] **Step 3: Replace the local send chain with token-prefetched `deliverSubmission`**

Keep `emitFormEvent(form, 'request_started', '')` immediately before delivery. Start a no-store token refresh in parallel with the primary call and preserve the previously prefetched valid bundle if refresh fails. Fallback is available when `config.enabled === true`, or only for the controlled admin test when `config.forcePrimaryFailure === true` and the in-memory bundle has `mode === 'test'`.

For that controlled case only, pass these guaranteed non-existent primary paths to the same normal delivery engine:

```js
var controlledPath = '/landing/v1/__controlled-fallback-test-no-route';
var primaryEndpoint = restBase + controlledPath;
var legacyPrimaryEndpoint = fallbackEndpoint(restBase).replace('/landing/v1/lead', controlledPath);
```

Never derive this behavior from `location.search` in JavaScript. The server-issued flag is the sole switch; public `testMode`, a forged query, or a missing/`live` token bundle cannot change either primary URL.

On an eligible failure, call `freezeFallbackReason` before body construction, use the fresh valid token if available or the prefetched valid token otherwise, and start the independent 15-second fallback. On resolved result:

```js
if (result.channel === 'primary') {
  emitConfirmedSuccess(form, {lead_id: result.lead_id}, context);
} else {
  emitFallbackSuccess(form, result.fallback_reason, context);
}
clearSubmissionId(form);
window.location.href = '/thank-you/';
```

On rejection, emit one coarse `request_failed` category, never log the error or payload with `console.error`, restore the button, keep the form/snapshot, and show the existing retry/WhatsApp message. Diagnostic telemetry remains best-effort and cannot change either success.

- [ ] **Step 4: Add the privacy-safe fallback analytics helper**

```js
function emitFallbackSuccess(form, reason, context) {
  if (form._lpSuccessEmitted) return;
  form._lpSuccessEmitted = true;
  try {
    window.dataLayer = window.dataLayer || [];
    if (typeof window.dataLayer.push !== 'function') return;
    window.dataLayer.push({
      event: 'lead_fallback_success',
      fallback_reason: reason,
      form_id: context.form_id,
      brand: context.brand,
      model: context.model,
      cta_key: context.cta_key
    });
  } catch (ignoredAnalyticsError) {}
}
```

- [ ] **Step 5: Run all frontend checks and scan for forbidden persistence/logging**

```bash
node --test tests/node/*.test.cjs
python3 -m unittest tests/python/test_urgent_launch_contract.py -v
rg -n "localStorage|sessionStorage|indexedDB|console\.(log|error).*phone|dataLayer.*(phone|email|name|message|receipt|submission)" 08_КОД/wp-theme/assets/js/lead-form.js
git diff --check
```

Expected: tests pass; `rg` returns no matches; `git diff --check` is silent.

- [ ] **Step 6: Commit the UI/analytics wiring**

```bash
git add 08_КОД/wp-theme/assets/js/lead-form.js tests/node/lead-delivery-protocol.test.cjs tests/python/test_urgent_launch_contract.py
git commit -m "fix(forms): redirect only after durable receiver receipt"
```

---

### Task 4: Publish an Accurate Versioned Privacy Policy Source

**Files:**
- Create: `/Users/kirillbezikov/Documents/Сайт Дубай /hybridautos-ae-lead-reliability-2026-07-15/08_КОД/legal-pages/privacy-policy-hybridautos-en.md`
- Create: `/Users/kirillbezikov/Documents/Сайт Дубай /hybridautos-ae-lead-reliability-2026-07-15/08_КОД/legal-pages/privacy-policy-hybridautos-en.html`
- Modify: `/Users/kirillbezikov/Documents/Сайт Дубай /hybridautos-ae-lead-reliability-2026-07-15/tests/python/test_urgent_launch_contract.py`

**Interfaces:**
- Consumes: approved retention, processor, encryption, consent, and cross-border statements.
- Produces: canonical English policy body published at `/privacy-policy/` with version `2026-07-16` before fallback enablement.

- [ ] **Step 1: Add a failing policy contract test**

Assert both canonical files contain all of these exact facts: `Effective date: 16 July 2026`, `Vercel`, `Upstash`, `independent backup`, `encrypted`, immediate deletion after `Telegram confirms delivery`, after `the primary website confirms storage`, and after `manual recovery is confirmed`, `no more than seven days`, `30 days`, `only after you consent and submit`, and `outside the United Arab Emirates`.

- [ ] **Step 2: Run and verify the missing-file failure**

```bash
python3 -m unittest tests/python/test_urgent_launch_contract.py -v
```

Expected: FAIL because both site-specific canonical policy files are absent.

- [ ] **Step 3: Create the tracked Markdown and HTML policy**

Copy the existing HybridCars UAE policy sections unchanged, update the effective date to `16 July 2026`, and insert this exact processor disclosure into section 4:

```html
<p>If the primary website system cannot confirm that a form request was stored, the same submitted request may be sent to an independent technical backup operated on Vercel and stored temporarily in Upstash Redis for delivery recovery. This backup is used only after you consent and submit the form; it is not used for draft forms or ordinary abandonment. Vercel and Upstash act as technical processors and may process data outside the United Arab Emirates.</p>
```

Insert this exact retention disclosure into section 6:

```html
<p>An independent fallback contact is encrypted while awaiting delivery. Its encrypted contact content is deleted immediately after Telegram confirms delivery, after the primary website confirms storage during reconciliation, or after manual recovery is confirmed. If delivery is unavailable or uncertain, encrypted contact content is retained for no more than seven days for recovery and is then deleted. A pseudonymous keyed duplicate-prevention receipt/fingerprint containing no direct contact values may remain for 30 days.</p>
```

Insert this exact security disclosure into section 8:

```html
<p>The independent backup uses encrypted transport and AES-256-GCM storage encryption. Backup credentials and Telegram credentials remain server-side and are not sent to the browser. No Internet service can guarantee absolute security.</p>
```

Use equivalent plain Markdown paragraphs in the `.md` file. Do not modify the generic Russian `policy.html.template`; it is not this UAE site's canonical notice.

- [ ] **Step 4: Run the policy and form-link checks**

```bash
python3 -m unittest tests/python/test_urgent_launch_contract.py -v
rg -n "href = '/privacy-policy/'|Privacy Policy" 08_КОД/wp-theme/assets/js/lead-form.js
```

Expected: all tests pass; the existing mandatory checkbox still points to `/privacy-policy/`.

- [ ] **Step 5: Commit the legal source**

```bash
git add 08_КОД/legal-pages/privacy-policy-hybridautos-en.md 08_КОД/legal-pages/privacy-policy-hybridautos-en.html tests/python/test_urgent_launch_contract.py
git commit -m "docs(privacy): disclose encrypted fallback processing"
```

---

### Task 5: Run the Cross-System Contract and Security Gate

**Files:**
- No production file changes.

**Interfaces:**
- Consumes: reviewed commits from the site, WordPress, and Vercel plans.
- Produces: one green local release candidate with identical token/request/receipt/status contracts.

- [ ] **Step 1: Run every repository's focused tests**

```bash
cd "/Users/kirillbezikov/Documents/Сайт Дубай /hybridautos-ae-lead-reliability-2026-07-15"
php tests/php/fallback-config.test.php
node --test tests/node/*.test.cjs
python3 -m unittest tests/python/test_urgent_launch_contract.py -v

cd "/Users/kirillbezikov/Documents/Сайт Дубай /landing_system/.worktrees/urgent-ad-launch-2026-07-15"
set -e
for test_file in skills/wp-landing-config/tests/test_*.php; do php "$test_file"; done

cd "/Users/kirillbezikov/Documents/Сайт Дубай /hybridautos-lead-fallback"
pnpm test
pnpm typecheck
pnpm build
```

Expected: every command exits `0`; no skipped security/idempotency test.

- [ ] **Step 2: Verify the exact shared constants**

Run `rg` across all three repositories and confirm exact agreement on: site ID `hybridautos-ae`, exact POST URL, exact token/status URLs, protocol `1`, policy `2026-07-16`, token wire format/lifetime, 16,384-byte body, 20,000-ms primary deadline, independent 15,000-ms fallback deadline, four fallback reasons, optional name, canonical `+971` plus nine digits, receipt regex, and the fact that idempotency excludes token/reason. Any mismatch stops release.

- [ ] **Step 3: Scan all staged Git content for credentials and contact fixtures**

```bash
git -C "/Users/kirillbezikov/Documents/Сайт Дубай /hybridautos-ae-lead-reliability-2026-07-15" grep -n -E "[0-9]{8,}:[A-Za-z0-9_-]{30,}|LP_FALLBACK_(SIGNING|STATUS)_SECRET=|\+971 5[0-9] [0-9]{3} [0-9]{4}" -- . ':!tests/**'
git -C "/Users/kirillbezikov/Documents/Сайт Дубай /landing_system/.worktrees/urgent-ad-launch-2026-07-15" grep -n -E "[0-9]{8,}:[A-Za-z0-9_-]{30,}|LP_FALLBACK_(SIGNING|STATUS)_SECRET=" -- .
git -C "/Users/kirillbezikov/Documents/Сайт Дубай /hybridautos-lead-fallback" grep -n -E "[0-9]{8,}:[A-Za-z0-9_-]{30,}|LP_FALLBACK_(SIGNING|STATUS)_SECRET=" -- .
```

Expected: no matches. Test-only dummy contacts remain under `tests/` and are labeled `DO NOT CONTACT`.

- [ ] **Step 4: Push reviewed branches and verify remote SHAs**

Push each branch, read it back with `gh api`, and require the remote SHA to equal local `git rev-parse HEAD`. Create immutable pre-release tags in the site and WordPress repositories before production deployment.

---

### Task 6: Create Fresh Full Backups and a Rollback Boundary

**Files:**
- Backup output only: `/Users/kirillbezikov/Documents/Сайт Дубай /backups/2026-07-16_before_independent_fallback/`

**Interfaces:**
- Consumes: current production before this release and a newly generated Keychain-held backup passphrase.
- Produces: two encrypted-at-creation artifacts containing complete `public_html` and complete database (including leads/audit/integration/policy state), plus a privacy-safe hash/cron/config inventory and verified Git/Vercel rollback identifiers; no plaintext SQL/config/archive is created locally or remotely.

- [ ] **Step 1: Create the backup key with restrictive local permissions**

```bash
umask 077
mkdir -p "/Users/kirillbezikov/Documents/Сайт Дубай /backups/2026-07-16_before_independent_fallback"
security add-generic-password -U -a "$USER" \
  -s hybridautos-fallback-backup-20260716 \
  -w "$(openssl rand -base64 48)"
```

Expected: Keychain entry exists, output directory mode is no broader than `700`, and the passphrase is never printed, committed, copied into a plan, or placed in shell history.

- [ ] **Step 2: Stream production directly into local encryption**

Use the existing Keychain value only through an environment variable in the local process. The remote commands write database/tar bytes to stdout and never create an export or archive file; local OpenSSL encrypts that stream directly into mode-0600 artifacts:

```bash
set -euo pipefail
umask 077
DEST='/Users/kirillbezikov/Documents/Сайт Дубай /backups/2026-07-16_before_independent_fallback'
export BACKUP_KEY="$(security find-generic-password -a "$USER" -s hybridautos-fallback-backup-20260716 -w)"
trap 'unset BACKUP_KEY' EXIT
ssh -i "$HOME/.ssh/id_ed25519" cmoevexs@cmoevexs.beget.tech \
  "/usr/local/bin/php8.3 /usr/local/bin/wp-cli.phar --path=/home/c/cmoevexs/hybridautos.ae/public_html db export - --quiet | gzip -9" \
  | openssl enc -aes-256-cbc -salt -pbkdf2 -iter 200000 -pass env:BACKUP_KEY \
      -out "$DEST/database.sql.gz.enc"
ssh -i "$HOME/.ssh/id_ed25519" cmoevexs@cmoevexs.beget.tech \
  "tar -C /home/c/cmoevexs/hybridautos.ae -czf - public_html" \
  | openssl enc -aes-256-cbc -salt -pbkdf2 -iter 200000 -pass env:BACKUP_KEY \
      -out "$DEST/public_html.tar.gz.enc"
chmod 600 "$DEST"/*.enc
```

If SSH is unavailable, use only a separately reviewed equivalent that streams the complete FTP tree into tar stdout and a complete database export over authenticated HTTPS stdout, with both stdout streams piped immediately into the same OpenSSL command. No helper may save SQL/archive/config, accept an unauthenticated request, or remain installed. A Beget snapshot may be created as additional protection but is not a substitute. If a complete stream-to-encryption path cannot be proven, stop with `ENCRYPTED_BACKUP_GATE_BLOCKED` before production edits.

- [ ] **Step 3: Verify encrypted streams and restore without backup plaintext files**

With the Keychain key still in the environment, require both integrity streams to exit 0:

```bash
openssl enc -d -aes-256-cbc -pbkdf2 -iter 200000 -pass env:BACKUP_KEY \
  -in "$DEST/database.sql.gz.enc" | gzip -t
openssl enc -d -aes-256-cbc -pbkdf2 -iter 200000 -pass env:BACKUP_KEY \
  -in "$DEST/public_html.tar.gz.enc" | tar -tzf - \
  | awk 'BEGIN{cfg=theme=mu=0} /public_html\/wp-config.php$/{cfg=1} /public_html\/wp-content\/themes\//{theme=1} /public_html\/wp-content\/mu-plugins\/landing-config\//{mu=1} END{exit !(cfg&&theme&&mu)}'
```

Stream-decrypt the SQL directly into the existing outbound-blocked disposable staging database—never into a `.sql` file—and confirm WordPress can read the policy and lead tables. The site artifact is verified by complete tar traversal and required rollback paths without extraction. Run `php -l` against reviewed source/live files rather than extracting backup plaintext. Drop the disposable database after proof. Require a scoped search to find no `.sql`, `.sql.gz`, `.tar`, `.tar.gz`, `wp-config.php`, `.env`, token, or decrypted contact artifact in backup/temp directories.

Expected: both ciphertext files non-empty/mode 0600, integrity and staging read pass, ciphertext SHA-256 values recorded, and no plaintext backup exists locally, remotely, or on staging.

- [ ] **Step 4: Record immutable rollback identifiers and retention**

Record without secrets: current site/WordPress Git SHAs and tags, active Vercel deployment ID/alias, ciphertext SHA-256/sizes, live SHA-256 for every allow-listed file, `wp-config.php` hash, Privacy Policy page ID/content hash, cron inventory hash, and integration IDs. Retain both local encrypted artifacts and their Keychain key through `2026-10-14` with file mode `600`/directory mode `700`; review deletion on/after `2026-10-15` only after a newer verified encrypted backup exists. Git code tags remain because they contain no contacts.

---

### Task 7: Deploy Every Layer Disabled First

**Files:**
- Production configuration and allow-listed release files only.

**Interfaces:**
- Consumes: green Task 5 and verified Task 6 backup.
- Produces: deployed Vercel, WordPress, policy, and frontend code with every contact-accepting path still disabled.

- [ ] **Step 1: Confirm free external resources and deploy Vercel in test/disabled mode**

Verify the private project `neuroboostpr-pixel/hybridautos-lead-fallback`, production alias `https://hybridautos-lead-fallback.vercel.app`, account authentication, existing Pro/Enterprise commercial eligibility, effective DPA/data-use setting, and that Redis/QStash are free or already included. Hobby or any request for a new unapproved charge stops release. Set all server-side values interactively and never in Git or command output: `FALLBACK_ACCEPTING_ENABLED=false`, `FALLBACK_TEST_MODE=true`, the token-signing secret shared only with WordPress, the separate status-signing secret shared only with WordPress, `LP_PAYLOAD_HASH_SECRET`, `LP_RATE_LIMIT_SECRET`, the AES-256-GCM encryption key, existing Telegram token/chat, Upstash Redis, and QStash credentials. Each of the four HMAC secrets is a different 64-lowercase-hex value; the encryption key is independent. The hardcoded test prefix is `[TEST — DO NOT CONTACT]`.

Deploy production, run `pnpm test`, `pnpm typecheck`, and `pnpm build`, then check the shallow `/api/v1/health`. While acceptance is false, a valid-looking POST must fail closed with the documented disabled `503`, create no receipt, schedule no QStash job, and send no Telegram message. Do not expect an end-to-end receipt or Telegram test yet; that is deliberately postponed until Task 8 while test mode is still on.

- [ ] **Step 2: Deploy WordPress token/status/monitoring code with all flags disabled**

Use the WordPress plan's mixed-version-safe sequence: install/enable the flocked one-minute system cron first; upload additive DB/new unused modules; migrate; replace the entrypoint while the old synchronous lead handler remains; prove a labeled due row drains; replace asynchronous `rest-lead.php` last; then require no queue growth. Configure in `wp-config.php`, without printing values:

```php
define('LP_FALLBACK_ENABLED', false);
define('LP_FALLBACK_TEST_MODE', false);
define('LP_FALLBACK_URL', 'https://hybridautos-lead-fallback.vercel.app/api/v1/fallback-leads');
define('LP_FALLBACK_SITE_ID', 'hybridautos-ae');
define('LP_FALLBACK_SIGNING_SECRET', /* protected 64-lowercase-hex value A */);
define('LP_FALLBACK_STATUS_URL', 'https://hybridautos-lead-fallback.vercel.app');
define('LP_FALLBACK_STATUS_SECRET', /* protected, different 64-lowercase-hex value B */);
define('LP_MONITOR_ENABLED', false);
define('LP_MONITOR_TELEGRAM_INTEGRATION_ID', /* existing verified positive integration ID */);
```

The comments are documentation placeholders, not pasteable PHP. In Beget's protected editor, enter valid quoted secret A/B values and the actual positive Telegram integration ID recorded in the backup inventory; never copy them into Git, chat, shell history, logs, or this plan. Secret A must equal Vercel's intake-token signing value and secret B its status-signing value. Vercel's additional `LP_PAYLOAD_HASH_SECRET` and `LP_RATE_LIMIT_SECRET` are separate roles. Require all four HMAC values to be distinct lowercase 64-hex strings and the encryption key to be independent. Verify only names, regex/equality across intended systems, and inequality between roles; do not print values.

Run migrations and verify the normal lead route remains compatible with cached requests. With both WordPress browser flags false, ordinary `GET /wp-json/landing/v1/fallback-token` must return `404`; unsigned public health and the correctly signed server-to-server submission-status/external-observation routes remain available independently of those browser flags, while bad signatures on the signed routes fail closed. No browser or third party can obtain a token or store a fallback receipt at this stage.

- [ ] **Step 3: Publish the Privacy Policy while fallback remains disabled**

Find the live page by slug, save its current revision, replace only `post_content` with `08_КОД/legal-pages/privacy-policy-hybridautos-en.html`, keep slug `/privacy-policy/`, publish, and verify HTTP 200 plus the exact Vercel/Upstash/7-day/30-day wording. Check every consent link on all six routes still opens that page.

- [ ] **Step 4: Deploy frontend files with `LP_FALLBACK_ENABLED=false`**

Atomically upload only:

```text
08_КОД/wp-theme/includes/fallback-config.php
08_КОД/wp-theme/functions.php
08_КОД/wp-theme/assets/js/lead-form.js
```

Upload the new include and JavaScript first; replace `functions.php` last. Download each file after upload and require local/live SHA-256 equality.

- [ ] **Step 5: Prove disabled-first production behavior**

Before any test submission, inspect the exact enabled integrations server-side: the sole lead Email recipient must equal `elapova00@gmail.com`; every previous Neuroboost Email/integration must be disabled; Telegram and Roistat/CRM must remain enabled with their recorded IDs. Evidence may mask the address, but the comparison itself uses the full exact value. Stop release if an old lead recipient remains enabled.

For `/`, `/li-auto/`, `/zeekr/`, `/xiaomi/`, `/lynk-co/`, and `/rox/`, assert the cacheable public config is exactly the seven-key contract with `enabled:false`, exact approved endpoint and token path, `testMode:false`, no token, and no optional admin keys or server secrets. Confirm the current cache-busted `lead-form.js`, the correct consent link, and no lead-handler console errors. Submit one reserved `[TEST — DO NOT CONTACT]` primary request through each distinct live form template and require one WordPress lead, one Thank You redirect, Email accepted for exactly `elapova00@gmail.com`, Telegram and Roistat/CRM success, no delivery to a previous/Neuroboost recipient, and no Vercel receipt; reconcile the UUIDs and delete/mark only the test records according to the existing test-data procedure.

---

### Task 8: Prove the Controlled Test, Turn Test Mode Off, Then Enable Live Fallback

**Files:**
- Production flags only; no new source edits.

**Interfaces:**
- Consumes: verified disabled-first deployment.
- Produces: a test-proven receiver followed by active live fallback and monitoring, with no test flag exposed to advertising traffic.

- [ ] **Step 1: Enable and observe privacy-safe WordPress monitoring**

Set `LP_MONITOR_ENABLED=true`, keep `LP_FALLBACK_ENABLED=false`, run cron, and require a fresh heartbeat for two consecutive minutes. Send one safe test alert and verify exactly one `[TEST — DO NOT CONTACT]` Telegram technical message. Confirm no contact appears in alert table/message/log.

- [ ] **Step 2: Enable the isolated test window while live fallback stays off**

Keep `LP_FALLBACK_ENABLED=false`. Set WordPress `LP_FALLBACK_TEST_MODE=true`; set Vercel `FALLBACK_ACCEPTING_ENABLED=true` while keeping `FALLBACK_TEST_MODE=true`; deploy production and verify health. The signed submission-status endpoint remains available to the authenticated Vercel worker exactly as it was with browser flags off; ordinary and anonymous token requests must still return `404`. Ordinary page HTML must still show `enabled:false`, `testMode:false`, no token, no `forcePrimaryFailure`, and no `testRestNonce`. A random user or arbitrary query string receives exactly the same ordinary response; only the admin POST can arm the one-time user transient.

- [ ] **Step 3: Run the admin-only controlled primary-failure test**

While logged into WordPress as a user with `manage_options`, submit the admin page's nonce-protected `lp_fallback_arm_controlled_failure` POST form. Require the action to set the 60-second user transient and return `303` to exact clean `home_url('/')` with no query, no-store, and `Referrer-Policy:no-referrer`. The redirected page must consume/delete the transient once under its named lock and expose the seven public keys plus `testMode:true`, `forcePrimaryFailure:true`, and a non-empty `testRestNonce`; refreshing the same clean URL must immediately return ordinary config. The token prefetch sends that REST nonce only in `X-WP-Nonce` and receives no-store `mode:'test'`. Both normal and legacy WordPress submissions route to the guaranteed nonexistent controlled-test paths only for that one server-issued state. No ordinary page, query visitor, expired/already-consumed transient, or `testMode` value by itself may alter either primary path.

Submit `TEST — DO NOT CONTACT — FALLBACK` with an empty name, canonical phone matching `^\+971[0-9]{9}$`, consent checked, and deliberately oversized Unicode message/UTM/click fields. Require: fallback begins only after the two controlled WordPress routes produce the eligible unconfirmed result; its new `AbortController` gives it a full independent 15,000 ms; the body remains at most 16,384 URL-encoded bytes while phone, consent, UUID, frozen first reason, exact endpoint, and token remain intact; response is HTTP success with `ok:true`, the exact UUID, `receipt_id` matching `/^rct_[0-9a-f]{32}$/`, `stored:true`, and `delivery_state:'pending'`; only then Thank You and `lead_fallback_success` occur. There must be no WordPress lead, `lead_success`, browser storage entry, or contact in logs/analytics.

The receipt is immediate but Telegram is intentionally delayed for reconciliation. At about 45 seconds the worker checks the signed WordPress status; if status is unreachable or malformed it retries about 30 seconds later. Require exactly one `[TEST — DO NOT CONTACT] 🛟 Резервная заявка` by about 75 seconds, not immediately, then verify encrypted contact deletion after confirmed Telegram delivery. The only residual duplicate scenario is a WordPress save completing after reconciliation while the signed status endpoint remains unreachable through both checks; if that rare case happens, the shared UUID identifies the two copies for reconciliation.

- [ ] **Step 4: Prove idempotent retry and complete the test-mode smoke before disabling it**

Replay the same normalized contact/context and UUID first with a refreshed valid token and then with a different `fallback_reason`. Both must return the same receipt, never `409`, create no second encrypted contact, and send no second Telegram message because Vercel's stable HMAC fingerprint excludes only `intake_token` and `fallback_reason`. Changing a contact field in the browser creates a new UUID; directly reusing the old UUID with a changed stable payload returns `409 idempotency_conflict` and sends nothing.

While Vercel is still `FALLBACK_TEST_MODE=true`, run:

```bash
cd "/Users/kirillbezikov/Documents/Сайт Дубай /hybridautos-lead-fallback"
pnpm dlx vercel@54.2.0 env run -e production -- pnpm smoke -- --base-url https://hybridautos-lead-fallback.vercel.app
```

Require green health, token validation, encryption/decryption, strict receipt, delayed Telegram, status reconciliation, same-payload replay, changed-payload conflict, cleanup, rate-limit, and redacted-log checks. Do not turn test mode off before this smoke is green.

- [ ] **Step 5: Exercise every form on all six advertising routes while the controlled test is available**

Enumerate every actual lead form on all six routes rather than assuming one form per page. In an authenticated, no-cache controlled-test browser session, exercise each form instance with a unique labeled UUID and valid consent. For each instance verify token prefetch on real focus/form start, immutable first-submit snapshot, canonical phone, empty name acceptance, oversized attribution truncation without contact loss, independent 15-second fallback deadline, strict pending receipt, Thank You only after `stored:true`, and one delayed test Telegram delivery. In a separate ordinary/anonymous session for the same URLs, prove the controlled paths and admin nonce are absent. Record route, form ID/CTA, UUID, receipt, expected delayed message count, and result without recording contact values.

- [ ] **Step 6: Close the test window, verify disabled state, then enable live browser fallback last**

First set WordPress `LP_FALLBACK_TEST_MODE=false`, delete any remaining per-user test transient, and purge caches; prove a fresh clean page has `testMode:false`, no force flag, no REST nonce, and cannot obtain a test token. Immediately restore Vercel to `FALLBACK_ACCEPTING_ENABLED=false,FALLBACK_TEST_MODE=true`, redeploy, prove effective flags and public POST 503, and complete the normal-primary/no-receipt check. While website fallback is still disabled, set Vercel to final `FALLBACK_ACCEPTING_ENABLED=true,FALLBACK_TEST_MODE=false`, redeploy, require green health/effective flags, and prove every still-due test receipt keeps its immutable TEST prefix. Only after those checks set `LP_FALLBACK_ENABLED=true`, leave `LP_MONITOR_ENABLED=true`, and purge WordPress/page/CDN caches.

On each of the six routes, the cacheable config must now have exactly seven keys, `enabled:true`, exact POST and token endpoints, `testMode:false`, and no token or admin properties. Real focus/form start must perform a PII-free same-origin no-store GET and keep the validated `mode:'live'` token only in form memory. Submit starts a refresh in parallel with the still-working WordPress primary; if refresh fails and WordPress later fails, an unexpired prefetched bundle remains usable. Cached HTML must never contain a token.

- [ ] **Step 7: Run the normal primary test, monitoring scenarios, and final six-route acceptance**

Use `TEST — DO NOT CONTACT — PRIMARY`, a reserved team test phone, consent checked, and very long UTM/click parameters. Expected: one WordPress lead, Telegram success, Email accepted for exactly `elapova00@gmail.com`, Roistat/CRM success, no delivery to any previous/Neuroboost recipient, Thank You, `lead_success`, no `lead_fallback_success`, and no Upstash receipt for that UUID. Confirm the exact effective integration IDs and recipient after the test; confirm Roistat, Metrika, Google Ads, and CRM goals/integrations have not changed; conversion remains tied to confirmed Thank You, not generic form interaction.

Demonstrate fresh evidence for: missing WordPress lead after five minutes creates one privacy-safe alert; pending receipt creates a non-terminal watch, pending>10m/unknown alerts while recoverable, delivered resolves, and expired/stored-false reopens missing; simulated integration failure creates one safe alert without changing the saved lead. For Beget-only or Redis-only outage with its independent ledger reachable, two failures create one outage and first healthy check one recovery. Separately verify the documented bounded/stateless simultaneous-outage behavior without claiming exact-once. Restore every deliberately failed component immediately.

For every form instance on `/`, `/li-auto/`, `/zeekr/`, `/xiaomi/`, `/lynk-co/`, and `/rox/`, run browser acceptance for focus/prefetch, validation, primary success, retry state, and an intercepted never-resolving fallback that must stop at the 15-second deadline instead of hanging. Require HTTP 200, same current handler hash/version, consent link correct, exact public config, no console error, no contact/token in browser storage, and no path that redirects before durable confirmation. Download every deployed allow-listed file and compare SHA-256 to reviewed Git commits. Confirm logs contain no request bodies, contacts, tokens, webhook URLs, or raw provider responses.

---

### Task 9: Verify Rollback and Observe the Release

**Files:**
- No source changes unless a defect is found; a defect triggers rollback, not an unreviewed production edit.

**Interfaces:**
- Consumes: Task 6 rollback artifacts and Task 8 active release.
- Produces: rehearsed rollback and a completed observation gate.

- [ ] **Step 1: Rehearse flag-only emergency rollback**

Document and test the fastest safe rollback in this order:

1. Set `LP_FALLBACK_ENABLED=false` and purge cache — newly loaded pages return to WordPress-only flow.
2. Set Vercel `FALLBACK_ACCEPTING_ENABLED=false`, redeploy the current worker-capable build, and verify public POST 503; this also blocks already-open/cached pages and still-valid 12-hour tokens without disabling internal workers, receipt status, or recovery.
3. Set `LP_MONITOR_ENABLED=false` only if monitoring itself is noisy; lead saving remains active.
4. Keep Vercel receipts and WordPress delivery rows intact for drain/recovery; do not delete pending encrypted contacts or queued integrations during rollback.

Expected: a normal test still saves in WordPress and opens Thank You; no new fallback receipt appears.

- [ ] **Step 2: Rehearse code rollback from immutable artifacts**

After intake is disabled, first inspect Vercel recoverable payload/due-work counts and WordPress `queued|sending|retry_wait` delivery rows. Keep the current Vercel workers/status/recovery and WordPress async worker loaded until those queues drain or are manually recovered. Only when Vercel has zero recoverable payloads/due jobs—or a proven backward-compatible target deployment uses the same Redis/env—may the alias be rolled back. Only when no fallback contact remains in processing may the previous Privacy Policy revision be restored. For WordPress rollback, switch to the old synchronous `rest-lead.php` first while the new worker remains harmlessly loaded, drain existing delivery rows, then restore the old entrypoint/modules. Re-download and hash-compare. Do not restore the full database for a code rollback; that would erase post-release leads.

- [ ] **Step 3: Define the database-restoration exception**

Use the full database dump only for proven schema/data corruption. Before restoration, export all post-snapshot leads, audit rows, delivery logs, incidents, and receipts; merge them after restore. A normal app rollback never overwrites these tables.

- [ ] **Step 4: Observe two monitoring intervals and real traffic**

Observe at least two QStash intervals (10 minutes) after enablement, then review again after the first real advertising lead. Correlate source/UTM, browser `submission_id`, WordPress lead/audit row or Vercel receipt, Thank You conversion, Email/Telegram/Roistat/CRM delivery state, and monitor incident without exposing the contact in logs. A fallback receipt proves encrypted storage immediately; its Telegram message is expected only after the 45-second status check or, when status is uncertain, the second check about 30 seconds later (about 75 seconds total). During that window it is pending, not lost, and its encrypted contact is recoverable under the seven-day rule.

Require: fresh WordPress heartbeat, healthy external check, no unexplained duplicate Telegram, no unresolved critical incident, integration success/accepted statuses, and no privacy leakage. Document the narrow residual duplicate risk: WordPress may finish after the browser timeout while both signed status checks are unreachable; the common UUID makes that late primary copy and fallback copy identifiable. If any gate fails, disable browser fallback first and investigate without stopping normal WordPress intake or deleting pending encrypted contacts.

- [ ] **Step 5: Final completion gate**

Release is complete only with fresh evidence of: primary success/no receipt; admin-only controlled fallback/one strict pending receipt/one delayed Telegram by about 75 seconds; replay with a fresh token or changed reason/same receipt/no duplicate; changed stable payload/`409`; independent 15-second timeout/no hang; oversized Unicode attribution/contact preserved; safe missing-lead alert; safe integration alert; outage/recovery pair; every form on all six routes current; cacheable HTML token-free; policy published; full encrypted backup restored successfully; reviewed Git SHAs equal live hashes; rollback verified; and clean logs. Only then report that the protection is active.
