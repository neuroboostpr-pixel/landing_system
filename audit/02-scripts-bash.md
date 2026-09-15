# Code Review: scripts/*.sh + .githooks/

Reviewed scripts (in scope):
`scripts/gate-check.sh`, `gate-state.sh`, `render-pipeline-map.sh`, `landing-final-check.sh`,
`verify-composed-premium.sh`, `verify-composed-has-visuals.sh`, `verify-content-preserved.sh`,
`verify-gutenberg-json.sh`, `verify-identity-preserved.sh`, `verify-photo-pipeline.sh`,
`verify-php-syntax.sh`, `verify-site-url.sh`, `verify-visual-qa.sh`, `check-deps.sh`,
`check-wiki-sync.sh`, `install-git-hooks.sh`, `install-codex.sh`,
`.githooks/post-commit`, plus the helpers they call (`validate-all.sh`, `preflight.sh`).

## Summary

PR intent (inferred): provide a hard pipeline gating mechanism so agents cannot skip
landing-system stages, plus a post-commit auto-rebuild for the wiki.

**Overall: Request Changes.** Two of the most important rails are leaky:

1. **`gate-check.sh` silently passes any check whose `type` it doesn't recognise.**
   Stage-gates.yaml already uses two such types (`file_or_dir_exists`,
   `dir_has_files`) — they are currently no-ops that print a warning and let the
   gate succeed. That's the exact "agent skips a stage" failure mode the gate is
   supposed to prevent.
2. **`.githooks/post-commit` will happily auto-commit during merges / rebases /
   amends, can stage secrets via `git add wiki/` if `wiki/` accidentally contains
   a `.env`, and exits 0 on every internal failure** — so a broken compiler is
   invisible.

Several `verify-*.sh` scripts are good (proper `set -euo pipefail`, NUL-safe `find -print0`,
clear exit codes). Several others are weaker than they should be for a "hard gate"
contract (output suppressed, missing pipefail, etc.). Details below, prioritised.

---

## Critical (must fix)

### C1. `gate-check.sh:166-168` — unknown check types pass silently
The dispatcher only handles `file_exists | http_ping | api_validator | api_validator_any_of | script`.
Anything else hits:
```bash
*)
    echo "  ⚠️  $check_id: unknown type $check_type" >&2
    ;;
```
…which does **not** set `fail=1`. `config/stage-gates.yaml` already uses two
unhandled types:

- `config/stage-gates.yaml:189` — `type: file_or_dir_exists` for
  `07a_prototype.prototype_source_exists` (the very first gate after onboarding).
- `config/stage-gates.yaml:266` — `type: dir_has_files` for `07d_photos.photos_inbox`.

Right now both checks succeed unconditionally — an agent can "approve" 07a with
zero prototype source on disk, exactly the scenario this rail is supposed to
block.

**Fix:** treat unknown types as hard failures (or implement them). Minimum patch:
```bash
*)
    echo "  ❌ $check_id: unknown type '$check_type' — refusing to pass" >&2
    fail=1
    ;;
```
Then implement the two missing types:
```bash
file_or_dir_exists)
    path="$(yq -r ".stages.\"$stage\".hard_checks[$i].path" "$GATES_YAML" | sed "s|{project}|$project|g")"
    if [ -e "$path" ]; then echo "  ✅ $check_id ($path)"
    else echo "  ❌ $check_id: missing $path"; fail=1; fi
    ;;
dir_has_files)
    path="$(yq -r ".stages.\"$stage\".hard_checks[$i].path" "$GATES_YAML" | sed "s|{project}|$project|g")"
    if [ -d "$path" ] && [ -n "$(ls -A "$path" 2>/dev/null)" ]; then
        echo "  ✅ $check_id ($path)"
    else
        echo "  ❌ $check_id: empty or missing $path"; fail=1
    fi
    ;;
```
Add a bats test that feeds a stage with `type: bogus` and asserts the gate fails.

### C2. `gate-check.sh:91` — `legacy: true` bypasses **every** hard check on **every** stage
```bash
if [ -f "$project/.landing-state.yaml" ] && grep -q "^[[:space:]]*legacy:[[:space:]]*true" ...; then
    echo "  ⚠ legacy:true — skipping all hard checks for $stage"
    checks_count=0
```
A single top-level `legacy: true` in any project's state file silently disables
the entire enforcement system. The grep is also lax: it matches anywhere in the
file (including a nested `stages.XX.legacy: true`).

**Fix:**
- Anchor strictly to the top level (use `yq -r '.legacy // false'` instead of grep).
- Require an explicit `legacy_bypass_until: <ISO date>` and refuse to bypass past
  that date, so legacy mode can't outlive its purpose.
- Log a CRITICAL line that names the project, the stage, and the user. A bypass
  that prints `⚠` and continues looks like a noisy warning — the agent will read
  past it.

### C3. `gate-check.sh:208-214` — wiki/pipeline-map auto-update runs on EVERY invocation but checks `fail` after `set -uo pipefail` may have re-set it
The "PR-G" block is `if [ "${fail:-1}" = "0" ]` — but `fail` is set to either
`0` (default) or `1` by the loop; after the early `exit 1` paths it would never
reach here. So the wiki write actually runs **whenever no failures occurred**,
which is fine — but the comment `if successful gate-check` is misleading because
this also triggers when `--approve` was passed (good) and when only soft checks
ran (probably fine). More importantly:

```bash
cd "$REPO_ROOT" && python3 -m scripts.wiki.compile ... >/dev/null 2>&1 || true
```
Suppressing both stdout and stderr **and** `|| true` means a broken wiki
compiler will never surface — same anti-pattern as the post-commit hook. Drop
the `2>&1` redirect, keep `|| true`, so errors are visible without breaking the
gate.

### C4. `gate-check.sh:148-164` — `script` runner has shell-injection + suppression problems
```bash
args_raw="$(yq -r ".stages.\"$stage\".hard_checks[$i].args[] // \"\"" "$GATES_YAML" | sed "s|{project}|$project|g")"
case "$script_path" in *.sh) runner="bash" ;; *) runner="python" ;; esac
# shellcheck disable=SC2086
if $runner "$REPO_ROOT/$script_path" $args_raw >/dev/null 2>&1; then
```
Problems:
1. `args_raw` is unquoted on purpose (the disable comment), but the substitution
   uses word-splitting and globbing. If `$project` contains spaces (the
   repo path itself has spaces — `"Обучение вайбкодинг Кодекс"`),
   `$args_raw` becomes multiple tokens and the script receives the wrong args.
   This silently runs the verifier on the wrong path, hiding real failures.
2. The first invocation suppresses stderr (`>/dev/null 2>&1`). On success, fine.
   On failure, the script is re-run a second time (line 161) — this is
   **double-execution** of every failed check (wastes time, and is unsafe if the
   verifier has side effects).

**Fix:** stop word-splitting; collect args into an array.
```bash
mapfile -t args_arr < <(
  yq -r ".stages.\"$stage\".hard_checks[$i].args[] // empty" "$GATES_YAML" \
  | sed "s|{project}|$project|g"
)
output=$("$runner" "$REPO_ROOT/$script_path" "${args_arr[@]}" 2>&1)
status=$?
if [ "$status" -eq 0 ]; then echo "  ✅ $check_id ($script_path)"
else
    echo "  ❌ $check_id: script $script_path failed"
    echo "$output" | sed 's/^/     /'
    [ -n "$fix_hint" ] && echo "     → $fix_hint"
    fail=1
fi
```
This eliminates the re-run, fixes the quoting, and still suppresses output on success.

### C5. `.githooks/post-commit:30-34` — auto-commit can run during merge/rebase/cherry-pick/amend
```bash
if [ -n "$(git status wiki/ --short 2>/dev/null)" ]; then
    git add wiki/
    git commit -m "chore(wiki): авто-обновление после изменений системы" --no-verify
fi
```
There is no guard against being inside a merge or rebase. A `chore(wiki)` commit
landing in the middle of a `git rebase -i` or `git merge` produces a confusing
extra commit (or, worse, a merge commit with wiki noise). The earlier
"recursion guard" only checks the **last** commit message — that breaks the
moment the user `git commit --amend`s a `chore(wiki)` commit into something
else, then commits again.

**Fix:** abort the hook if `.git/MERGE_HEAD`, `.git/CHERRY_PICK_HEAD`,
`.git/REVERT_HEAD`, or `.git/rebase-apply` / `.git/rebase-merge` exist:
```bash
GIT_DIR="$(git rev-parse --git-dir)"
for marker in MERGE_HEAD CHERRY_PICK_HEAD REVERT_HEAD rebase-apply rebase-merge; do
    if [ -e "$GIT_DIR/$marker" ]; then
        echo "post-commit: skipping wiki auto-commit during $marker" >&2
        exit 0
    fi
done
```

### C6. `.githooks/post-commit:31` — `git add wiki/` can commit anything that lands in wiki/
`wiki/` is a directory the compiler regenerates. If the compiler ever writes a
secret-bearing artefact there (a debug dump, an error trace containing a key
from `.env`, etc.), the hook silently commits it with `--no-verify`, skipping
any pre-commit secret scanners the user has installed.

**Fix:**
- Drop `--no-verify` (or document why it's needed — pre-commit hooks should
  still run on wiki commits).
- Explicitly stage only known wiki artefacts (`git add wiki/*.md wiki/concepts/`),
  never the whole directory.
- Add a sanity check before commit:
  ```bash
  if git diff --cached --name-only | xargs grep -lE 'sk_live_|sk-[A-Za-z0-9]{32}|BEGET_PASSWORD' 2>/dev/null; then
      echo "post-commit: refusing to commit possible secret in wiki/" >&2
      git reset wiki/
      exit 1
  fi
  ```

### C7. `.githooks/post-commit:24-28` — compile failure is invisible
```bash
if ! python3 -m scripts.wiki.compile --source-mode=system 2>&1 | tail -3; then
    echo "⚠️  compile.py упал — wiki не обновлена. Запусти вручную:"
    ...
    exit 0  # не блокируем commit
fi
```
Two problems:
1. The `if !` test reads the pipeline exit status — but pipefail is **not** set
   (only `set -uo pipefail` is set at the top of the file). Without `set -o
   pipefail`, the status reflects only `tail -3` (which almost always succeeds),
   so the failure branch never runs.
2. Even if it did, the hook exits 0 — so the warning vanishes from any agent's
   automated output and the wiki drifts silently. `check-wiki-sync.sh` then
   surfaces it many commits later as if it were the user's fault.

**Fix:**
```bash
set -euo pipefail   # at top of script
...
output=$(python3 -m scripts.wiki.compile --source-mode=system 2>&1) || {
    echo "::warning:: wiki compile failed:" >&2
    echo "$output" | tail -20 >&2
    exit 0   # still don't break commit, but at least visible
}
```

### C8. `landing-final-check.sh:38` — `eval "$CMD"` with embedded single-quoted paths
```bash
CHECKS=(
    "wiki-sync|bash '$REPO_ROOT/scripts/check-wiki-sync.sh'|no"
    "composed-premium|bash '$REPO_ROOT/scripts/verify-composed-premium.sh' '$PROJECT/07b_COMPOSED/composed.html'|yes"
    ...
)
...
OUTPUT=$(eval "$CMD" 2>&1) || EXIT=$?
```
`eval` on a string assembled from `$REPO_ROOT` and `$PROJECT`. If a project name
contains a single quote (unlikely but possible) the eval breaks open the
quoting and runs arbitrary code. Even if you trust your own paths, `eval` is
unnecessary here.

**Fix:** store the script + args as bash arrays and dispatch directly:
```bash
declare -a CHECKS=(
    "wiki-sync:no:bash:$REPO_ROOT/scripts/check-wiki-sync.sh"
    "composed-premium:yes:bash:$REPO_ROOT/scripts/verify-composed-premium.sh:$PROJECT/07b_COMPOSED/composed.html"
    ...
)
for entry in "${CHECKS[@]}"; do
    IFS=':' read -r NAME REQUIRED RUNNER SCRIPT ARG1 <<< "$entry"
    OUTPUT=$("$RUNNER" "$SCRIPT" ${ARG1:+"$ARG1"} 2>&1) || EXIT=$?
    ...
done
```
(Or use a per-check function — `eval` is the wrong tool.)

Also: the `OUTPUT=$(...) || EXIT=$?` idiom is broken under `set -e` because the
subshell return value is captured. Here `set -e` is NOT set (only `set -uo
pipefail`), so it accidentally works, but the `EXIT="${EXIT:-0}"` default would
also trigger if the previous iteration failed — `unset EXIT` at end of loop
(line 60) handles it, but easy to miss.

### C9. `verify-composed-has-visuals.sh:19` — placeholder regex is too narrow
```bash
grep -qE '\[SLOT:|\[INFOGRAPHIC:|\[photo slot:' "$FILE"
```
Other parts of the system emit placeholders like `[ICON:`, `[CHART:`,
`[VISUAL:`, `[photo:hero]`, and the Russian variants (`[ФОТО:`, `[ИКОНКА:`).
`block-composer.md` and the photo skill use these. If a composed.html contains
`[ICON: feature-1]` but no `[SLOT: ...]`, this script reports OK and the 07f
hard-gate passes — exactly the leak this script is meant to catch.

**Fix:** broaden the pattern and pull the canonical list from
`docs/standards/`:
```bash
PLACEHOLDER_RE='\[(SLOT|INFOGRAPHIC|ICON|CHART|VISUAL|PHOTO|ФОТО|ИКОНКА|photo slot)[: ]'
if grep -qE -- "$PLACEHOLDER_RE" "$FILE"; then ...
```
Plus a unit test with each placeholder variant.

### C10. `gate-check.sh` PIPELINE_ORDER is out of sync with `render-pipeline-map.sh` and `config/stage-gates.yaml`
`gate-check.sh:54-59` lists 20 stages but `render-pipeline-map.sh:39-44`
lists 21 (adds `08b_style`). `08b_style` exists in `config/stage-gates.yaml:354`
and gates real artefacts (`block_php_markers`, `section5_has_css`). Result:

- `gate-check.sh`'s soft-lock "previous stage approved?" warning **does not
  fire** for `08b_style` (the loop never finds it in PIPELINE_ORDER, so `prev`
  stays empty → no warning ever shown).
- Order between 10_qa and 09_deploy is also unusual (10_qa before 09_deploy in
  both arrays). Worth a comment explaining why.

**Fix:** single source of truth. Generate the array from
`config/stage-gates.yaml` keys, or factor it into one shared file
(`scripts/lib/pipeline-order.sh`) that both scripts source.

---

## Major (should fix)

### M1. `gate-check.sh:39` — `set +a` after sourcing `.env` swallows export failures
```bash
[ -f "$REPO_ROOT/.env" ] && set -a && . "$REPO_ROOT/.env" && set +a
```
Because `set -e` is not enabled, a malformed `.env` (with `KEY=value with spaces`)
gets partially loaded and the script continues. At minimum, log when `.env` is
missing vs. successfully loaded so the agent can tell.

### M2. Most `verify-*.sh` use `set -uo pipefail` but not `set -e`
`verify-composed-premium.sh:13`, `gate-check.sh:5`, `gate-state.sh:8`,
`render-pipeline-map.sh:15`, `landing-final-check.sh:3`,
`verify-content-preserved.sh:3`, `verify-identity-preserved.sh:3`,
`verify-photo-pipeline.sh:3`, `verify-visual-qa.sh:3`,
`check-wiki-sync.sh:5` — all omit `-e`.

For a "fail loud" verifier, missing `-e` means any unhandled command failure
just continues silently and the script reaches a misleading "OK" print at the
end. Counter-example done right: `verify-composed-has-visuals.sh:10`,
`verify-gutenberg-json.sh:11`, `verify-php-syntax.sh:11`, `verify-site-url.sh:11`
all have `set -euo pipefail`.

**Fix:** standardise on `set -euo pipefail` everywhere unless there's a documented
reason. Where you genuinely want to handle errors locally (`gate-check.sh`'s
script-runner), wrap with `if ! cmd; then ... fi` or `cmd || handle`.

### M3. `verify-composed-premium.sh:32` — the parallax regex matches almost any CSS
```
(scrollY|[^a-zA-Z_0-9]y)[[:space:]]*\*[[:space:]]*0\.[0-9]
```
`[^a-zA-Z_0-9]y * 0.5` matches **any** lowercase `y` preceded by punctuation or
whitespace, multiplied by a small decimal — e.g. `border-radius: calc(border-y * 0.5)`,
random CSS variables, JS code unrelated to parallax. False positives mean the
gate passes even when there's no actual parallax. Replace with a positive match
for the concrete pattern you want, e.g.:
```
window\.scrollY|requestAnimationFrame.*translateY|data-parallax
```

### M4. `verify-composed-premium.sh:38-42` — duplicate / redundant checks
Lines 30, 40 both check `backdrop-filter:[[:space:]]*blur` (same feature, two
checklist items). Line 34 and line 38 both check `IntersectionObserver`. The
script then reports `Passed: 18 / 18` — but several of those 18 are the same
feature. Either dedupe or, better, drive the list from the canonical checklist
markdown so it can't drift.

### M5. `verify-site-url.sh:19-26` — inline heredoc Python uses `yaml.safe_load`, which isn't in stdlib
```python
import yaml, sys
data = yaml.safe_load(...)
```
`pyyaml` is not in the Python stdlib. If the user runs this on a fresh Python
environment, the gate fails with `ModuleNotFoundError`. There's no preflight
check for pyyaml in `check-deps.sh`.

**Fix:** either depend on `yq` (consistent with the rest of the codebase) or
add `pyyaml` to `check-deps.sh` and document it in onboarding.
```bash
URL="$(yq -r '.stages."09_deploy".deploy_url // ""' "$STATE")"
```

### M6. `gate-state.sh:31, 37` — YAML keys are interpolated unsafely into `yq` expressions
```bash
yq -i ".stages.\"$stage\".status = \"$status\" | ...
```
A stage name containing `"` (improbable but possible) breaks the yq expression
or, worse, lets an attacker controlling the state file injects yq
filter syntax. Use `--arg`-style env injection:
```bash
stage="$stage" status="$status" ts="$ts" \
  yq -i '.stages[env(stage)].status = env(status) | .stages[env(stage)].timestamp = env(ts)' "$state_file"
```

### M7. `verify-identity-preserved.sh:13-26` — heredoc embeds shell-interpolated path
```bash
python3 - <<PYTHON
import json, sys
data = json.load(open("$MANIFEST"))
```
`$MANIFEST` is interpolated by the shell into the Python source. A path
containing `"` or `\n` breaks the Python script. Pass via argv instead:
```bash
python3 - "$MANIFEST" <<'PYTHON'
import json, sys
data = json.load(open(sys.argv[1]))
...
```
Note the quoted heredoc tag to prevent shell expansion inside.

### M8. `check-wiki-sync.sh:46-50` — Python invoked per-file (N processes)
```bash
for pattern in "${SOURCES[@]}"; do
    for f in $pattern; do
        ...
        cached_hash=$(python3 -c "import json,sys; c=json.load(open('$CACHE')); ..." 2>/dev/null)
    done
done
```
For a 200-block library this is hundreds of Python startups per invocation.
Also: the inner `for f in $pattern` relies on glob expansion of an unquoted
string — fine here but breaks on filenames with spaces (`.claude/worktrees/` has
none, but `block-library` could). And `'$CACHE'` is interpolated into Python
source — same heredoc-injection risk as M7.

**Fix:** read the cache JSON once in Python and stream filenames in:
```bash
mapfile -t files < <(printf '%s\n' "${SOURCES[@]}" | xargs -n1 ls -1d 2>/dev/null)
python3 - "$CACHE" "${files[@]}" <<'PY'
import json, sys, hashlib, pathlib
cache = json.load(open(sys.argv[1]))
for f in sys.argv[2:]:
    h = hashlib.sha256(pathlib.Path(f).read_bytes()).hexdigest()
    if cache.get(f) != h:
        print(f)
PY
```

### M9. `check-wiki-sync.sh:46` — `for f in $pattern` glob expansion
```bash
for f in $pattern; do
```
If the glob matches nothing, you get the literal pattern as `f` (e.g. `agents/*.md`
when there are no files). The `[ -f "$f" ] || continue` guard catches it, but
relying on that is fragile. Either `shopt -s nullglob` at top, or use `find`.

### M10. `gate-check.sh:179-191` — soft checks silently accept "skipped"
```bash
case "$ans" in
    yes|y) ...
    no|n)  ... fail=1 ;;
    *)     echo "    ⚠️  partial / skipped" ;;
esac
```
Anything that isn't `yes`/`no` is treated as **passing** (because `fail` stays
0). That includes pressing Enter, typing `idk`, or `nyet`. For a system whose
selling point is "agent cannot skip", silent acceptance of unknown answers is
the same skip pattern in a different form.

**Fix:** treat empty / unknown answers as a failure (or at least re-prompt
once). Record the answer into `.landing-state.yaml` so the audit trail shows
what the user actually said.

### M11. `install-codex.sh:50` — writes to predictable `/tmp` path
```bash
if ! npm i -g @openai/codex 2>/tmp/codex-install.err; then
    if grep -qi "eacces..." /tmp/codex-install.err; then
```
`/tmp/codex-install.err` is a symlink-attack vector on multi-user systems (and
also leaks across runs). Use `mktemp`:
```bash
err=$(mktemp -t codex-install.XXXXXX.err)
trap 'rm -f "$err"' EXIT
if ! npm i -g @openai/codex 2>"$err"; then ...
```

### M12. `install-git-hooks.sh:19` — `chmod +x "$HOOKS_DIR/"*` is too broad
```bash
chmod +x "$HOOKS_DIR/"*
```
This makes every file in `.githooks/` executable, including non-hook files
(READMEs, configs). The glob also fails noisily if `.githooks` contains
sub-directories. Either enumerate hooks by known names or filter:
```bash
find "$HOOKS_DIR" -maxdepth 1 -type f -exec chmod +x {} +
```

### M13. `landing-final-check.sh:54` — `head -20` truncates the very evidence the report exists for
Each verify-script's output is truncated to the first 20 lines in the report.
For `verify-composed-premium.sh`, that means the "Failed:" list at the end gets
chopped. Either drop the `head` or `tail -20` the failure tail (errors usually
land at the end).

### M14. `gate-check.sh` — no machine-readable output
The whole stack writes human prose and ANSI-coloured glyphs. An agent that
wants to "know" whether 07b passed has to grep `❌`/`✅` (and a future locale
change breaks it). Add a `--json` mode:
```json
{"stage": "07b_composed", "fail": 0, "checks": [{"id":"...","pass":true}, ...]}
```
…then teach orchestrator + agents to read JSON. This is the single biggest
win for "agents cannot skip".

---

## Minor

- `gate-check.sh:22` — `*) shift ;;` silently drops unknown flags. Should `echo "unknown flag $1" >&2; exit 2`.
- `gate-check.sh:62` — `$stage_lock` default `"soft"` — a YAML stage with no `lock:` key (e.g. `08b_style`, `config/stage-gates.yaml:354`) becomes soft by default. `08b_style` looks like it should be hard. Worth an explicit `lock:` on every entry and a CI check that fails missing keys.
- `gate-check.sh:46` — message reads "Required prior stages approved: $required" even when `$required` is one stage (Russian/English mix). Cosmetic.
- `render-pipeline-map.sh:71` — `render_map` is defined but never `local`-scoped; uses globals. Fine for a one-shot script.
- `verify-photo-pipeline.sh` / `verify-content-preserved.sh` / `verify-visual-qa.sh` are 4-line `exec python3 ...` wrappers — could be replaced by direct calls in stage-gates.yaml (`type: script` already supports `.py`, line 154 of gate-check.sh). Dead-weight indirection.
- `verify-php-syntax.sh:22` — exits 2 ("dir missing OR php not installed") in two different conditions. The gate then can't distinguish "PHP not installed on dev box" (fine to ignore) from "directory missing" (real failure).
- `check-deps.sh` does **not** check for `yq`, `python3`, `php`, `curl`, or `pyyaml` — all of which are required by other scripts. Misleading "All dependencies OK." after this script passes.
- `install-codex.sh:64` — uses `codex auth status` but the codex CLI may not have that subcommand (varies by version). No version pin.
- `.githooks/post-commit:7` — `cd "$REPO_ROOT"` without checking it succeeded. With `set -u` only (no `-e`), a failed cd is fatal at next reference but with confusing error. Use `cd "$REPO_ROOT" || exit 0` (don't break commits).
- `verify-composed-premium.sh:24` — the heredoc-stored checklist drifts from `docs/standards/premium-07b-checklist.md`. Generate one from the other.
- `gate-state.sh:46` — `[ "$status" != "approved" ] && [ "$status" != "skipped" ] && [ "$status" != "n/a" ]` — three different "ok" tokens with no schema validation. Easy for an agent to write a different token (`done`, `complete`, `ok`) and silently bypass the check.

---

## Positive

- **`verify-composed-has-visuals.sh`, `verify-gutenberg-json.sh`, `verify-php-syntax.sh`, `verify-site-url.sh`** all use `set -euo pipefail` correctly, document exit codes in the header, and use `find -print0`/`read -d ''` for NUL-safe file iteration. Good template.
- `gate-check.sh` separating `hard_checks` (machine) from `soft_checks` (human) is the right design.
- `gate-state.sh` recording an ISO-8601 UTC timestamp on every state change is exactly right — gives the audit trail real value.
- `render-pipeline-map.sh` writing to `wiki/pipeline-map.md` on every gate-check is a smart, low-cost way to keep the visible state in sync without extra commands. The Mermaid output is genuinely useful for both humans and agents.
- `install-codex.sh` handles the EACCES case explicitly with actionable advice — nicer than the typical "npm exited 1" black box.
- `verify-composed-premium.sh` storing the checklist as `pattern<TAB>desc` and looping with `read -r` is idiomatic. Once the regexes are tightened (M3) and de-duped (M4), it's a solid hard-gate.
- `landing-final-check.sh` bundling all post-deploy checks into one markdown report under `10_QA/final-check-report.md` is exactly the right move for handoff.

---

## Verdict

**Request Changes.** Fix at minimum **C1, C2, C5, C7, C8, C9, C10** before relying on
this gate to stop agents from skipping stages — today, several of them are
already skippable. The post-commit hook needs C5/C6/C7 before it can be trusted
to auto-commit on user machines.

After the criticals, M2 (uniform `set -euo pipefail`), M10 (soft-check
default-pass), and M14 (JSON mode) are the biggest reliability wins.

### Suggested test additions (bats)
1. `gate-check.sh` with stage that has `type: bogus` → expect exit 1 (currently exit 0).
2. `gate-check.sh` with stage using `file_or_dir_exists` and no path → expect exit 1.
3. `gate-check.sh` invoked with `$project` containing spaces → expect script runner to receive correct args (currently broken — C4).
4. `.githooks/post-commit` invoked during simulated rebase (`touch .git/rebase-merge/head-name`) → expect to skip auto-commit (currently commits anyway — C5).
5. `verify-composed-has-visuals.sh` with `[ICON: foo]` only → expect exit 1 (currently exit 0 — C9).
6. `gate-state.sh` with status `done` → currently `all_approved` rejects this (good), but no schema validator enforces allowed values when writing.
