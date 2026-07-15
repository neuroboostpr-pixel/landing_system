# HybridAutos Theme, Browser Attribution, and Analytics Reliability Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Put the complete current HybridAutos theme under verified private source control, make every browser form keep and retry the same submission safely, preserve first-touch advertising attribution, and count a conversion only after WordPress confirms a saved lead with a positive numeric `lead_id`.

**Architecture:** The private `hybridautos-ae` repository is the source of truth for the production theme. A small attribution module captures the first non-empty advertising touch in `sessionStorage`; the form module owns one UUID per submission lifecycle, calls the primary REST route with a narrowly scoped fallback, and treats only `{ "ok": true, "lead_id": positive integer }` as success. Modal code carries stable CTA context without resetting a failed attempt. A single `lead_success` data-layer event drives GTM, Yandex Metrika, and Google Ads; the thank-you page is presentation only. Theme assets are versioned by file content/mtime, deployed only after the compatible backend, and verified by anonymous public checks on all six landing pages.

**Tech Stack:** WordPress/PHP 8.1 theme, browser JavaScript ES2018, `URLSearchParams`, `sessionStorage`, Fetch API, Node.js built-in test runner, Playwright Chromium, Python 3 standard library, Git/GitHub, GTM container `GTM-WZXC5HVS`, Yandex Metrika counter `110335743`, Google Ads conversion tag already present in that GTM container.

## Global Constraints

- Work in the private repository `https://github.com/neuroboostpr-pixel/hybridautos-ae.git`, local checkout `/Users/kirillbezikov/Documents/Сайт Дубай /hybridautos-ae`, branch `fix/lead-reliability-observability`.
- This plan owns theme/browser/attribution/analytics work only. The compatible WordPress endpoint, durable lead storage, audit log, delivery queue, Email/Telegram/Roistat adapters, and database migration `1.1.0` are implemented by the companion `landing_system` plan. Do not duplicate those server changes here.
- Never deploy before the fresh full files/database backup and restore rehearsal pass. Never use a site-wide `--delete`; production activation replaces only the manifest allow-list.
- GitHub contains source only: no `wp-config.php`, credentials, tokens, database dumps, logs, uploads, screenshots containing contacts, or customer data.
- The repository currently tracks SQL dumps under `09_ДЕПЛОЙ/backups/`. That violates the approved design. Cleaning the current tree is mandatory; rewriting existing GitHub history is a coordinated, explicitly approved operation because it changes shared commit SHAs. Do not push feature/backup branches until the history scan is clean.
- Active reCAPTCHA execution and blocking are removed from the theme: no Google reCAPTCHA script, `grecaptcha.execute`, `lpRecaptchaSiteKey`, or `recaptcha_token`. Dormant WordPress settings may remain only in the companion server code for backward compatibility.
- Do not push name, phone, email, message, budget, purpose, referrer, URL, UTM values, or click IDs to GTM/Ads/Metrika. The `lead_success` event contains only `lead_id`, `form_id`, `brand`, `model`, and `cta_key`.
- Generic CTAs send `model=""`. Only an explicit model button or a user-selected model sends a model. `Lynk & Co 900` must survive HTML entity decoding exactly as that string.
- The privacy checkbox is unchecked and required. `/privacy-policy/` returned HTTP 404 during plan preparation on 2026-07-15. Production release is blocked until the owner/legal reviewer approves the exact policy text and the published URL returns HTTP 200. Do not invent company/legal details in code.
- Missing/broken `sessionStorage`, Yandex, Roistat, cookies, GTM, or an ad blocker must never delay or reverse a confirmed contact save.
- Paid traffic remains off until both gates pass: **contact preservation ready** and **advertising analytics ready**.

---

## File Map and Interfaces

All paths in this section are relative to `/Users/kirillbezikov/Documents/Сайт Дубай /hybridautos-ae` unless an absolute path is shown.

| Path | Action | Responsibility |
|---|---|---|
| `.gitignore` | Modify | Exclude database dumps and local release evidence containing sensitive data. |
| `scripts/pull-production-theme.py` | Create | Read Beget FTP credentials from the existing local secrets file, download only the complete production theme, and produce a SHA-256 manifest without printing secrets. |
| `scripts/write-release-manifest.py` | Create | Bind the tested theme code commit, companion `landing_system` commit, DB version `1.1.0`, and theme-file hashes. |
| `scripts/verify-public-theme.py` | Create | Verify versioned public JavaScript and exact SHA-256 values anonymously on `/`, `/li-auto/`, `/zeekr/`, `/xiaomi/`, `/lynk-co/`, and `/rox/`. |
| `package.json` | Create | Pin and expose browser/unit quality-control commands. |
| `playwright.config.mjs` | Create | Run Chromium tests serially with traces retained on failure. |
| `tests/node/lead-attribution.test.cjs` | Create | First-touch, cookie fallback, safe decoding, and unavailable-storage tests. |
| `tests/node/lead-form.test.cjs` | Create | UUID, response validation, REST fallback, payload, and exactly-once analytics tests. |
| `tests/browser/form-reliability.spec.mjs` | Create | Real browser lifecycle, modal retry, navigation, success/error, and data-layer checks. |
| `tests/browser/fixtures/form-page.html` | Create | PII-free form fixture with generic and model-specific CTA paths. |
| `tests/python/test_theme_contract.py` | Create | Parse all theme markup and enforce the CTA/form/consent/honeypot/script registry. |
| `08_КОД/wp-theme/lead-cta-registry.json` | Create | The authoritative 32-path CTA inventory used by tests and manual production checks. |
| `08_КОД/wp-theme/assets/js/lead-attribution.js` | Create | Capture/read first touch and runtime attribution without persistent pre-consent writes. |
| `08_КОД/wp-theme/assets/js/lead-form.js` | Modify | Validate, submit, retry, preserve UUID/values, emit one confirmed-success event, and redirect safely. |
| `08_КОД/wp-theme/assets/js/modal.js` | Modify | Copy stable CTA context and preserve failed submission lifecycle across close/reopen. |
| `08_КОД/wp-theme/assets/css/main.css` | Modify | Accessible consent/error styling and off-screen honeypot styling. |
| `08_КОД/wp-theme/functions.php` | Modify | Remove active reCAPTCHA, enqueue attribution in dependency order, inject runtime config, and cache-bust standalone page assets. |
| `08_КОД/wp-theme/blocks/lazyblock-custom/block.php` | Modify | Home CTA/form attributes, honeypot, explicit consent, and error region. |
| `08_КОД/wp-theme/li-auto.html` | Modify | Li Auto CTA registry, blank generic model, consent/honeypot, and attribution script. |
| `08_КОД/wp-theme/zeekr.html` | Modify | Zeekr CTA registry, blank generic model, consent/honeypot, and attribution script. |
| `08_КОД/wp-theme/xiaomi.html` | Modify | Xiaomi CTA registry, blank generic model, consent/honeypot, and attribution script. |
| `08_КОД/wp-theme/lynk-co.html` | Modify | Generic blank model plus explicit `Lynk & Co 900`, consent/honeypot, and attribution script. |
| `08_КОД/wp-theme/rox.html` | Modify | ROX CTA registry, blank generic model, consent/honeypot, and attribution script. |
| `09_ДЕПЛОЙ/releases/2026-07-15-lead-reliability-theme.json` | Generate after code commit | Immutable release record with real values only. |

### Browser-to-server request contract

Every primary and fallback POST uses the same encoded body and the same UUID:

```text
name, phone, message, source_block, pd_consent, website, submission_id,
landing_url, submit_url, landing_referrer,
utm_source, utm_medium, utm_campaign, utm_term, utm_content,
gclid, gbraid, wbraid, yclid, fbclid, msclkid,
ym_client_id, roistat_visit,
form_id, brand, model, cta_key, cta_label, cta_placement
```

The browser contract is:

```js
// Only this shape is success. lead_id must be a JSON number, integer, and > 0.
{ ok: true, lead_id: 123, delivery_status: 'queued' }
```

Malformed JSON, HTTP 4xx/5xx, network failure, `{ ok: false }`, missing `lead_id`, `lead_id: 0`, a negative ID, a decimal ID, and `lead_id: "123"` are errors: no redirect and no conversion.

### Public JavaScript interfaces

`lead-attribution.js` exposes `window.LPLeadAttribution` in the browser and `module.exports` in Node tests:

```js
{
  STORAGE_KEY: 'lp_first_touch_v1',
  AD_KEYS: [
    'utm_source', 'utm_medium', 'utm_campaign', 'utm_term', 'utm_content',
    'gclid', 'gbraid', 'wbraid', 'yclid', 'fbclid', 'msclkid'
  ],
  captureFirstTouch(locationHref, documentReferrer, storage),
  readFirstTouch(storage),
  readCookie(cookieString, name),
  readRuntimeIds(windowObject, cookieString),
  buildAttribution(locationHref, documentReferrer, storage, cookieString, runtimeIds)
}
```

`lead-form.js` exposes `window.LPLeadForm` in the browser and `module.exports` in Node tests:

```js
{
  isPositiveLeadId(value),
  getOrCreateSubmissionId(form, cryptoObject),
  clearConfirmedSubmission(form),
  isRouteLevel404(response, parsedBody, usedPrimaryRoute),
  buildRequestBody(form, attribution),
  requestLead(fetchFunction, restBase, encodedBody),
  emitLeadSuccessOnce(data, context, storage, dataLayer, redirectFunction),
  initForm(form)
}
```

`modal.js` exposes `window.lpModal.open(id, context)`, `window.lpModal.close(modal)`, and `window.lpModal.contextFromTrigger(trigger)`. `context` has exactly `model`, `ctaKey`, `ctaLabel`, and `ctaPlacement`.

---

### Task 1: Establish a clean, complete production-theme baseline in the private repository

**Files:**
- Create: `scripts/pull-production-theme.py`
- Modify: `.gitignore`
- Replace from verified production source: `08_КОД/wp-theme/**`

- [ ] **Step 1: Clone the exact reviewed remote state and verify privacy**

```bash
cd "/Users/kirillbezikov/Documents/Сайт Дубай "
git clone https://github.com/neuroboostpr-pixel/hybridautos-ae.git hybridautos-ae
cd hybridautos-ae
git rev-parse HEAD
gh repo view neuroboostpr-pixel/hybridautos-ae --json visibility --jq .visibility
```

Expected initial output:

```text
2f3ee31125b9506c39bf552b6aa9814d8305a9a3
PRIVATE
```

If `main` has moved, stop and review the new commits before continuing; do not reset it to the recorded SHA.

- [ ] **Step 2: Add a failing repository-content test before cleanup**

Add a test in `tests/python/test_theme_contract.py` named `test_git_tree_contains_source_only`. It runs `git ls-files` and fails if any tracked path matches:

```text
*.sql
wp-config.php
*.log
wp-content/uploads/**
```

Run:

```bash
python3 -m unittest tests.python.test_theme_contract.ThemeRepositoryContractTest.test_git_tree_contains_source_only -v
```

Expected result before cleanup: `FAIL`, with the tracked `09_ДЕПЛОЙ/backups/*.sql` paths reported. This red test proves the known repository problem is detected.

- [ ] **Step 3: Clean the current tree and coordinate existing-history remediation**

Add these exact ignore rules:

```gitignore
09_ДЕПЛОЙ/backups/*.sql
09_ДЕПЛОЙ/backups/*.sql.gz
09_ДЕПЛОЙ/backups/*.zip
09_ДЕПЛОЙ/releases/evidence-private/
```

Remove dumps from the current Git tree without deleting the user's local backup copies:

```bash
git rm --cached -- '09_ДЕПЛОЙ/backups/'*.sql
git add .gitignore tests/python/test_theme_contract.py
git commit -m "security(repo): keep database dumps out of source control"
```

Then scan all history:

```bash
git rev-list --objects --all | rg '09_ДЕПЛОЙ/backups/.*\.sql$|wp-config\.php$|wp-content/uploads/'
```

Expected final output before any new branch is pushed: no output, exit code `1` from `rg` because no prohibited path exists. The current remote is known to contain historical dump paths, so reaching that result requires an owner-approved coordinated history rewrite. Use `git filter-repo` only after explicit approval, then force-update all affected shared refs and tell every collaborator to re-clone. Do not treat removing files only from the latest commit as a clean history.

After that explicit approval, rewrite every remote branch/tag through a mirror so an old side branch cannot retain the dumps. The local `main` cleanup commit is injected into the mirror before filtering:

```bash
test ! -e /private/tmp/hybridautos-ae-history-clean-20260715.git
git ls-remote origin > /private/tmp/hybridautos-ae-remote-refs-before-history-clean-20260715.txt
git clone --mirror https://github.com/neuroboostpr-pixel/hybridautos-ae.git /private/tmp/hybridautos-ae-history-clean-20260715.git
git -C /private/tmp/hybridautos-ae-history-clean-20260715.git fetch "/Users/kirillbezikov/Documents/Сайт Дубай /hybridautos-ae" main:refs/heads/main
git -C /private/tmp/hybridautos-ae-history-clean-20260715.git filter-repo --force --path-glob '09_ДЕПЛОЙ/backups/*.sql' --invert-paths
git -C /private/tmp/hybridautos-ae-history-clean-20260715.git remote add origin https://github.com/neuroboostpr-pixel/hybridautos-ae.git
git -C /private/tmp/hybridautos-ae-history-clean-20260715.git rev-list --objects --all | rg '09_ДЕПЛОЙ/backups/.*\.sql$|wp-config\.php$|wp-content/uploads/'
git -C /private/tmp/hybridautos-ae-history-clean-20260715.git push --force --prune origin 'refs/heads/*:refs/heads/*'
git -C /private/tmp/hybridautos-ae-history-clean-20260715.git push --force --prune origin 'refs/tags/*:refs/tags/*'
git ls-remote origin > /private/tmp/hybridautos-ae-remote-refs-after-history-clean-20260715.txt
```

Expected scan output before either force-push: none. The implementation worker must review the before/after ref lists, verify all intended branches/tags still exist, and obtain approval in the active task immediately before the two force-push commands. Afterward, replace the working clone with a fresh clone of the rewritten remote, rerun the source-only test, and require every collaborator to re-clone; merging an old clone would reintroduce the removed history. Retain no unfiltered local Git clone after the rewritten remote and fresh clone have been verified.

- [ ] **Step 4: Write the production-theme puller with a no-secret interface**

`scripts/pull-production-theme.py` must:

1. accept exactly one destination directory argument;
2. read `/Users/kirillbezikov/Documents/Сайт Дубай /Секреты.txt` with the same `KEY=value` parsing rules as `/Users/kirillbezikov/Documents/Сайт Дубай /backup_ftp.py`;
3. use `PROD_BEGET_FTP_HOST`, `PROD_BEGET_FTP_USER`, and `PROD_BEGET_FTP_PASSWORD` without printing their values;
4. download only `/hybridautos.ae/public_html/wp-content/themes/lp-hibridcars-uae` recursively;
5. refuse a non-empty destination, so stale files cannot be mixed into the baseline;
6. write `theme.sha256` containing sorted `sha256  relative/path` rows for every downloaded regular file except `theme.sha256`;
7. print only file count, byte count, destination, and manifest path;
8. exit non-zero on an FTP error or an empty theme.

Add unit tests with a fake FTP object for a nested directory, an empty directory, and a failed transfer. Run:

```bash
python3 -m unittest tests.python.test_pull_production_theme -v
```

Expected output: three tests, all `OK`.

- [ ] **Step 5: Import the complete current production theme and prove byte-for-byte parity**

```bash
python3 scripts/pull-production-theme.py /private/tmp/hybridautos-theme-production-20260715
rsync -a --delete --exclude theme.sha256 /private/tmp/hybridautos-theme-production-20260715/ 08_КОД/wp-theme/
(cd 08_КОД/wp-theme && find . -type f ! -name theme.sha256 -print0 | sort -z | xargs -0 shasum -a 256 | sed 's#  \./#  #' > /private/tmp/hybridautos-theme-repo.sha256)
diff -u /private/tmp/hybridautos-theme-production-20260715/theme.sha256 /private/tmp/hybridautos-theme-repo.sha256
shasum -a 256 08_КОД/wp-theme/assets/js/lead-form.js
```

`rsync --delete` is permitted here only because both sides are local copies of the single theme directory; it is never used against the production site. Expected `diff` output: empty. Expected production hotfix hash at the time this plan was written:

```text
34410806e241b51e576bc8d0e21fc4005e5250d967eab73d9905322e4b2c4522
```

If the live hash differs, inspect the production file and the already captured local copy at `/Users/kirillbezikov/Documents/Сайт Дубай /site-current/wp-content/themes/lp-hibridcars-uae/assets/js/lead-form.js`; do not silently choose either copy.

- [ ] **Step 6: Commit and publish the immutable pre-change theme baseline**

```bash
git add 08_КОД/wp-theme scripts/pull-production-theme.py tests .gitignore
git commit -m "chore(theme): import current production baseline"
git branch backup/hybridautos-prod-before-reliability-2026-07-15
git push origin backup/hybridautos-prod-before-reliability-2026-07-15
git switch -c fix/lead-reliability-observability
test "$(git rev-parse backup/hybridautos-prod-before-reliability-2026-07-15)" = "$(git ls-remote origin refs/heads/backup/hybridautos-prod-before-reliability-2026-07-15 | cut -f1)"
```

Expected output from `test`: none, exit code `0`. Business meaning: the exact live theme before reliability work is recoverable from the private remote, not only from one laptop.

---

### Task 2: Install the test harness and write the browser contracts first

**Files:**
- Create: `package.json`
- Create: `playwright.config.mjs`
- Create: `tests/node/lead-attribution.test.cjs`
- Create: `tests/node/lead-form.test.cjs`
- Create: `tests/browser/form-reliability.spec.mjs`
- Create: `tests/browser/fixtures/form-page.html`

- [ ] **Step 1: Add the exact test commands**

Create `package.json`:

```json
{
  "name": "hybridautos-theme-reliability",
  "private": true,
  "scripts": {
    "test:unit": "node --test tests/node/*.test.cjs",
    "test:contract": "python3 -m unittest discover -s tests/python -p 'test_*.py' -v",
    "test:browser": "playwright test",
    "test": "npm run test:unit && npm run test:contract && npm run test:browser"
  },
  "devDependencies": {
    "@playwright/test": "1.55.0"
  }
}
```

Create `playwright.config.mjs`:

```js
import { defineConfig, devices } from '@playwright/test';

export default defineConfig({
  testDir: './tests/browser',
  fullyParallel: false,
  workers: 1,
  retries: 0,
  timeout: 20_000,
  use: {
    baseURL: 'https://hybridautos.test',
    trace: 'retain-on-failure'
  },
  projects: [
    { name: 'chromium-desktop', use: { ...devices['Desktop Chrome'] } },
    { name: 'chromium-mobile', use: { ...devices['iPhone 13'] } }
  ]
});
```

Install deterministically:

```bash
npm install
npx playwright install chromium
```

Expected output: dependency install exits `0`; Chromium install exits `0`; `package-lock.json` is created and committed.

- [ ] **Step 2: Create a PII-free fixture with both CTA types**

The fixture must contain:

- a modal `id="lead-form"`;
- one generic trigger with `data-modal-model=""` and key `fixture.generic`;
- one explicit trigger with `data-modal-model="Li L6"` and key `fixture.li-l6`;
- a form with `data-lead-form`, `data-form-id="fixture-form"`, and `data-brand="Li Auto"`;
- name, UAE phone, model select whose first option is `<option value="">Model not selected</option>`, honeypot `name="website"`, unchecked required `name="pd_consent"`, submit button, and `[data-submit-error]` alert;
- `/privacy-policy/` as the only consent link;
- no real person data.

- [ ] **Step 3: Write unit tests for the exact contracts and run them red**

`tests/node/lead-attribution.test.cjs` must assert:

1. first ad landing captures all five UTM fields and all six click IDs;
2. a later internal URL with no ad values does not overwrite them;
3. a later ad URL does not replace an already non-empty first ad set;
4. an initial direct visit can be upgraded by the first later non-empty ad set in the same tab;
5. `submit_url` is always the current submit page while `landing_url` remains first touch;
6. malformed percent-encoding does not throw;
7. existing same-name consent-managed cookies are fallback only and never overwrite stored values;
8. `_ym_uid` and `roistat_visit` are read synchronously when present;
9. missing cookies, `ym`, `roistat`, or throwing storage returns empty optional values without blocking;
10. no code path calls `document.cookie =` or `localStorage.setItem`.

`tests/node/lead-form.test.cjs` must assert:

1. UUID is RFC 4122-shaped and reused for retry/fallback;
2. UUID remains after `failed` and only clears after confirmed success;
3. only a JSON numeric positive integer `lead_id` with `ok === true` passes;
4. REST fallback runs once only for a route-level primary 404 and gets byte-identical body;
5. no fallback for validation 400, rate limit 429, server 500, malformed JSON, or network failure;
6. payload contains every browser-to-server contract key;
7. unchecked consent is rejected before fetch and `pd_consent=1` is sent only when checked;
8. `website` is sent as entered, so the server can detect bots;
9. `lead_success` contains only the six allowed keys plus callback/timeout;
10. two calls with the same `lead_id` cause one data-layer push because `lead_success:{lead_id}` exists in session storage;
11. analytics/storage exceptions still invoke the idempotent redirect fallback after confirmation;
12. error responses never call redirect.

Run:

```bash
npm run test:unit
```

Expected result before implementation: failures because `lead-attribution.js` does not exist and the old `lead-form.js` does not satisfy the exported contract. Do not weaken assertions to make the old code pass.

- [ ] **Step 4: Write integrated browser cases and run them red**

`tests/browser/form-reliability.spec.mjs` must route `https://hybridautos.test/**` locally, inject the fixture and real theme scripts, and cover:

1. HTTP 500: values, UUID, and modal survive close/reopen; error shown; button enabled; no navigation; no `lead_success`;
2. malformed 200 JSON: same error behavior;
3. network abort: same error behavior;
4. primary WordPress `rest_no_route` 404 then fallback success: same UUID/body; one event; one redirect;
5. success `{ok:true,lead_id:41}`: `lead_id` is string `"41"` in data layer, `eventTimeout` is `1200`, callback exists, and redirect occurs even if GTM never invokes it;
6. responses with IDs `"41"`, `0`, `-1`, and `1.5`: no conversion/redirect;
7. ad landing on `/li-auto/?utm_source=google&utm_medium=cpc&utm_campaign=dubai&gclid=GCLID-41`, internal navigation to `/zeekr/`, then submit: original ad values plus current Zeekr `submit_url` are posted;
8. generic CTA posts `model=""`; explicit model CTA posts `model="Li L6"`;
9. missing `window.ym`, `window.roistat`, cookies, and blocked session storage still permit a successful POST;
10. submitted name/phone never appear in `dataLayer`.

Run:

```bash
npm run test:browser
```

Expected result before implementation: failures for lifecycle, attribution, event, and model-selection cases.

- [ ] **Step 5: Commit the red contract suite**

```bash
git add package.json package-lock.json playwright.config.mjs tests
git commit -m "test(forms): define reliability and attribution contracts"
```

---

### Task 3: Implement consent-safe first-touch attribution

**Files:**
- Create: `08_КОД/wp-theme/assets/js/lead-attribution.js`
- Modify: `tests/node/lead-attribution.test.cjs`

- [ ] **Step 1: Implement the UMD module without persistent writes**

Use storage key `lp_first_touch_v1`. The stored JSON shape is exactly:

```js
{
  landing_url: 'https://hybridautos.ae/li-auto/?utm_source=google',
  landing_referrer: 'https://www.google.com/',
  utm_source: 'google',
  utm_medium: 'cpc',
  utm_campaign: 'dubai',
  utm_term: '',
  utm_content: '',
  gclid: 'GCLID-41',
  gbraid: '',
  wbraid: '',
  yclid: '',
  fbclid: '',
  msclkid: ''
}
```

Required behavior:

- Wrap every storage/cookie/runtime access in a small safe helper; an exception returns an empty value.
- Capture the initial landing URL/referrer. If it has no ad values, allow the first later URL with any `AD_KEYS` value to become the advertising first touch. Once any stored ad value is non-empty, never replace that set in the tab.
- Use `URL`/`URLSearchParams`, trim strings, normalize `null` to `""`, and safe-decode cookie values. Do not manually decode values already decoded by `URLSearchParams`.
- `buildAttribution()` returns all attribution keys every time, including empty strings, and always replaces `submit_url` with the current URL.
- Cookie fallback may read same-name UTM/click-ID cookies, `_ym_uid`, `ym_client_id`, and `roistat_visit`. It must not write a cookie or use `localStorage`.
- At page initialization, optionally call `ym(110335743, 'getClientID', callback)` and cache the callback value in memory. Do not initialize Metrika and do not await the callback at submit.
- At submit, optionally call synchronous `window.roistat.getVisit()` inside `try/catch`; fall back to the cookie. Do not await any integration.
- Expose the exact interface in the File Map and auto-call `captureFirstTouch(window.location.href, document.referrer, window.sessionStorage)` once when loaded.

- [ ] **Step 2: Run focused tests green**

```bash
node --test tests/node/lead-attribution.test.cjs
```

Expected output: all attribution tests pass, `fail 0`.

- [ ] **Step 3: Commit**

```bash
git add 08_КОД/wp-theme/assets/js/lead-attribution.js tests/node/lead-attribution.test.cjs
git commit -m "feat(forms): preserve first-touch attribution in the browser"
```

---

### Task 4: Replace false-success submission behavior with an idempotent lifecycle

**Files:**
- Modify: `08_КОД/wp-theme/assets/js/lead-form.js`
- Modify: `tests/node/lead-form.test.cjs`
- Modify: `tests/browser/form-reliability.spec.mjs`

- [ ] **Step 1: Preserve presentation helpers and replace the submit core**

Keep the existing UAE phone mask, thousands formatting, and custom-select accessibility. Replace the old submit core with these states on the form element:

```text
data-lead-state="idle"       no active failed request
data-lead-state="submitting" request in flight
data-lead-state="failed"     retry must keep values, CTA context, and UUID
data-lead-state="confirmed"  server returned a valid saved lead; UUID may clear
data-submission-id="UUID"    one ID for the complete lifecycle
```

Generate with `crypto.randomUUID()` where available and a cryptographically random RFC 4122 v4 fallback using `crypto.getRandomValues()`. Never use timestamp/`Math.random()` as the only entropy. Reuse the same ID for primary request, fallback, retry, and failed modal reopen.

- [ ] **Step 2: Build the exact payload without compressing attribution**

`buildRequestBody(form, attribution)` returns `URLSearchParams` containing every contract key. Rules:

- preserve existing `message` logic for message or budget/purpose;
- keep `name` optional and the UAE phone required; do not reintroduce a browser-only name requirement that can discard an otherwise valid phone lead;
- preserve `source_block` for backward compatibility as `submit_url + " -- " + cta_label`, but do not use it instead of separate fields;
- use `form.dataset.formId`, `form.dataset.brand`, and the active CTA values copied by `modal.js`;
- use the native `select[name="model"]` value after generic/model-specific synchronization;
- append `pd_consent=1` only when the required checkbox is checked;
- append `website` even when empty;
- append all attribution and CTA keys as strings, including empty optional values;
- never include reCAPTCHA fields.

Because the Home form uses `novalidate`, validate consent explicitly in JavaScript: when unchecked, set `aria-invalid="true"`, focus the checkbox, show no server error, and return before UUID creation/fetch. When checked, clear `aria-invalid`. Also fix the custom select to preserve the native option value exactly: an empty option displays `Model not selected` but keeps `select.value === ""`; never substitute the visible label as the submitted value.

- [ ] **Step 3: Implement the narrow REST fallback**

Primary endpoint:

```text
{window.lpLeadRuntime.restBase}/landing/v1/lead
```

Fallback endpoint:

```text
/?rest_route=/landing/v1/lead
```

Use the fallback at most once and only when the primary response is HTTP 404 and either:

- parsed WordPress JSON has `code === "rest_no_route"`; or
- the body is non-JSON/empty, indicating the pretty REST route itself was not routed.

Do not fall back when a JSON application error is returned. The identical serialized body, including `submission_id`, is reused.

- [ ] **Step 4: Enforce confirmed-success semantics**

After parsing JSON, accept success only when:

```js
data.ok === true && Number.isInteger(data.lead_id) && data.lead_id > 0
```

For all other outcomes:

- set `data-lead-state="failed"`;
- retain UUID and every field value;
- re-enable the button and restore its label;
- show `[data-submit-error]` with `role="alert"`;
- do not call `form.reset()`;
- do not navigate;
- do not push analytics.

Do not redirect in `catch`.

- [ ] **Step 5: Emit `lead_success` once and redirect independently**

On confirmed success, create an idempotent `redirectOnce()` and use this exact event contract:

```js
window.dataLayer = window.dataLayer || [];
window.dataLayer.push({
  event: 'lead_success',
  lead_id: String(data.lead_id),
  form_id: context.formId,
  brand: context.brand,
  model: context.model,
  cta_key: context.ctaKey,
  eventCallback: redirectOnce,
  eventTimeout: 1200
});
```

Before pushing, check session key `lead_success:{lead_id}`. Mark it before the push and maintain an in-memory set as a fallback when session storage is blocked. A repeated response for the same lead redirects but never pushes a second event. Independently call `setTimeout(redirectOnce, 1300)`. `redirectOnce()`:

1. does nothing on a second call;
2. clears the confirmed form's submission ID;
3. sets `data-lead-state="confirmed"`;
4. navigates to `/thank-you/`.

Wrap storage and `dataLayer.push` independently. An analytics error cannot convert a confirmed lead back into an error and cannot prevent the 1.3-second redirect.

- [ ] **Step 6: Run unit and integrated lifecycle tests green**

```bash
node --test tests/node/lead-form.test.cjs
npx playwright test tests/browser/form-reliability.spec.mjs --grep "HTTP|malformed|network|fallback|success"
```

Expected output: all selected tests pass on desktop and mobile, with no redirect/event in error cases and exactly one in success cases.

- [ ] **Step 7: Commit**

```bash
git add 08_КОД/wp-theme/assets/js/lead-form.js tests/node/lead-form.test.cjs tests/browser/form-reliability.spec.mjs
git commit -m "fix(forms): confirm saved lead before success and preserve retries"
```

---

### Task 5: Make modal state and CTA context stable across retries

**Files:**
- Modify: `08_КОД/wp-theme/assets/js/modal.js`
- Modify: `tests/browser/form-reliability.spec.mjs`

- [ ] **Step 1: Add failing modal lifecycle tests**

Add assertions that:

- the first open from a CTA resets stale idle values, copies CTA context, and sets the correct model;
- a failed submit followed by close/Escape/reopen preserves input values, model, context, and UUID;
- opening a different CTA while the same form is `failed` does not silently change the already attempted CTA/model;
- a generic first open sets the native/custom model select to the blank `Model not selected` option;
- an explicit Lynk & Co trigger sets `Lynk & Co 900` exactly.

Run:

```bash
npx playwright test tests/browser/form-reliability.spec.mjs --grep "modal|generic|explicit"
```

Expected result before implementation: failures caused by unconditional `form.reset()` and missing context fields.

- [ ] **Step 2: Implement stable context copying**

`contextFromTrigger(trigger)` returns:

```js
{
  model: trigger.getAttribute('data-modal-model') || '',
  ctaKey: trigger.getAttribute('data-cta-key') || '',
  ctaLabel: trigger.getAttribute('data-cta-label') || trigger.textContent.trim(),
  ctaPlacement: trigger.getAttribute('data-cta-placement') || ''
}
```

On a first/idle open only:

- reset form controls;
- clear prior error UI;
- copy context to `form.dataset.activeModel`, `activeCtaKey`, `activeCtaLabel`, and `activeCtaPlacement`;
- set select to the exact model, including the blank option for generic CTA;
- leave/generate UUID only when submit begins.

When state is `failed` or `submitting`, reopen without reset and without replacing active context. Closing never resets a form.

Update `setSelectModel()` so an explicitly empty model selects the option whose value is `""`; do not return early merely because `modelText` is empty. This is what makes generic CTA submissions verifiably model-free.

- [ ] **Step 3: Run focused browser tests green**

```bash
npx playwright test tests/browser/form-reliability.spec.mjs --grep "modal|generic|explicit"
```

Expected output: all selected tests pass in both projects.

- [ ] **Step 4: Commit**

```bash
git add 08_КОД/wp-theme/assets/js/modal.js tests/browser/form-reliability.spec.mjs
git commit -m "fix(forms): retain failed modal lifecycle and CTA context"
```

---

### Task 6: Add the authoritative 32-path CTA registry and honest consent markup

**Files:**
- Create: `08_КОД/wp-theme/lead-cta-registry.json`
- Create/Modify: `tests/python/test_theme_contract.py`
- Modify: `08_КОД/wp-theme/blocks/lazyblock-custom/block.php`
- Modify: `08_КОД/wp-theme/li-auto.html`
- Modify: `08_КОД/wp-theme/zeekr.html`
- Modify: `08_КОД/wp-theme/xiaomi.html`
- Modify: `08_КОД/wp-theme/lynk-co.html`
- Modify: `08_КОД/wp-theme/rox.html`
- Modify: `08_КОД/wp-theme/assets/css/main.css`

- [ ] **Step 1: Write the registry contract test first**

Using Python standard-library `html.parser`, make `tests/python/test_theme_contract.py` load the registry and assert:

- exactly 32 entries and unique `cta_key` values;
- every registry selector finds exactly one CTA in the stated page source;
- every CTA opening `lead-form` is in the registry and has all three stable attributes;
- registry `cta_label` equals the CTA's explicit `data-cta-label`;
- generic entries have `model=""` and explicit `data-modal-model=""`;
- model entries match an exact `<option value>` in their form;
- each form has the exact `form_id` and `brand` from its registry rows;
- every form contains one off-screen text honeypot named `website` and one unchecked required checkbox named `pd_consent` linked to `/privacy-policy/`;
- no checkbox has `checked` and no script fabricates consent;
- every brand model select starts with `<option value="">Model not selected</option>`;
- the Lynk page has a model select with blank plus `Lynk & Co 900`;
- attribution, modal, then form scripts are present in that order on every standalone brand page.

Run:

```bash
python3 -m unittest tests.python.test_theme_contract.ThemeMarkupContractTest -v
```

Expected result before markup changes: failures for missing registry, attributes, blank options, consent, honeypot, Lynk model, and attribution script.

- [ ] **Step 2: Create these exact registry rows**

Each JSON object has `page`, `source_file`, `selector`, `form_id`, `brand`, `model`, `cta_key`, `cta_label`, and `cta_placement`. Use the following inventory without adding inferred models:

| Page | Form ID | Brand | Model | CTA key | Label | Placement |
|---|---|---|---|---|---|---|
| `/` | `home-custom-order` | `HybridAutos` | empty | `home.custom-order.consultation` | `Get a car selection and consultation` | `custom-order` |
| `/li-auto/` | `li-auto-lead` | `Li Auto` | empty | `li-auto.hero.test-drive` | `Request a test drive` | `hero` |
| `/li-auto/` | `li-auto-lead` | `Li Auto` | `Li L6` | `li-auto.model.li-l6.offer` | `Get an offer` | `model-card` |
| `/li-auto/` | `li-auto-lead` | `Li Auto` | `Li L7` | `li-auto.model.li-l7.offer` | `Get an offer` | `model-card` |
| `/li-auto/` | `li-auto-lead` | `Li Auto` | `Li L8` | `li-auto.model.li-l8.offer` | `Get an offer` | `model-card` |
| `/li-auto/` | `li-auto-lead` | `Li Auto` | `Li L9` | `li-auto.model.li-l9.offer` | `Get an offer` | `model-card` |
| `/li-auto/` | `li-auto-lead` | `Li Auto` | `Li MEGA` | `li-auto.model.li-mega.offer` | `Get an offer` | `model-card` |
| `/li-auto/` | `li-auto-lead` | `Li Auto` | empty | `li-auto.test-drive.request` | `Request a test drive` | `test-drive-section` |
| `/zeekr/` | `zeekr-lead` | `Zeekr` | empty | `zeekr.hero.test-drive` | `Request a test drive` | `hero` |
| `/zeekr/` | `zeekr-lead` | `Zeekr` | `Zeekr 8X` | `zeekr.model.8x.offer` | `Get an offer` | `model-card` |
| `/zeekr/` | `zeekr-lead` | `Zeekr` | `Zeekr 9X` | `zeekr.model.9x.offer` | `Get an offer` | `model-card` |
| `/zeekr/` | `zeekr-lead` | `Zeekr` | `Zeekr 009` | `zeekr.model.009.offer` | `Get an offer` | `model-card` |
| `/zeekr/` | `zeekr-lead` | `Zeekr` | empty | `zeekr.test-drive.request` | `Request a test drive` | `test-drive-section` |
| `/zeekr/` | `zeekr-lead` | `Zeekr` | `Zeekr 8X` | `zeekr.model.8x.details-offer` | `Get an offer` | `model-details` |
| `/zeekr/` | `zeekr-lead` | `Zeekr` | `Zeekr 9X` | `zeekr.model.9x.details-offer` | `Get an offer` | `model-details` |
| `/zeekr/` | `zeekr-lead` | `Zeekr` | `Zeekr 009` | `zeekr.model.009.details-offer` | `Get an offer` | `model-details` |
| `/xiaomi/` | `xiaomi-lead` | `Xiaomi` | empty | `xiaomi.hero.test-drive` | `Request a test drive` | `hero` |
| `/xiaomi/` | `xiaomi-lead` | `Xiaomi` | `Xiaomi YU7` | `xiaomi.model.yu7.offer` | `Get an offer` | `model-card` |
| `/xiaomi/` | `xiaomi-lead` | `Xiaomi` | `Xiaomi SU7` | `xiaomi.model.su7.offer` | `Get an offer` | `model-card` |
| `/xiaomi/` | `xiaomi-lead` | `Xiaomi` | `Xiaomi YU7` | `xiaomi.model.yu7.details-offer` | `Get an offer` | `model-details` |
| `/xiaomi/` | `xiaomi-lead` | `Xiaomi` | `Xiaomi SU7` | `xiaomi.model.su7.details-offer` | `Get an offer` | `model-details` |
| `/xiaomi/` | `xiaomi-lead` | `Xiaomi` | empty | `xiaomi.test-drive.request` | `Request a test drive` | `test-drive-section` |
| `/lynk-co/` | `lynk-co-lead` | `Lynk & Co` | empty | `lynk-co.hero.test-drive` | `Request a test drive` | `hero` |
| `/lynk-co/` | `lynk-co-lead` | `Lynk & Co` | `Lynk & Co 900` | `lynk-co.model.900.offer` | `Get an offer` | `model-card` |
| `/lynk-co/` | `lynk-co-lead` | `Lynk & Co` | empty | `lynk-co.test-drive.request` | `Request a test drive` | `test-drive-section` |
| `/lynk-co/` | `lynk-co-lead` | `Lynk & Co` | `Lynk & Co 900` | `lynk-co.model.900.details-offer` | `Get an offer` | `model-details` |
| `/rox/` | `rox-lead` | `ROX` | empty | `rox.hero.test-drive` | `Request a test drive` | `hero` |
| `/rox/` | `rox-lead` | `ROX` | `ROX 01` | `rox.model.01.offer` | `Get an offer` | `model-card` |
| `/rox/` | `rox-lead` | `ROX` | `ROX ADAMAS` | `rox.model.adamas.offer` | `Get an offer` | `model-card` |
| `/rox/` | `rox-lead` | `ROX` | empty | `rox.test-drive.request` | `Request a test drive` | `test-drive-section` |
| `/rox/` | `rox-lead` | `ROX` | `ROX 01` | `rox.model.01.details-offer` | `Get an offer` | `model-details` |
| `/rox/` | `rox-lead` | `ROX` | `ROX ADAMAS` | `rox.model.adamas.details-offer` | `Get an offer` | `model-details` |

The JSON `selector` is always `[data-cta-key="the exact key from the row"]`; `source_file` is `blocks/lazyblock-custom/block.php` for Home and the page HTML filename for brand pages.

- [ ] **Step 3: Apply stable form/CTA attributes and model rules**

Every trigger gets:

```html
data-open-modal="lead-form"
data-modal-model=""
data-cta-key="li-auto.hero.test-drive"
data-cta-label="Request a test drive"
data-cta-placement="hero"
```

Use the registry's exact values per row. Model-specific triggers use their exact non-empty model. Each form gets `data-form-id` and `data-brand` from the table. Insert a blank first option in all brand selects. Add the missing Lynk select with blank and `Lynk & Co 900`.

- [ ] **Step 4: Add honest consent, honeypot, and error UI to all six forms**

Use the same markup in every form, with unique input IDs per page:

```html
<div class="lf-honeypot" aria-hidden="true">
  <label>Leave this field empty
    <input type="text" name="website" value="" tabindex="-1" autocomplete="off">
  </label>
</div>
<label class="lf-consent">
  <input type="checkbox" name="pd_consent" value="1" required>
  <span>I agree to the processing of my personal data according to the <a href="/privacy-policy/" target="_blank" rel="noopener">Privacy Policy</a>.</span>
</label>
<p class="lf-submit-error" data-submit-error role="alert" hidden>
  We could not send your request. Your details remain in the form. Please try again or contact us by WhatsApp.
</p>
```

Add CSS that moves `.lf-honeypot` off-screen with absolute positioning, a 1px box, and overflow hidden; do not use `type="hidden"` or remove it from the form. Add visible focus/error/consent styling. Do not pre-check consent in HTML or JavaScript.

- [ ] **Step 5: Resolve the privacy-page release gate**

The technical work may merge with the URL in place, but production traffic may not start until the owner/legal reviewer supplies and approves the real policy content and WordPress publishes `/privacy-policy/`. Verify:

```bash
curl -sS -o /dev/null -w '%{http_code}\n' https://hybridautos.ae/privacy-policy/
```

Expected release output: `200`. The observed pre-implementation output was `404`.

- [ ] **Step 6: Run the complete markup contract green**

```bash
python3 -m unittest tests.python.test_theme_contract.ThemeMarkupContractTest -v
```

Expected output: all contract tests `OK`, registry count `32`, no unregistered form-opening CTA.

- [ ] **Step 7: Commit**

```bash
git add 08_КОД/wp-theme/lead-cta-registry.json 08_КОД/wp-theme/blocks/lazyblock-custom/block.php 08_КОД/wp-theme/li-auto.html 08_КОД/wp-theme/zeekr.html 08_КОД/wp-theme/xiaomi.html 08_КОД/wp-theme/lynk-co.html 08_КОД/wp-theme/rox.html 08_КОД/wp-theme/assets/css/main.css tests/python/test_theme_contract.py
git commit -m "feat(forms): register every CTA and require explicit consent"
```

---

### Task 7: Remove active reCAPTCHA and version every form script on every page

**Files:**
- Modify: `08_КОД/wp-theme/functions.php`
- Modify: `08_КОД/wp-theme/li-auto.html`
- Modify: `08_КОД/wp-theme/zeekr.html`
- Modify: `08_КОД/wp-theme/xiaomi.html`
- Modify: `08_КОД/wp-theme/lynk-co.html`
- Modify: `08_КОД/wp-theme/rox.html`
- Modify: `tests/python/test_theme_contract.py`

- [ ] **Step 1: Add failing script/dead-code tests**

Assert:

- no active theme file contains `grecaptcha`, `lpRecaptchaSiteKey`, `recaptcha_token`, or `google.com/recaptcha`;
- Home enqueues `lead-attribution.js` before `modal.js`, then `lead-form.js`;
- every standalone brand page contains those scripts in that order;
- runtime config exposes only `restBase` and `ymCounterId` needed here;
- standalone renderer appends a filemtime `ver` query to the three local scripts;
- the thank-you page contains no success/conversion emitter.

Run:

```bash
python3 -m unittest tests.python.test_theme_contract.ThemeScriptContractTest -v
```

Expected result before implementation: failures for active reCAPTCHA and missing attribution/cache-bust behavior.

- [ ] **Step 2: Change WordPress enqueue dependencies**

In `lp_enqueue_assets()` enqueue:

```php
wp_enqueue_script('lp-lead-attribution', $uri . '/assets/js/lead-attribution.js', [], $v('/assets/js/lead-attribution.js'), true);
wp_enqueue_script('lp-modal', $uri . '/assets/js/modal.js', ['lp-lead-attribution'], $v('/assets/js/modal.js'), true);
wp_enqueue_script('lp-lead-form', $uri . '/assets/js/lead-form.js', ['lp-lead-attribution', 'lp-modal'], $v('/assets/js/lead-form.js'), true);
```

Inject runtime data before `lp-lead-attribution`:

```php
$runtime = [
    'restBase'    => rtrim(rest_url(), '/'),
    'ymCounterId' => 110335743,
];
wp_add_inline_script('lp-lead-attribution', 'window.lpLeadRuntime=' . wp_json_encode($runtime) . ';', 'before');
```

Remove the theme's reCAPTCHA option reads, external script enqueue, and site-key injection.

- [ ] **Step 3: Version standalone assets and inject the same runtime**

In `lp_render_subpage()`:

- inject `window.lpLeadRuntime={restBase:...,ymCounterId:110335743}`;
- remove all reCAPTCHA injection;
- before the subdirectory path rewrite, use `preg_replace_callback` on local `assets/js/*.js` and `assets/css/*.css` `src`/`href` values, resolve each path under the theme directory, and append `?ver=` plus its `filemtime` (or `&ver=` when a query already exists);
- never version external URLs;
- keep landing-config snippet injection intact because GTM/Roistat still use it.

Add `<script src=".../assets/js/lead-attribution.js"></script>` immediately before `modal.js` on all five brand HTML pages.

- [ ] **Step 4: Prove reCAPTCHA is inactive and scripts are ordered/versioned**

```bash
rg -n "grecaptcha|lpRecaptchaSiteKey|recaptcha_token|google\.com/recaptcha" 08_КОД/wp-theme
python3 -m unittest tests.python.test_theme_contract.ThemeScriptContractTest -v
php -l 08_КОД/wp-theme/functions.php
```

Expected output: `rg` has no matches and exits `1`; tests are `OK`; PHP reports `No syntax errors detected`.

- [ ] **Step 5: Commit**

```bash
git add 08_КОД/wp-theme/functions.php 08_КОД/wp-theme/li-auto.html 08_КОД/wp-theme/zeekr.html 08_КОД/wp-theme/xiaomi.html 08_КОД/wp-theme/lynk-co.html 08_КОД/wp-theme/rox.html tests/python/test_theme_contract.py
git commit -m "fix(theme): remove active recaptcha and version form assets"
```

---

### Task 8: Run all local quality gates and inspect every page/CTA in a real browser

**Files:**
- Modify: `tests/browser/form-reliability.spec.mjs`
- Modify: `tests/python/test_theme_contract.py`

- [ ] **Step 1: Add page-wide browser registry coverage**

For every row in `lead-cta-registry.json`, the browser test must:

1. render the row's source page or a faithful extracted form/CTA fixture;
2. click the unique selector;
3. assert modal open, exact active CTA key/placement/label, form ID, brand, and model;
4. submit against a mocked confirmed response;
5. inspect the POST for exact context and a valid UUID;
6. assert one PII-free `lead_success` event and one redirect.

Add one error-response iteration for each of the six pages and assert form values/UUID remain and no event/redirect occurs.

- [ ] **Step 2: Run complete automated quality control**

```bash
npm test
php -l 08_КОД/wp-theme/functions.php
git diff --check
```

Expected output:

```text
Node unit tests: fail 0
Python contract tests: OK
Playwright: all tests passed in chromium-desktop and chromium-mobile
No syntax errors detected in 08_КОД/wp-theme/functions.php
git diff --check: no output
```

- [ ] **Step 3: Manually inspect desktop and mobile**

Open Home and all five brand pages from a local/staging WordPress copy. For every registry path verify:

- modal layout and close/reopen behavior;
- blank model for generic CTA and exact model for specific CTA;
- checkbox keyboard focus and required validation;
- privacy link target;
- honeypot invisible to a normal visitor but present in submitted form data;
- no horizontal overflow or submit button overlap at 390px width;
- error message is readable and fields are retained.

Expected result: 32/32 CTA rows pass on desktop; 32/32 pass on mobile; 6/6 error paths retain the contact in the form.

- [ ] **Step 4: Commit final test refinements**

```bash
git add tests
git commit -m "test(forms): cover every page and CTA path"
```

---

### Task 9: Generate the release manifest and verify both GitHub commits

**Files:**
- Create: `scripts/write-release-manifest.py`
- Generate: `09_ДЕПЛОЙ/releases/2026-07-15-lead-reliability-theme.json`

- [ ] **Step 1: Test manifest generation before implementation**

The test creates two temporary Git repos and asserts the script:

- refuses a dirty theme or companion repo;
- reads real `HEAD` SHAs rather than accepting text arguments;
- writes database version exactly `1.1.0`;
- includes all regular files under `08_КОД/wp-theme` with relative path, byte size, and SHA-256;
- records `GTM-WZXC5HVS`, Metrika counter `110335743`, goal ID `lead_success`, and the 32-row registry hash;
- contains no credential values or customer data;
- writes deterministic sorted JSON.

Run:

```bash
python3 -m unittest tests.python.test_write_release_manifest -v
```

Expected result before script implementation: import/file-not-found failure.

- [ ] **Step 2: Implement the exact command interface**

The script accepts:

```bash
python3 scripts/write-release-manifest.py \
  --landing-system-repo "/Users/kirillbezikov/Documents/Сайт Дубай /landing_system/.worktrees/lead-reliability-2026-07-15" \
  --output 09_ДЕПЛОЙ/releases/2026-07-15-lead-reliability-theme.json
```

It derives the theme repo from its own location, refuses either dirty working tree, and writes real runtime values only. Enforce this exact field contract:

| JSON field | Exact source/validation |
|---|---|
| `release` | Literal `2026-07-15-lead-reliability` |
| `production_site` | Literal `https://hybridautos.ae` |
| `database_migration_version` | Literal `1.1.0` |
| `theme_code_commit` | Output of `git -C theme-repo rev-parse HEAD`; regex `^[0-9a-f]{40}$` |
| `landing_system_commit` | Output of `git -C companion-worktree rev-parse HEAD`; regex `^[0-9a-f]{40}$` |
| `analytics.gtm_container` | Literal `GTM-WZXC5HVS` |
| `analytics.yandex_counter` | Integer `110335743` |
| `analytics.yandex_goal` | Literal `lead_success` |
| `cta_registry_sha256` | Calculated SHA-256 of `08_КОД/wp-theme/lead-cta-registry.json` |
| `theme_files` | Sorted objects with actual `path`, positive/non-negative `bytes`, and calculated 64-character lowercase `sha256` for every regular theme file |

The generator rejects missing files, dirty repositories, non-Git inputs, duplicate paths, invalid hashes, and any value copied from documentation instead of calculated from the checked-out code.

- [ ] **Step 3: Commit code, generate from clean code commits, then commit the manifest**

```bash
git add scripts/write-release-manifest.py tests/python/test_write_release_manifest.py
git commit -m "build(release): generate deterministic theme manifest"
python3 scripts/write-release-manifest.py --landing-system-repo "/Users/kirillbezikov/Documents/Сайт Дубай /landing_system/.worktrees/lead-reliability-2026-07-15" --output 09_ДЕПЛОЙ/releases/2026-07-15-lead-reliability-theme.json
python3 -m json.tool 09_ДЕПЛОЙ/releases/2026-07-15-lead-reliability-theme.json >/dev/null
git add 09_ДЕПЛОЙ/releases/2026-07-15-lead-reliability-theme.json
git commit -m "chore(release): record lead reliability theme manifest"
npm test
```

Expected output: manifest JSON validates and all tests pass.

- [ ] **Step 4: Push and compare exact remote SHAs**

```bash
git push -u origin fix/lead-reliability-observability
test "$(git rev-parse HEAD)" = "$(git ls-remote origin refs/heads/fix/lead-reliability-observability | cut -f1)"
git -C "/Users/kirillbezikov/Documents/Сайт Дубай /landing_system/.worktrees/lead-reliability-2026-07-15" rev-parse HEAD
git -C "/Users/kirillbezikov/Documents/Сайт Дубай /landing_system/.worktrees/lead-reliability-2026-07-15" ls-remote origin refs/heads/fix/lead-reliability-observability
```

Expected result: local and remote theme SHAs are identical; the companion plan must likewise show identical local/remote SHAs before production. Business meaning: the release can be reconstructed and audited.

---

### Task 10: Deploy compatibly, purge caches, and prove public browser code on all six pages

**Files:**
- Create: `scripts/verify-public-theme.py`
- Read: `09_ДЕПЛОЙ/releases/2026-07-15-lead-reliability-theme.json`
- Deploy only manifest-listed theme targets changed by this branch.

- [ ] **Step 1: Enforce the backend-first release gate**

Before any theme upload, obtain evidence from the companion plan that:

- the fresh full files/database backup and staging restore rehearsal passed;
- additive DB migration `1.1.0` passed on a copy of the real DB;
- the backward-compatible endpoint is live;
- an old-format POST without `submission_id` returns `{ok:true,lead_id:positive integer}` and creates a recoverable lead/audit row;
- no new PHP errors appeared.

If any item is absent, stop. Browser code must not arrive before the compatible endpoint.

- [ ] **Step 2: Stage only this exact production allow-list**

```text
wp-content/themes/lp-hibridcars-uae/functions.php
wp-content/themes/lp-hibridcars-uae/assets/js/lead-attribution.js
wp-content/themes/lp-hibridcars-uae/assets/js/lead-form.js
wp-content/themes/lp-hibridcars-uae/assets/js/modal.js
wp-content/themes/lp-hibridcars-uae/assets/css/main.css
wp-content/themes/lp-hibridcars-uae/blocks/lazyblock-custom/block.php
wp-content/themes/lp-hibridcars-uae/li-auto.html
wp-content/themes/lp-hibridcars-uae/zeekr.html
wp-content/themes/lp-hibridcars-uae/xiaomi.html
wp-content/themes/lp-hibridcars-uae/lynk-co.html
wp-content/themes/lp-hibridcars-uae/rox.html
wp-content/themes/lp-hibridcars-uae/lead-cta-registry.json
```

Upload each file to a sibling temporary name containing `2026-07-15-lead-reliability`, download it back, compare SHA-256 to the release manifest, then atomically rename only that file into place while retaining its prior version in the release rollback directory. Do not delete the theme directory and do not upload tests, `node_modules`, Git metadata, or database files.

- [ ] **Step 3: Purge every relevant cache**

After activation:

- clear WordPress/page cache;
- clear any Beget/CDN cache configured for `hybridautos.ae`;
- reset PHP OPcache for the site if the hosting panel exposes it;
- load each page anonymously with `Cache-Control: no-cache`;
- confirm script URLs have non-empty `ver` query strings matching the deployed file mtimes.

- [ ] **Step 4: Implement and run anonymous public-hash verification**

`scripts/verify-public-theme.py` must:

1. load the release manifest;
2. request the six exact page URLs with a neutral desktop user agent and `Cache-Control: no-cache`;
3. parse the rendered HTML for `lead-attribution.js`, `modal.js`, and `lead-form.js` URLs;
4. require a `ver` parameter on all 18 references;
5. fetch each script without cookies/authentication;
6. compare its SHA-256 to the corresponding manifest hash;
7. verify page HTTP 200 and report one line per page/script;
8. fail on a missing, duplicate, stale, or unversioned script.

Run:

```bash
python3 scripts/verify-public-theme.py --manifest 09_ДЕПЛОЙ/releases/2026-07-15-lead-reliability-theme.json --site https://hybridautos.ae
```

Expected output: 6 pages `HTTP 200`, 18 script checks `SHA256 OK`, summary `pages=6 scripts=18 failures=0`.

- [ ] **Step 5: Run real ad-like submissions for the entire registry**

Use a new incognito tab and these safe synthetic parameters on every page:

```text
utm_source=google&utm_medium=cpc&utm_campaign=lead_reliability_20260715&utm_content=qa&gclid=QA-GCLID-20260715
```

For each of the 32 registry rows:

- open/click that CTA;
- verify generic/model context before submit;
- use an explicitly marked test phone/contact approved for QA;
- check the browser POST and response;
- record `submission_id`, returned `lead_id`, page, CTA key, and timestamp in the private release evidence location, never in Git if it contains contact data;
- verify exactly one lead/audit row in WordPress and the same attribution/context fields;
- verify the downstream delivery statuses through the companion server plan.

Also force one 500/network failure per page in browser developer tools: no redirect/event, values retained, retry with the same UUID succeeds.

Expected result: 32/32 registry submissions saved and traceable; 6/6 forced failures retain/retry; no duplicate lead for a repeated UUID.

---

### Task 11: Make GTM the single conversion source and validate Yandex/Google Ads exactly once

**External systems:**
- GTM container: `GTM-WZXC5HVS`
- Yandex Metrika counter: `110335743`
- Yandex JavaScript-event goal ID: `lead_success`
- Google Ads: existing HybridAutos conversion action/tag in `GTM-WZXC5HVS`

- [ ] **Step 1: Capture the current published analytics state before editing**

In authenticated GTM Preview and the relevant Ads/Metrika accounts, record privately:

- current GTM published version number;
- existing Google Ads Conversion ID and Conversion Label;
- existing Google conversion counting setting;
- current URL-contains-`thank-you` trigger/tag associations;
- every Yandex Metrika initialization source;
- current Yandex goals related to form/DOM detection.

Do not change the existing Google Conversion ID or Label. The known public container is `GTM-WZXC5HVS`; the known public counter is `110335743`.

- [ ] **Step 2: Remove the duplicate direct Metrika initialization**

The live page currently contains a direct `ym(110335743, 'init', ...)` snippet while Metrika is also loaded through GTM. Disable/delete the direct WordPress landing-config snippet, leaving GTM as the only initializer. Do not remove GTM or Roistat snippets.

Public-source check after publication:

```bash
curl -fsSL https://hybridautos.ae/ | rg -c "ym\(110335743, ['\"]init['\"]"
```

Expected output: `0` from static HTML. In an anonymous browser, exactly one Metrika tag resource initializes through GTM.

- [ ] **Step 3: Create exact GTM variables and one trigger**

Create Data Layer Variables, version 2:

```text
DLV - lead_id    -> lead_id
DLV - form_id    -> form_id
DLV - brand      -> brand
DLV - model      -> model
DLV - cta_key    -> cta_key
```

Create Custom Event trigger:

```text
Name: CE - lead_success
Event name: lead_success
This trigger fires on: All Custom Events
```

No URL, page-view, form-element, DOM-XPath, or thank-you trigger may fire a conversion.

- [ ] **Step 4: Rewire the existing Google Ads conversion tag**

Keep its existing Conversion ID and Conversion Label. Set:

```text
Transaction ID: {{DLV - lead_id}}
Trigger: CE - lead_success
```

Remove every `thank-you` URL trigger from that conversion tag. In Google Ads, set the conversion action's count to `One`. This gives one advertising conversion per saved lead even if the browser retries or reloads.

- [ ] **Step 5: Create/use the exact Yandex goal and GTM call**

In counter `110335743`, create or verify a JavaScript-event goal whose identifier is exactly `lead_success`. Replace DOM/form-element/XPath goals as the release proof; they may remain only as non-primary diagnostic goals if clearly excluded from advertising optimization.

Create a GTM Custom HTML tag `Yandex - lead_success` with:

```html
<script>
(function () {
  var leadId = {{DLV - lead_id}};
  if (!leadId || typeof window.ym !== 'function') return;
  window.ym(110335743, 'reachGoal', 'lead_success', { lead_id: String(leadId) });
})();
</script>
```

Trigger only on `CE - lead_success`. The `lead_id` parameter contains no personal data.

- [ ] **Step 6: Validate Preview mode before publishing**

Run these cases in GTM Preview/Tag Assistant:

| Case | `lead_success` event | Google Ads tag | Yandex goal tag | Redirect |
|---|---:|---:|---:|---:|
| Confirmed `{ok:true,lead_id:123}` | 1 | 1 | 1 | 1 |
| Same response/event attempted again | 0 additional | 0 additional | 0 additional | no additional conversion |
| HTTP 400/429/500 | 0 | 0 | 0 | 0 |
| Network failure | 0 | 0 | 0 | 0 |
| Direct `/thank-you/` visit | 0 | 0 | 0 | page displays only |
| Reload `/thank-you/` | 0 | 0 | 0 | page displays only |

Inspect the successful event and confirm:

- Google Transaction ID equals returned `lead_id`;
- Yandex `reachGoal` receives the same `lead_id` parameter;
- phone/name/URL/UTM/click IDs are absent;
- only one Metrika initialization occurs;
- the browser still redirects after about 1.3 seconds when GTM is blocked.

- [ ] **Step 7: Publish and record the actual version**

Publish the tested GTM workspace. Record the actual new numeric GTM version, publisher, timestamp, unchanged Google Conversion ID/Label, Google Count=`One`, Yandex counter `110335743`, goal `lead_success`, and Tag Assistant evidence in the private release record. Do not write `pending`, example values, or contact data into the Git manifest.

- [ ] **Step 8: Run post-publication cabinet validation**

Use one confirmed QA lead and verify:

- Tag Assistant: both tags fired exactly once on `lead_success`;
- Google Ads diagnostics receives the tag with Transaction ID equal to `lead_id`;
- Yandex Debug/goal report receives JavaScript goal `lead_success` for counter `110335743` with the same ID parameter;
- a direct and reloaded thank-you page records neither conversion;
- an error submission records neither conversion;
- source/network inspection shows a single Metrika init.

Expected result: **advertising analytics ready**. If authenticated cabinet access or any proof is missing, report this gate as not ready and keep paid traffic off even when contacts are already preserved.

---

### Task 12: Rehearse rollback and sign off the two release gates

**Files:**
- Read: `09_ДЕПЛОЙ/releases/2026-07-15-lead-reliability-theme.json`
- Read: private deployment evidence (must remain outside Git when it contains contacts)

- [ ] **Step 1: Rehearse theme rollback on staging**

From the retained pre-change production theme release:

1. stop test traffic and disable the new analytics tags/workspace publication if rollback includes analytics;
2. restore only the 12 allow-listed theme files from the immutable pre-change archive/branch;
3. clear WordPress/page/CDN cache and PHP OPcache;
4. run the public hash checker against the rollback manifest;
5. run one old-format control submission against the still-compatible backend;
6. leave additive DB columns intact;
7. reapply the tested release and repeat the public hash/form checks.

Expected result: rollback and reapply both complete without deleting unrelated theme/site files or losing new lead rows.

- [ ] **Step 2: Sign off contact preservation**

Mark **contact preservation ready** only when all are true:

- clean private Git history/current tree and verified remote backup/feature SHAs;
- full current theme and deterministic release manifest present;
- companion backend/queue/audit plan passed;
- 32/32 CTA paths save and are recoverable;
- 6/6 forced browser errors retain values and UUID for retry;
- public anonymous hashes match on all six pages;
- privacy policy is approved and HTTP 200;
- no active reCAPTCHA execution and no new PHP/JS errors;
- rollback rehearsal passed.

- [ ] **Step 3: Sign off advertising analytics**

Mark **advertising analytics ready** only when all are true:

- GTM `GTM-WZXC5HVS` published version recorded;
- direct duplicate Metrika init removed;
- Google and Yandex fire exactly once from `lead_success` only;
- Google Transaction ID equals `lead_id` and Count is `One`;
- Yandex counter `110335743` goal ID is exactly `lead_success` and receives `lead_id`;
- direct/reloaded thank-you and failed submissions create no conversion;
- cabinet evidence is complete.

- [ ] **Step 4: Make the business decision**

Paid traffic may restart only when both gates are ready. If contact preservation passes but analytics does not, contacts are safer but advertising remains paused. If analytics passes but contact preservation does not, apparent conversion counts cannot be trusted and advertising remains paused.

---

## Final Verification Commands

Run from `/Users/kirillbezikov/Documents/Сайт Дубай /hybridautos-ae`:

```bash
npm test
php -l 08_КОД/wp-theme/functions.php
rg -n "grecaptcha|lpRecaptchaSiteKey|recaptcha_token|google\.com/recaptcha" 08_КОД/wp-theme
python3 scripts/verify-public-theme.py --manifest 09_ДЕПЛОЙ/releases/2026-07-15-lead-reliability-theme.json --site https://hybridautos.ae
curl -sS -o /dev/null -w '%{http_code}\n' https://hybridautos.ae/privacy-policy/
git diff --check
git status --short
test "$(git rev-parse HEAD)" = "$(git ls-remote origin refs/heads/fix/lead-reliability-observability | cut -f1)"
```

Expected final evidence:

```text
All Node/Python/Playwright checks pass.
functions.php has no syntax errors.
Active-theme reCAPTCHA search returns no matches.
Public verification reports pages=6 scripts=18 failures=0.
Privacy policy returns 200.
git diff --check and git status --short produce no output.
Local and remote feature-branch SHAs match.
Contact preservation ready: YES.
Advertising analytics ready: YES.
Paid traffic restart: ALLOWED only after both YES results are recorded.
```

## Completion Review

- [ ] Compare every implementation and release result against `/Users/kirillbezikov/Documents/Сайт Дубай /landing_system/.worktrees/lead-reliability-2026-07-15/docs/superpowers/specs/2026-07-15-hybridautos-lead-reliability-design.md`.
- [ ] Confirm no unfinished marker, fake SHA, sample credential, unapproved legal copy, or unregistered CTA remains.
- [ ] Confirm all path names, form IDs, CTA keys, request fields, data-layer variables, Yandex counter/goal, and GTM container are internally consistent.
- [ ] Confirm the final handoff distinguishes saved contact, accepted Email, successful Telegram/Roistat delivery, and advertising conversion; a thank-you page alone proves none of those.
