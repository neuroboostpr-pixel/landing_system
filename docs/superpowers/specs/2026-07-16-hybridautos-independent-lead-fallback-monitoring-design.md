# HybridAutos Independent Lead Fallback and Telegram Monitoring Design

**Date:** 2026-07-16  
**Status:** Approved architecture — amended after security review; binding for implementation
**Production site:** `https://hybridautos.ae`  
**Primary hosting:** Beget  
**Independent fallback:** Vercel + Upstash Redis + Upstash QStash
**Operations channel:** existing HybridCars Telegram chat

## 1. Goal

Prevent a browser, WordPress, database, hosting, or integration failure from silently losing a consented HybridAutos advertising contact while avoiding duplicate Telegram leads when WordPress saved the lead but its response was lost.

The finished system must:

1. Keep WordPress as the primary receiver.
2. Store a consented fallback contact encrypted outside Beget when WordPress cannot confirm success.
3. Reconcile with WordPress before notifying Telegram.
4. Send one Telegram fallback lead only when WordPress explicitly lacks it or remains unreachable after two delayed checks.
5. Detect WordPress missing leads, integration failures, and a complete Beget outage.
6. Keep monitoring failure outside the normal lead-success decision.
7. Keep all Telegram, Redis, QStash, HMAC, encryption, database, and Roistat secrets out of browser code and logs.
8. Avoid storing draft contacts before the visitor consents and submits.
9. Retain enough pseudonymous state without direct contact fields to prevent duplicates for 30 days while retaining encrypted contact for no more than 7 days.

## 2. Non-goals

- Do not send every lead to WordPress and Vercel in parallel.
- Do not send Telegram immediately from the public fallback handler.
- Do not create a public “controlled failure” route.
- Do not alert on `form_started`, ordinary abandonment, honeypot traffic, or a visitor correcting validation.
- Do not store contact values in anonymous form events, technical alerts, QStash messages, application logs, analytics, or receipt-status responses.
- Do not call Telegram or Roistat from the browser.
- Do not require reCAPTCHA, Turnstile, or another third-party challenge.
- Do not treat Telegram response as a prerequisite for the normal WordPress success response.
- Do not retry an ambiguous Telegram call.
- Do not expose Redis-backed deep health through the public health endpoint.

## 2.1 Commercial account and cost constraint

- Vercel Hobby is forbidden for this commercial lead receiver. Production requires a verified existing Vercel Pro/Enterprise plan, effective DPA coverage, and the account/project customer-data/model-training setting reviewed and disabled where applicable. If only Hobby is available or any item is ambiguous, stop with `COMMERCIAL_PLAN_GATE_BLOCKED`; never activate intake or send a contact there.
- Pin Vercel CLI to `54.2.0` for all documented commands; do not use `latest`.
- Provision only Marketplace products `upstash/upstash-kv` and `upstash/upstash-qstash` with plan `free`.
- QStash must report `prodPack=false`.
- Redis must report `autoUpgrade=false`.
- The commercially eligible project must have one included WAF rate-limit rule available for the fallback endpoint.
- If authentication, commercial plan/DPA/data-use setting, exact product slug, exact `free` Marketplace plan, `prodPack=false`, `autoUpgrade=false`, or the included WAF rule cannot be proven before provisioning, stop with `COMMERCIAL_PLAN_GATE_BLOCKED`. Do not incur a new charge without explicit user authorization and do not silently omit WAF.

## 3. Chosen architecture

The system uses a primary-first, passive-independent fallback with delayed reconciliation.

~~~text
Visitor consents and submits
        |
        v
WordPress primary endpoint
   | confirmed                         | eligible unconfirmed failure
   v                                   v
Lead + audit saved              Vercel public fallback endpoint
   |                                   |
Thank You                       atomic encrypted receipt + token-use binding
                                       |
                                QStash delivery job after 45 seconds
                                       |
                          signed WordPress submission-status check
                         /                                  \
                  exists=true                         exists=false
                  delete payload                      Telegram fallback lead
                  no Telegram
                         \
                     ambiguous
                         |
                  one check-2 job after 30 seconds
                         |
                  exists=true -> delete/no Telegram
                  otherwise -> Telegram fallback lead
~~~

Monitoring remains separate:

~~~text
WordPress form events + delivery logs
        |
privacy-safe alert queue
        |
worker -> Telegram technical alert

QStash every 5 minutes
        |
Vercel signed deep Beget/Redis/heartbeat check
        |
outage/recovery state in Upstash -> Telegram
~~~

This architecture avoids:

- duplicate fallback messages caused by WordPress saving a lead but losing its HTTP response;
- WordPress-only monitoring becoming blind during a Beget outage;
- making Vercel the primary gateway;
- sending contact in QStash bodies.

## 4. Shared submission identity and stable duplicate control

Every attempt uses an existing UUID v4 `submission_id`.

### 4.1 Browser rules

- A validated submission creates one immutable in-memory snapshot containing contact, consent, context, bounded attribution, and one `submission_id`.
- Retrying without editing contact fields reuses the snapshot and ID.
- Editing name, phone, email, or message after failure creates a new ID.
- Contact is never written to `localStorage`, `sessionStorage`, IndexedDB, cookies, analytics, console, or anonymous telemetry.
- The browser obtains an intake token only from the same-origin WordPress no-store endpoint `GET /wp-json/landing/v1/fallback-token`. The token is not embedded in cached HTML or JavaScript.

### 4.2 WordPress idempotency

- WordPress treats a valid `submission_id` as its idempotency key.
- A named database lock serializes concurrent requests for the same ID.
- If a lead already has that ID, WordPress returns the original positive `lead_id` without inserting or redispatching integrations.
- A request without a valid ID remains backward compatible.

### 4.3 Vercel fingerprint

- `LP_PAYLOAD_HASH_SECRET` is a dedicated 64-character lowercase hexadecimal literal representing 32 random bytes.
- It must differ from `LP_FALLBACK_SIGNING_SECRET`, `LP_FALLBACK_STATUS_SECRET`, and `LP_RATE_LIMIT_SECRET`.
- Decode it from hex and compute lowercase hexadecimal HMAC-SHA256 over canonical normalized fallback fields.
- The canonical fingerprint excludes `intake_token` and `fallback_reason`.
- Excluding `fallback_reason` makes a replay stable when the same immutable contact snapshot reaches a different eligible failure classification.
- The first request’s `fallback_reason` is frozen in the receipt and is never overwritten by a replay.
- The 64-character lowercase fingerprint is pseudonymous, never public, and retained with the receipt for 30 days.
- Same `submission_id` and fingerprint returns the original receipt.
- The receipt also freezes non-contact `intake_mode=live|test`. Same UUID/fingerprint with a different signed mode returns HTTP 409 `mode_conflict`; it never reuses a test receipt as live success.
- Same `submission_id` with a different fingerprint returns HTTP 409 `idempotency_conflict` without overwrite.

### 4.4 Receipt identity

- Receipt ID format is exactly `rct_` plus 32 lowercase hexadecimal characters.
- Validation regex is `/^rct_[0-9a-f]{32}$/`.
- Receipt IDs are non-contact operational identifiers but remain absent from technical Telegram outage alerts.

## 5. WordPress no-store intake token

### 5.1 Endpoint

`GET /wp-json/landing/v1/fallback-token`:

- same-origin only;
- browser request is exactly `GET` with `Accept: application/json`, `credentials: same-origin`, no body, and no query-string test flag;
- `Cache-Control: no-store, private, max-age=0`;
- `Pragma: no-cache` and `Expires: 0`;
- no CDN, browser, page, or service-worker caching;
- no contact in request or response;
- response contains exact protocol/policy versions and one random nonce.

Mode selection is server-controlled:

- first, return `mode=test` only when `LP_FALLBACK_TEST_MODE=true`, the caller has a logged-in session and `manage_options`, and header `X-WP-Nonce: <wp_create_nonce('wp_rest')>` passes `wp_verify_nonce(..., 'wp_rest')`;
- otherwise, return `mode=live` only when `LP_FALLBACK_ENABLED=true`, regardless of whether the separate admin test flag is also on;
- otherwise return the same 404 to every public, logged-out, non-admin, missing-nonce, or invalid-nonce request; the test flag by itself never opens the route publicly;
- the controlled-test gate is armed only by an authenticated admin `POST` with a WordPress nonce in the POST body; it stores a 60-second user-scoped one-time transient and returns a `303` to the exact clean homepage URL with no query string. The frontend consumes/deletes that transient once under a per-user named lock before exposing the REST nonce; the admin action nonce therefore never appears in a URL, referrer, analytics, token request, or Vercel request;
- `forcePrimaryFailure` is a browser-local switch only: it is absent from the Vercel POST allow-list/body, and Vercel recognizes test mode only after validating the signed token’s HMAC and `mode=test` claim.

Response:

~~~json
{
  "ok": true,
  "site_id": "hybridautos-ae",
  "protocol_version": "1",
  "privacy_policy_version": "2026-07-16",
  "mode": "live",
  "issued_at": 1789000000,
  "expires_at": 1789043200,
  "nonce": "0123456789abcdef0123456789abcdef",
  "token": "v1.1789000000.1789043200.0123456789abcdef0123456789abcdef.live.aaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaa"
}
~~~

### 5.2 Token format and signature

Token wire format:

~~~text
v1.<iat>.<exp>.<nonce>.<mode>.<64 lowercase hex HMAC>
~~~

Canonical HMAC bytes:

~~~text
v1
hybridautos-ae
<iat>
<exp>
<nonce>
<mode>
~~~

Rules:

- `LP_FALLBACK_SIGNING_SECRET` is a dedicated, distinct 64-character lowercase hex key decoded to 32 bytes.
- `exp = iat + 43,200` seconds.
- `nonce` is exactly 32 lowercase hexadecimal characters.
- `mode` is `live` or `test`.
- Future issue-time skew is at most 300 seconds; expired tokens are rejected.
- `test` mode is emitted only under the exact authenticated WordPress administrator checks in section 5.1 and the browser plan’s admin-only test gate.
- Vercel accepts a token only when its signed claim exactly matches the effective service mode: `test` while `FALLBACK_TEST_MODE=true`, otherwise `live`. A mismatch returns fixed HTTP 403 `token_mode_mismatch` before any Redis, QStash, or Telegram access, so an old 12-hour test token cannot become an unlabelled live lead.
- A production primary-failure simulation is permitted only with a signed `mode=test` token and the admin-only frontend flag. There is no public controlled route.

### 5.3 Atomic nonce binding

Origin is a browser policy, not authentication. A copied token must not authorize multiple unrelated submissions.

The same Upstash Lua operation that creates the receipt must:

1. inspect `token-use:{nonce}`;
2. if absent, set it to the first `submission_id` with `EX 43200`;
3. if equal to the current `submission_id`, allow an idempotent replay;
4. if different, reject `409 token_reuse`;
5. create receipt, receipt-ID index, encrypted payload, initial contact-free `due-work:{receipt_id}` metadata, and its `due-work` sorted-set member in the same Lua operation only when token binding is valid.

No separate pre-check is sufficient because concurrent requests must be serialized atomically.

Tests must cover:

- forged `Origin` with a valid-looking body;
- valid Origin with forged token;
- cached/reused token response;
- concurrent same-nonce/same-UUID replay;
- concurrent same-nonce/different-UUID rejection;
- no receipt or ciphertext for rejected reuse.

## 6. Browser delivery behavior

### 6.1 Primary success

Success requires HTTP success, valid JSON, `ok === true`, and positive integer `lead_id`. On success the browser never calls Vercel, emits existing `lead_success`, and redirects to `/thank-you/`.

### 6.2 Eligible primary failure

Fallback is attempted only for:

- network failure;
- 20-second timeout;
- HTTP 5xx;
- both WordPress REST route variants unavailable;
- empty, malformed, or unconfirmed success response.

Fallback is not attempted for validation failure, honeypot, consent rejection, or HTTP 400, 401, 403, 409, 422, or 429.

The pretty WordPress route and legacy `?rest_route=` variant share the same 20-second primary deadline. Any HTTP 404 from the first lead POST—including a proxy/hosting HTML 404—tries the legacy variant because this endpoint has no business-level 404. Only after the legacy variant also returns 404 are the two routes classified unavailable and fallback attempted once. Other protected 4xx responses never bypass WordPress.

The browser sends the fallback POST immediately after the eligible primary failure is known. That fallback request has its own independent 15,000 ms `AbortController`; the 45-second delay applies only to Vercel's later reconciliation worker, never to storing the backup contact.

### 6.3 Fallback acceptance flags

Both exact required variables are fail-closed:

- `FALLBACK_ACCEPTING_ENABLED=false|true`;
- `FALLBACK_TEST_MODE=false|true`.

Rules:

- missing, empty, or any value other than exact lowercase `true`/`false` makes configuration loading fail;
- initial preview and production deploy uses `FALLBACK_ACCEPTING_ENABLED=false` and `FALLBACK_TEST_MODE=true`;
- public POST returns HTTP 503 `service_disabled` while accepting is false;
- non-production Telegram messages always begin `[TEST — DO NOT CONTACT]`;
- production fallback-lead messages derive the prefix from immutable receipt `intake_mode`; production technical health/test messages use the effective environment/test rules;
- real contacts cannot be enabled until policy is published, production flags are `accepting=true,test=false`, the service is redeployed and verified, and the website/browser fallback flag is still disabled;
- only after those checks may the website/browser flag be enabled.

### 6.4 Fallback response

Vercel success requires HTTP success, `ok===true`, matching `submission_id`, exact receipt ID, and `stored===true`.

Initial accepted response:

~~~json
{
  "ok": true,
  "site_id": "hybridautos-ae",
  "submission_id": "d9428888-122b-4b3e-a105-4d4f0a13262f",
  "receipt_id": "rct_d9428888122b4b3ea1054d4f0a13262f",
  "stored": true,
  "delivery_state": "pending"
}
~~~

The browser may redirect to Thank You once the encrypted contact is durably recoverable. Telegram delivery happens asynchronously after reconciliation.

If neither receiver confirms durable storage, the form remains filled, the button re-enables, a visible retry message appears, no conversion event fires, and Thank You does not open.

## 7. Vercel service routes

- `POST /api/v1/fallback-leads` — validate and atomically store/schedule.
- `GET /api/v1/receipts/:submission_id` — signed server-to-server status only.
- `GET /api/v1/health` — shallow public process health only; no Redis/network probe.
- `POST /api/internal/fallback-delivery` — QStash-authenticated 45-second reconciliation/delivery worker.
- `POST /api/internal/telegram-cleanup` — QStash-authenticated cleanup-only state repair after confirmed Telegram send.
- `POST /api/internal/health-check` — QStash-authenticated deep Beget/Redis/heartbeat monitor.

### 7.1 Public fallback contract

- `application/x-www-form-urlencoded` only.
- Maximum encoded body 16,384 bytes.
- `credentials: omit` and `referrerPolicy: no-referrer`.
- CORS exact `https://hybridautos.ae`.
- Fixed allow-list; duplicate or unknown fields rejected.
- Required: protocol/site/version, `submission_id`, `fallback_reason`, `pd_consent=1`, policy version, token, UAE phone.
- Name is optional 0–191 characters because phone-only production leads exist.
- Email/message/form/model/brand/CTA/source/UTM/Roistat/click IDs are bounded by Unicode code points consistently in browser and Vercel, while the complete URL-encoded body is bounded by bytes.
- Cross-runtime tests require 191 emoji to satisfy a 191-character field, 192 to be truncated by the browser or rejected consistently by direct server input, with no surrogate split; an oversized Unicode UTM/message body must still preserve phone/consent/UUID/token under 16,384 encoded bytes.
- Honeypot must be empty.
- Body/contact is never logged.

### 7.2 Abuse protection

- Validate CORS, token, nonce binding, consent, UUID, phone, honeypot, allow-list, duplicates, and limits.
- Vercel WAF on the verified commercial plan rate-limits fallback POST by IP with the confirmed included rule.
- Upstash adds per-IP and per-submission counters.
- `LP_RATE_LIMIT_SECRET` is a dedicated distinct 64-character lowercase hex key decoded before HMAC.
- Store only a short HMAC-derived IP key, never raw IP.
- If the commercial-plan WAF rule is unavailable, stop release rather than silently depending on Redis only.

## 8. Storage, state, and retention

### 8.1 Keys

Use separate keys:

- `receipt:{submission_id}` — pseudonymous receipt/fingerprint without direct contact fields, 30-day TTL;
- `receipt-id:{receipt_id}` — receipt index, 30-day TTL;
- `payload:{receipt_id}` — AES-GCM ciphertext, maximum 7-day TTL;
- `token-use:{nonce}` — bound UUID, 12-hour TTL;
- `due-work` plus `due-work:{receipt_id}` — contact-free recovery index/job metadata for a QStash publication that was not confirmed;
- rate/lock/health keys with purpose-specific TTL;
- `recovery:audit` — pseudonymous audit stream without direct contact fields, maximum 1,000 entries, 90-day TTL.

### 8.2 Encryption and exact secrets

- `LP_ENCRYPTION_KEY_B64` must decode to exactly 32 random bytes.
- AES-256-GCM uses a random 12-byte IV, 16-byte tag, and AAD `hybridautos-ae:{submission_id}:{receipt_id}`.
- Signing, status, payload-hash, and rate-limit keys are four different 64-character lowercase hex literals.
- Configuration fails closed if any two are equal, a hex key does not match `/^[0-9a-f]{64}$/`, or encryption does not decode to 32 bytes.

### 8.3 Internal and public state

Internal states may include `pending`, `reconcile_wait`, `schedule_unknown`, `reconcile_retry_wait`, `telegram_sending`, `telegram_rate_wait`, `cleanup_pending`, `schedule_failed`, `primary_confirmed`, `telegram_sent`, `telegram_unknown`, `telegram_failed_permanent`, `manual_recovered`, and `payload_expired`.

Public `delivery_state` is exactly:

- `pending` — recoverable ciphertext exists and no ambiguous Telegram send occurred;
- `delivered` — internal `telegram_sent`, `primary_confirmed`, or `manual_recovered`;
- `unknown` — Telegram may have accepted the message and recoverable ciphertext still exists;
- `expired` — no terminal delivery/recovery proof and ciphertext no longer exists.

Public `stored` is:

- `true` for `telegram_sent`, `primary_confirmed`, or `manual_recovered`;
- otherwise `true` only while `payload:{receipt_id}` exists;
- `false` when the payload has expired/disappeared without terminal proof.

The public status endpoint must check current payload existence. A 30-day receipt alone never justifies `stored:true`.

### 8.4 TTL-preserving transitions

- Every receipt update uses Redis `SET ... KEEPTTL`.
- No transition resets or extends the original 30-day receipt TTL or seven-day payload TTL.
- Tests inspect TTL after every state transition and after simulated payload expiry.

## 9. Delayed WordPress reconciliation

### 9.1 Initial job

After atomic storage, the public handler schedules one QStash message after 45 seconds:

~~~json
{"v":1,"receipt_id":"rct_d9428888122b4b3ea1054d4f0a13262f","action":"reconcile","check":1}
~~~

The message contains no contact.

### 9.2 Signed submission check

Worker calls:

`GET /wp-json/landing/v1/submission-status/{submission_id}`

Headers:

- `X-LP-Site-Id: hybridautos-ae`
- `X-LP-Timestamp: <Unix seconds>`
- `X-LP-Signature: hex(HMAC-SHA256("GET\n/path\n<timestamp>\nhybridautos-ae", LP_FALLBACK_STATUS_SECRET))`

`LP_FALLBACK_STATUS_SECRET` is validated as a distinct 64-character lowercase hex literal and decoded to 32 bytes before HMAC, consistently with the other three HMAC keys.

Safe response:

~~~json
{
  "ok": true,
  "site_id": "hybridautos-ae",
  "submission_id": "d9428888-122b-4b3e-a105-4d4f0a13262f",
  "exists": true
}
~~~

### 9.3 Decision

- `exists=true`: atomically mark `primary_confirmed` with KEEPTTL, delete ciphertext, do not call Telegram.
- Valid explicit `exists=false`: proceed to Telegram once.
- Timeout, network error, 5xx, malformed/stale/mismatched response on check 1: schedule exactly one second reconciliation check after 30 seconds.
- Ambiguous check 2: proceed to Telegram to favor contact recovery.
- Duplicate QStash deliveries use receipt locks and state checks; they never produce duplicate Telegram calls.

## 10. Telegram delivery correctness

### 10.1 Message

Use existing HybridCars bot/chat. Preview always uses the test prefix. Production fallback prefix is derived from the receipt's immutable signed `intake_mode`, never from the service's current flag: every `intake_mode=test` receipt remains `[TEST — DO NOT CONTACT]` even if the deployment has since switched live. Include contact, model/message, page/CTA, UTM, frozen first reason, short submission ID, and receipt ID with safe Telegram escaping and length bounds.

### 10.2 State machine

Before calling Telegram:

1. atomically persist `telegram_sending` with a unique attempt ID using KEEPTTL;
2. release no competing worker into a second call;
3. call Telegram once.

Outcome:

- HTTP 200, `ok=true`, positive `message_id`: atomically mark `telegram_sent` with `SET KEEPTTL` and delete payload.
- HTTP 429 with valid `retry_after`: mark `telegram_rate_wait` with KEEPTTL and schedule one QStash retry respecting the delay and attempt cap.
- Any other 4xx: `telegram_failed_permanent`, no automatic resend, keep ciphertext until its original seven-day expiry/manual recovery.
- 5xx, timeout, network error, malformed 200, invalid Telegram body, or stale `telegram_sending`: `telegram_unknown`, no automatic resend.

Only HTTP 429 is automatically retried. This rule also applies to technical outage/recovery alerts.

### 10.3 Transition failure after confirmed send

If Telegram confirms a positive `message_id` but the Redis delivered transition fails:

- schedule `POST /api/internal/telegram-cleanup` containing only receipt ID, message ID, and attempt ID;
- cleanup verifies current attempt, marks delivered with KEEPTTL, and deletes ciphertext;
- cleanup never calls Telegram and never resends the message;
- until cleanup succeeds, public state is `unknown` and ciphertext remains recoverable.

### 10.4 Recovery when scheduling itself is not confirmed

Every job-publication boundary is made durable before calling QStash. This covers the initial 45-second reconciliation, the second reconciliation check, a definite Telegram HTTP 429 retry, and cleanup-only repair:

- the initial receipt Lua atomically stores contact-free job metadata/due time and adds the receipt ID to the `due-work` sorted set together with receipt/payload creation, so a crash after storage cannot leave an undiscoverable contact;
- every later state-to-job transition uses one Lua operation to KEEPTTL-update state, read the receipt's remaining PTTL, SET the due metadata with that exact remaining PX TTL, and ZADD the due member before publishing;
- after confirmed publication, atomically remove that due-work entry;
- if publication fails or its result is ambiguous, keep the appropriate `schedule_unknown`, `reconcile_retry_wait`, `telegram_rate_wait`, or `cleanup_pending` state and due entry; the browser may still receive truthful durable-storage success;
- each QStash-authenticated deep-health run examines at most 500 due members and publishes at most 50 valid jobs under per-receipt locks; missing due metadata/receipt or a terminal/non-job state is guarded-removed as stale; reconcile/check-2/Telegram-429 jobs additionally require live ciphertext, while `cleanup_pending` requires only its matching receipt/attempt/message and must finalize `delivered` even when ciphertext is already absent or expired, without ever calling Telegram; hundreds of stale members cannot starve a later valid contact;
- a failed recovery publication is retried at most five times and no more often than every five minutes; after the fifth failure, mark `schedule_failed`, create one privacy-safe technical incident when possible, and keep ciphertext available for manual recovery until its original seven-day expiry;
- the sweep never republishes a Telegram call from `telegram_sending`, `telegram_unknown`, or another ambiguous-send state. It may recreate a Telegram job only from an explicit persisted HTTP 429 state.

Workers re-check state and remain idempotent, so duplicate QStash delivery cannot duplicate a Telegram message. If QStash itself is unavailable, the durable due entry is processed by the first later authenticated deep-health run.

## 11. Receipt status

WordPress signs `GET /api/v1/receipts/{submission_id}` with:

- `X-LP-Site-Id`;
- `X-LP-Timestamp`;
- `X-LP-Signature` over exact method/path/timestamp/site canonical string.

Response contains only:

~~~json
{
  "ok": true,
  "submission_id": "d9428888-122b-4b3e-a105-4d4f0a13262f",
  "exists": true,
  "stored": true,
  "delivery_state": "pending"
}
~~~

No contact, ciphertext, fingerprint, reason, IP hash, provider response, or internal state is returned. Receipt observation is lifecycle-aware:

- `pending,stored=true` provisionally defers the ordinary missing-lead alert but creates a privacy-safe watch and is polled again; if still pending 10 minutes after first observation, create one `fallback_delivery_stuck` incident while continuing to poll;
- `unknown,stored=true` immediately creates one `fallback_delivery_uncertain` incident while the contact remains manually recoverable;
- only `delivered,stored=true` or a matching WordPress lead is terminal recovery and stops polling/resolves the incidents;
- `expired,stored=false` or a disappeared payload reopens/creates the missing-lead incident, even if an earlier pending receipt existed.

Watches contain only submission UUID, public state, and due time—never contact—and poll no more often than every five minutes until a terminal result.

## 12. Manual recovery

Manual recovery is two-phase and TTY-only:

1. `list` prints privacy-safe pending receipt IDs/states/ages only.
2. Operator identity comes only from exact environment variable `RECOVERY_OPERATOR_ID` matching the fixed approved allow-list; it is not accepted from CLI arguments.
3. `view --receipt-id` acquires a lock, appends `view_started` audit, decrypts in memory, and prints plaintext to an interactive TTY.
4. Ciphertext remains stored while the operator reviews it.
5. CLI asks for exact confirmation `DELETE <receipt_id>`.
6. Only exact confirmation atomically deletes payload and marks `manual_recovered` with KEEPTTL, then appends `recovery_confirmed`.
7. EOF, crash, timeout, wrong input, or no confirmation releases the lock and leaves ciphertext recoverable.

Audit entries contain event, receipt ID, fixed operator ID, and timestamp only. On every append, first exact-trim stream IDs older than Unix-now minus 90 days with `XTRIM MINID <cutoff_ms>-0`, then apply `MAXLEN ~ 1000`, and refresh key expiry to 90 days. The age trim is mandatory even when the stream has fewer than 1,000 entries. Never write plaintext to a file, clipboard, application log, audit, shell argument, or provider message.

## 13. Health monitoring

### 13.1 Public shallow health

`GET /api/v1/health` returns process/build readiness only:

~~~json
{"ok":true,"status":"ready","site_id":"hybridautos-ae"}
~~~

It must not read Redis, call WordPress, expose flags, or disclose provider status.

### 13.2 Signed/QStash deep health

Only QStash-authenticated `POST /api/internal/health-check` performs:

- Redis ping/read/write probe with a non-contact short-TTL key;
- public site response;
- exact unsigned public WordPress health response over TLS with redirects forbidden and strict PII-free schema validation;
- WordPress lead endpoint/database/heartbeat assessment;
- the bounded contact-free due-work recovery sweep described in section 10.4.

Health state uses an independent ledger for the component being checked:

- while Redis is healthy, Beget/WordPress failure counters and pre-send Telegram state live in Redis;
- whenever the WordPress observation route is reachable, the external checker sends the current Redis `failed|ok` observation for every five-minute slot, including the first healthy slot after a Redis outage; WordPress stores/deduplicates the no-contact two-failure/recovery incident and its existing monitoring worker sends Telegram with pre-send state;
- `checked_at_slot` is exactly `floor(X-LP-Timestamp / 300)`; WordPress ignores every authenticated observation with `checked_at_slot <= last_processed_slot` as a duplicate/stale success response, and consecutive failures require distinct adjacent increasing slot numbers;
- the observation body is exactly `{v:1,site_id:"hybridautos-ae",target:"redis",status:"ok|failed",checked_at_slot:<integer>}` and is HMAC-authenticated with the decoded status key over `POST`, exact path `/wp-json/landing/v1/external-health-observation`, Unix timestamp, site ID, and lowercase SHA-256 of the exact raw body bytes; redirects are forbidden;
- WordPress returns exact no-store JSON `{ok:true,site_id:"hybridautos-ae",accepted:true,duplicate:<bool>}` for both a new and same-slot authenticated observation; Vercel rejects any other keys/value;
- every outage episode has a privacy-safe generation derived from its first accepted failure slot; fingerprints include `(site,target,episode_generation,kind)`, so repeats inside one episode do not resend while a new failure episode after recovery can send a new outage/recovery pair;
- when at least one independent ledger is reachable, two consecutive failures produce one outage and the first later healthy observation produces one recovery; two complete failure/recovery cycles produce two separate pairs, while an older delayed failure can never reopen a newer recovered episode; ambiguous Telegram delivery is never retried;
- WordPress watches the external checker itself: after monitoring has been enabled for more than 15 minutes, no newer accepted signed observation for strictly more than 900 seconds creates one `external_monitor_stale` episode; the first later valid increasing-slot observation creates one `external_monitor_recovery` for that episode;
- if Redis and WordPress are simultaneously unreachable, exact durable deduplication is impossible. The QStash worker may send one contact-free `[DEGRADED STATELESS]` outage notice only in each 30-minute UTC bucket with QStash retries disabled. Duplicate function delivery may duplicate that notice, and exact recovery cannot be promised until a ledger is reachable. This is an explicit residual boundary, not reported as exact-once monitoring.

## 14. WordPress monitoring

Keep the approved privacy-safe `landing_monitor_alerts` queue, missing-lead detector after five minutes, exact integration IDs, one-minute cron heartbeat, non-recursive technical Telegram client, and read-only admin Monitoring page.

Changes required by this amendment:

- after a lead and its early audit are durably stored, WordPress returns the positive `lead_id` immediately;
- Telegram, Email, and Roistat delivery runs asynchronously after durable storage, so adapter delay/failure cannot delay, revoke, or replace the successful lead response;
- watch `pending,stored=true`, alert if it exceeds 10 minutes, and continue bounded polling;
- immediately alert on `unknown,stored=true` while manual recovery is still possible;
- treat only `delivered,stored=true` or a matching WordPress lead as terminal recovery, and treat `expired/stored=false` as missing/reopened;
- provide the no-store token endpoint;
- provide the signed `submission-status/{uuid}` endpoint;
- keep public WordPress health PII-free;
- never return contact to Vercel.

## 15. Privacy policy and backups

Before `FALLBACK_ACCEPTING_ENABLED=true`:

- publish policy text naming Vercel and Upstash as technical processors;
- state immediate deletion after confirmed Telegram, primary reconciliation, or manual recovery;
- state maximum seven-day pending encrypted retention and 30-day pseudonymous duplicate-prevention receipt;
- keep consent mandatory.

Backups:

- every production database/config backup must be encrypted at creation or streamed directly into an encrypted archive;
- resulting backup files must be mode `0600`;
- passphrases/keys live only in the approved password manager;
- never leave a plaintext SQL dump, `wp-config.php`, `.env`, Vercel environment export, token file, or decrypted contact in local/server temporary directories;
- record ciphertext hash and restore instructions without secrets;
- source-code Git backups contain no credentials or contacts.

## 16. Repositories and files

### WordPress backend `landing_system`

- database/idempotency/monitoring modules;
- no-store token endpoint;
- unsigned public health plus signed submission-status and external-observation endpoints;
- safe admin monitoring and tests.

### Frontend `hybridautos-ae`

- primary-first/fallback delivery state;
- no-store token fetch;
- immutable snapshot;
- admin-only production test flag;
- disabled-by-default public fallback config;
- tests on all six advertising pages.

### Private Vercel project `hybridautos-lead-fallback`

- public fallback, signed receipt, shallow health;
- internal fallback-delivery, cleanup-only, and deep health workers;
- HMAC/encryption/storage/Telegram/recovery modules;
- unit/integration/security/release tests;
- pinned CLI/resource/WAF evidence.

## 17. Required automated scenarios

1. Primary success never calls Vercel.
2. Eligible primary failures call Vercel once; protected 4xx/429 never bypass WordPress.
3. Token endpoint is no-store and not embedded/cached.
4. Forged Origin/token and nonce reuse across UUIDs are rejected.
5. Same nonce/UUID and same fingerprint replays one receipt.
6. Same submission ID/different fingerprint returns 409.
7. Different fallback reason with otherwise identical payload replays and preserves first reason.
8. Atomic create binds nonce and creates receipt/index/ciphertext together.
9. Receipt ID is exactly `rct_` plus 32 hex.
10. Initial stored receipt schedules one 45-second delivery job and sends no immediate Telegram.
11. WordPress exists=true deletes ciphertext and sends no Telegram.
12. Explicit missing sends once.
13. First ambiguous check schedules one +30-second check; second ambiguous sends once.
14. Telegram state is persisted as sending before the call.
15. Only 429 retries; 5xx/timeout/malformed/stale sending never resends.
16. Confirmed send transition failure schedules cleanup-only and never resends.
17. All receipt transitions preserve TTL.
18. Payload expiry changes public status to expired/stored=false unless terminal delivered.
19. Manual recovery crash/no-confirm retains payload; confirm deletes/marks.
20. Recovery audit is bounded to 1,000 and expires within 90 days.
21. Public health never calls Redis; deep health requires QStash.
22. With an independent ledger reachable, two external failures send one outage and recovery sends one recovery; simultaneous Redis+WordPress outage follows the explicit bounded stateless boundary.
23. Configuration rejects missing/invalid flags, non-exact secrets, or equal secrets.
24. Failed initial/check-2/429/cleanup publication leaves durable due work; a later deep-health sweep republishes only the exact idempotent job, and the fifth failure becomes one safe visible incident/manual-recovery state.
25. No logs, QStash bodies, analytics, technical alerts, Git, or backups contain plaintext contact/credentials.
26. Two complete fail/fail/recovery outage cycles produce two distinct outage/recovery pairs; a duplicate slot produces nothing and an older delayed failure after recovery cannot reopen the incident.
27. A due set containing more than 50 stale members removes them safely and still reaches a later valid due job within the 500-member examination budget.
28. The enabled Email integration recipient is exactly `elapova00@gmail.com`, every old Neuroboost recipient/integration is disabled, and one labeled primary test proves Email to that address plus Telegram plus Roistat/CRM without delivery to a previous recipient.
29. Redis failed at slots N/N+1 then healthy at N+2 still posts `ok` to WordPress and creates exactly one recovery.
30. No signed external observation for strictly more than 900 seconds creates one monitor-stale alert; the first newer valid observation creates one recovery.
31. Matching `cleanup_pending` with absent ciphertext finalizes `delivered` and never calls Telegram.

## 18. Executable release order

1. Verify encrypted `0600` backups and Git rollback points.
2. Verify Vercel CLI 54.2.0 authentication, a commercial Pro/Enterprise plan with DPA and data-use setting, exact free Marketplace products, QStash `prodPack=false`, Redis `autoUpgrade=false`, and one included WAF rule; Hobby stops release.
3. Deploy private Vercel service with `accepting=false,test=true`.
4. Verify preview/integration tests and test-prefixed messages; public POST must remain disabled.
5. Deploy WordPress storage, token/status/monitoring endpoints with browser fallback disabled.
6. Publish and independently verify Privacy Policy.
7. Deploy frontend token/fallback code with website fallback disabled.
8. While website fallback is disabled, temporarily set production `accepting=true,test=true`, redeploy, and verify those exact effective flags server-side.
9. Use only the admin-only frontend flag and signed `mode=test` token for the controlled end-to-end test; there is no public controlled route.
10. Remove/disable the admin-only flag, immediately restore `accepting=false,test=true`, redeploy, and verify public POST is disabled again.
11. Verify normal primary success makes no Vercel receipt.
12. Verify delayed fallback reconciliation, Telegram, replay, cleanup, status, expiry, health, WAF, and no-PII evidence.
13. While website fallback is still disabled, set production `accepting=true,test=false` and redeploy.
14. Verify exact effective flags server-side without exposing them publicly, and prove any delayed test receipt remains test-prefixed from immutable `intake_mode` (or no test due work remains).
15. Enable website fallback last.
16. Verify all six advertising pages, live hashes, clean logs, schedules, tags, and rollback procedure.

## 19. Acceptance criteria

Release is complete only when fresh evidence shows:

- valid phone-only contact is accepted;
- normal production success creates one WordPress lead and no external receipt;
- lost/failed primary response creates one encrypted pending receipt;
- delayed reconciliation suppresses Telegram when WordPress has the lead;
- explicit/second-ambiguous missing state sends exactly one fallback message;
- same receipt cannot be delivered twice;
- only 429 retries;
- public state is one of pending/delivered/unknown/expired and `stored` follows payload/terminal proof;
- expired payload is not falsely reported recoverable;
- pending/unknown receipt watches remain non-terminal, warn before seven-day expiry, and reopen missing-lead when the payload disappears;
- manual view without confirmation retains contact;
- no-store token and nonce binding prevent cross-submission reuse;
- four HMAC keys are exact, distinct, and secret; encryption key is exact 32 bytes;
- public health is shallow and deep health is authenticated;
- commercial Vercel plan/DPA/data-use and included Marketplace/WAF constraints are proven;
- exact effective integration bindings are proven server-side: `elapova00@gmail.com` is the only enabled lead Email recipient, Neuroboost is disabled, and a labeled test confirms Email, Telegram, Roistat/CRM delivery with no message to an old recipient;
- policy, encrypted `0600` backup, private Git revision, production hashes, clean logs, and rollback evidence exist before website enablement.
