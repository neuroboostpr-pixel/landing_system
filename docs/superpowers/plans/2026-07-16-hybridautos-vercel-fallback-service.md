# HybridAutos Vercel Fallback Service Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Build a private-source Vercel service that atomically stores a consented fallback contact outside Beget, reconciles it with WordPress before Telegram, exposes truthful privacy-safe status, and monitors outages without duplicates.

**Architecture:** The public handler validates a no-store WordPress token, binds its nonce to the first submission UUID in the same Upstash Lua transaction that stores a 30-day pseudonymous receipt and seven-day AES-GCM payload, then schedules a contact-free QStash delivery job after 45 seconds. The worker checks signed WordPress submission status before Telegram, uses a second check after 30 seconds when ambiguous, persists sending before Telegram, retries only HTTP 429, and uses a cleanup-only job after confirmed-send transition failure.

**Tech Stack:** Node.js 22.x, TypeScript 7.0.2, Vercel Functions, Vercel CLI 54.2.0, pnpm, Vitest 4.1.10, Zod 4.4.3, `node:crypto`, `@upstash/redis` 1.38.0, `@upstash/qstash` 2.11.1, Telegram Bot API, Upstash Redis/QStash Marketplace free plans.

## Global Constraints

- Repository: `neuroboostpr-pixel/hybridautos-lead-fallback`, visibility `PRIVATE`.
- Local root: `/Users/kirillbezikov/Documents/Сайт Дубай /hybridautos-lead-fallback`.
- Vercel project/alias: `hybridautos-lead-fallback` / `https://hybridautos-lead-fallback.vercel.app`.
- Use Vercel CLI exactly `54.2.0`. No command may use `vercel@latest` or an unpinned global CLI.
- Provision only `upstash/upstash-kv` with plan `free` and `autoUpgrade=false`, plus `upstash/upstash-qstash` with plan `free` and `prodPack=false`.
- Vercel Hobby is forbidden for commercial production. Require an existing Pro/Enterprise plan, effective DPA coverage, reviewed/disabled customer-data model-training use where applicable, and one included WAF rule for fallback POST. If any item is absent/ambiguous, stop with `COMMERCIAL_PLAN_GATE_BLOCKED` before provisioning; never create a charge without explicit user authorization.
- Deploy initially with `FALLBACK_ACCEPTING_ENABLED=false` and `FALLBACK_TEST_MODE=true`. Missing/invalid values fail configuration loading.
- Public POST returns 503 `service_disabled` while accepting is false. Public shallow health, signed receipt status, and QStash internal monitoring remain available.
- Non-production technical Telegram always uses hardcoded `[TEST — DO NOT CONTACT]`; production technical alerts use it when `FALLBACK_TEST_MODE=true`. Fallback-lead formatting never uses the current config prefix and derives TEST status only from immutable receipt `intake_mode`.
- Real acceptance is forbidden until policy is live, production is `accepting=true,test=false`, Vercel is redeployed/verified, and website fallback remains disabled; website enables last.
- `LP_FALLBACK_SIGNING_SECRET`, `LP_FALLBACK_STATUS_SECRET`, `LP_PAYLOAD_HASH_SECRET`, and `LP_RATE_LIMIT_SECRET` are four different `/^[0-9a-f]{64}$/` values decoded from hex before HMAC.
- `LP_ENCRYPTION_KEY_B64` decodes to exactly 32 bytes.
- Exact receipt ID is `rct_` plus 32 lowercase hex characters.
- Stable fingerprint excludes `intake_token` and `fallback_reason`; first reason is stored and never overwritten.
- The public handler accepts signed token `mode=test` only while `FALLBACK_TEST_MODE=true`, and accepts `mode=live` only while it is false. Any mismatch returns fixed HTTP 403 `token_mode_mismatch` before Redis, QStash, or Telegram.
- All receipt transitions use `SET ... KEEPTTL`. Receipt/fingerprint TTL is 2,592,000 seconds; ciphertext maximum TTL is 604,800 seconds; token-use TTL is 43,200 seconds.
- Public `delivery_state` is exactly `pending|delivered|unknown|expired`. `stored=true` only with terminal proof or currently existing ciphertext.
- The public fallback handler never calls Telegram; it stores then schedules QStash after 45 seconds.
- Every initial/check-2/definite-429/cleanup publication is recorded first in contact-free Redis due-work. An unconfirmed publication is recovered by the bounded deep-health sweep; it is never silently abandoned.
- Only Telegram HTTP 429 is automatically retried. 5xx, timeout, network, malformed response, invalid 200, and stale sending are `unknown` with no resend.
- Public `GET /api/v1/health` is shallow and never reads Redis or WordPress. Deep health is QStash-authenticated.
- QStash bodies contain operational IDs/check numbers only, never contact.
- Outbound signed WordPress fetches use `redirect:"error"`; a redirect is ambiguous and signed headers/contact are never forwarded.
- Manual recovery is interactive two-phase; view/crash/no confirmation retains ciphertext.
- Recovery audit has no contact, is exact-trimmed by stream ID age to at most 90 days on every append, is additionally capped at approximately 1,000 entries, and has a 90-day key expiry.
- Production database/config backups must be encrypted at creation, mode `0600`, and leave no plaintext SQL/config/env/token/decrypted-contact artifact.
- Commit `pnpm-lock.yaml`. Never commit credentials, contacts, provider bodies, `.env*`, or `.vercel`.

## File and Interface Map

All paths below are relative to the new service root.

- `package.json`, `pnpm-lock.yaml`, `tsconfig.json`, `vitest.config.ts`, `vercel.json`, `.gitignore` — pinned project and `typecheck`/test/build scripts.
- `src/config.ts` — exact flags, five cryptographic inputs, distinct-secret check, fixed recovery operator.
- `src/http/errors.ts`, `src/http/cors.ts` — stable no-contact errors and exact Origin policy.
- `src/contracts/fallback.ts` — strict 16 KiB form-urlencoded contract.
- `src/security/intake-token.ts` — exact WordPress `v1.iat.exp.nonce.mode.hmac` verification.
- `src/security/status-signature.ts` — signed WordPress/Vercel GET canonical protocol.
- `src/security/canonical-json.ts`, `src/security/fingerprint.ts`, `src/security/encryption.ts` — stable HMAC fingerprint and AES-GCM.
- `src/storage/types.ts`, `src/storage/upstash-receipts.ts`, `src/storage/rate-limit.ts` — atomic nonce/receipt create, KEEPTTL transitions, payload existence, locks, audit.
- `src/qstash/receiver.ts`, `src/qstash/scheduler.ts` — QStash authentication and contact-free delayed jobs.
- `src/wordpress/submission-status.ts` — signed reconciliation lookup.
- `src/telegram/message.ts`, `src/telegram/client.ts` — bounded message and exact outcome classification.
- `src/handlers/fallback-leads.ts` — store/schedule only.
- `src/handlers/fallback-delivery.ts` — reconciliation and Telegram state machine.
- `src/handlers/telegram-cleanup.ts` — cleanup-only, never sends.
- `src/handlers/receipt-status.ts` — truthful public state mapping.
- `src/handlers/public-health.ts` — shallow static readiness.
- `src/handlers/deep-health.ts`, `src/health/state-machine.ts` — authenticated external monitoring.
- `src/runtime.ts` — production dependency construction.
- `api/v1/fallback-leads.ts`, `api/v1/receipts/[submission_id].ts`, `api/v1/health.ts` — public entrypoints.
- `api/internal/fallback-delivery.ts`, `api/internal/telegram-cleanup.ts`, `api/internal/health-check.ts` — QStash-only entrypoints.
- `scripts/recover-receipt.ts`, `scripts/check-runtime-config.ts`, `scripts/smoke.ts` — operator/release controls.
- `tests/unit/*.test.ts`, `tests/integration/*.test.ts`, `tests/helpers/*.ts` — deterministic quality evidence.
- `docs/api-contract.md`, `docs/environment.md`, `docs/commercial-plan-gate.md`, `ops/backup-evidence.md`, `ops/release-evidence.md`, `ops/rollback.md` — auditable non-secret operations.

---

### Task 1: Commercial-plan gate, private repository, pinned skeleton, and fail-closed config

**Files:**
- Create: `package.json`
- Create: `pnpm-lock.yaml`
- Create: `tsconfig.json`
- Create: `vitest.config.ts`
- Create: `vercel.json`
- Create: `.gitignore`
- Create: `src/config.ts`
- Create: `tests/unit/config.test.ts`
- Create: `docs/commercial-plan-gate.md`
- Create: `docs/environment.md`

**Interfaces:**
- Consumes: authenticated Vercel account; production proceeds only on verified existing Pro/Enterprise.
- Produces: `loadConfig(env: NodeJS.ProcessEnv): AppConfig` and a private, pinned TypeScript service.

- [ ] **Step 1: Prove account/product/WAF availability without provisioning**

Run:

~~~bash
cd '/Users/kirillbezikov/Documents/Сайт Дубай '
pnpm dlx vercel@54.2.0 whoami
pnpm dlx vercel@54.2.0 teams list
pnpm dlx vercel@54.2.0 integration discover --format=json
pnpm dlx vercel@54.2.0 integration add upstash/upstash-kv --help
pnpm dlx vercel@54.2.0 integration add upstash/upstash-qstash --help
pnpm dlx vercel@54.2.0 firewall rules --help
~~~

Expected: authenticated existing Pro/Enterprise scope; effective DPA/data-use setting is recorded without secrets; discovery contains exact two product slugs; both help outputs offer Marketplace `free`; KV metadata supports `autoUpgrade=false`; QStash supports `prodPack=false`; Firewall confirms one included rule is available. If plan/DPA/data-use or any assertion is absent/ambiguous, stop before `gh repo create` or `integration add` and record `COMMERCIAL_PLAN_GATE_BLOCKED`. A Hobby result is an immediate stop.

- [ ] **Step 2: Create the private repository**

~~~bash
cd '/Users/kirillbezikov/Documents/Сайт Дубай '
gh repo create neuroboostpr-pixel/hybridautos-lead-fallback --private --clone --description 'Encrypted delayed fallback receiver for hybridautos.ae'
cd '/Users/kirillbezikov/Documents/Сайт Дубай /hybridautos-lead-fallback'
gh repo view --json nameWithOwner,visibility
~~~

Expected: `{"nameWithOwner":"neuroboostpr-pixel/hybridautos-lead-fallback","visibility":"PRIVATE"}`. If it already exists, clone and verify rather than create another.

- [ ] **Step 3: Write failing config tests**

Create `tests/unit/config.test.ts`:

~~~ts
import { describe, expect, it } from "vitest";
import { loadConfig } from "../../src/config.js";

const h = (c: string) => c.repeat(64);
const valid: NodeJS.ProcessEnv = {
  VERCEL_ENV: "preview",
  FALLBACK_ACCEPTING_ENABLED: "false",
  FALLBACK_TEST_MODE: "true",
  UPSTASH_REDIS_REST_URL: "https://example.upstash.io",
  UPSTASH_REDIS_REST_TOKEN: "r".repeat(32),
  QSTASH_TOKEN: "q".repeat(32),
  QSTASH_CURRENT_SIGNING_KEY: "c".repeat(32),
  QSTASH_NEXT_SIGNING_KEY: "n".repeat(32),
  LP_FALLBACK_SIGNING_SECRET: h("1"),
  LP_FALLBACK_STATUS_SECRET: h("2"),
  LP_PAYLOAD_HASH_SECRET: h("3"),
  LP_RATE_LIMIT_SECRET: h("4"),
  LP_ENCRYPTION_KEY_B64: Buffer.alloc(32, 5).toString("base64"),
  TELEGRAM_BOT_TOKEN: "123456:abcdefghijklmnopqrstuvwxyz",
  TELEGRAM_CHAT_ID: "-1001234567890",
  RECOVERY_OPERATOR_ID: "kirill-bezikov",
  LP_KEY_PREFIX: "ha:test:preview",
  PUBLIC_SERVICE_URL: "https://hybridautos-lead-fallback.vercel.app"
};

describe("loadConfig", () => {
  it("loads exact booleans and exposes only a technical preview prefix", () => {
    const value = loadConfig(valid);
    expect(value.acceptingEnabled).toBe(false);
    expect(value.testMode).toBe(true);
    expect(value.technicalMessagePrefix).toBe("[TEST — DO NOT CONTACT]\n");
    expect("messagePrefix" in value).toBe(false);
  });

  it.each(["", "TRUE", "1", "yes"])("rejects invalid flag %s", (flag) => {
    expect(() => loadConfig({ ...valid, FALLBACK_ACCEPTING_ENABLED: flag }))
      .toThrow();
  });

  it("rejects equal HMAC keys", () => {
    expect(() => loadConfig({
      ...valid,
      LP_PAYLOAD_HASH_SECRET: valid.LP_FALLBACK_SIGNING_SECRET
    })).toThrow("distinct");
  });

  it("rejects non-hex and a 31-byte encryption key", () => {
    expect(() => loadConfig({ ...valid, LP_RATE_LIMIT_SECRET: "z".repeat(64) }))
      .toThrow();
    expect(() => loadConfig({
      ...valid,
      LP_ENCRYPTION_KEY_B64: Buffer.alloc(31).toString("base64")
    })).toThrow();
  });
});
~~~

- [ ] **Step 4: Verify red**

Run: `pnpm test -- tests/unit/config.test.ts`
Expected: FAIL with missing `src/config.ts`.

- [ ] **Step 5: Create pinned manifests and config**

Create `package.json`:

~~~json
{
  "name": "hybridautos-lead-fallback",
  "version": "1.0.0",
  "private": true,
  "type": "module",
  "engines": { "node": "22.x" },
  "scripts": {
    "typecheck": "tsc --noEmit",
    "build": "pnpm typecheck",
    "test": "vitest run",
    "test:unit": "vitest run tests/unit",
    "test:integration": "RUN_UPSTASH_INTEGRATION=1 vitest run tests/integration",
    "recover": "tsx scripts/recover-receipt.ts",
    "check:config": "tsx scripts/check-runtime-config.ts",
    "smoke": "tsx scripts/smoke.ts"
  }
}
~~~

Install exact dependencies:

~~~bash
corepack enable
pnpm add --save-exact @upstash/qstash@2.11.1 @upstash/redis@1.38.0 zod@4.4.3
pnpm add --save-dev --save-exact @types/node@22.20.1 tsx@4.23.1 typescript@7.0.2 vitest@4.1.10
~~~

Use strict NodeNext TypeScript, Vitest Node environment, Vercel region `fra1`/30-second functions, and ignore `.env*`/`.vercel`/logs/coverage/private evidence.

`src/config.ts` must:

~~~ts
const HEX_32 = /^[0-9a-f]{64}$/;
const BOOL = z.enum(["true", "false"]);
const APPROVED_RECOVERY_OPERATORS = new Set(["kirill-bezikov"]);

const decoded = [
  raw.LP_FALLBACK_SIGNING_SECRET,
  raw.LP_FALLBACK_STATUS_SECRET,
  raw.LP_PAYLOAD_HASH_SECRET,
  raw.LP_RATE_LIMIT_SECRET
];
if (decoded.some((value) => !HEX_32.test(value))) {
  throw new Error("HMAC keys must be 64 lowercase hex characters");
}
if (new Set(decoded).size !== decoded.length) {
  throw new Error("HMAC keys must be distinct");
}
if (!APPROVED_RECOVERY_OPERATORS.has(raw.RECOVERY_OPERATOR_ID)) {
  throw new Error("RECOVERY_OPERATOR_ID is not allowlisted");
}
~~~

Decode all HMAC keys with `Buffer.from(value, "hex")`, not UTF-8. Parse booleans only after Zod exact validation. `technicalMessagePrefix` is hardcoded when non-production or service test mode and is used only by technical/outage messages; no generic/fallback `messagePrefix` exists. Fallback workers read receipt `intake_mode`.

- [ ] **Step 6: Run and commit**

~~~bash
pnpm test -- tests/unit/config.test.ts
pnpm typecheck
pnpm build
git diff --check
git add package.json pnpm-lock.yaml tsconfig.json vitest.config.ts vercel.json .gitignore src/config.ts tests/unit/config.test.ts docs/commercial-plan-gate.md docs/environment.md
git commit -m "chore: bootstrap secure fallback service"
~~~

Expected: tests/typecheck/build PASS; no whitespace errors; no secret values in docs.

---

### Task 2: Strict fallback contract, CORS, flags, and exact no-store token verification

**Files:**
- Create: `src/http/errors.ts`
- Create: `src/http/cors.ts`
- Create: `src/contracts/fallback.ts`
- Create: `src/security/intake-token.ts`
- Create: `tests/unit/fallback-contract.test.ts`
- Create: `tests/unit/intake-token.test.ts`
- Create: `docs/api-contract.md`

**Interfaces:**
- Consumes: public `Request` and WordPress token.
- Produces: `parseFallbackRequest(request): Promise<FallbackPayload>` and `verifyIntakeToken(token,key,now): IntakeClaims`.

- [ ] **Step 1: Write failing tests**

Cover:

- exact Origin `https://hybridautos.ae`;
- forged/missing Origin rejected;
- form-urlencoded only and 16,384-byte maximum;
- duplicate/unknown fields rejected;
- phone-only UAE lead accepted; name optional;
- consent/honeypot/UUID/phone/field limits;
- field character limits count Unicode code points, not JavaScript UTF-16 code units: 191 emoji is accepted for a 191-character field, direct 192 is rejected, no surrogate pair is split, and the browser's 192-emoji value truncates to the same accepted 191-code-point prefix;
- an end-to-end oversized Unicode message/UTM/click payload stays <=16,384 URL-encoded bytes and preserves phone, consent, UUID, token, and first fallback reason;
- exact error contract reserves HTTP 503 `service_disabled`; Task 5 proves the handler returns it before body/token/storage;
- exact token `v1.iat.exp.nonce.mode.64hex`;
- HMAC canonical bytes `v1\nhybridautos-ae\niat\nexp\nnonce\nmode`;
- `exp=iat+43200`, 300-second future skew, exact nonce, `live|test`;
- forged/expired/cached-old token rejected.
- the shared WordPress/Vercel known vector proves that the 64-hex key is decoded to 32 bytes before HMAC;

Fixture:

~~~ts
const validFields = {
  protocol_version: "1",
  site_id: "hybridautos-ae",
  submission_id: "d9428888-122b-4b3e-a105-4d4f0a13262f",
  fallback_reason: "primary_timeout",
  pd_consent: "1",
  privacy_policy_version: "2026-07-16",
  intake_token: "v1.1789000000.1789043200.0123456789abcdef0123456789abcdef.live." +
    "a".repeat(64),
  name: "",
  phone: "+971 50 123 4567",
  email: "",
  message: "Model: ROX 01",
  model: "ROX 01",
  form_id: "rox-test-drive",
  brand: "ROX",
  cta_key: "request-test-drive",
  cta_label: "Request a test drive",
  cta_placement: "modal",
  source_path: "/rox/",
  source_label: "Request a test drive",
  utm_source: "google",
  utm_medium: "cpc",
  utm_campaign: "rox-search",
  utm_term: "",
  utm_content: "",
  roistat_visit: "",
  gclid: "",
  gbraid: "",
  wbraid: "",
  yclid: "",
  fbclid: "",
  msclkid: "",
  website: ""
};
~~~

- [ ] **Step 2: Verify red**

Run: `pnpm test -- tests/unit/fallback-contract.test.ts tests/unit/intake-token.test.ts`
Expected: FAIL because contract/security modules do not exist.

- [ ] **Step 3: Implement exact schema and token verifier**

Allowed reasons:

~~~ts
export const FALLBACK_REASONS = [
  "primary_timeout",
  "primary_network",
  "primary_5xx",
  "primary_invalid_response"
] as const;
~~~

Limits: name/form/model/brand/CTA/UTM/source-label 191; phone 64; email 191; message 4096; source path 1024; Roistat 64; click IDs 512. Implement one `unicodeCodePointLength(value)` helper (for example, iteration by Unicode scalar/code point) and Zod custom refinements using it; do not use JavaScript `.length` for these character limits. The encoded request limit remains raw bytes before parsing. Canonical UAE phone is `^\+971[0-9]{9}$` after removing spaces, parentheses, and hyphens.

Token verifier:

~~~ts
const parts = token.split(".");
if (parts.length !== 6 || parts[0] !== "v1") invalid();
const [version, iatRaw, expRaw, nonce, mode, signature] = parts;
const iat = Number(iatRaw);
const exp = Number(expRaw);
if (!Number.isInteger(iat) || !Number.isInteger(exp) || exp !== iat + 43_200) invalid();
if (!/^[0-9a-f]{32}$/.test(nonce) || !/^(live|test)$/.test(mode)) invalid();
if (now < iat - 300 || now > exp || !/^[0-9a-f]{64}$/.test(signature)) invalid();
const canonical = [
  version, "hybridautos-ae", String(iat), String(exp), nonce, mode
].join("\n");
const expected = createHmac("sha256", signingKey).update(canonical, "utf8").digest();
const actual = Buffer.from(signature, "hex");
if (actual.length !== expected.length || !timingSafeEqual(actual, expected)) invalid();
return { iat, exp, nonce, mode: mode as "live" | "test" };
~~~

Every success/error/fallback response uses `Cache-Control:no-store`. CORS never uses wildcard. Document the exact WP token endpoint contract: public live mode is server-controlled; admin test mode has no query flag and requires `GET`, `Accept: application/json`, `credentials: same-origin`, authenticated `manage_options`, and `X-WP-Nonce` verified for `wp_rest`; a public/non-admin/invalid-nonce request while WP test mode is active returns 404. `forcePrimaryFailure` remains browser-local and is forbidden as an unknown Vercel POST field; Vercel derives test mode only from a valid signed token claim. Require `Cache-Control:no-store, private, max-age=0`, `Pragma:no-cache`, `Expires:0`, and no cached HTML token.

- [ ] **Step 4: Run and commit**

~~~bash
pnpm test -- tests/unit/fallback-contract.test.ts tests/unit/intake-token.test.ts
pnpm typecheck
git add src/http src/contracts src/security/intake-token.ts tests/unit/fallback-contract.test.ts tests/unit/intake-token.test.ts docs/api-contract.md
git commit -m "feat: validate signed fallback intake"
~~~

Expected: forged Origin/token/cache/reuse fixtures reject without contact echo.

---

### Task 3: Stable HMAC fingerprint and AES-256-GCM envelope

**Files:**
- Create: `src/security/canonical-json.ts`
- Create: `src/security/fingerprint.ts`
- Create: `src/security/encryption.ts`
- Create: `tests/unit/fingerprint.test.ts`
- Create: `tests/unit/encryption.test.ts`

**Interfaces:**
- Consumes: normalized `FallbackPayload`, decoded payload-hash key, decoded encryption key.
- Produces: `payloadFingerprint(payload,key): string`, `encryptContact`, and `decryptContact`.

- [ ] **Step 1: Write failing tests**

Assert:

- output is exactly 64 lowercase hex;
- reordering keys is stable;
- changing contact/attribution changes fingerprint;
- changing only `intake_token` or `fallback_reason` does not;
- two encryptions use different 12-byte IVs;
- AAD binds `site:submission:receipt`;
- modified ciphertext/tag/receipt/submission fails authentication;
- plaintext/encryption errors never enter logger.

- [ ] **Step 2: Verify red**

Run: `pnpm test -- tests/unit/fingerprint.test.ts tests/unit/encryption.test.ts`
Expected: missing-module FAIL.

- [ ] **Step 3: Implement**

~~~ts
export function payloadFingerprint(
  payload: FallbackPayload,
  key: Buffer
): string {
  const { intake_token: _token, fallback_reason: _reason, ...stable } = payload;
  return createHmac("sha256", key)
    .update(canonicalJson(stable), "utf8")
    .digest("hex");
}
~~~

Encrypt all recoverable normalized fields except token/honeypot using AES-256-GCM, random 12-byte IV, 16-byte tag, and AAD:

~~~ts
Buffer.from(
  "hybridautos-ae:" + payload.submission_id + ":" + receiptId,
  "utf8"
)
~~~

`receiptId` must match `/^rct_[0-9a-f]{32}$/` before encryption.

- [ ] **Step 4: Run and commit**

~~~bash
pnpm test -- tests/unit/fingerprint.test.ts tests/unit/encryption.test.ts
pnpm typecheck
git add src/security/canonical-json.ts src/security/fingerprint.ts src/security/encryption.ts tests/unit/fingerprint.test.ts tests/unit/encryption.test.ts
git commit -m "feat: fingerprint and encrypt fallback payloads"
~~~

---

### Task 4: Atomic nonce binding, receipt creation, truthful status, KEEPTTL, and rate limits

**Files:**
- Create: `src/storage/types.ts`
- Create: `src/storage/upstash-receipts.ts`
- Create: `src/storage/rate-limit.ts`
- Create: `src/scheduling/due-work.ts`
- Create: `tests/helpers/memory-receipts.ts`
- Create: `tests/unit/receipt-store.test.ts`
- Create: `tests/unit/public-state.test.ts`
- Create: `tests/unit/rate-limit.test.ts`
- Create: `tests/unit/due-work.test.ts`
- Create: `tests/integration/upstash-store.test.ts`

**Interfaces:**
- Consumes: token nonce, signed intake mode, submission ID, receipt ID, fingerprint, frozen reason, encrypted envelope.
- Produces: `ReceiptStore.createAtomic`, `transitionKeepTtl`, atomic `transitionAndRegisterDueWork`, guarded due removal, `markTerminalAndDeletePayload`, `publicStatus`, `payloadExists`, locks, and rate limits.

- [ ] **Step 1: Write failing storage tests**

Cover:

1. atomic first create binds nonce and creates receipt/index/payload plus initial reconcile due metadata/ZSET member in the same Lua operation;
2. same nonce/same UUID/same fingerprint/same signed mode replays original receipt;
3. same nonce/different UUID returns `token_reuse` and writes nothing;
4. same UUID/different fingerprint returns `conflict`;
5. same payload/different reason replays and keeps first reason;
6. receipt ID exact;
7. receipt/index TTL 30 days; payload 7 days; token-use 12 hours;
8. every state transition preserves existing TTL;
9. terminal transition atomically KEEPTTL-updates receipt and deletes payload;
10. pending+payload => pending/stored true;
11. Telegram ambiguity+payload => unknown/stored true;
12. terminal proof => delivered/stored true without payload;
13. missing payload without proof => expired/stored false;
14. same UUID/fingerprint but different signed mode returns exact `mode_conflict` without rewriting or reusing the receipt;
15. a simulated crash immediately after `createAtomic` but before QStash publication still leaves discoverable initial due work;
16. every later state-to-job transition atomically KEEPTTL-updates state and registers due metadata/member before publish;
17. raw IP never stored; 11th IP/minute and 21st UUID/12h rejected.

- [ ] **Step 2: Verify red**

Run: `pnpm test -- tests/unit/receipt-store.test.ts tests/unit/public-state.test.ts tests/unit/rate-limit.test.ts`
Expected: storage modules missing.

- [ ] **Step 3: Define types**

~~~ts
export type InternalState =
  | "pending" | "schedule_unknown"
  | "reconcile_wait" | "reconcile_retry_wait" | "primary_confirmed"
  | "telegram_sending" | "telegram_rate_wait" | "telegram_sent"
  | "cleanup_pending" | "schedule_failed"
  | "telegram_unknown" | "telegram_failed_permanent"
  | "manual_recovered";

export type PublicDeliveryState = "pending" | "delivered" | "unknown" | "expired";

export interface ReceiptRecord {
  v: 1;
  site_id: "hybridautos-ae";
  submission_id: string;
  receipt_id: string;
  payload_fingerprint: string;
  intake_mode: "live" | "test";
  first_fallback_reason: FallbackReason;
  internal_state: InternalState;
  created_at: number;
  updated_at: number;
  telegram_attempts: number;
  telegram_attempt_id: string | null;
  telegram_message_id: number | null;
  manual_recovered_at: number | null;
}
~~~

- [ ] **Step 4: Implement the one atomic create Lua script**

~~~lua
#!lua flags=allow-key-locking
local bound = redis.call("GET", KEYS[4])
if bound and bound ~= ARGV[3] then
  return {-1, ""}
end
local current = redis.call("GET", KEYS[1])
if current then
  if not bound then
    redis.call("SET", KEYS[4], ARGV[3], "EX", 43200)
  end
  return {0, current}
end
if not bound then
  redis.call("SET", KEYS[4], ARGV[3], "EX", 43200)
end
redis.call("SET", KEYS[1], ARGV[1], "EX", 2592000)
redis.call("SET", KEYS[2], ARGV[2], "EX", 604800)
redis.call("SET", KEYS[3], ARGV[3], "EX", 2592000)
redis.call("SET", KEYS[5], ARGV[4], "EX", 2592000)
redis.call("ZADD", KEYS[6], ARGV[5], ARGV[6])
return {1, ARGV[1]}
~~~

Keys are receipt, payload, receipt-ID index, token-use, initial due metadata, and due-work ZSET. Args are receipt JSON, encrypted envelope JSON, submission UUID, contact-free initial reconcile metadata JSON, due Unix score, and receipt ID. Result `-1` token reuse, `0` existing receipt, `1` created. On existing receipt compare both fingerprint and immutable `intake_mode`: same fingerprint/mode is replay, changed mode is exact `mode_conflict`, changed fingerprint is `idempotency_conflict`. Never update first reason or mode.

All updates:

~~~lua
local current = redis.call("GET", KEYS[1])
if not current then return 0 end
redis.call("SET", KEYS[1], ARGV[1], "KEEPTTL")
return 1
~~~

Terminal transition adds `DEL KEYS[2]` in the same script. A separate atomic transition-and-job Lua KEEPTTL-updates the receipt, reads its remaining `PTTL`, requires it to be positive, SETs contact-free due metadata with that exact `PX` TTL (never `KEEPTTL` on a newly recreated due key), and ZADDs its member before every later QStash publication. Confirmed publication uses a guarded Lua removal that deletes only the matching due metadata/version and ZREM member.

Public mapping checks current payload existence; a receipt alone cannot claim recoverability.

- [ ] **Step 5: Run unit/live integration controls**

~~~bash
pnpm test -- tests/unit/receipt-store.test.ts tests/unit/public-state.test.ts tests/unit/rate-limit.test.ts tests/unit/due-work.test.ts
pnpm typecheck
pnpm dlx vercel@54.2.0 env run -e preview -- pnpm test:integration
~~~

Expected: unit and scoped random-prefix Upstash tests PASS; TTL remains within original bounds after each transition and expiry simulation.

- [ ] **Step 6: Commit**

~~~bash
git add src/storage src/scheduling/due-work.ts tests/helpers/memory-receipts.ts tests/unit/receipt-store.test.ts tests/unit/public-state.test.ts tests/unit/rate-limit.test.ts tests/unit/due-work.test.ts tests/integration/upstash-store.test.ts
git commit -m "feat: atomically bind and store fallback receipts"
~~~

---

### Task 5: QStash authentication/scheduling and public store-then-schedule handler

**Files:**
- Create: `src/qstash/receiver.ts`
- Create: `src/qstash/scheduler.ts`
- Modify: `src/scheduling/due-work.ts`
- Create: `src/handlers/fallback-leads.ts`
- Create: `src/runtime.ts`
- Create: `api/v1/fallback-leads.ts`
- Create: `tests/unit/qstash.test.ts`
- Modify: `tests/unit/due-work.test.ts`
- Create: `tests/unit/fallback-handler.test.ts`

**Interfaces:**
- Consumes: Tasks 1–4.
- Produces: `scheduleInitialDelivery(receiptId): Promise<void>`, durable contact-free due-work registration, and `POST /api/v1/fallback-leads`.

- [ ] **Step 1: Write failing handler tests**

Assert:

- disabled => 503 `service_disabled` before parsing/storage;
- forged Origin/token => no storage/schedule;
- created => 201, pending/stored true, one QStash schedule after 45s, zero Telegram calls;
- replay => 200 original receipt, no second schedule;
- token reuse/conflict => 409 stable code;
- storage failure => 503;
- schedule failure after storage => still 201/stored true, internal `schedule_unknown`, recoverable payload;
- created response has exactly six keys `{ok,site_id,submission_id,receipt_id,stored,delivery_state}` with exact site/UUID/receipt, `stored:true`, and `delivery_state:"pending"`; replay has the same exact response shape and original receipt;
- response contains no fingerprint/internal state/contact or seventh key;
- signed token mode/config mismatch => fixed 403 `token_mode_mismatch`, zero Redis/QStash/Telegram access;
- before every schedule call, a contact-free due item exists with action/check/due/attempt; confirmed publication removes it, while failure keeps it for recovery;
- QStash body is exactly contact-free:

~~~json
{"v":1,"receipt_id":"rct_d9428888122b4b3ea1054d4f0a13262f","action":"reconcile","check":1}
~~~

- [ ] **Step 2: Verify red**

Run: `pnpm test -- tests/unit/qstash.test.ts tests/unit/due-work.test.ts tests/unit/fallback-handler.test.ts`
Expected: FAIL missing modules.

- [ ] **Step 3: Implement scheduling and orchestration**

~~~ts
await qstash.publishJSON({
  url: config.publicServiceUrl + "/api/internal/fallback-delivery",
  body: { v: 1, receipt_id: receipt.receipt_id, action: "reconcile", check: 1 },
  delay: "45s",
  retries: 0,
  contentBasedDeduplication: true
});
~~~

Handler order: OPTIONS/CORS → method → accepting flag → parse/token → require `claims.mode === (config.testMode ? "test" : "live")` → rate limit → fingerprint → exact receipt ID → encrypt → atomic create/token-bind → replay/conflict decision → schedule once only for created → pending success. Mode mismatch is rejected before the first storage/provider access.

The initial due record/member already exists atomically when `createAtomic` returns; do not create it in a later crash-prone step. Publish QStash, then guarded-remove only the matching due version after confirmed publication. Failure KEEPTTL-marks `schedule_unknown` and leaves due work for Task 10's bounded recovery sweep. Never call/decrypt for Telegram here. After atomic storage, schedule failure or process death cannot turn recoverable contact into browser failure or make it undiscoverable.

- [ ] **Step 4: Add thin entrypoint and run**

~~~ts
import { handleFallbackLead } from "../../src/handlers/fallback-leads.js";
import { runtimeDependencies } from "../../src/runtime.js";

export default {
  fetch(request: Request): Promise<Response> {
    return handleFallbackLead(request, runtimeDependencies());
  }
};
~~~

~~~bash
pnpm test -- tests/unit/qstash.test.ts tests/unit/due-work.test.ts tests/unit/fallback-handler.test.ts
pnpm typecheck
git add src/qstash src/scheduling/due-work.ts src/handlers/fallback-leads.ts src/runtime.ts api/v1/fallback-leads.ts tests/unit/qstash.test.ts tests/unit/due-work.test.ts tests/unit/fallback-handler.test.ts
git commit -m "feat: store and schedule fallback receipts"
~~~

---

### Task 6: Signed WordPress reconciliation and delayed delivery worker

**Files:**
- Create: `src/security/status-signature.ts`
- Create: `src/wordpress/submission-status.ts`
- Create: `src/handlers/fallback-delivery.ts`
- Create: `api/internal/fallback-delivery.ts`
- Create: `tests/unit/status-signature.test.ts`
- Create: `tests/unit/submission-status.test.ts`
- Create: `tests/unit/fallback-delivery.test.ts`

**Interfaces:**
- Consumes: QStash delivery body, signed WP route, receipt/payload/locks.
- Produces: `checkWordPressSubmission(uuid): Promise<"exists"|"missing"|"ambiguous">` and QStash-only delivery worker.

- [ ] **Step 1: Write failing reconciliation tests**

Cover:

- QStash signature required;
- request path exact `/wp-json/landing/v1/submission-status/{uuid}`;
- HMAC canonical `GET\n/path\ntimestamp\nhybridautos-ae`;
- valid `exists=true|false` only;
- redirect/timeout/network/5xx/invalid JSON/mismatched UUID/stale response => ambiguous, and no redirect is followed;
- exists true => KEEPTTL `primary_confirmed` + payload delete + no Telegram;
- missing => enter Telegram flow;
- check 1 ambiguous => exactly one +30s check 2, no Telegram;
- check 2 ambiguous => enter Telegram flow;
- duplicate workers/terminal/payload-expired => no duplicate send;
- locks release only by owner.

- [ ] **Step 2: Verify red**

Run: `pnpm test -- tests/unit/status-signature.test.ts tests/unit/submission-status.test.ts tests/unit/fallback-delivery.test.ts`
Expected: FAIL missing reconciliation modules.

- [ ] **Step 3: Implement signed check**

Headers:

~~~ts
{
  "X-LP-Site-Id": "hybridautos-ae",
  "X-LP-Timestamp": String(timestamp),
  "X-LP-Signature": signStatusRequest(path, timestamp, statusKey)
}
~~~

Response exact:

~~~ts
z.strictObject({
  ok: z.literal(true),
  site_id: z.literal("hybridautos-ae"),
  submission_id: uuidV4Schema,
  exists: z.boolean()
})
~~~

Use 8-second abort and `redirect:"error"`. A valid non-redirect HTTP response with `exists=false` is the only explicit missing signal.

- [ ] **Step 4: Implement state decisions**

The endpoint parses a strict discriminated union with no unknown keys:

~~~ts
type DeliveryJob =
  | { v: 1; receipt_id: ReceiptId; action: "reconcile"; check: 1 | 2 }
  | { v: 1; receipt_id: ReceiptId; action: "telegram_rate_retry"; attempt: 2 | 3 };
~~~

This task implements the `reconcile` branch; Task 7 implements the already-declared `telegram_rate_retry` branch. Acquire the receipt lock before state/load. Check payload existence before contact work.

For check-1 ambiguity:

~~~ts
await store.transitionKeepTtl(receiptId, "reconcile_retry_wait");
await scheduler.scheduleReconcile(receiptId, 2, 30);
~~~

The shared scheduler first persists check-2 due work; a failed/ambiguous publish leaves that same state and due entry for Task 10. It never falls through to Telegram merely because scheduling failed.

For check-2 ambiguity call the same Telegram path as explicit missing to favor recovery. For exists=true use one atomic terminal/delete transition.

- [ ] **Step 5: Run and commit**

~~~bash
pnpm test -- tests/unit/status-signature.test.ts tests/unit/submission-status.test.ts tests/unit/fallback-delivery.test.ts
pnpm typecheck
git add src/security/status-signature.ts src/wordpress src/handlers/fallback-delivery.ts api/internal/fallback-delivery.ts tests/unit/status-signature.test.ts tests/unit/submission-status.test.ts tests/unit/fallback-delivery.test.ts
git commit -m "feat: reconcile fallback receipts with WordPress"
~~~

---

### Task 7: Telegram pre-send state, 429-only retry, and cleanup-only repair

**Files:**
- Create: `src/telegram/message.ts`
- Create: `src/telegram/client.ts`
- Create: `src/handlers/telegram-cleanup.ts`
- Create: `api/internal/telegram-cleanup.ts`
- Create: `tests/unit/telegram.test.ts`
- Create: `tests/unit/telegram-state.test.ts`
- Create: `tests/unit/telegram-cleanup.test.ts`

**Interfaces:**
- Consumes: decrypted payload only inside locked delivery worker.
- Produces: `TelegramOutcome`, `sendTelegramOnce`, and cleanup-only internal endpoint.

- [ ] **Step 1: Write failing tests**

Assert:

- message escaping/4096 limit and mandatory phone/reason/receipt;
- preview always test-prefixed;
- production prefix iff the immutable receipt `intake_mode` is `test`, independent of the deployment's current flag;
- create a test receipt, flip effective config to live, run its delayed worker, and still require `[TEST — DO NOT CONTACT]`;
- `telegram_sending` with unique attempt ID is persisted before fetch;
- positive Telegram HTTP 200/`ok=true`/`message_id>0` is sent;
- only 429 yields retry with clamped `retry_after` and maximum 3 attempts;
- other 4xx permanent/no retry;
- 5xx/timeout/network/malformed/invalid 200 => unknown/no retry;
- stale `telegram_sending` => unknown/no resend;
- confirmed-send transition success KEEPTTL-updates + deletes payload atomically;
- transition failure schedules cleanup body with receipt/message/attempt only;
- cleanup validates attempt/message, marks/deletes, and never calls Telegram.
- definite-429 and cleanup publications both persist their contact-free due-work metadata before QStash; failed publication leaves `telegram_rate_wait` or `cleanup_pending` for Task 10 and never retries an ambiguous Telegram send.

- [ ] **Step 2: Verify red**

Run: `pnpm test -- tests/unit/telegram.test.ts tests/unit/telegram-state.test.ts tests/unit/telegram-cleanup.test.ts`
Expected: FAIL missing Telegram modules.

- [ ] **Step 3: Implement exact outcome**

~~~ts
export type TelegramOutcome =
  | { state: "sent"; messageId: number }
  | { state: "rate_limited"; retryAfterSeconds: number }
  | { state: "failed_permanent"; safeCode: number }
  | { state: "unknown"; safeCode: number | null };
~~~

No 5xx retry branch exists. Before fetch:

~~~ts
const attemptId = randomUUID();
await store.markSendingKeepTtl(receiptId, attemptId);
const outcome = await telegram.send(message);
~~~

429 schedule body:

~~~json
{"v":1,"receipt_id":"rct_d9428888122b4b3ea1054d4f0a13262f","action":"telegram_rate_retry","attempt":2}
~~~

Cleanup body:

~~~json
{"v":1,"receipt_id":"rct_d9428888122b4b3ea1054d4f0a13262f","attempt_id":"3f34d090-52ab-4f03-ae1a-c17613f365bf","message_id":12345}
~~~

Cleanup never imports/injects Telegram client.

- [ ] **Step 4: Run and commit**

~~~bash
pnpm test -- tests/unit/telegram.test.ts tests/unit/telegram-state.test.ts tests/unit/telegram-cleanup.test.ts
pnpm typecheck
git add src/telegram src/handlers/telegram-cleanup.ts api/internal/telegram-cleanup.ts tests/unit/telegram.test.ts tests/unit/telegram-state.test.ts tests/unit/telegram-cleanup.test.ts
git commit -m "feat: deliver Telegram without ambiguous resend"
~~~

---

### Task 8: Signed truthful receipt status and shallow public health

**Files:**
- Create: `src/handlers/receipt-status.ts`
- Create: `src/handlers/public-health.ts`
- Create: `api/v1/receipts/[submission_id].ts`
- Create: `api/v1/health.ts`
- Create: `tests/unit/receipt-status.test.ts`
- Create: `tests/unit/public-health.test.ts`

**Interfaces:**
- Consumes: signed server request and current receipt/payload existence.
- Produces: exact safe receipt response and Redis-free health.

- [ ] **Step 1: Write failing tests**

Status tests cover missing/stale HMAC, unknown UUID, all internal-state mappings, payload expiry after each transition, and exact response keys:

~~~json
{
  "ok": true,
  "submission_id": "d9428888-122b-4b3e-a105-4d4f0a13262f",
  "exists": true,
  "stored": true,
  "delivery_state": "pending"
}
~~~

Health test injects a Redis client whose methods throw if touched and expects:

~~~json
{"ok":true,"status":"ready","site_id":"hybridautos-ae"}
~~~

- [ ] **Step 2: Verify red**

Run: `pnpm test -- tests/unit/receipt-status.test.ts tests/unit/public-health.test.ts`
Expected: missing handler FAIL.

- [ ] **Step 3: Implement**

Receipt endpoint has no CORS and always `Cache-Control:no-store`. Map:

- terminal proof → delivered/true;
- ambiguous+payload → unknown/true;
- other recoverable payload → pending/true;
- no payload/no proof → expired/false;
- no receipt → exists false/stored false/expired.

Public health is a constant response and receives no Redis/WordPress dependency.

- [ ] **Step 4: Run and commit**

~~~bash
pnpm test -- tests/unit/receipt-status.test.ts tests/unit/public-health.test.ts
pnpm typecheck
git add src/handlers/receipt-status.ts src/handlers/public-health.ts api/v1/receipts api/v1/health.ts tests/unit/receipt-status.test.ts tests/unit/public-health.test.ts
git commit -m "feat: expose truthful fallback status"
~~~

---

### Task 9: Two-phase manual recovery and bounded audit

**Files:**
- Create: `scripts/recover-receipt.ts`
- Create: `tests/unit/manual-recovery.test.ts`
- Create: `tests/unit/recovery-audit.test.ts`
- Create: `tests/unit/no-pii-output.test.ts`

**Interfaces:**
- Consumes: fixed `RECOVERY_OPERATOR_ID=kirill-bezikov` and interactive TTY.
- Produces: `list` safe IDs and `view --receipt-id` two-phase recovery.

- [ ] **Step 1: Write failing tests**

Cover:

- `list` prints only receipt ID/public state/age;
- operator not exact allow-list rejected;
- non-TTY rejected;
- `view` appends `view_started` before printing;
- EOF/crash/timeout/wrong confirmation keeps ciphertext/state;
- exact `DELETE rct_<32hex>` deletes payload + KEEPTTL marks manual recovered;
- audit fields are only event/receipt/operator/timestamp;
- every append first exact-trims IDs older than `now-7,776,000s` via `XTRIM MINID <cutoff_ms>-0`, then uses approximate MAXLEN 1000 and expiry 7,776,000 seconds;
- a day-100 append removes a day-0 entry even when the stream has fewer than 1,000 entries;
- second confirmed recovery cannot print;
- source/log static scan finds no contact/secret logger.

- [ ] **Step 2: Verify red**

Run: `pnpm test -- tests/unit/manual-recovery.test.ts tests/unit/recovery-audit.test.ts tests/unit/no-pii-output.test.ts`
Expected: missing CLI/audit FAIL.

- [ ] **Step 3: Implement exact flow**

Commands:

~~~bash
pnpm dlx vercel@54.2.0 env run -e production -- pnpm recover -- list
pnpm dlx vercel@54.2.0 env run -e production -- pnpm recover -- view --receipt-id "$RECEIPT_ID"
~~~

Flow: validate operator/TTY/ID → lock → verify payload → exact `XTRIM MINID <now-minus-90-days>-0` → XADD `view_started` MAXLEN ~1000 + EXPIRE 90d → decrypt/print → prompt exact `DELETE <receipt_id>` → only exact input terminal transition/delete + `recovery_confirmed`. Apply the same age trim before `recovery_confirmed`. Any other exit releases lock without deletion.

- [ ] **Step 4: Run and commit**

~~~bash
pnpm test -- tests/unit/manual-recovery.test.ts tests/unit/recovery-audit.test.ts tests/unit/no-pii-output.test.ts
pnpm typecheck
git add scripts/recover-receipt.ts tests/unit/manual-recovery.test.ts tests/unit/recovery-audit.test.ts tests/unit/no-pii-output.test.ts
git commit -m "feat: add two-phase fallback recovery"
~~~

---

### Task 10: QStash-only deep health, outage/recovery deduplication

**Files:**
- Create: `src/handlers/deep-health.ts`
- Create: `src/health/state-machine.ts`
- Create: `src/scheduling/recovery.ts`
- Create: `api/internal/health-check.ts`
- Create: `tests/unit/deep-health.test.ts`
- Create: `tests/unit/health-state-machine.test.ts`
- Create: `tests/unit/schedule-recovery.test.ts`

**Interfaces:**
- Consumes: QStash signature, Redis, public site, exact unsigned public WordPress health over TLS, and signed WordPress external-observation endpoint.
- Produces: exact two-failure/one-recovery behavior whenever the component under test has an independent live ledger, plus an explicitly bounded stateless simultaneous-outage fallback.

- [ ] **Step 1: Write failing tests**

Cover QStash-only auth; Redis ping/read/write short-TTL probe; site and exact unsigned public WP health with strict schema/TLS and redirects rejected. Beget-only failure uses Redis: first failure no alert, second one outage, repeats no duplicate, first healthy one recovery; run a second complete fail/fail/recovery cycle and require a second pair from a new privacy-safe episode generation. On every slot when WordPress is reachable, whether Redis is failed or healthy, send the current exact signed no-contact Redis observation to `/wp-json/landing/v1/external-health-observation`; specifically prove failed N/N+1 then healthy N+2 posts `ok` and produces one WordPress recovery. Require `checked_at_slot=Math.floor(headerTimestamp/300)`, every slot `<= lastProcessedSlot` treated as stale duplicate, adjacent increasing-slot failures, exact body keys, canonical POST/path/timestamp/site/body-digest HMAC with decoded status key, `redirect:"error"`, and strict no-store response `{ok:true,site_id:"hybridautos-ae",accepted:true,duplicate:<bool>}` with no extra keys. When both Redis and WordPress are unavailable, prove no false exact-once claim: only a `[DEGRADED STATELESS]` contact-free alert in a 30-minute UTC bucket, QStash retries 0, and document that duplicate delivery can duplicate it/no exact recovery is promised. For stateful paths prove sending persisted before Telegram, 429-only retry, ambiguous technical Telegram no resend, parallel lock, and no contact/receipt IDs/provider bodies. Add due-work recovery cases for initial reconcile, check 2, explicit-429 retry, and cleanup: at most 50 publishes and 500 examined due members, per-receipt lock, current-state validation, stable deduplication key, success removes due work, failure delays at least five minutes, maximum five publication attempts, fifth failure marks `schedule_failed` and creates one privacy-safe incident/manual-recovery visibility, and `telegram_sending|telegram_unknown` is never republished. Missing due metadata/receipt or a terminal/non-job state is guarded-removed stale. Reconcile/check-2/Telegram-429 jobs require a live payload; `cleanup_pending` instead requires matching receipt/attempt/message and finalizes `delivered` even with absent/expired payload, never calling Telegram. More than 50 stale members cannot starve a later valid member within the 500-item examination budget.

- [ ] **Step 2: Verify red**

Run: `pnpm test -- tests/unit/deep-health.test.ts tests/unit/health-state-machine.test.ts tests/unit/schedule-recovery.test.ts`
Expected: missing health modules.

- [ ] **Step 3: Implement**

Call unsigned public `GET https://hybridautos.ae/wp-json/landing/v1/health` and root with 8-second timeouts and `redirect:"error"`; send no HMAC headers to the public health route. Validate the agreed exact PII-free WP health schema over TLS. The internal route alone probes Redis and calls `recoverDueSchedules({maxPublish:50,maxExamined:500})` when Redis is reachable. Recovery reads only contact-free due metadata, guarded-removes state-invalid stale members, republishes only a state-valid idempotent QStash job, and applies the exact five-attempt/five-minute rules; cleanup validation is payload-independent. Persist Beget `sending_outage|open|sending_recovery|telegram_unknown` plus a new episode generation in Redis, so two real outage cycles produce two pairs without duplicates inside either episode. Independently of that Redis-led Beget ledger, if WordPress is reachable POST that slot's signed current Redis `failed|ok` observation every time; the first healthy slot therefore closes a WP-owned Redis outage. If both are unavailable, use only the documented 30-minute stateless notice with no QStash or Telegram retry and include the residual-duplicate/no-exact-recovery boundary in release evidence.

- [ ] **Step 4: Run and commit**

~~~bash
pnpm test -- tests/unit/deep-health.test.ts tests/unit/health-state-machine.test.ts tests/unit/schedule-recovery.test.ts
pnpm typecheck
git add src/handlers/deep-health.ts src/health src/scheduling/recovery.ts api/internal/health-check.ts tests/unit/deep-health.test.ts tests/unit/health-state-machine.test.ts tests/unit/schedule-recovery.test.ts
git commit -m "feat: add authenticated deep health monitor"
~~~

---

### Task 11: Free Marketplace provisioning, WAF, preview, and disabled production shell

**Files:**
- Create: `scripts/check-runtime-config.ts`
- Create: `scripts/smoke.ts`
- Create: `tests/integration/service.test.ts`
- Create: `ops/backup-evidence.md`
- Create: `ops/release-evidence.md`
- Create: `ops/rollback.md`

**Interfaces:**
- Consumes: green service, commercial-plan gate, and exact free-Marketplace-resource gate.
- Produces: disabled/test-mode production shell, approved free Marketplace resources, one included WAF rule, preview evidence.

- [ ] **Step 1: Provision exact free products**

Link project and re-run help. Only after exact free metadata is visible:

~~~bash
cd '/Users/kirillbezikov/Documents/Сайт Дубай /hybridautos-lead-fallback'
pnpm dlx vercel@54.2.0 link --yes --project hybridautos-lead-fallback
pnpm dlx vercel@54.2.0 integration add upstash/upstash-kv --name hybridautos-fallback-redis --plan free --metadata autoUpgrade=false --environment preview --environment production
pnpm dlx vercel@54.2.0 integration add upstash/upstash-qstash --name hybridautos-fallback-qstash --plan free --metadata prodPack=false --environment preview --environment production
pnpm dlx vercel@54.2.0 integration list --format=json
~~~

Expected JSON: exact two resources, plan free, Redis autoUpgrade false, QStash prodPack false. Any different plan/metadata/billing prompt => cancel/STOP.

- [ ] **Step 2: Configure required env fail-closed**

Use interactive `vercel env add/update`; never put secret values in command arguments. Preview and initial production:

~~~text
FALLBACK_ACCEPTING_ENABLED=false
FALLBACK_TEST_MODE=true
RECOVERY_OPERATOR_ID=kirill-bezikov
LP_KEY_PREFIX=ha:test:preview or ha:prod
PUBLIC_SERVICE_URL=https://hybridautos-lead-fallback.vercel.app
~~~

Add four distinct 64-hex secrets, one 32-byte base64 encryption key, Redis/QStash credentials/keys, and Telegram credentials. `scripts/check-runtime-config.ts` prints only:

~~~json
{"accepting":false,"testMode":true,"secretsValid":true,"operatorValid":true}
~~~

- [ ] **Step 3: Deploy preview and disabled production**

~~~bash
pnpm test
pnpm typecheck
pnpm build
pnpm dlx vercel@54.2.0 deploy
pnpm dlx vercel@54.2.0 env run -e preview -- pnpm test:integration
pnpm dlx vercel@54.2.0 deploy --prod
pnpm dlx vercel@54.2.0 env run -e production -- pnpm check:config
~~~

Expected: tests green; preview Telegram test prefix; production POST returns 503 service_disabled; shallow health 200 without Redis access.

- [ ] **Step 4: Configure exactly one included commercial-plan WAF rule**

~~~bash
pnpm dlx vercel@54.2.0 firewall rules --help
pnpm dlx vercel@54.2.0 firewall rules add --ai "For POST requests whose path equals /api/v1/fallback-leads, rate limit by source IP to 10 requests per minute and return HTTP 429 after the limit. Do not apply to receipt, health, or internal QStash routes."
pnpm dlx vercel@54.2.0 firewall diff
~~~

Capture the new draft rule ID without exposing credentials. Inspect the draft with `pnpm dlx vercel@54.2.0 firewall rules inspect <RULE_ID>` and `firewall diff`; require method POST, exact path, source-IP key, 60-second window, limit 10, 429, and one included rule on the verified commercial plan. If unavailable or it requests a new unapproved charge, delete the draft and STOP. Then run `pnpm dlx vercel@54.2.0 firewall publish` (publish is at the `firewall` level, not `firewall rules`), verify active state with `firewall overview` plus `firewall rules inspect <RULE_ID>`, and only then prove the 11th live request is 429 while shallow health is unaffected.

- [ ] **Step 5: Verify encrypted backup evidence**

`ops/backup-evidence.md` must record only encrypted archive path/hash/mode and restore owner. Evidence must show:

- archive encrypted at creation/streamed encryption;
- mode `0600`;
- no plaintext SQL, `wp-config.php`, `.env`, Vercel export, token, or contact left locally/remotely;
- key/passphrase stored in approved password manager, not the document.

Run a filesystem search in the scoped backup directory and fail release if plaintext artifacts exist.

- [ ] **Step 6: Preview smoke and commit**

Smoke must prove disabled 503, no-store headers, forged Origin/token rejection, atomic nonce reuse behavior, 45s/+30s worker decisions, 429-only retry, cleanup-only, truthful expiry, shallow/deep health separation, and no PII logs. Test messages use synthetic `+971500000000`.

~~~bash
pnpm dlx vercel@54.2.0 env run -e preview -- pnpm smoke
pnpm dlx vercel@54.2.0 logs --environment preview --level error --since 30m
git diff --check
git status --short
git add scripts/check-runtime-config.ts scripts/smoke.ts tests/integration/service.test.ts ops/backup-evidence.md ops/release-evidence.md ops/rollback.md
git commit -m "test: verify disabled fallback deployment"
git push -u origin HEAD
~~~

Expected: no real contact/secret/provider body in logs/Git; disabled shell is reversible.

---

### Task 12: Executable controlled test, final enablement, monitoring schedule, and release proof

**Files:**
- Modify: `ops/release-evidence.md`
- Modify: `ops/rollback.md`

**Interfaces:**
- Consumes: published policy, WP token/status/async integration behavior, frontend disabled/admin test flag, encrypted backup evidence.
- Produces: tested and safely enabled production fallback.

- [ ] **Step 1: Enforce pre-test gates**

Fresh evidence must show:

- WordPress returns durable lead success immediately after storage and runs Telegram/Email/Roistat asynchronously; integration delay/failure cannot delay/change `lead_id` success.
- WP token endpoint is no-store and submission-status route is signed.
- Privacy Policy names Vercel/Upstash and exact retention.
- Frontend production fallback remains disabled.
- Service is currently `accepting=false,test=true`.
- Encrypted `0600` backup and Git rollback points exist.

If any is false, stop.

- [ ] **Step 2: Temporarily enable admin-only controlled production test**

While public website fallback remains disabled:

~~~bash
pnpm dlx vercel@54.2.0 env update FALLBACK_ACCEPTING_ENABLED production
pnpm dlx vercel@54.2.0 env update FALLBACK_TEST_MODE production
pnpm dlx vercel@54.2.0 deploy --prod
pnpm dlx vercel@54.2.0 env run -e production -- pnpm check:config
~~~

Enter exact values `true` and `true`. Expected safe config output: `{"accepting":true,"testMode":true,"secretsValid":true,"operatorValid":true}`.

Use only the authenticated WordPress admin gate: a nonce-protected admin POST arms a 60-second user transient and returns `303` to the clean homepage; the frontend consumes it once before making `GET /wp-json/landing/v1/fallback-token` with `Accept: application/json`, `credentials: same-origin`, and a valid `X-WP-Nonce` for `wp_rest`. The token GET sends no test query/body. WordPress must also prove the logged-in user has `manage_options` before emitting signed `mode=test`. Public/non-admin/invalid-nonce requests in WP test mode return 404. The admin action nonce remains only in the POST body and is never sent to the token route, URL, referrer, analytics, or Vercel. Do not create/use a public controlled route. Prove:

1. normal primary success creates WordPress lead and no Vercel receipt;
2. admin-controlled primary failure creates pending receipt, no immediate Telegram;
3. WP exists=true at 45s deletes payload/no Telegram;
4. explicit missing sends one test-prefixed Telegram;
5. first ambiguity at 45s schedules +30s; second ambiguity sends once;
6. replay/nonce/fingerprint/first-reason rules;
7. confirmed-send transition failure uses cleanup-only/no resend;
8. public status/expiry truth;
9. immutable `intake_mode`: a delayed test receipt stays test-prefixed after a simulated flag flip, and same UUID/fingerprint with a live token returns exact `mode_conflict`.

- [ ] **Step 3: Immediately return to disabled/test state**

After controlled evidence, remove/disable admin frontend flag, then:

~~~bash
pnpm dlx vercel@54.2.0 env update FALLBACK_ACCEPTING_ENABLED production
pnpm dlx vercel@54.2.0 env update FALLBACK_TEST_MODE production
pnpm dlx vercel@54.2.0 deploy --prod
pnpm dlx vercel@54.2.0 env run -e production -- pnpm check:config
~~~

Enter `false` and `true`. Expected: disabled/test config and POST 503. This closes the test window before final review. Existing test receipts retain `intake_mode=test`; do not delete their due work or ciphertext merely to change flags.

- [ ] **Step 4: Create one QStash health schedule**

Create/overwrite exact schedule:

~~~text
scheduleId: hybridautos-beget-health-v1
destination: https://hybridautos-lead-fallback.vercel.app/api/internal/health-check
cron: */5 * * * *
body: {"v":1,"site_id":"hybridautos-ae","kind":"health-check"}
retries: 0
~~~

List schedules and assert exactly one matching ID. Verify two healthy calls, controlled preview two-failure/one-recovery test, no PII.

- [ ] **Step 5: Set final server flags while website remains disabled**

~~~bash
pnpm dlx vercel@54.2.0 env update FALLBACK_ACCEPTING_ENABLED production
pnpm dlx vercel@54.2.0 env update FALLBACK_TEST_MODE production
pnpm dlx vercel@54.2.0 deploy --prod
pnpm dlx vercel@54.2.0 env run -e production -- pnpm check:config
~~~

Enter `true` then `false`. Expected: `{"accepting":true,"testMode":false,"secretsValid":true,"operatorValid":true}`. Website/browser fallback is still disabled during this verification. Before enabling it, prove either no test due work remains or every remaining test receipt has immutable `intake_mode=test` and its delayed formatter remains test-prefixed under this live deployment. A mode-changed replay must be 409 `mode_conflict`, never live success.

- [ ] **Step 6: Enable website last and verify all six pages**

Enable the reviewed frontend fallback flag. Verify home, Li Auto, Zeekr, Xiaomi, Lynk & Co, and ROX load the same handler/token protocol. Run one labeled normal primary-success check; it must not create a fallback receipt.

- [ ] **Step 7: Final quality/release evidence**

~~~bash
pnpm test
pnpm typecheck
pnpm build
pnpm dlx vercel@54.2.0 logs --environment production --level error --since 30m
pnpm dlx vercel@54.2.0 integration list --format=json
git status --short
git rev-parse HEAD
git ls-remote origin HEAD
~~~

Expected:

- all tests/typecheck/build pass;
- commercial account plus free Marketplace resource plans/metadata and included WAF remain exact;
- one health schedule;
- no contact/secrets/provider bodies in logs;
- sent/primary/manual terminal state has no ciphertext;
- pending/unknown ciphertext never exceeds seven days;
- 30-day pseudonymous receipt TTL is not extended;
- local/remote SHA match and worktree clean;
- encrypted backup mode/hash/restore evidence current.

- [ ] **Step 8: Commit/tag**

~~~bash
git add ops/release-evidence.md ops/rollback.md
git commit -m "docs: record verified fallback release"
git tag -a hybridautos-fallback-v1 -m "Verified delayed fallback release"
git push origin HEAD hybridautos-fallback-v1
~~~

## Final Acceptance Checklist

- [ ] Exact no-store token endpoint is used; token is absent from cached HTML.
- [ ] Forged Origin/token and nonce reuse across UUIDs are rejected atomically.
- [ ] Fingerprint uses dedicated decoded hex HMAC key and excludes token/reason.
- [ ] First reason is frozen; same payload/different reason replays.
- [ ] Receipt ID is exactly `rct_` plus 32 lowercase hex.
- [ ] Public handler stores then schedules 45s; it never calls Telegram.
- [ ] WP exists suppresses Telegram; explicit missing sends; ambiguity checks twice.
- [ ] Sending is persisted before Telegram.
- [ ] Only 429 retries; 5xx/timeout/malformed/stale sending never resends.
- [ ] Confirmed-send transition failure schedules cleanup-only.
- [ ] Every transition preserves TTL.
- [ ] Public state is exact and payload expiry yields expired/stored=false without terminal proof.
- [ ] Manual view/no-confirm retains ciphertext; exact confirmation deletes/marks.
- [ ] Recovery audit is ≤1,000 entries and ≤90 days.
- [ ] Public health is Redis-free; deep health requires QStash.
- [ ] Four HMAC secrets are exact/distinct; encryption key is exactly 32 bytes.
- [ ] Required flags fail closed and final production is accepting=true/test=false before website enable.
- [ ] Vercel 54.2.0, existing Pro/Enterprise plan, DPA/data-use setting, exact free Marketplace resources, metadata, and one included WAF rule are proven; Hobby is rejected.
- [ ] WordPress success is immediate after durable storage; integrations are asynchronous.
- [ ] Backups are encrypted `0600` and no plaintext artifact remains.
- [ ] All six pages, logs, Git SHA/tag, schedule, rollback, and no-PII evidence are fresh.
