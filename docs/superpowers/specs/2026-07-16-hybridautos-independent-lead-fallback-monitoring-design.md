# HybridAutos Independent Lead Fallback and Telegram Monitoring Design

**Date:** 2026-07-16  
**Status:** Approved architecture, pending implementation-plan approval  
**Production site:** `https://hybridautos.ae`  
**Primary hosting:** Beget  
**Independent fallback:** Vercel + Upstash  
**Operations channel:** existing HybridCars Telegram chat

## 1. Goal

Prevent a new browser, WordPress, database, hosting, or integration failure from silently losing a HybridAutos advertising lead.

The finished system must:

1. Keep the existing WordPress route as the normal lead receiver.
2. Save a contact outside Beget when WordPress cannot confirm the lead.
3. Send one clear Telegram message for a fallback lead or a technical incident.
4. Detect a submission attempt that did not produce a WordPress lead.
5. Detect a complete Beget or lead-endpoint outage from outside Beget.
6. Avoid blocking a valid lead because monitoring itself failed.
7. Avoid exposing Telegram, Roistat, database, or signing secrets in browser code.
8. Avoid storing draft contacts before the visitor consents and submits.

## 2. Non-goals

- Do not send every lead to both receivers in parallel. That would create routine duplicates.
- Do not alert on `form_started`, ordinary abandonment, honeypot traffic, or a visitor correcting a validation error.
- Do not store contact values in anonymous form-event or technical-alert tables.
- Do not use the browser to call Telegram or Roistat directly; credentials must remain server-side.
- Do not make reCAPTCHA, Turnstile, or another third-party challenge a requirement for submitting a lead.
- Do not make a Telegram delivery response a prerequisite for the normal WordPress success response after the lead is safely stored.

## 2.1 Cost and account constraint

- Use the existing Vercel account and free-tier or already-included resources only.
- Do not activate a paid Vercel plan, paid Marketplace resource, or new billing commitment without separate user approval.
- If Vercel authentication or the required free Upstash Redis/QStash resources cannot be confirmed, implementation pauses before any production change; WordPress-only monitoring may still be prepared but must not be presented as an independent fallback.

## 3. Chosen architecture

The system uses a **primary-first, passive-independent-fallback** flow.

```text
Visitor submits after consent
        |
        v
WordPress primary endpoint (Beget)
   | confirmed                         | not confirmed
   v                                   v
Lead + audit saved              Vercel fallback endpoint
   |                                   |
Thank You                       encrypted durable receipt in Upstash
   |                                   |
delivery logs                   Telegram fallback-lead message
                                       |
                                   Thank You
```

Monitoring is a separate path:

```text
WordPress form events + delivery logs
        |
privacy-safe alert queue
        |
background worker -> Telegram technical alert

Upstash QStash (outside Beget)
        |
health check every 5 minutes
        |
Telegram outage / recovery alert
```

This is preferred over the alternatives:

- **WordPress-only alerts** cannot operate during a Beget outage.
- **Always send to both systems** makes duplicates the normal case.
- **Make Vercel the only gateway** creates a new primary point of failure and unnecessarily changes the working path.

## 4. Shared submission identity and duplicate control

Every attempt uses the existing UUID v4 `submission_id`.

### 4.1 Browser rules

- A validated submission creates one immutable in-memory snapshot containing the contact, consent, form context, and bounded attribution.
- Retries without editing contact fields reuse the same snapshot and `submission_id`.
- Editing the name, phone, email, or message after a failed attempt creates a new `submission_id` before the next request.
- Contact data is never written to `localStorage`, `sessionStorage`, IndexedDB, cookies, analytics, console logs, or anonymous telemetry.

### 4.2 WordPress rules

- WordPress treats `submission_id` as the idempotency key.
- A named database lock serializes concurrent requests for the same valid ID.
- If an existing lead already has that ID, WordPress returns its positive `lead_id` without inserting or redispatching integrations.
- A request without a valid ID remains supported for backward compatibility and follows the existing insert path.

### 4.3 Vercel rules

- Upstash stores one receipt under `hybridautos-ae + submission_id` using an atomic create-if-absent operation.
- The receipt stores a payload hash, receipt ID, delivery state, timestamps, and encrypted contact only while delivery is pending or uncertain.
- A replay with the same ID and same payload hash returns the original receipt and does not send Telegram again.
- The same ID with a different payload hash returns HTTP `409 idempotency_conflict` and never overwrites the first contact.

## 5. Browser delivery behavior

The browser first sends the unchanged bounded payload to WordPress.

### 5.1 Primary success

Success requires all of the following:

- HTTP success;
- valid JSON;
- `ok === true`;
- positive integer `lead_id`.

On success, the fallback endpoint is not called. Analytics receives the existing `lead_success` event and the visitor is redirected to `/thank-you/`.

### 5.2 Primary failure eligible for fallback

The fallback is attempted only for:

- network failure;
- a 20-second timeout;
- HTTP `5xx`;
- both WordPress REST route variants being unavailable;
- empty, malformed, or unconfirmed success response.

The fallback is not attempted for:

- visitor validation errors;
- HTTP `400`, `401`, `403`, `409`, `422`, or `429`;
- honeypot detection;
- explicit consent rejection.

This prevents the backup from bypassing WordPress security and rate-limit decisions.

### 5.3 Fallback success

Vercel success requires:

- HTTP success;
- `ok === true`;
- matching `submission_id`;
- non-empty `receipt_id`;
- `stored === true`.

The contact is considered protected once the encrypted durable receipt exists, even if Telegram is temporarily unavailable. The browser emits `lead_fallback_success` without contact data and redirects to `/thank-you/`.

### 5.4 Both paths fail

If neither receiver confirms storage:

- the form stays filled;
- the button is enabled again;
- a visible retry message is shown;
- no conversion event is emitted;
- no Thank You redirect occurs.

## 6. Vercel fallback service

The independent service lives in a new private project and exposes:

- `POST /api/v1/fallback-leads` — receive and durably store a fallback lead;
- `GET /api/v1/receipts/:submission_id` — server-to-server status only;
- `GET /api/v1/health` — public service health without secrets or lead data;
- `POST /api/internal/health-check` — QStash-authenticated Beget check.

### 6.1 Request contract

The public lead request uses `application/x-www-form-urlencoded`, a maximum encoded body of 16 KiB, `credentials: omit`, and `referrerPolicy: no-referrer`.

Allowed fields are fixed:

- protocol version and `site_id=hybridautos-ae`;
- `submission_id` and fallback reason;
- `pd_consent=1` and privacy-policy version;
- bounded name, phone, email, message, model, form ID, brand, CTA key;
- bounded UTM values, Roistat visit, source path, and source label;
- empty honeypot field;
- short-lived signed intake token.

Unknown fields, oversized fields, missing consent, non-UAE phone values, a filled honeypot, invalid UUID, expired signature, or a disallowed origin are rejected.

### 6.2 Signed intake token

- WordPress creates a short-lived HMAC-SHA256 token with `site_id`, issue time, expiry, and random nonce.
- Token lifetime is 12 hours so a cached or already-open page can still use the fallback during a later Beget failure.
- A dedicated random signing secret is stored in `wp-config.php` and Vercel encrypted environment variables.
- WordPress authentication salts are never copied to Vercel.
- The token is public proof of a recently rendered site page, not a reusable server credential.
- Receipt-status requests use a second dedicated `LP_FALLBACK_STATUS_SECRET`. The browser never receives this secret.

### 6.3 Abuse protection

- CORS allows only `https://hybridautos.ae`.
- Vercel WAF rate-limits the fallback route by IP.
- Upstash enforces a second per-IP and per-submission limit.
- The endpoint validates the honeypot, consent, UUID, phone, exact allow-list, and sizes before durable storage.
- Request bodies and contacts are never written to Vercel application logs.

### 6.4 Contact encryption and retention

- Pending contact data is encrypted with AES-256-GCM before it is written to Upstash.
- The encryption key exists only in Vercel encrypted environment variables.
- After Telegram confirms delivery, encrypted contact data is deleted immediately; the non-personal receipt and payload hash remain for 30 days to prevent duplicates.
- If Telegram is unavailable or ambiguous, encrypted contact remains for at most 7 days for automatic or manual recovery, then is deleted.
- No contact is returned by the receipt-status endpoint.
- Manual recovery is available only through an audited operator CLI command inside the Vercel project. It accepts a receipt ID, loads and decrypts one pending payload in memory, prints it once to the authorized operator, and never writes the plaintext to a file or application log.

### 6.5 Telegram delivery

The fallback uses the existing HybridCars Telegram bot and chat. Tokens are copied into Vercel encrypted environment variables, never committed.

Message format:

```text
🛟 Резервная заявка

Имя: ...
Телефон: ...
Модель/сообщение: ...
Страница и CTA: ...
UTM: ...
Причина резерва: primary_timeout | primary_network | primary_5xx | primary_invalid_response
Попытка: <short submission id>
Квитанция: <receipt id>
```

A successful Telegram send requires HTTP 200, `ok=true`, and a positive `message_id`. A definite rate-limit response follows Telegram's `retry_after`; permanent `4xx` is not retried. An ambiguous timeout is stored as `unknown` and is not blindly resent, because Telegram may already have accepted it. The encrypted receipt remains recoverable for seven days.

## 7. WordPress monitoring

### 7.1 Privacy-safe alert queue

Add a per-site `landing_monitor_alerts` table containing:

- unique incident fingerprint;
- incident kind and severity;
- submission ID, lead ID, integration ID, adapter, safe status/category;
- occurrence count;
- first/last seen, due, locked, sent, resolved, and response timestamps;
- non-sensitive Telegram result identifiers.

The table must never contain names, phones, emails, messages, IP addresses, User-Agent values, webhook URLs, tokens, provider bodies, or raw database errors.

### 7.2 Missing-lead detector

A worker scans form-event groups after a five-minute grace period:

- `request_started` or `request_failed` with no WordPress lead and no external receipt creates one critical incident;
- `submit_attempt` with neither `request_started` nor `validation_failed` creates one lower-severity JavaScript-stall incident;
- a WordPress lead suppresses or resolves the incident;
- a confirmed external receipt resolves it as externally recovered and suppresses a duplicate missing-lead message;
- `form_started`, normal abandonment, `validation_failed`, consent rejection, and honeypot traffic do not create immediate alerts.

The external receipt check uses only the UUID and a server-to-server HMAC signature. It never sends contact data back to WordPress.

### 7.3 Integration failures

Each delivery result records the exact `integration_id`. Status `success` or Email `accepted` creates no incident. `unknown`, `retry_wait`, `failed_permanent`, adapter exception, or invalid adapter response creates or updates one fingerprint for `site + lead_id + integration_id`.

Monitoring never calls the normal lead Telegram adapter. It uses a separate non-recursive monitoring client with the same bot/chat credentials.

### 7.4 Internal Telegram messages

```text
🚨 Заявка не появилась
Попытка: <short submission id>
Страница/форма/CTA: ...
Последний шаг: request_started | request_failed | submit_attempt
Возраст: 5 minutes
Контакт: не передавался в технический журнал
```

```text
⚠️ Ошибка доставки заявки #<lead id>
Канал: Email | Telegram | Roistat
Статус: retry_wait | failed_permanent | unknown
Код ответа: <safe code or none>
```

Repeated observations increment the incident counter and do not create repeated Telegram messages. Parallel workers use atomic locks so only one may send an alert.

### 7.5 Worker scheduling

- Beget system cron calls WordPress cron once per minute.
- WordPress schedules the monitor scan and queue worker once per minute.
- Each run updates a privacy-safe heartbeat.
- A stale heartbeat makes the public health endpoint return a degraded status.
- Failure of the monitor or alert queue never changes a lead API response.

## 8. External Beget monitoring

Upstash QStash calls the Vercel health-check function every five minutes. The function checks:

- the public site responds;
- the WordPress lead namespace is reachable;
- the WordPress monitoring heartbeat is current;
- a lightweight database read succeeds through a dedicated no-PII health endpoint.

Two consecutive failures create one Telegram message:

```text
🔴 HybridAutos: приём заявок недоступен
Компонент: site | lead endpoint | database | monitor heartbeat
Первый сбой: ...
Проверок подряд: 2
```

The first subsequent fully healthy check creates one recovery message:

```text
✅ HybridAutos: приём заявок восстановлен
Компонент: ...
Длительность сбоя: ...
```

State and deduplication live in Upstash, so this monitor works while all of Beget is down.

## 8.1 Telegram-channel limitation

Telegram is the user-approved notification channel and therefore remains a notification dependency. If Telegram itself is unavailable, WordPress leads remain in WordPress and fallback leads remain encrypted in Upstash for up to seven days, but no chat message can appear until Telegram accepts it or an operator performs manual recovery. The system must report this state as `telegram_unknown` or `telegram_failed`; it must never claim chat delivery from storage success alone.

## 9. WordPress administration

Add a read-only Monitoring section that shows:

- monitor enabled state;
- last internal worker heartbeat;
- last external health result;
- counts of pending, sent, and resolved incidents;
- recent safe incidents;
- a safe test-alert button;
- whether the external fallback URL and signing secret are configured.

The page never displays full bot tokens, signing secrets, fallback encryption keys, or contact payloads.

## 9.1 Privacy and legal text

Before enabling the independent receiver, update the site Privacy Policy so it accurately describes Vercel and Upstash as technical processors used for short-lived encrypted backup storage and incident recovery. The text must state the seven-day maximum for an undelivered encrypted fallback contact and the immediate removal of fallback contact data after confirmed Telegram delivery. The consent checkbox continues to link to the same policy and remains mandatory before either receiver is called.

## 10. Files and repositories

### WordPress backend repository `landing_system`

- Modify `skills/wp-landing-config/mu-plugin/landing-config/includes/db.php`.
- Create `skills/wp-landing-config/mu-plugin/landing-config/includes/monitoring-alerts.php`.
- Create `skills/wp-landing-config/mu-plugin/landing-config/includes/rest-health.php`.
- Create `skills/wp-landing-config/mu-plugin/landing-config/includes/admin-monitoring.php`.
- Modify `skills/wp-landing-config/mu-plugin/landing-config/includes/rest-lead.php`.
- Modify `skills/wp-landing-config/mu-plugin/landing-config/includes/rest-form-events.php` only where monitoring hooks are required.
- Modify `skills/wp-landing-config/mu-plugin/landing-config/landing-config.php`.
- Add focused PHP tests and extend the existing test bootstrap.

### Website frontend repository `hybridautos-ae`

- Modify `08_КОД/wp-theme/assets/js/lead-form.js`.
- Modify `08_КОД/wp-theme/functions.php` to expose only public fallback configuration and a signed short-lived token.
- Extend `tests/node/urgent-lead-form.test.cjs`.
- Extend `tests/python/test_urgent_launch_contract.py`.
- Add a focused delivery-protocol test if the existing Node file becomes too broad.

### New private Vercel project

- Create a small TypeScript service with fallback, receipt, health, and scheduled-monitor handlers.
- Add unit and integration tests for validation, encryption, idempotency, Telegram, receipt checks, and health-state transitions.
- Configure Vercel environment variables, WAF, Upstash Redis, and QStash.
- Keep deployment metadata and non-secret configuration in Git; keep all credentials in encrypted service settings.

## 11. Test and release strategy

Implementation follows test-first development. Each behavior is first demonstrated by a failing automated test, then implemented minimally.

Required automated scenarios:

1. Primary success never calls Vercel.
2. Timeout, network error, `5xx`, or invalid response calls Vercel once.
3. Validation, protected `4xx`, and `429` never bypass WordPress.
4. Confirmed fallback receipt opens Thank You; unconfirmed fallback keeps the form.
5. Same fallback ID and body returns one receipt and one Telegram message.
6. Same ID with changed body returns `409`.
7. WordPress replay returns the original lead without redelivery.
8. Missing lead after five minutes creates one privacy-safe incident.
9. A WordPress lead or external receipt suppresses the missing-lead alert.
10. Integration failure creates one alert; success does not.
11. Alerting failure never blocks or changes a saved lead.
12. Two monitor workers cannot send the same message twice.
13. Two external health failures send one outage message; recovery sends one recovery message.
14. No monitoring table, application log, analytics event, or technical Telegram alert contains contact data or credentials.

Release order:

1. Back up production WordPress files and database and record hashes.
2. Confirm Vercel authentication and provision only free or already-included Upstash Redis/QStash resources.
3. Deploy and verify the Vercel service with every test message prefixed `[TEST — DO NOT CONTACT]`.
4. Deploy WordPress storage, monitoring, health, and idempotency without enabling browser fallback.
5. Configure Beget system cron and verify heartbeat and test alerts.
6. Update and verify the Privacy Policy before any fallback contact is accepted.
7. Deploy frontend fallback disabled, verify public configuration contains no secrets.
8. Enable fallback and run one labeled end-to-end primary-success test.
9. Simulate a WordPress failure against a controlled test route and verify exactly one fallback Telegram message and one receipt.
10. Verify all six advertising pages load the same current handler.
11. Verify rollback artifacts, Git tags, branch pushes, production hashes, and clean logs.

## 12. Acceptance criteria

The release is complete only when all of the following are demonstrated with fresh evidence:

- a normal production test creates one WordPress lead and no fallback receipt;
- a controlled primary failure creates one durable external receipt and one Telegram fallback message;
- replaying the same fallback does not create another Telegram message;
- a missing WordPress lead produces one technical alert after the grace period;
- an integration failure produces one safe alert without exposing the contact;
- a simulated Beget outage produces one external outage alert and one recovery alert;
- contacts remain absent from browser storage, analytics, anonymous form events, technical alert rows, and logs;
- current production files match the reviewed Git revisions;
- full backup and rollback instructions are verified before enabling the feature.
