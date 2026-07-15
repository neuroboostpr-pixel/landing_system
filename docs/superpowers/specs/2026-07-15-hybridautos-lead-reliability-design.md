# HybridAutos lead reliability and attribution design

**Date:** 2026-07-15  
**Status:** Owner-approved; reviewer corrections incorporated  
**Production site:** `https://hybridautos.ae`

## 1. Goal

Make every real form submission recoverable and observable before paid traffic is restarted:

1. save the contact in WordPress before calling Email, Telegram, Roistat, or a downstream CRM;
2. never show the thank-you page until WordPress confirms a saved lead with a numeric `lead_id`;
3. record a separate delivery status and error for every external channel;
4. retry only failures that are safe to retry;
5. preserve advertising attribution across internal navigation;
6. count an advertising conversion only after a confirmed saved lead;
7. keep a tested rollback point for both code and the database.

Business result: a temporary integration failure may delay a notification, but it must not erase the customer’s phone or email.

## 2. Confirmed failure mode

The old browser script redirected to `/thank-you/` from its error handler. A 404, rate limit, reCAPTCHA rejection, database error, network break, or PHP error therefore looked like a successful submission to the visitor and analytics even when WordPress had not saved a lead.

The published Google Ads trigger also counted any visit to a URL containing `thank-you`. A direct visit, reload, or false redirect could therefore be counted as a conversion. Yandex Metrika was initialized twice, making the evidence noisier, but duplicate Metrika initialization did not itself delete contacts.

This design removes both false-success paths.

## 3. Backup and source-control boundaries

- The permanent Beget backup `Before form endpoint fix 2026-07-15` remains an emergency recovery point, but it is not the normal release rollback because it predates the current browser fix, Email recipient, and later leads.
- Production deployment is forbidden until a fresh current-state backup contains all site files and the current database, has a recorded timestamp/checksum manifest, and has passed a restore rehearsal on a non-production database/site copy. This may be a Beget snapshot or an encrypted local export that creates no recurring charge.
- GitHub stores source code only. It must never contain `wp-config.php`, passwords, tokens, database dumps, logs, uploads, or customer contacts.
- Branch `backup/hybridautos-prod-before-reliability-2026-07-15` at local commit `1c3372c` preserves the production-only lead-audit hotfix before this work. It is not considered a remote backup until GitHub reports the same commit SHA.
- New work is isolated in `fix/lead-reliability-observability`.
- A separate private `hybridautos-ae` repository must contain the complete current custom theme, the current fixed form script, and the release manifest before production deployment.
- Both backup and feature branches must be published and verified through GitHub before production deployment. A release record binds the exact `landing_system` commit, theme commit, database migration version, and SHA-256 file manifest.
- Database changes are additive only: no renamed/dropped columns and no new required column without a safe default. The old server code must continue to run against the migrated schema.

## 4. Server-side data flow

For every form POST:

1. The browser creates a UUID `submission_id` and reuses it for retries of that same submission lifecycle. The REST fallback receives the same UUID. Closing/reopening an unsuccessful modal keeps it; a confirmed success clears it and the next form attempt gets a new UUID.
2. WordPress writes the raw, sanitized attempt to the audit table before validation.
3. WordPress validates the honeypot, contact fields, explicit consent, and rate limit.
4. Active reCAPTCHA execution and blocking are removed. The dormant settings may remain temporarily only for backward-compatible administration; no reCAPTCHA script or token is required.
5. `submission_id` is validated as a UUID and stored as nullable `CHAR(36)` with a unique database index. For compatibility, an old cached browser request without it receives a server-generated UUID and is still saved.
6. WordPress atomically attempts the insert. A duplicate UUID with the same contact fingerprint returns the original `lead_id`; the same UUID with a different phone/email returns `409 submission_conflict` and leaves both attempts recoverable in audit.
7. WordPress saves the contact, full attribution, and a JSON delivery plan containing the enabled integration IDs, labels, adapter types, and safe configuration hashes at submission time. It stores no tokens or passwords in that plan.
8. WordPress creates one first-attempt pending delivery row for every integration in that saved plan.
9. WordPress returns `{ "ok": true, "lead_id": 123, "delivery_status": "queued" }` immediately.
10. A background worker sends Email, Telegram and Roistat independently and records the outcome.
11. A reconciliation job creates missing jobs only from the saved delivery plan and only for leads at or after a recorded `cutover_lead_id`. Historical leads are shown as `legacy/untracked` and are never mass-resubmitted.

If queue creation fails after the contact has been saved, WordPress still returns success and the reconciliation job repairs the missing queue rows.

## 5. Delivery queue and retry policy

The existing unused `landing_lead_log` table becomes the durable outbox (a stored list of messages waiting to be delivered). One row represents one delivery attempt. The migration raises `DB_VERSION` to `1.1.0`, checks existing rows before adding indexes, and adds:

- `integration_id`, `integration_label`, `config_hash`, `idempotency_key`;
- `next_attempt_at`, `locked_at`, `lock_token`, `finished_at`, `updated_at`, `provider_id`;
- unique `(lead_id, adapter, integration_id, attempt)` and lookup index `(status, next_attempt_at)`.

There are at most five attempts per planned channel. The worker claims a row with one conditional database `UPDATE` and proceeds only when exactly one row changed. A lock lease lasts five minutes. A stale `sending` row becomes `unknown`, never automatically `pending`, because the external send may already have succeeded.

Statuses:

- `pending`: waiting;
- `sending`: claimed by one worker;
- `success`: provider confirmed delivery;
- `accepted`: local mail system accepted the email, but inbox delivery is not yet proven;
- `retry_wait`: confirmed temporary failure;
- `failed_permanent`: configuration or non-retryable client error;
- `unknown`: request may have reached the provider but its reply was lost; do not blindly repeat it.

Safe retries run immediately, then after 1 minute, 5 minutes, 30 minutes, and 2 hours. HTTP 429 respects the provider’s retry delay. Only a failure proven to occur before delivery may retry automatically. Timeout, read failure, HTTP 5xx, and a worker crash after sending are `unknown` unless the provider has confirmed idempotency. After five safe failed attempts, the channel becomes `failed_permanent` and is surfaced in red to the administrator.

Channel rules:

- Telegram succeeds only on HTTP 200 plus JSON `ok=true`; save `message_id`.
- Roistat accepts both its documented JSON success and the live plain-text response `Lead was successfully created`; pass `site_lead_id`. Until Roistat/CRM deduplication on that field is confirmed, ambiguous Roistat results remain `unknown` without automatic retry.
- Email is recorded as `accepted` when `wp_mail()` hands it to the mail system. It must not be described as guaranteed inbox delivery.
- Every adapter uses the exact selected `integration_id`, not the first integration of the same type.
- The old synchronous `send_admin_email()` path is removed. Only the explicitly enabled Email integration (currently `elapova00@gmail.com`) sends mail, preventing an untracked duplicate to the WordPress system address.
- If an integration is deleted or its configuration hash changes while jobs are pending, those jobs pause as `failed_permanent/config_changed`. An administrator must explicitly bind and retry them against the new configuration.
- This design prevents local duplicate attempts. Telegram, Email, and unconfirmed Roistat timeouts cannot honestly guarantee external exactly-once delivery; `unknown` requires human verification before retry.

WP-Cron may accelerate processing, but a Beget system cron must invoke the queue worker every minute so delivery does not depend on site visits. The worker records a `last_worker_run` heartbeat. Production acceptance requires a real delayed retry, an empty due queue afterwards, and a two-worker concurrency test with no duplicate send.

## 6. Recoverability and administrator view

- The early audit retains sanitized contact and attribution whenever the POST reaches WordPress, even if later validation or saving fails.
- Every saved lead shows per-channel delivery status, timestamp, response, and error.
- An administrator can retry a selected failed channel. `success` and `accepted` cannot be retried. Retrying `unknown` requires an explicit warning that an external duplicate is possible.
- Promoting a recoverable audit row requires explicit confirmation of the current delivery plan and then creates jobs for that plan; it never silently selects every current integration.
- Logs must redact tokens and secrets. Response bodies are length-limited.
- A cleanup policy removes or anonymizes old audit records in accordance with the site’s privacy policy.

If a POST never reaches the server, WordPress cannot recover data that existed only in the browser. The form therefore keeps the entered values on error, offers a retry using the same `submission_id`, and uses the WordPress REST fallback route. Protection while the whole hosting account is unavailable would require a separate external collector and is outside this urgent release.

## 7. Browser form behavior

- Submit to `/wp-json/landing/v1/lead`, then retry the WordPress `?rest_route=` form only for a route-level 404.
- Treat success as valid only when `ok === true` and `lead_id` is a positive integer.
- On any other response, keep all entered values, re-enable the button, and show a clear retry message. Never redirect from `catch`.
- The form keeps its `submission_id` on the form element/session state across REST fallback, retry, modal close, and reset after failure. Only confirmed success clears it; a later new submission receives a new UUID.
- Include a hidden honeypot and an unchecked, required consent checkbox with a link to `/privacy-policy/`.
- Consent text and the privacy page require owner/legal review; the technical implementation must not pre-check consent.
- Generic calls to action must use “model not selected” instead of silently choosing the first car.
- Lynk & Co must carry `Lynk & Co 900` when that model is explicitly associated with its page/form.

## 8. Attribution fields

Save first-touch data at landing and use it even after internal navigation. The urgent release stores the first non-empty advertising set in `sessionStorage` for the current tab, never overwrites it with an empty/internal URL, and always stores the current `submit_url` separately. Existing consent-managed first-party cookies may be read as a fallback; the new code does not create a persistent advertising cookie before consent. Missing `ym_client_id` or `roistat_visit` is read once at submit time but never delays contact saving.

- `landing_url`, `submit_url`, `landing_referrer`;
- `utm_source`, `utm_medium`, `utm_campaign`, `utm_term`, `utm_content`;
- `gclid`, `gbraid`, `wbraid`, `yclid`, `fbclid`, `msclkid`;
- `ym_client_id`, `roistat_visit`;
- `form_id`, `brand`, `model`;
- `cta_key`, `cta_label`, `cta_placement`.

All values are decoded safely, sanitized server-side, and length-limited. These fields are stored separately, not compressed into the short `source_block` field. They are included in Email, Telegram and Roistat messages where supported. Personally identifiable information must never be pushed to GTM or advertising systems.

Every form/CTA receives stable data attributes. `form_id`, `cta_key`, and `cta_placement` are technical keys and do not change when visible button copy changes. Before release, a page/CTA registry enumerates Home, Li Auto, Zeekr, Xiaomi, Lynk & Co, and ROX, with separate generic and model-specific cases. Generic CTAs send an empty model; model cards send only their explicit model.

## 9. Analytics contract

After a confirmed server response, the browser pushes exactly one event. A `lead_success:{lead_id}` key in session storage prevents a repeated response/retry from firing the Yandex goal twice. Google additionally receives `lead_id` as its Transaction ID.

```js
window.dataLayer = window.dataLayer || [];
window.dataLayer.push({
  event: 'lead_success',
  lead_id: String(data.lead_id),
  form_id,
  brand,
  model,
  cta_key,
  eventCallback: redirectOnce,
  eventTimeout: 1200
});
```

An independent 1.3-second timer calls the idempotent `redirectOnce()` fallback if GTM is blocked. Analytics errors never change the already confirmed lead result. The Yandex `reachGoal` call receives `lead_id` as a parameter.

GTM becomes the single analytics source:

- remove the direct duplicate Yandex Metrika initialization;
- trigger Google Ads and the Yandex goal from `lead_success` only;
- use `lead_id` as Google Ads Transaction ID to deduplicate conversions;
- remove the URL-contains-`thank-you` conversion trigger;
- keep the thank-you page as presentation only, never as proof of a saved lead.

Publishing the final GTM/Yandex/Google Ads changes requires authenticated cabinet access. Two separate gates are reported: **contact preservation ready** and **advertising analytics ready**. Paid traffic must not restart until the old `/thank-you/` conversion trigger is unpublished and the advertising analytics gate passes.

## 10. Testing and acceptance

Tests are written before implementation and must cover:

- lead remains saved when all external adapters fail;
- exactly one queue job is created per active integration;
- repeated POST with one `submission_id` returns the original `lead_id`;
- two concurrent POSTs with one UUID produce one lead and one delivery plan; a different contact with that UUID receives `409` and remains in audit;
- concurrent workers do not duplicate an attempt;
- a successful delivery does not repeat;
- retryable failure, timeout/unknown, Telegram `ok=false`, and live Roistat plain-text success;
- worker crash after external success but before local status update becomes `unknown`;
- audit promotion and reconciliation create missing jobs;
- browser never redirects on malformed, 4xx, 5xx, or network responses;
- browser redirects and emits `lead_success` only after a positive numeric `lead_id`;
- first-touch attribution survives navigation;
- first-touch attribution is not replaced by an internal page URL and missing counter cookies do not block saving;
- the CTA registry checks generic and model-specific form paths on every brand page, plus the Home form.

Production acceptance requires:

1. both GitHub repositories/branches and exact remote commit SHAs verified, including the full current theme and release manifest;
2. a fresh full file/database recovery point plus a successful staging restore rehearsal;
3. schema migration test on a copy of the real database and proof that old server code still runs on the additive schema;
4. syntax and automated test checks;
5. deploy compatible backend first, verify an old-format request, then deploy versioned/cache-busted JavaScript, purge server/CDN caches, and verify the actual public JS SHA-256 from an anonymous browser on all six pages;
6. ad-like submissions for Home and every generic/model-specific CTA path in the registry;
7. each contact visible in WordPress with an audit row; Telegram is `success` with `message_id`, Email is `accepted` plus manual inbox confirmation, and Roistat is confirmed `success`; no due `pending` or stale `sending` remains;
8. Beget cron runs once per minute, heartbeat advances, a delayed retry executes, and concurrent workers do not duplicate a send;
9. GTM Preview shows Google Ads and Yandex firing exactly once on `lead_success`; direct/reloaded `/thank-you/` and an error response fire neither; Google receives `Transaction ID = lead_id`, Count is `One`, the Yandex JavaScript goal ID is exact, only one Metrika init remains, and the published GTM version is recorded;
10. no new PHP errors;
11. rollback command/checklist is rehearsed and tied to exact Git commits, release archive, and SHA-256 manifest.

## 11. Rollback

The plugin and theme live in different directories, so they cannot be one atomic operation. Deploy in compatible stages with a strict allow-list and never use a site-wide `--delete`: additive database migration → backward-compatible server plugin → old-format control POST → cache-busted browser JS/theme enqueue → new-format control POST → analytics publication. Upload each file set to a temporary path, verify it, then replace only its allow-listed targets. Never delete the live plugin before a complete replacement exists.

On failure:

1. stop paid traffic and disable the new worker/cron;
2. wait for or classify active locks; never reset an ambiguous `sending` delivery to `pending`;
3. restore the previous versioned plugin and form files from the immutable release archive;
4. clear WordPress/page/CDN cache and PHP OPcache, then verify the public JS checksum;
5. confirm the old code does not process the new queue and run one control submission;
6. leave additive database columns in place for the normal rollback;
7. use full Beget/database restore only for serious corruption. Immediately before it, take an emergency full database dump and preserve/merge `landing_leads`, `landing_lead_audit`, `landing_lead_log`, `landing_lead_status_log`, integration `wp_posts/wp_postmeta`, and relevant `lp_*`/`landing_*` `wp_options` created or changed after the snapshot;
8. after a database restore, re-check that the active Email recipient is `elapova00@gmail.com`, reconcile `sending/unknown` manually, then restart the worker.

## 12. Completion boundary

Contact preservation is complete only when both code repositories are verified in GitHub, production points to the tested release, every CTA registry case passes, cron/queue evidence is visible, and the fresh rollback rehearsal passes. Advertising analytics is complete only after the published GTM/Yandex/Google Ads checks pass. Paid traffic requires both gates. Downstream CRM receipt must be confirmed from Roistat/CRM evidence and is never inferred from a thank-you page.
