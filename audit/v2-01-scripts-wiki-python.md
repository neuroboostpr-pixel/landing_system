# Code Review v2: scripts/wiki/ + scripts/*.py

**Date:** 2026-05-20
**Branch:** `feat/audit-top10-fixes` (40 commits)
**Methodology:** Jeffallan code-reviewer skill (Context → Structure → Details → Tests → Feedback)
**PR Intent (one sentence):** Land the Top-10 audit fixes — primarily token-leak repairs (#5, #6) and the new PreToolUse stage-gate enforcement hook (#1) — without regressing the rest of the Python pipeline.

---

## Summary

The two Top-10 Python fixes (#5 O(N²) cache write, #6 SDK-error hash cache) are **correctly implemented and survive code review**. The new `scripts/hooks/enforce_stage_gate.py` (Phase 5) is **solid, fail-open, well-tested (6/6 pass), but has two real consistency bugs** with `config/stage-gates.yaml` that should be fixed in a follow-up. All other deferred Python items from v1 remain open (as expected — they were deferred, not in the Top-10).

**Counts:**
- ✅ Fixed and verified: **2** (#5 O(N²), #6 SDK negative-cache)
- 🟡 Deferred (still open as planned): **10**
- 🔴 NEW regressions: **0**
- 🆕 New code reviewed (`enforce_stage_gate.py`): **2 important / 2 minor**
- ⚪ Pre-existing not in v1: **1** (`schema_version: 2` parsing path is fragile if state corrupts mid-flight — minor)

**Verdict:** **Approve with follow-up** — the merge is regression-free, but the two `enforce_stage_gate.py` inconsistencies with `stage-gates.yaml` (PIPELINE_ORDER missing `08b_style`; ordering of `09_deploy`/`10_qa` disagrees) should be tracked as a follow-up since they will mis-enforce real production stages once `08_build` lands.

---

## ✅ Fixed (verified against v1 audit)

### #5 — O(N²) `save_cache` inside per-file loop — FIXED
**File:** `scripts/wiki/system_compiler.py:199–208`

The per-iteration `hash_cache.save_cache(...)` is gone from inside the loop. A single guarded call now runs ONCE after the loop:

```python
# Line 199-202
if not dry_run:
    utils.atomic_write(concept_path, content)
    cache[rel_key] = hash_cache.compute_hash(source_path)
compiled.append(rel_key)

# Line 207-208 — outside the for-loop, single write
if not dry_run and (compiled or errors):
    hash_cache.save_cache(cache_path, cache)
```

**Verification:** For 3 files processed, `save_cache` is invoked at most twice — once during bootstrap (line 147) and once at the end (line 208). The bootstrap call has its own justification (resume after crash) and could be merged into the main loop (v1 finding #1, deferred), but the O(N²) regression is removed. Cache file is 62KB / 473 entries — at the previous per-iteration cadence even one full compile burned ~30 MB of redundant writes. ✅

### #6 — SDK error path now caches source hash — FIXED
**File:** `scripts/wiki/system_compiler.py:179–188`

```python
try:
    content = _compile_concept(source_path, repo_root)
except sdk_client.SDKError as e:
    errors.append(f"{rel_key}: {e}")
    # Кэшируем hash даже при ошибке — иначе post-commit будет
    # звать SDK на этот файл КАЖДЫЙ раз.
    cache[rel_key] = hash_cache.compute_hash(source_path)
    continue
```

The `cache[rel_key] = ...` line is set BEFORE `continue`. The guard at line 207 (`if compiled or errors`) ensures the cache is persisted even when only errors were collected (no successful compiles). This correctly closes the "token leak on every git commit for the same broken file" path. ✅

**One subtle gotcha (acceptable):** the cache update happens BEFORE knowing whether the SDK transiently failed (rate limit, network) or persistently (content filter, malformed input). A genuine transient error now requires the user to manually edit the source file to re-trigger SDK. The trade-off is documented in the inline comment ("кэш починится при следующем коммите с обновлённым source-файлом"). Acceptable given the alternative was infinite retry.

---

## 🟡 Remains (deferred — still open as planned)

| # | Loc | Issue | v1 Ref | Why still open |
|---|---|---|---|---|
| R1 | `lint.py:121–139` | `--llm-check` sends ~235K chars to SDK with no cache | v1 #7 | Phase 2 (token efficiency), not in Top-10; `--llm-check` is opt-in flag, not on hot path |
| R2 | `sdk_client.py:53` | `max_turns=50` (still); should be `max_turns=1` for one-shot generate | v1 #5 | Phase 2; insurance fix, no measured leak |
| R3 | `system_compiler.py:139–147` | Bootstrap pass globs all sources before main loop also globs them (repo walked ~2x) | v1 #1 | Phase 2; correctness-neutral now that #5 is fixed |
| R4 | `lint.py:60` & `lint.py:93` | Each concept file is `.read_text()`'d twice (body pass + stale-meta pass) — 946 reads for 473 concepts | v1 #6 | Phase 2; lint runs ad-hoc, not on commit |
| R5 | `flush.py:88` | `except SDKError: return` — silent swallow, no error log | v1 #4 | Cluster F; flush is detached background, low priority |
| R6 | `hash_cache.py:18–20` | Corrupt cache silently treated as empty `{}` → mass SDK re-runs | v1 #17 | Cluster F; rare path (cache only corrupts on crash mid-write) |
| R7 | `hash_cache.py:23–26` | `save_cache` uses plain `cache_path.write_text(...)` — NOT atomic, despite docstring saying "Пишет JSON-кэш атомарно" | v1 #35 | Cluster F; docstring is **misleading** (says atomic, isn't) — see ⚪ Pre-existing below |
| R8 | `cleanup_broken_links.py:44` | `path.write_text(...)` — non-atomic | v1 #21 | Cluster F |
| R9 | `verify_photo_pipeline.py:104–127` | `_find_block_meta(bid, library_root)` called inside per-img loop — re-walks 200+ block library per `<img>` | v1 #20 | Cluster F; cheap fix (cache by `bid`), but not in Top-10 |
| R10 | `session_end.py:25` / `pre_compact.py:26` | Trust `payload.get("transcript_path", "")` from stdin without restricting to `~/.claude/projects/` | v1 #23 | Cluster F; low impact (read-only path; downstream `read_text` would error harmlessly on `/etc/shadow`) |

**Net deferred:** all 10 deferred items remain. None silently fixed, none silently broken. The deferral was explicit (not in Top-10) and the v1 risk assessment still holds.

---

## 🔴 NEW findings (introduced by Phase 1-9)

**None.** Re-reading the diffed files (`system_compiler.py`, `enforce_stage_gate.py`, and adjacent) shows no regressions to existing behaviour. The Phase 1 changes are tightly localized — they add a fall-through to `cache[rel_key] = ...` on SDK error and move one `save_cache` call out of the loop. Test suite (`tests/gate-check/test_enforce_stage_gate.py`) passes 6/6.

---

## ⚪ Pre-existing (not in v1, found now)

### P1 — `hash_cache.save_cache` docstring lies about atomicity
**File:** `scripts/wiki/hash_cache.py:23–26`

```python
def save_cache(cache_path: Path, data: dict[str, str]) -> None:
    """Пишет JSON-кэш атомарно."""
    cache_path.parent.mkdir(parents=True, exist_ok=True)
    cache_path.write_text(json.dumps(data, indent=2, sort_keys=True))
```

The docstring says "атомарно" but the implementation is `write_text(...)`, which is NOT atomic — interrupted writes leave a truncated JSON. v1 #35 flagged the non-atomicity; what's new is the **docstring is actively misleading**, increasing the risk that a future maintainer trusts the docstring and removes any external atomic-write wrapping.

**Fix (cheap):** either implement `utils.atomic_write` here (`utils.atomic_write(cache_path, json.dumps(data, indent=2, sort_keys=True))`) or change the docstring to "Пишет JSON-кэш (non-atomic — caller responsible)". Strong preference for the former since `utils.atomic_write` is right there.

---

## 🆕 `scripts/hooks/enforce_stage_gate.py` — full review

**Lines:** 156
**Tests:** `tests/gate-check/test_enforce_stage_gate.py` — 6/6 PASS (verified via `python3 -m pytest`)

### Strengths

1. **Top-level fail-open wrapper (`main` → `_main_inner` with broad `except`)** — `enforce_stage_gate.py:108–119`. The right call. A broken hook on every Write/Edit would brick the user. Stderr message includes exception type + message so issues are visible without being blocking. Pattern matches `gate-check.sh` philosophy.
2. **Path mapping externalized to `_stage_paths.yaml`** — keeps prompts/code/data separate; mappings are reviewable.
3. **`always_allowed` allowlist** correctly lets edits to `.landing-state.yaml`, `wiki/`, `.env`, `deploy.sh` bypass gate (these MUST be writable from any stage).
4. **Missing predecessors treated as implicit `n/a`** — `enforce_stage_gate.py:96–98`. Load-bearing for prototype-first projects per `CLAUDE.md`. Explicitly tested (`test_missing_predecessor_treated_as_na`).
5. **Test coverage** is unusually comprehensive for a hook script — covers pass, block, allowed, outside-project, missing-key, AND corrupt-state-file (fail-open) cases. Tests use real subprocess invocation, not unit mocks — high signal.
6. **JSON.decode error fail-open** at `_main_inner:126–128` — bad payload from harness doesn't break editing.

### Important (should fix before relying on this in production)

#### I1 — `PIPELINE_ORDER` is out of sync with `config/stage-gates.yaml`
**File:** `enforce_stage_gate.py:35–42` vs `config/stage-gates.yaml`

Two concrete inconsistencies:

**a) `08b_style` missing from PIPELINE_ORDER.** Comment on line 42–44 says "intentionally omitted — sub-phase of 08_build". But `stage-gates.yaml:359–386` defines `08b_style` as a top-level stage with `require_approved: ["08_build"]` and its own hard_checks. And `_stage_paths.yaml` routes `08_КОД/**` → `08_build` (not `08b_style`). The hook will therefore enforce `08_build` predecessors for both 08_build and 08b_style edits — meaning **`08b_style` gate logic is bypassed at the hook level**. Whether that's intentional should be documented in both files (right now only the hook comment exists; `stage-gates.yaml` doesn't acknowledge the merge).

**b) `09_deploy` requires `10_qa` per `stage-gates.yaml:388–391`, but in `PIPELINE_ORDER` `09_deploy` (index 16) comes BEFORE `10_qa` (index 17).** The hook's `_stage_predecessors_approved` walks `PIPELINE_ORDER[:idx]` only — so editing in `09_ДЕПЛОЙ/` will NOT block on `10_qa` even though `gate-check.sh` would. Two enforcement layers, two different rules. Confusing for the user and a real footgun when a sub-agent tries to deploy.

**Fix:** load `PIPELINE_ORDER` from `config/stage-gates.yaml` keys (preserve insertion order; Python 3.7+ dicts are ordered) so there's a single source of truth. Or codify the discrepancies as intentional with prose justification in `_stage_paths.yaml`.

#### I2 — `_glob_to_regex` doesn't validate that the project root is safe to interpolate
**File:** `enforce_stage_gate.py:60–64`

```python
def _glob_to_regex(glob: str, project_root: str) -> re.Pattern[str]:
    pattern = glob.replace("{project}", project_root)
    pattern = re.escape(pattern).replace(r"\*\*", ".*").replace(r"\*", "[^/]*")
    return re.compile(f"^{pattern}$")
```

`re.escape` runs AFTER `{project}` substitution, so any regex metacharacters in `project_root` (dots, brackets) are properly escaped. ✅ Verified empirically: `/Users/a.b/proj/` matches only literal `a.b`, not `aXb`. Good.

**However:** the order also means that `{project}` cannot contain a literal `**` — the substitution string would be `re.escape`-d as `\*\*` and then UN-escaped back into `.*`. Hypothetical: a malicious folder named `**` in someone's home dir would create a wildcard. Probably not exploitable in practice (project_root comes from `_find_project_root` which finds `.landing-state.yaml`; planting one in `/Users/**/` requires write access already), but worth a defensive `assert "**" not in project_root` or a hardened replace that uses a sentinel.

### Minor

#### M1 — `_find_project_root` walks until filesystem root with no depth limit
**File:** `enforce_stage_gate.py:51–57`

For an edit deep in `/Users/.../Lendings/foo/01a_АНАЛИЗ_НИШИ/.../bar.md`, this is fine. But for paths outside any project (e.g. `/tmp/foo.txt`), it walks all the way to `/`. Cheap, but accumulates resolve() calls. Cap to a sane depth (e.g. 20) or short-circuit if `parent == parent.parent` (root reached).

#### M2 — Path map is re-read on every hook invocation
**File:** `enforce_stage_gate.py:47–48`

`_load_path_map()` reads `_stage_paths.yaml` and parses it on EVERY Write/Edit. Tiny file (~60 lines), but the hook runs N times per agent turn. `functools.lru_cache` on the loader would be ~free since the script is short-lived (cache survives a single hook invocation only, but globs are also re-built on each call — that's the real cost, ~20 `re.compile` per hook). For a long agent session with hundreds of edits, this is measurable. Pre-compile globs once at module load.

### Performance verdict

Running on every Write/Edit/MultiEdit is fine **at current scale**. For a chatty session (50 edits), the hook does ~50 × (yaml parse + 22 regex compiles + path resolves) ≈ tens of ms total. Acceptable.

### Hook contract verdict

✅ Correctly returns `0` for allow, `2` for block (matches Anthropic Claude Code PreToolUse spec). Stderr messages are user-facing and actionable (mention the predecessor stage + remediation: "Run gate-check.sh and approve previous stages"). Good UX for the model to act on.

---

## Test verification

```
$ python3 -m pytest tests/gate-check/test_enforce_stage_gate.py -v
============================== 6 passed in 0.21s ===============================
```

Test names cover the right surface:
- `test_allows_write_to_current_stage` — happy path
- `test_blocks_write_to_future_stage` — hard block
- `test_always_allowed_paths_pass` — `.landing-state.yaml` exception
- `test_paths_outside_project_pass` — non-project edits unaffected
- `test_missing_predecessor_treated_as_na` — prototype-first design holds
- `test_corrupt_state_file_allows_edit` — fail-open under poison input

**Missing test coverage (suggest adding):**
- Bypass attempt via symlink: place a symlink in a project dir pointing to outside → does `_find_project_root` get confused? (`file_path.resolve()` should defend, but no explicit test).
- `_stage_paths.yaml` missing or malformed — main calls `_load_path_map()` outside the wrapper; would `FileNotFoundError`/`YAMLError` be caught by the top-level `except`? **Yes** (line 111: `except Exception`) — but no test asserts this. One-line test would lock the contract.
- `08_КОД/style/foo.css` (would-be 08b_style territory) — explicit test that it routes to `08_build` per the documented merge.

---

## Verdict

**Approve regression-free**, with two follow-up tickets:

1. **(Important)** Reconcile `enforce_stage_gate.PIPELINE_ORDER` with `config/stage-gates.yaml` — either generate it from the YAML or document the merged stages (`08b_style`) and the deliberate divergence on `09_deploy`/`10_qa` ordering. Otherwise the two enforcement layers disagree, which is exactly the "policy without police" pattern v1 warned against.
2. **(Cheap)** Fix the misleading docstring in `hash_cache.save_cache` — either implement `utils.atomic_write` (preferred; it's already imported elsewhere) or change the docstring to say non-atomic.

All other deferred items (R1–R10) carry forward to Phase 2 (token efficiency) as planned in `audit/REPORT.md`.
