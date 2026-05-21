# Code Review v2: agents/ + skills/ + commands/

**Дата:** 2026-05-20
**Scope:** 33 `agents/*.md` + 24 `skills/*/SKILL.md` + 28 `commands/*.md` + 26 `.claude/commands/*.md`.
**Reference:** original `audit/03-agents-skills-commands.md` + Cluster B of `audit/REPORT.md`.

## Summary

| Bucket | Count |
|---|---|
| Fixed (with proof) | 6 |
| Remains (deferred / partial) | 5 |
| NEW findings (regressions) | 3 |
| Pre-existing (newly noticed) | 4 |

**Top-10 audit status:** items #2 (preamble), #9 (broken refs), #10 (PR-D notes) all **substantively fixed**, but each carries a tail of leftovers (sync, related ACF refs, preamble drift) — see Remains/New buckets.

---

## ✅ Fixed (with proof)

### F1. Stage Execution Protocol preamble — all 33 agent files carry it
All `agents/*.md` files contain a `Stage Execution Protocol` section. None has a leftover `<STAGE>` placeholder. 10 helper agents (`icon-generator`, `infographic-builder`, `landing-onboarding-wizard`, `lifecycle-keeper`, `onboarding-guide`, `photo-classifier`, `photo-matcher`, `photo-preview-board`, `photo-stylist`, `system-setup`) carry a `Helper agent` / `Helper sub-agent` / `System-level agent` marker and correctly **omit** the `bash scripts/gate-check.sh ...` invocation (delegating to parent).

**Proof:** matrix run on every file shows `protocol=1 placeholder=0` and helpers have `helper=1 gate-check=0`.

### F2. `agents/integrations-engineer.md` — `acf-fields.json` removed
**Verify:** `grep -n "acf-fields" agents/integrations-engineer.md` → no match (was line 16 in original audit).

### F3. `agents/seo-optimizer.md` — uses `00_БРИФ/brief.md`
**Verify:** `seo-optimizer.md:40` reads `00_БРИФ/brief.md`; `:45` confirms. `approved-design-brief.md` is gone.

### F4. `agents/content-writer.md` — reads `07_ПРОТОТИП/prototype.md`
**Verify:** `content-writer.md:41` — `Читаю 07_ПРОТОТИП/prototype.md`. The other 4 `07_КОНТЕНТ/*.md` refs at `:45, :46, :67, :68` are **outputs** (`final-copy.md`, `seo-copy.md`) — correct path, not a stale ref.

### F5. `commands/landing-content.md` — same path fix
**Verify:** `commands/landing-content.md:26` — `Read 07_ПРОТОТИП/prototype.md`. **Note (see N1):** `.claude/commands/landing-content.md` still has the old `07_КОНТЕНТ/prototype.md` — sync gap.

### F6. `agents/prototype-importer.md` — auto-quiz path corrected
**Verify:** `prototype-importer.md:47` and `:80` use `python3 skills/wireframe-rendering/scripts/enrich-quiz-funnel.py prototype.yaml`. The file exists at that path (`skills/wireframe-rendering/scripts/enrich-quiz-funnel.py`). The agent now actually invokes it in step 7 (was previously prose-only).

### F7. `landing-orchestrator.md` — `Phase 1 Scope` removed
**Verify:** `grep -c "Phase 1 Scope" agents/landing-orchestrator.md` → 0. The "Phase 1 завершён / Этапы 02–12 будут доступны" claim is gone. A "Текущий scope (PR-D shipped, 2026-05-13)" replacement at line 65 clarifies orchestrator runs the full pipeline.

### F8. PR-D contradictions in commands removed
**Verify:** `grep -rln "не интегрировано\|задача PR-D" commands/ .claude/commands/` → 0 matches. All 5 PR-A/B/C command files (compose, photos, visuals, wireframe, prototype) are clean.

### F9. `.claude/commands/` mostly synced
Phase 8 sync commit (`fdfcfca`) updated most files. 23 of 26 `.claude/commands/*.md` files are byte-identical to `commands/*.md`. Three exceptions remain — see N1.

---

## 🟡 Remains (deferred — still open)

### R1. Phase 7 follow-up — 4 stale ACF references still present
Original audit flagged these explicitly; commits a4bcf7c/d1a3a32/f14edbb/bf7a4d3 fixed only the primary agent (`integrations-engineer.md`). The downstream chain still contains:

| File | Line | Content |
|---|---|---|
| `agents/landing-orchestrator.md` | 167 | `Run scripts/deploy.sh . → rsync + wp theme activate + ACF import` |
| `agents/wp-deployer.md` | 34 | `Тема загружается, активируется, ACF-поля импортируются` |
| `commands/landing-deploy.md` | 24, 37 | `rsync theme, activate, import ACF` / `Theme activated, ACF fields imported` |
| `.claude/commands/landing-deploy.md` | 24, 37 | (same — both copies) |
| `skills/landing-versioning-and-cloning/scripts/create-version.sh` | 14 | `cp -r "$PROJECT/08_КОД/acf-fields.json" "$SNAPSHOT_DIR/" 2>/dev/null \|\| true` |

Since `agents/wp-builder.md:129` explicitly says `acf-fields.json — это артефакты прежней ACF-Blocks эпохи` and `:34` says `ACF Blocks (Pro-only) больше не используются`, the deploy/version chain documentation lies. The `2>/dev/null || true` in `create-version.sh:14` hides the failure silently — perfect noise filter for a phantom dependency.

**Fix:** replace `import ACF` wording with `import Lazy Blocks config`; in `create-version.sh:14` replace `acf-fields.json` with `block-spec.yaml` (or delete the line if nothing matters).

### R2. `agents/landing-orchestrator.md` still carries `Phase 2/3/4/5 Scope` blocks
`grep -n "Phase [2345] Scope" agents/landing-orchestrator.md`:
```
74:## Phase 2 Scope (расширение)
106:## Phase 3 Scope (расширение)
134:## Phase 4 Scope (Stage 08 — Код)
157:## Phase 5 Scope (Stages 09–12 — Деплой, QA, Версионирование)
316:- `Phase 1`, `Phase 2 Scope` секции выше — остаются документацией старого flow для совместимости
```
Original audit (C2) flagged Phase 1; the fix removed only Phase 1 but left Phases 2–5. Line 316 explicitly acknowledges "остаются документацией старого flow" — but they read as authoritative dispatch tables. An LLM reading the file top-down hits Phase 2/3/4/5 dispatch instructions *before* it hits the PR-D dispatch table at line 256+.

**Fix:** move Phases 2–5 blocks under a clearly-marked `## Legacy (archived)` heading at the bottom, or delete them entirely.

### R3. Stage Execution Protocol drift — orchestrator preamble does NOT match canonical
`docs/standards/stage-agent-preamble.md` is the canonical block (7 numbered steps, references PreToolUse hook, uses `<STAGE>` substitution variable). `agents/landing-orchestrator.md:7-39` uses a hand-rolled 4-step format ("Шаг 1 / Шаг 2 / Шаг 3 / Шаг 4") with sub-numbering. Both cover the same 4 protocol steps and reference `docs/standards/stage-execution-protocol.md`, but they're structurally different.

This is the "drift" my v1 review flagged. Practical impact: low (both reach the same outcome), but maintenance becomes a footgun — change the canonical block and the orchestrator silently lags. Choose one: either (a) collapse orchestrator's expanded version into the canonical block + a 1-line note "I dispatch all stages, not just one", or (b) explicitly declare orchestrator preamble is an authorized superset (then add a CI check that both reach the same step list).

### R4. M1 loopholes (HARD GATE without `gate-check --approve`) — partially fixed
After preamble rollout, the agents that newly contain `gate-check.sh` calls also gain the `Step 7` line `bash scripts/gate-state.sh approve <project> <STAGE>` from the canonical preamble. But the orchestrator still has its own "HARD GATE: дождаться утверждения" wording in many spots (e.g. `landing-orchestrator.md:172`, `:178`) that do **not** invoke `gate-state.sh approve`. The preamble doesn't apply — those are orchestrator's per-stage dispatch flow, not the preamble. So a sub-dispatch path can still pass approval verbally without writing state.

**Fix:** every orchestrator `HARD GATE` line should be followed by `→ bash scripts/gate-state.sh approve <project> <stage_id>`.

### R5. M2 — `frontend-builder.md` "if you believe JS is required, leave a TODO" still present
`agents/frontend-builder.md:60` still has the loophole language:
> `assets/js/*` (zero-JS by default; if you believe JS is required, leave a `// TODO: needs JS — discuss with manager` comment in `block.php`, do not write JS).

Same on `:83` for tokens (`If a token doesn't exist, leave a comment ... and proceed`). Original audit M2 flagged this as an "open invitation to fall back" — unchanged. 90% of premium-07b features require JS, so this rule is at war with the HARD GATE 07b standard.

### R6. M5 — `niche-analyst.md` mass-scrape has no rate-limit / fail-stop
Unchanged. `agents/niche-analyst.md:62+` still tells the agent to scrape 15-25 competitors via `mcp__firecrawl__scrape` without try/catch or "stop after 3 failures" guard.

### R7. Other M-issues from v1 audit
M1a (qa-auditor missing pre-flight), M1c (photo-stylist 80-question batching), M1d (visual-curator manual yaml check), M3 (wp-builder reads 01a files that don't exist in prototype-first), M4 (prototype-importer batching cap), M6 (wizard "если фоток нет — я сгенерю" misleading), M7 (photo-classifier unclassified silent skip), M8 (seo-optimizer hardcoded LocalBusiness schema) — **all unchanged**. These were not in the Top-10 so deferral is consistent with the stated plan. Flagging for posterity.

---

## 🔴 NEW findings (regressions / discovered in v2)

### N1. `.claude/commands/` desynced from `commands/` for 3 files (regression after Phase 8.1)

`diff -rq commands/ .claude/commands/`:
```
Files commands/landing-content.md and .claude/commands/landing-content.md differ
Files commands/landing-go.md and .claude/commands/landing-go.md differ
Files commands/landing-qa.md and .claude/commands/landing-qa.md differ
Only in commands: landing-final-check.md, landing-import-blocks.md, landing-previews.md
Only in .claude/commands: landing-style.md
```

Concrete impacts:

1. **`.claude/commands/landing-content.md:26`** still reads `07_КОНТЕНТ/prototype.md` (broken — was fixed only in `commands/` copy). When user invokes `/landing-content` from inside Claude Code, **this** file is loaded — so the fix is invisible to the runtime.
2. **`.claude/commands/landing-go.md`** is missing the "Mark upstream stages n/a" code block (17 lines, lines 26-42 in `commands/landing-go.md`) which sets prototype-first stages to `n/a` via `gate-state.sh`. Runtime `/landing-go` skips that logic.
3. **`commands/landing-qa.md`** vs **`.claude/commands/landing-qa.md`** are essentially two DIFFERENT commands:
   - `commands/` version: Visual QA on composed.html via Playwright + codex (referenced by Skill `visual-qa`)
   - `.claude/commands/` version: live-site QA on stage 10 (referenced by `qa-auditor` agent)
   This is not a sync bug — they were authored as different things, but they share the same slug `/landing-qa`. The runtime will use `.claude/commands/landing-qa.md` and ignore the visual-QA flow entirely.
4. `landing-final-check`, `landing-import-blocks`, `landing-previews` exist only in `commands/` — **invisible to runtime**.
5. `landing-style` exists only in `.claude/commands/` — **invisible to docs/source** (and `Mn3` in v1 audit already noted this).

**Fix:** either (a) make `commands/` a generator of `.claude/commands/` (e.g. via post-commit hook) and decide which `landing-qa` is the real one, or (b) document the asymmetry. Currently the situation is "looks synced for 23 files, silently diverges for 5".

### N2. `commands/landing-deploy.md:24,37` and `.claude/commands/landing-deploy.md:24,37` carry stale ACF wording (downstream of Phase 7)
Already covered in R1 — flagging separately because this is a *new* regression surface that the audit didn't list: the broken-ref fix-list named the **agent** files but didn't sweep the **command** files. Phase 7 was incomplete on its own scope.

### N3. `agents/photo-stylist.md` has NO `gate-check.sh` call
Matrix output: `photo-stylist.md ... helper=1 gate-check=0`. Marker says "Helper agent — dispatched by `photo-curator`". Fine — but the original audit M1c specifically flagged photo-stylist's "ask user for each of 80 photos" loophole, which is still present at `:30`:
> 2. For each photo, ask user about intended use (hero / about / proof).

Helper status doesn't excuse this — the loophole compounds because the helper has no Stage Execution Protocol, no batch limit, no fail-stop. If parent `photo-curator` dispatches it on a 100-photo project, this single line creates 100 sequential user prompts. Independent regression risk.

---

## ⚪ Pre-existing (newly noticed)

### P1. `skills/gpt5-prompting-engine/SKILL.md:40` — "if applicable"
> `- API recommendations if applicable;`

Minor in this context (skill description prose, not action instruction) — but worth flagging because the same phrasing in an agent-action context is exactly the skip-the-step pattern. Leave.

### P2. `agents/system-setup.md:30` — "можно пропустить если пока не деплоим"
> `BEGET_USER, BEGET_HOST, BEGET_PATH → для деплоя (можно пропустить если пока не деплоим)`

Allows user to defer; the agent itself isn't choosing — user-facing prose. Acceptable.

### P3. `agents/block-composer.md:109` — "Это необязательно блокирующий шаг"
Already flagged in v1 audit Mn6 — unchanged. The styles.csv pre-flight read is still "optional but not optional". Leave-or-tighten decision needed.

### P4. `agents/frontend-builder.md` zero-JS rule
Already R5 above. Re-noting because `commands/landing-style.md` (only in `.claude/`) dispatches `frontend-builder`, and a manager reading the source-of-truth `commands/` folder won't find it.

---

## Cross-reference report

**Scripts referenced in `agents/` + `commands/`:** 66 unique paths.

**Resolution check (each ref tested via `[ -f scripts/$ref ]` then fallback `find skills/ -name $(basename $ref)`):**

- 19 paths exist at top-level `scripts/*` and are correctly referenced as `scripts/foo` in prompts (e.g. `scripts/gate-check.sh`, `scripts/render-pipeline-map.sh`, `scripts/hooks/enforce_stage_gate.py`, `scripts/wizard.sh`, `scripts/preflight.sh`, `scripts/deploy.sh`, `scripts/derive-landing-structure.py`, `scripts/install-codex.sh`, `scripts/setup-flag.sh`, `scripts/validate-all.sh`, `scripts/gate-state.sh`, `scripts/landing-go-next-stage.py`, `scripts/generate-wp-blocks.py`, `scripts/visual-cache.py`, etc.).
- 47 paths are referenced WITHOUT the `skills/X/scripts/` prefix in regex output but in actual prompt text use the full path (e.g. `python3 skills/brand-kit-build/scripts/build.py` at `agents/brand-architect.md:46`). My regex `scripts/[a-z_/\-]+\.(sh|py)` matched only the suffix; full ref is correct. **No false positives.**
- **Zero broken refs found.** All 66 resolve.

**One latent risk:** preamble template references `bash scripts/verify-<STAGE>.sh (если есть)`. Only 9 verify scripts actually exist (`verify-composed-premium.sh`, `verify-composed-has-visuals.sh`, `verify-content-preserved.sh`, `verify-gutenberg-json.sh`, `verify-identity-preserved.sh`, `verify-photo-pipeline.sh`, `verify-php-syntax.sh`, `verify-site-url.sh`, `verify-visual-qa.sh`). The "(если есть)" qualifier prevents fail, but most stages (01a, 03, 04, 05, 06, 07, 08, 09, 10, 11, 12) silently lack any verify enforcement at the preamble level. This is correct as-written (the verify scripts are stage-specific and few stages have hard verifiers) but it means the preamble's Step 7 is decorative for most stages.

---

## Skip-the-step audit

Quoted loopholes still active after Top-10 fixes:

| File:line | Phrase | Risk |
|---|---|---|
| `agents/frontend-builder.md:60` | `if you believe JS is required, leave a TODO` | HIGH — at war with premium-07b HARD GATE |
| `agents/frontend-builder.md:83` | `If a token doesn't exist, leave a comment ... and proceed` | MED — silent token drift |
| `agents/block-composer.md:109` | `необязательно блокирующий шаг — если styles.csv не доступен, пропустить` | LOW — flagged in v1 Mn6, unchanged |
| `agents/photo-stylist.md:30` | `For each photo, ask user about intended use` | HIGH — 80 sequential prompts, no batching cap (compounds with helper-agent status that bypasses preamble) |
| `agents/niche-analyst.md:62+` | mass scrape via firecrawl, no fail-stop | MED — operational fragility |
| `landing-orchestrator.md` "HARD GATE: дождаться утверждения" lines | verbal approval without `gate-state.sh approve` | HIGH — state machine can fall out of sync with reality |

**No NEW skip-the-step loopholes were introduced by the Top-10 fixes.** The preamble rollout in fact *closed* the largest set (every stage agent now has `bash scripts/gate-check.sh --stage <X> --project <project>` as Step 4 of its preamble).

**Identity/role anchors:** all 33 agents have valid `name: + description:` frontmatter. No drift mid-prompt observed.

---

## Verdict

**Approve with caveats.**

The Top-10 fixes substantively land: 100% preamble coverage, all 4 primary broken refs fixed, PR-D contradictions cleared from commands. The system is materially closer to "policy with police" than at v1.

However:
- **N1 (commands/.claude/commands desync)** is the single biggest risk introduced/exposed by this round. `landing-content.md` runtime still reads the broken path. `landing-go.md` runtime is missing 17 lines of upstream-stage-marking logic. `landing-qa` is two different commands sharing a slug. This needs a one-shot sync + a guarding mechanism (post-commit hook or `commands/` → `.claude/commands/` build step).
- **R1 (4 stale ACF refs)** is leftover trash from Phase 7's narrow scope. 5-minute fix; do it.
- **R2 (orchestrator Phase 2-5 Scope blocks)** is the same class of risk as Phase 1 was — should be removed not just commented on.
- **R3 (preamble drift)** — pick one canonical and enforce.
- **R5 (frontend-builder zero-JS escape hatch)** unchanged from v1; this is the loophole most likely to silently degrade quality of generated builds.

Recommended next-round priorities: R1 → N1 → R2 → R5 → R3 → R4. Total est. effort ~3 hours.

---

## Files reviewed (absolute paths)

- Agents (33): `/Users/kirillbezikov/Desktop/Обучение вайбкодинг Кодекс/02_projects - проекты/Агентство лидогенерации/landing-system/agents/*.md`
- Skills (24): `/Users/kirillbezikov/Desktop/Обучение вайбкодинг Кодекс/02_projects - проекты/Агентство лидогенерации/landing-system/skills/*/SKILL.md`
- Commands source (28): `/Users/kirillbezikov/Desktop/Обучение вайбкодинг Кодекс/02_projects - проекты/Агентство лидогенерации/landing-system/commands/*.md`
- Commands runtime (26): `/Users/kirillbezikov/Desktop/Обучение вайбкодинг Кодекс/02_projects - проекты/Агентство лидогенерации/landing-system/.claude/commands/*.md`
- Standards: `/Users/kirillbezikov/Desktop/Обучение вайбкодинг Кодекс/02_projects - проекты/Агентство лидогенерации/landing-system/docs/standards/stage-execution-protocol.md`, `stage-agent-preamble.md`
