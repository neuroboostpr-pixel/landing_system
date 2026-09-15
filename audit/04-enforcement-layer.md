# Audit 04 — Enforcement Layer

**Scope:** `config/*.yaml`, `docs/standards/*.md`, `CLAUDE.md`, `.claude/settings*.json`, `template/` — everything that is *supposed* to physically prevent agents from skipping pipeline stages or shipping sub-premium output.

**One-sentence intent:** the layer claims it enforces a 13-stage pipeline with HARD GATEs and verify-scripts, so agents cannot ship a landing without passing each stage's checks.

**Overall assessment:** the enforcement is **documentation + a manually-invoked gate-check script**. There is **no harness-level mechanism** (no `PreToolUse` hook, no Stop hook, no pre-commit guard) that *physically* blocks an agent from writing into the wrong stage, skipping a stage, or claiming approval without `gate-check.sh` ever running. The `lock: hard` / `lock: soft` labels in `stage-gates.yaml` are essentially decorative — see Critical-1. The current system relies on the orchestrator voluntarily calling the right script. As soon as a sub-agent (or a fresh session) bypasses the orchestrator, the gates evaporate.

---

## Critical issues (must fix)

### CRITICAL-1 — `lock: hard` is documentation-only; no PreToolUse / Stop hook enforces stage order

**Evidence:**
- `.claude/settings.json` (repo) defines hooks for **`SessionStart`, `SessionEnd`, `PreCompact` only** — all three are wiki-compile hooks (`scripts/wiki/hooks/*.py`). None of them block tool calls.
- `.claude/settings.local.json` is `bypassPermissions` + `skipDangerousModePermissionPrompt: true` + `skipAutoPermissionPrompt: true`. No hooks at all.
- `template/.claude/settings.json` mirrors the same three wiki hooks; no `PreToolUse`, no `UserPromptSubmit`, no `Stop`.
- `scripts/gate-check.sh` line 61 reads `lock`, but the only branch that *uses* it (line 63) is `if [ "$stage_lock" = "soft" ] && [ -z "$required" ]` — i.e. **`lock` is only consulted to decide whether to print an interactive "Точно зайти?" warning for soft stages with no `require_approved`**. For hard stages, the entire enforcement is `require_approved` — which is the same list that already gates soft stages. **`lock: hard` adds zero runtime behavior beyond labelling.**
- `gate-check.sh` is only invoked when somebody types `/landing-go` (or another slash command) — nothing forces an agent to invoke it before writing files. An agent can `Write` `07b_COMPOSED/composed.html` straight from `07a_prototype` and never touch the gate.

**Why this is fatal:**
- The premise of the system ("HARD GATE между этапами") is the user's #1 quality bet. Right now, "HARD GATE" means "the orchestrator's prose says it is one." A skill, sub-agent, or even an inattentive run of the orchestrator can bypass every gate without the harness noticing.
- Recent commit `fd79b04 feat(orchestrator): Stage Execution Protocol — Mermaid карта + TodoWrite дисциплина` added discipline *inside the orchestrator prompt*, not in the harness. Same gap.

**Concrete fix:**

1. Add a `PreToolUse` hook in `.claude/settings.json` that wraps `Write` and `Edit`:
   ```jsonc
   "PreToolUse": [{
     "matcher": "Write|Edit",
     "hooks": [{
       "type": "command",
       "command": "python3 ${LANDING_SYSTEM_DIR}/scripts/hooks/enforce_stage_gate.py"
     }]
   }]
   ```
   The script (new — does not yet exist) reads the target path from the tool call, maps it to a stage (`07b_COMPOSED/*` → `07c_composed`), reads `<project>/.landing-state.yaml`, and **exits non-zero** if any `require_approved` predecessor is not `approved`. Non-zero from a `PreToolUse` hook actually blocks the call.
2. Add a `Stop` hook (or `SessionEnd`) that fails the run if the current stage was advanced (file artifact appeared) without a matching `gate-check.sh --approve` log entry in `.landing-state.yaml`.
3. Add a pre-commit hook (`.githooks/pre-commit`) that runs `gate-check.sh` for every stage whose artifact files appear in the diff. Currently `.githooks/post-commit` only re-compiles the wiki — *after* the commit, when it's already too late.
4. Rename `lock: hard` / `lock: soft` to something honest (`strict: true`) or actually use the field — e.g. `if stage_lock == "hard" && fail: refuse approval even with --force`.

### CRITICAL-2 — `gate-check.sh` is bypassable via `legacy: true` flag with no audit trail

**Evidence:** `gate-check.sh` lines 121-126:
```bash
if [ -f "$project/.landing-state.yaml" ] && grep -q "^[[:space:]]*legacy:[[:space:]]*true" "$project/.landing-state.yaml" 2>/dev/null; then
    echo "  ⚠ legacy:true — skipping all hard checks for $stage"
    checks_count=0
```
Any agent (or user) can `echo "legacy: true" >> .landing-state.yaml` and **all hard checks across the entire pipeline are silently skipped** with no warning beyond a single stdout line. There is no allowlist of which stages can be legacy-bypassed, no required justification, no logging.

**Concrete fix:**
- Require `legacy_reason: "<text>"` adjacent to `legacy: true` or refuse to honour the flag.
- Log every bypass to `<project>/wiki/gate-bypasses.log` with timestamp + stage + reason.
- Restrict legacy bypass to a configurable allowlist (e.g. only the 00–02 upstream stages, never 07b/07c/08/09).

### CRITICAL-3 — `verify-content-preserved.sh`, `verify-photo-pipeline.sh`, `verify-identity-preserved.sh` and `verify-composed-premium.sh` errors get swallowed

**Evidence:** `gate-check.sh` lines 155-164 (the `script` check type):
```bash
if $runner "$REPO_ROOT/$script_path" $args_raw >/dev/null 2>&1; then
    echo "  ✅ $check_id ($script_path)"
else
    echo "  ❌ $check_id: script $script_path failed"
    $runner "$REPO_ROOT/$script_path" $args_raw 2>&1 | sed 's/^/     /' || true
    [ -n "$fix_hint" ] && echo "     → $fix_hint"
    fail=1
fi
```
The script is run **twice** when it fails: once silenced, once for output. Two issues:
1. Non-deterministic verifiers (e.g. ones that hash, ping, or shell out to codex) can pass the first invocation and fail the second, or vice versa. The exit code that decides the gate is from the first (silenced) run; the user sees output from the second.
2. If the verifier has side-effects (writes a report, downloads an asset), it runs twice silently.

**Concrete fix:** capture stdout/stderr into a temp file once, then `cat` it on failure:
```bash
out=$(mktemp); rc=0
$runner "$REPO_ROOT/$script_path" $args_raw >"$out" 2>&1 || rc=$?
if [ "$rc" -eq 0 ]; then echo "  ✅ ..."; else sed 's/^/     /' "$out"; fail=1; fi
rm -f "$out"
```

### CRITICAL-4 — Premium 07b verifier wired only on `07c_composed`; not re-run on `08_build` or `09_deploy`

**Evidence:** in `stage-gates.yaml` the `verify-composed-premium.sh` check is wired into `07c_composed` (line 227) and `07f_composed_final` (line 285). After that, `08_build` and `09_deploy` do not re-check the composed file. If the wp-builder agent rewrites `composed.html` (or extracts CSS that loses parallax/glassmorphism), `09_deploy` ships a downgraded landing with no alarm.

**Concrete fix:** add `verify-composed-premium.sh` as a hard check on `08_build` and `09_deploy` as well, pointed at the final theme assets, not the composed source. Or add a `verify-theme-premium.sh` that re-applies the same 13 checks against the rendered theme.

---

## Major issues (should fix)

### MAJOR-1 — `08b_style` stage has NO `lock:` field at all

`stage-gates.yaml` line 354-356:
```yaml
"08b_style":
  name: "Frontend style"
  require_approved: ["08_build"]
```
No `lock:` key. `gate-check.sh` line 61 defaults missing `lock` to `soft`. Either:
- This is deliberate — but undocumented, no comment explains why a stage that gates real customer-visible CSS rendering is `soft`.
- Or this is an oversight — given how strict the other code-touching stages are (`07c_composed`, `08_build` both `hard`), `08b_style` looks like coverage hole.

**Fix:** add explicit `lock: hard` (assuming intent) and document the decision.

### MAJOR-2 — `verify-visual-qa.sh` exists but is orphaned

`scripts/verify-visual-qa.sh` is shipped (and has a `.doc.md`), but `grep` finds **zero references** in `config/stage-gates.yaml` or anywhere in `gate-check.sh`. The corresponding soft check `visual_qa_passed` (lines 244-245, 306-307) is an interactive `yes/no` prompt — never actually runs the script.

**Fix:** convert the soft prompt into a hard `script` check on `07c_composed` and `07f_composed_final`, OR delete the orphan verifier so future maintainers don't trust it. Right now the system **claims** to have visual QA but the script is never called.

### MAJOR-3 — Stage Execution Protocol coverage is voluntary; only 1 of 32 agents references it

`docs/standards/stage-execution-protocol.md` says (line 4): "Применяется к: `landing-orchestrator` + любым агентам, выполняющим этап pipeline". Grepping the protocol reference across `agents/`:
- `landing-orchestrator.md` — yes (the link is in its body)
- `block-composer.md`, `frontend-builder.md`, `niche-analyst.md` — reference `premium-07b-checklist.md` or `gate-check.sh` directly but **not** the execution protocol
- The other 28 agents — silent

So the canonical "agent must (1) read state, (2) render pipeline map, (3) TodoWrite remaining stages, (4) verify→approve" pattern is enforced only when the user enters via `/landing-go`. Direct slash commands (`/landing-compose`, `/landing-photos`, `/landing-visuals`) call agents that have no reminder to follow the protocol.

**Fix:**
- Add a frontmatter field `stage_execution_protocol: required` to every stage agent's `.md`, then have a CI check (or the wiki compiler) refuse to publish an agent without it.
- Better: embed a `SessionStart` hook that, when `current_stage != null` in any nearby `.landing-state.yaml`, **prints the pipeline map and asks the agent to write a TodoWrite list** before the first message — same way wiki hooks already run on SessionStart.
- Even better: when a slash command is invoked, have a `UserPromptSubmit` hook (Anthropic schema) inject the protocol reminder into the prompt.

### MAJOR-4 — CLAUDE.md contains conflict between "никогда не пропускай HARD GATE" and "PR-A команды вызываются ВРУЧНУЮ, не через `landing-orchestrator`"

`CLAUDE.md` says repeatedly: HARD GATE между этапами проектов — агент не идёт на следующий этап workflow без явного утверждения. But four sections later, three NOTE blocks (PR-A, PR-B, PR-C) explicitly say: *"команда вызывается ВРУЧНУЮ, не через `landing-orchestrator`. Интеграция в orchestrator — задача PR-D"*. PR-D is documented as shipped (`/landing-go` exists). So either:
1. The NOTEs are stale (likely — PR-D is described as complete on the next page).
2. Or the manual entry-points are still in use and bypass gating.

Either way, this is a contradiction the user/agent has to resolve at runtime. Today an agent reading the file will see two conflicting instructions.

**Fix:** sweep CLAUDE.md, delete the three "вызывается ВРУЧНУЮ" NOTEs now that PR-D is shipped, OR explicitly document which entry-points are still legitimate vs deprecated.

### MAJOR-5 — `template/.landing-state.yaml` pre-marks 00/01/01a/02 as `n/a` for ALL projects

```yaml
"00_brief":             {status: n/a, timestamp: ""}
"01_context":           {status: n/a, timestamp: ""}
"01a_niche_analysis":   {status: n/a, timestamp: ""}
"02_assets":            {status: n/a, timestamp: ""}
```
And `gate-check.sh` line 78 treats `n/a` as "previous stage is satisfied" (`if [ "$prev_status" != "approved" ] && [ "$prev_status" != "n/a" ]`). This means every new project starts assuming brief, niche analysis, and assets have been done elsewhere — but the template doesn't enforce that the user actually attached those upstream artifacts. The `01a_niche_analysis` stage in `stage-gates.yaml` has 14 hard checks (the most of any stage!) — all skipped by default.

**Fix:** either
- Make `n/a` require an explicit declaration in `/landing-start` ("Is niche analysis already done elsewhere? Where is it?"), with a path to the upstream artifact stored in `.landing-state.yaml`.
- Or default new projects to `status: locked` and force the user to mark `n/a` explicitly when they truly skip a stage.

### MAJOR-6 — `gate-check.sh` ignores soft-check `partial` answers (treats them as pass)

Lines 184-190:
```bash
case "$ans" in
    yes|y) echo "    ✅ confirmed" ;;
    no|n)  echo "    ❌ not satisfied"; fail=1 ;;
    *)     echo "    ⚠️  partial / skipped" ;;
esac
```
`partial` doesn't set `fail=1`. For soft checks like `legal_blocks` ("152-ФЗ блок и cookie-баннер присутствуют? yes / no / partial") this means a partial-coverage cookie banner ships without complaint. The prompt advertises three states; the code accepts only two.

**Fix:** define what `partial` means (block? warn? require comment?) and either ban it from the prompts or implement the third branch.

---

## Minor issues

### MINOR-1 — `stage-gates.yaml` mixes `file_exists` and `file_or_dir_exists` types but no schema validation

`07a_prototype` uses `file_or_dir_exists` (line 189). The other 30 stages use `file_exists`. If a maintainer typos the type, `gate-check.sh` line 168 silently emits `⚠️ unknown type` and continues — **doesn't fail the gate**. A schema (JSON Schema or `yq` lint) for `stage-gates.yaml` would catch this.

### MINOR-2 — `n/a` and `failed` are not in `gate-state.sh` enum but appear in template

The header comment of `template/.landing-state.yaml` lists `locked → in_progress → approved | failed | n/a` as valid statuses. But no script transitions to `failed` — only to `in_progress` (via gate fail) or `approved`. The `failed` status is documentation aspiration.

### MINOR-3 — `premium-07b-checklist.md` lists 20 features but `verify-composed-premium.sh` checks 13 (per CLAUDE.md)

The checklist itself has §1–§13 plus PR-P additions §14–§20 added later. CLAUDE.md still says "все 13 premium-фич". If the verify script checks only the original 13, the §14–§20 (scroll-driven, glassmorphism, mesh gradient, mix-blend-mode, prefers-reduced-motion, clip-path) are aspirational — not gated. Either update the verifier or update the docs.

### MINOR-4 — `06_stack`'s `http_ping` checks ping external CDNs (Iconify, Bunny Fonts, jsdelivr) every gate-run

This is a soft form of vendor lock-in: if Iconify is down, `06_stack` cannot be approved even though the local project is fine. Add `required: false` or fall back to a cached "ok within 24h" file.

---

## Positive feedback (working well)

- **`scripts/gate-check.sh` is well-structured** — clean separation of `require_approved` precondition, hard checks, soft prompts, approval transition. Good base to extend.
- **`stage-gates.yaml` is data-driven** — adding a stage means YAML, not code. Excellent.
- **`docs/standards/premium-07b-checklist.md` is exceptional documentation** — concrete, with reference implementation (`dubai-avto-liza`), bad-vs-good code snippets, ban-list. This is the strongest piece of the enforcement layer.
- **Verify scripts are co-located in `scripts/verify-*.sh`** with `.doc.md` siblings — discoverable.
- **`gate-check.sh` writes the pipeline map after every check** (line 224-228) — this means the project wiki always reflects current state without manual sync. Good design.
- **The auto-fix loop** (orchestrator → `fix_hint` → re-run gate) is a sensible compromise between automation and approval, *as long as it's actually invoked* — which is the gap above.

---

## Questions for author

1. Was `lock: hard` ever intended to do more than label? If so, what behaviour did you have in mind that's missing from `gate-check.sh`?
2. Is the `legacy: true` bypass intended for migration only, or do you rely on it for active projects? If migration-only, fence it off (sunset date, allowlist of stages).
3. Are the PR-A/B/C "manual command" NOTEs in `CLAUDE.md` still accurate, or can they be deleted now that `/landing-go` orchestrates everything?
4. Should `verify-visual-qa.sh` become a hard check on 07c/07f, or do you want to keep visual QA optional?

---

## Verdict

**Request Changes — Critical gap.**

Today the enforcement layer is **policy without police**. The standards are excellent (premium-07b-checklist is genuinely top-tier), the gate script is solid, but nothing in the harness *forces* an agent to invoke them before shipping artifacts. Any agent or fresh session that bypasses `/landing-go` walks straight through every "HARD GATE" untouched.

**Priority sequence to close the gap:**
1. (Critical-1) Ship a `PreToolUse` hook in `.claude/settings.json` that maps file path → stage and refuses Write/Edit when predecessors aren't approved. **This is the single highest-leverage change in the entire audit.** Without it, every other rule is honour-system.
2. (Critical-2) Lock down the `legacy: true` bypass.
3. (Major-3) Make Stage Execution Protocol mandatory for every stage agent (frontmatter + CI check + `UserPromptSubmit` hook injection).
4. (Critical-3) Fix the double-invocation bug in script verifiers.
5. (Major-1, Major-2, Major-4) Tidy the labelled gaps: missing `lock:` on `08b_style`, orphan `verify-visual-qa.sh`, contradictions in CLAUDE.md.
6. (Critical-4) Re-run premium verifier on `08_build` and `09_deploy`.

Until item 1 is shipped, treat every "HARD GATE" mention in the codebase as aspirational documentation, not a guarantee.
