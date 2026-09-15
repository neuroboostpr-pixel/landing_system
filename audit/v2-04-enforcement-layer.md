# Code Review v2: Enforcement Layer

**Scope:** `config/stage-gates.yaml`, `scripts/gate-check.sh`, `scripts/gate-state.sh`, `scripts/hooks/enforce_stage_gate.py`, `scripts/hooks/_stage_paths.yaml`, `.claude/settings.json`, `docs/standards/*.md`, `CLAUDE.md`, `template/.landing-state.yaml`. Re-audit after Phases 3, 5, 6 attempted to close Top‑10 findings.

**One-sentence intent:** verify that the new `PreToolUse` hook actually delivers what v1 demanded — a harness-level block that prevents an agent from skipping stages — and check whether the residual v1 findings (legacy bypass, soft-check `partial`, double script-run, n/a defaults, protocol coverage, CLAUDE.md contradictions, premium re-check) were closed.

---

## Summary

The central finding (C1 "policy without police") is **largely fixed**. A real `PreToolUse` hook now ships in `.claude/settings.json`, matches `Write|Edit|MultiEdit`, runs `scripts/hooks/enforce_stage_gate.py`, and **does** exit non-zero when a predecessor stage is `locked`. I verified this end-to-end with the audit scenario. Six unit tests pass. The legacy bypass (C2) is properly tightened (allowlist + reason + audit log). Stage Execution Protocol coverage went from 1/33 to **33/33 agents**.

However, the implementation introduced one real bug (PIPELINE_ORDER mismatch between hook and `gate-check.sh` for stages 09/10), several deliberate fail-open holes (empty state, missing predecessors, exception path, `Bash` tool unmatched), and three v1 findings remain untouched (C3 script double-run, C4 premium verifier scoped to 07c/07f only, M6 soft `partial`). Net: the system is **dramatically safer than before**, but a determined agent can still find seams.

---

## Walkthrough: would the hook actually block the scenario? **YES**

Scenario: project created from template defaults → user skips prototype → orchestrator dispatches `brand-architect` for `04_brand` → agent tries `Write` to `04_БРЕНД/brand-kit.md` before `03_references` approved.

Trace (verified by running the hook against a real fixture):

1. `Write` is in matcher `"Write|Edit|MultiEdit"` → hook runs. ✅
2. Hook receives `{"tool_name":"Write","tool_input":{"file_path":"/tmp/test-proj-cyrillic/04_БРЕНД/brand-kit.md"}}`.
3. `_find_project_root()` walks up, finds `.landing-state.yaml`. ✅
4. `_stage_for_path()` matches glob `{project}/04_БРЕНД/**` → returns `04_brand`. ✅
5. State file (copied from `template/.landing-state.yaml`) shows `00_brief: locked` (Phase 3 change).
6. Loop over `PIPELINE_ORDER[:idx(04_brand)]` hits `00_brief` first → status `locked` ≠ `approved`/`n/a` → returns `(False, reason)`.
7. Hook writes to stderr `❌ Stage gate enforcement: Cannot Write/Edit to '04_brand' — predecessor '00_brief' has status 'locked'. ...` and exits **2**. ✅

Actual stdout from the test run:
```
❌ Stage gate enforcement: Cannot Write/Edit to '04_brand' — predecessor '00_brief' has status 'locked'. Run gate-check.sh and approve previous stages before editing this one.
EXIT: 2
```

The Anthropic PreToolUse contract treats non-zero exit as block-with-message-to-model. So **the brand-architect would receive the rejection** and could not proceed. The audit's #1 demand is met.

---

## ✅ Fixed

### C1 — PreToolUse hook ships and blocks
- `.claude/settings.json` lines 60–70: `PreToolUse[].matcher = "Write|Edit|MultiEdit"`, command `python3 "$CLAUDE_PROJECT_DIR/scripts/hooks/enforce_stage_gate.py"`. Uses `$CLAUDE_PROJECT_DIR` (Anthropic env var) — clean.
- `scripts/hooks/enforce_stage_gate.py` is well-structured (156 lines, one responsibility per function), correctly parses stdin JSON, exits 2 on block (matches Anthropic spec for "blocking error").
- 6/6 pytest cases in `tests/gate-check/test_enforce_stage_gate.py` pass; 2/2 bats integration tests pass.
- **Manual verification:** Cyrillic paths, paths with spaces, MultiEdit payloads, symlinks (resolved), relative paths — all handled correctly.

### C2 — legacy bypass tightened
`scripts/gate-check.sh:43–93` now requires **all three**: (a) `legacy_allowed` allowlist membership in `config/stage-gates.yaml` (defaulted to `[]`), (b) non-empty `legacy_reason` field in state file, (c) timestamped append to `audit/legacy-bypass.log`. Without all three, gate fails with explicit error. ✅

### M3 — Stage Execution Protocol coverage went from 1/33 to 33/33
`grep -rl "Stage Execution Protocol" agents/` returns all 33 stage-owner agents. `docs/standards/stage-agent-preamble.md` is the canonical copy-paste source and explicitly tells agents to expect the `PreToolUse` hook. Effectively makes the protocol two-layer (agent prompt + harness hook).

### M5 — template `.landing-state.yaml` upstream defaults flipped to `locked`
`template/.landing-state.yaml:13–17` now defaults `00_brief, 01_context, 01a_niche_analysis, 02_assets` to `status: locked` (was `n/a`). Comment explains the audit motivation. Hook walkthrough above confirms this is load-bearing — without this change, the hook would not have blocked the scenario.

### Positive: Always-allowed paths whitelist
`_stage_paths.yaml:51–57` correctly whitelists `.landing-state.yaml`, `wiki/**`, `CLAUDE.md`, `README.md`, `.env`, `deploy.sh` — preventing the bootstrap chicken-and-egg of "can't edit state file because state file says you can't edit". Verified.

### Positive: Fail-open is bounded and logged
`enforce_stage_gate.py:108–119` catches all exceptions, writes `⚠️ enforce_stage_gate hook error (allowing edit)` to stderr, returns 0. The user sees the warning. Better than a silent fall-through. Test `test_corrupt_state_file_allows_edit` codifies this.

---

## 🟡 Remains (from v1)

### C3 — `gate-check.sh:247–263` still runs failing scripts twice
Unchanged from v1 audit. Still:
```bash
if $runner "$REPO_ROOT/$script_path" $args_raw >/dev/null 2>&1; then
    echo "  ✅ $check_id ($script_path)"
else
    echo "  ❌ $check_id: script $script_path failed"
    $runner "$REPO_ROOT/$script_path" $args_raw 2>&1 | sed 's/^/     /' || true
    ...
```
Non-deterministic verifiers (anything that hashes/pings/calls codex) can flip between runs; verifiers with side-effects run twice. Fix is one mktemp + cat as documented in v1.

### C4 — `verify-composed-premium.sh` still scoped only to 07c/07f
`grep -n verify-composed-premium config/stage-gates.yaml` → lines 232 and 289 only. `08_build` and `09_deploy` still do not re-check the composed file. If `wp-builder` downgrades the rendered theme (loses parallax/glassmorphism), nothing alarms. Not addressed.

### M6 — soft-check `partial` answer still silently treated as pass
`scripts/gate-check.sh:287–291`:
```bash
case "$ans" in
    yes|y) echo "    ✅ confirmed" ;;
    no|n)  echo "    ❌ not satisfied"; fail=1 ;;
    *)     echo "    ⚠️  partial / skipped" ;;
esac
```
The catch-all `*` branch doesn't set `fail=1`. Prompts like `legal_blocks: "yes / no / partial"` still allow a `partial` cookie-banner to ship. Unchanged.

### M2 — `verify-visual-qa.sh` orphan/dead status
The script file appears to have been removed (`ls scripts/verify-visual-qa.sh` → not found), but the `visual_qa_passed` soft prompt still lives in `stage-gates.yaml:249–250` and 312–313 as an interactive question instead of a hard check. Either remove the prompt (and drop the doc) or wire a real verifier.

### M4 — CLAUDE.md still contains stale "вызывается ВРУЧНУЮ" NOTEs
Lines 30, 47, 69 still say PR-A/B/C commands are manual ("не через `landing-orchestrator`"), even though Phase 8 wired the orchestrator to call them and `/landing-go` is the documented happy path. Contradiction the agent has to resolve at runtime.

### MINOR-1/2/3/4 — all unchanged
- `stage-gates.yaml` schema validation: still missing.
- `gate-state.sh:46` accepts `skipped` as approved-equivalent, undocumented in template header comment.
- `failed` status is still aspirational — no script transitions to it.
- `06_stack` `http_ping` checks ping external CDNs every gate-run.
- `premium-07b-checklist.md` has 20 features, `verify-composed-premium.sh` checks 13 per CLAUDE.md.

---

## 🔴 NEW edge-case findings

### NEW-1 (HIGH) — Hook PIPELINE_ORDER mismatches `gate-check.sh` for 09/10
**Evidence:**
- `scripts/hooks/enforce_stage_gate.py:35–41` defines order `..."08_build", "09_deploy", "10_qa", "11_analytics", "12_seo"`.
- `scripts/gate-check.sh:110–115` defines order `..."08_build", "10_qa", "09_deploy", "11_analytics", "12_seo"`.
- The dependency graph (`stage-gates.yaml:391`) makes 09_deploy `require_approved: ["08_build", "10_qa"]` — so the gate-check order is correct, hook is wrong.

**Impact:** verified by running hook against `09_deploy: locked, 10_qa: locked`:
- **Allows** writes to `09_ДЕПЛОЙ/` even when 10_qa not approved (deploy without QA — the more dangerous case).
- **Blocks** writes to `10_QA/` until 09_deploy approved (impossible — you QA before deploying; agent can never produce QA report).

**Concrete fix:** swap the order in `enforce_stage_gate.py:40` to `"08_build", "10_qa", "09_deploy", ...` to match the declared dependency graph, and ideally derive the order from `stage-gates.yaml` rather than duplicating.

### NEW-2 (MEDIUM) — `Bash` tool not in matcher → trivial shell-escape
**Evidence:** matcher is `Write|Edit|MultiEdit`. A `Bash(...)` invocation like `bash -c 'cat > 04_БРЕНД/brand-kit.md <<EOF ... EOF'` is not intercepted by the hook. Confirmed: payload `{"tool_name":"Bash","tool_input":{"command":"echo hi > /tmp/test-proj-cyrillic/04_БРЕНД/brand-kit.md"}}` returns exit 0.

**Impact:** any agent (or user) instructed to "use the Bash tool" can bypass the gate. The `permissions.allow` list in `.claude/settings.json` allows `Bash(echo:*)`, `Bash(cat:*)`, `Bash(cp:*)`, `Bash(mv:*)` etc., all of which can write files.

**Concrete fix:** either (a) add `Bash` to the matcher and have the hook parse `tool_input.command` for redirects/heredocs/`cp`/`mv`/`tee` targets, or (b) deny file-writing Bash patterns at the `permissions.deny` level. Option (a) is more thorough but fragile (shell parsing). Option (b) is simpler but blocks legitimate uses.

### NEW-3 (MEDIUM) — Empty/sparse state file = silent bypass
**Evidence:** verified with `touch .landing-state.yaml; mkdir 04_БРЕНД; <write payload>` → exit 0. The loop `for prev_stage in PIPELINE_ORDER[:idx]:` skips any stage whose key is missing or whose `status` is `None`. Combined with `test_missing_predecessor_treated_as_na` (codified as design), this is "the hook always allows when the state file is incomplete".

**Impact:** an agent that creates an empty state file (or one that drops keys) gains a free pass. The mitigation is `template/.landing-state.yaml` shipping with all keys → but only if the project was created via the template, and only if those keys aren't deleted later.

**Concrete fix:** in `_stage_predecessors_approved`, change the `if status is None: continue` to `if status is None: return False, "predecessor 'X' missing from state file"`, OR add an upfront sanity check `if not state.get("stages"): return BLOCK`. Either tightens the contract.

### NEW-4 (MEDIUM) — `01_context` is in hook PIPELINE_ORDER but not declared in `stage-gates.yaml`
**Evidence:** `grep -E '^\s*"01_context":' config/stage-gates.yaml` → no match. The hook nonetheless places it at index 1 in `PIPELINE_ORDER`, and `_stage_paths.yaml:11–12` maps `01_КОНТЕКСТ/**` → `01_context`. If an agent has `01_context: locked` in state, the hook blocks everything downstream — but `gate-check.sh` has no way to approve it (no checks defined). The template ships with `01_context: locked`, so this is "soft-bricked by default" until the user manually edits state.

**Concrete fix:** either declare `01_context` in `stage-gates.yaml` with `lock: soft, hard_checks: []` (so it can be n/a-fied or auto-approved), or drop it from both PIPELINE_ORDER and `_stage_paths.yaml`. In practice it works today because template defaults trip the block, but the asymmetry is real.

### NEW-5 (LOW) — `NotebookEdit` tool not in matcher
The system-reminder enumerates `NotebookEdit` as an available tool. Hook matcher `Write|Edit|MultiEdit` doesn't cover it. Anybody writing `.ipynb` files into a stage folder bypasses the gate. Low impact for this codebase (no Jupyter usage observed), but completeness gap.

### NEW-6 (LOW) — `_stage_paths.yaml` glob translation is naive
`enforce_stage_gate.py:60–64`:
```python
pattern = pattern.replace("{project}", project_root)
pattern = re.escape(pattern).replace(r"\*\*", ".*").replace(r"\*", "[^/]*")
return re.compile(f"^{pattern}$")
```
This works for the simple globs in the file today, but:
- `{project}` is substituted **before** `re.escape`, so a project path containing regex meta-chars (`.`, `+`, `(`) is correctly escaped. ✓
- A path that happens to contain the literal string `\*\*` (very unlikely on disk) would be mistranslated. ✗ (acceptable.)
- Globs `**` and `*` work; no support for `?`, `[a-z]`, brace expansion `{a,b}`. Acceptable for this use case but worth a comment.

### NEW-7 (LOW) — `gate-state.sh set` accepts any string as status
`scripts/gate-state.sh:26–31` writes whatever string the caller passes. No enum validation. An agent (or buggy caller) could set `status: aproved` (typo) and the hook would block forever because the typo ≠ `approved`. A 5-line validator (`case "$status" in locked|in_progress|approved|failed|n/a|skipped) ;; *) exit 1;; esac`) would catch this.

### NEW-8 (INFO) — `08b_style` correctly handled
The audit listed M1 as concern. Phase changes made the architecturally correct call: `08b_style` is intentionally omitted from hook PIPELINE_ORDER (see comment in `enforce_stage_gate.py:42–44`), and `08_КОД/**` maps to `08_build`. `gate-check.sh` still gates `08b_style` independently via `require_approved: ["08_build"]`, which is the desired ordering. This is **good design**, not a gap.

### NEW-9 (INFO) — Hook design is fail-open by policy
This is documented intent (`enforce_stage_gate.py:113–119`): "a broken hook should not brick the user's editing session". The trade-off is reasonable for a Claude Code harness, but it does mean the hook is a "high-confidence assist", not a fortress. Combined with the `Bash` gap (NEW-2), an adversarial agent has multiple escape valves.

---

## ⚪ Pre-existing (not raised in v1)

### PE-1 — `gate-state.sh:46` accepts `skipped` as approved-equivalent
Undocumented in `template/.landing-state.yaml` header comment (lists `locked/in_progress/approved/failed/n/a` only). Either remove `skipped` from `gate-state.sh` or document it.

### PE-2 — `template/CLAUDE.md` is inside the template subdir but bundled into project copies
The `template/CLAUDE.md` content (shown in this session's context) duplicates a lot of master `CLAUDE.md`. Not enforcement-critical, but as a downstream effect: master CLAUDE.md's stale "вызывается ВРУЧНУЮ" notes don't propagate into project CLAUDE.md (cleaner there), so the project-level guidance is actually correct. Fix master CLAUDE.md and the issue evaporates.

### PE-3 — `.claude/settings.local.json` overrides
The local settings ship `bypassPermissions` + `skipDangerousModePermissionPrompt: true` + `skipAutoPermissionPrompt: true`. These don't disable hooks — hooks always run — but they remove the user's ability to be prompted on dangerous Bash, compounding NEW-2.

---

## Verdict

**Approve with changes.** The Phase 5 hook **closes the central v1 finding**. The walkthrough scenario the audit asked about is genuinely blocked. The legacy bypass is tightened. Protocol coverage is now complete. This is a real, measurable improvement to the safety profile.

**However**, the following should land before claiming "audit complete":

| Priority | Finding | Effort |
|---|---|---|
| 🔴 P0 | NEW-1: fix hook PIPELINE_ORDER 09/10 swap (data corruption risk: deploy without QA) | 1 line |
| 🔴 P0 | NEW-3: tighten "missing predecessor = silent pass" (escape valve) | ~5 lines |
| 🟡 P1 | NEW-2: cover Bash redirects/heredoc — at least document the gap in `stage-agent-preamble.md` | hours |
| 🟡 P1 | M4: delete the three "вызывается ВРУЧНУЮ" notes in CLAUDE.md | minutes |
| 🟡 P1 | C3: fix `gate-check.sh` double-invocation of failing scripts | ~5 lines |
| 🟢 P2 | M6: define `partial` semantics (block / warn / require comment) | small |
| 🟢 P2 | C4: re-run `verify-composed-premium.sh` on 08/09 | YAML edit |
| 🟢 P2 | M2: delete orphan visual-qa references | minutes |
| 🟢 P2 | NEW-4: declare `01_context` in stage-gates.yaml or drop from hook | small |
| 🟢 P2 | NEW-7: validate status enum in `gate-state.sh set` | 5 lines |

The single highest-leverage outstanding item is **NEW-1** — the 09/10 PIPELINE_ORDER swap is the kind of bug that does real harm in production (an agent could deploy a landing that has never been QA'd, because the hook allows it). One-line fix in `scripts/hooks/enforce_stage_gate.py:40`.

Overall, the enforcement layer has moved from "policy without police" to "policy with police that have a few documented gaps and one misconfigured beat". Good progress.
