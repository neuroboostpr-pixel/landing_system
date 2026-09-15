# Second-Pass Review: `scripts/*.sh` + `.githooks/`

**Дата:** 2026-05-20 (v2)
**Базовый отчёт:** [`audit/02-scripts-bash.md`](02-scripts-bash.md), Top-10 в [`audit/REPORT.md`](REPORT.md)
**Скоуп фаз 1-4 фиксов:** Cluster A (enforcement), Cluster D (auto-commit safety).
**Cluster E (verifier hygiene) явно отложен** — отмечаю что осталось.

---

## Summary

PR intent (recap): закрыть top-10 утечки enforcement-гейтов (#3 unknown types, #4 legacy bypass, #7 post-commit safety) после первого аудита, не трогая Cluster E.

**Verdict: Approve with Comments.** Все три заявленных top-10 фикса сделаны корректно. `gate-check.sh` теперь fail-hard на unknown types и реализует `file_or_dir_exists` + `dir_has_files` с edge-cases (empty dir, brace-pattern reject). `legacy: true` bypass теперь требует allowlist + reason + пишет TSV-лог. `post-commit` получил `set -Eeuo pipefail`, ERR-trap с `exit 0`, защиту от merge/rebase/cherry-pick/bisect, явный список путей вместо `git add wiki/`, убран `--no-verify`.

Cluster E как и было заявлено — не трогали. Несколько новых мелочей всплыли в Phase 2/4 правках (см. NEW), все низкого риска.

---

## 🟢 FIXED (top-10 verified)

### F1. C1 / Top-10 #3 — unknown check types now hard-fail
`scripts/gate-check.sh:265-269`
```bash
*)
    echo "  ❌ $check_id: unknown check type '$check_type'" >&2
    echo "     → implement this type in scripts/gate-check.sh ..." >&2
    fail=1
    ;;
```
Default case sets `fail=1` and prints actionable hint. Matches the patch proposed in C1.

### F2. C1 / Top-10 #3 — `file_or_dir_exists` implemented with empty-dir check
`scripts/gate-check.sh:168-184`
```bash
file_or_dir_exists)
    path="$(yq -r ...| sed "s|{project}|$project|g")"
    if [ -e "$path" ]; then
        if [ -d "$path" ] && [ -z "$(ls -A "$path" 2>/dev/null)" ]; then
            echo "  ❌ $check_id: directory $path exists but is empty"
            fail=1
        else
            echo "  ✅ $check_id ($path)"
        fi
    else
        echo "  ❌ $check_id: missing $path"
        fail=1
    fi
    ;;
```
Edge case (empty directory) handled — that's *better* than the original C1 fix proposal which would have passed on an empty dir.

### F3. C1 / Top-10 #3 — `dir_has_files` implemented with pattern + min_count + brace-pattern detection
`scripts/gate-check.sh:185-211`
```bash
dir_has_files)
    path="$(yq ... | sed ...)"
    pattern="$(yq -r ... // \"*\")"
    min_count="$(yq -r ... // 1)"
    if [ ! -d "$path" ]; then ... fail=1
    else
        case "$pattern" in
            *\{*)
                echo "  ❌ $check_id: brace patterns not supported ($pattern)"
                echo "     → use a single fnmatch glob ..."
                fail=1
                continue
                ;;
        esac
        count="$(find "$path" -maxdepth 1 -type f -name "$pattern" | wc -l ...)"
        if [ "$count" -ge "$min_count" ]; then
            echo "  ✅ ..."
        else
            echo "  ❌ ... has $count files matching '$pattern', need ≥$min_count"
            fail=1
        fi
    fi
```
Properly handles pattern (defaults `*`), min_count (defaults 1), rejects brace patterns (which `find -name` doesn't expand). `find -maxdepth 1` is correct — only top-level files, matching intent.

### F4. C2 / Top-10 #4 — legacy bypass is now strict
`scripts/gate-check.sh:43-93`

- Uses `yq -r ".stages.\"$stage\".legacy // false"` (anchored, no loose `grep`).
- Falls back to top-level `legacy: true` for backwards compat with pre-PR-D state files.
- Requires `$stage` ∈ `legacy_allowed` from `config/stage-gates.yaml` (`legacy_allowed: []` by default — defaults to *no bypass possible*).
- Requires non-empty `legacy_reason` field (per-stage or top-level fallback).
- Both missing-allowlist and missing-reason cases `exit 1`, not just warn.
- Logs `<ts>\t<project>\t<stage>\t<reason>` to `${LANDING_SYSTEM_ROOT:-$REPO_ROOT}/audit/legacy-bypass.log` (TSV, with tab escaping in reason/project to keep parseable).
- Bypass also disables `require_approved` check (line 96) so legacy projects don't get blocked on prior-stage approvals.

This is stricter than the original C2 fix proposal (no `legacy_bypass_until` date but the allowlist-by-stage is functionally equivalent — Code-Owner has to edit YAML to grant a bypass).

### F5. C5 / Top-10 #7 — post-commit guards against merge/rebase/cherry-pick/bisect
`.githooks/post-commit:17-25`
```bash
GIT_DIR="$(git rev-parse --git-dir)"
for marker in MERGE_HEAD REBASE_HEAD CHERRY_PICK_HEAD BISECT_LOG; do
    if [ -e "$GIT_DIR/$marker" ] || [ -d "$GIT_DIR/rebase-merge" ] || [ -d "$GIT_DIR/rebase-apply" ]; then
        echo "ℹ️  post-commit: skip wiki rebuild (in $marker / rebase state)"
        exit 0
    fi
done
```
Covers MERGE / REBASE / CHERRY_PICK / BISECT plus interactive rebase dirs (`rebase-merge`, `rebase-apply`). Matches C5 fix recipe.

### F6. C5/C7 — `set -Eeuo pipefail` + ERR trap
`.githooks/post-commit:5-6`
```bash
set -Eeuo pipefail
trap 'echo "post-commit failed at line $LINENO" >&2; exit 0' ERR
```
`-E` propagates trap to functions/subshells; `-e` fails on any unhandled error; `pipefail` makes pipelines fail when any stage fails (fixes C7 — `if !` was previously reading only `tail`'s exit). ERR trap surfaces failure with line number but exits 0 to not break commits.

### F7. C6 — `--no-verify` removed, explicit paths added
`.githooks/post-commit:48-55`
```bash
git add wiki/index.md wiki/log.md wiki/concepts/ wiki/preview.html 2>/dev/null || true
# Без --no-verify ...
if git commit -m "chore(wiki): авто-обновление после изменений системы" 2>&1; then
    echo "✅ wiki/ авто-закоммичено"
else
    echo "⚠️  wiki/ commit заблокирован (pre-commit hook?). Запусти руками."
fi
```
- `git add wiki/` заменён на 4 явных пути.
- `--no-verify` снят (комментарий объясняет, что pre-commit hook должен сработать).
- Commit-failure branch не падает, а предупреждает (правильный UX).

### F8. C2 — `legacy_allowed: []` empty by default in config
`config/stage-gates.yaml:7`
```yaml
legacy_allowed: []  # Empty by default. Add entries explicitly when needed.
```
Default-deny posture. Без явного редактирования YAML — bypass невозможен.

### F9. verify-visual-qa orphan → used
`scripts/landing-final-check.sh:19`
```bash
"visual-qa|bash '$REPO_ROOT/scripts/verify-visual-qa.sh' '$PROJECT'|no"
```
Раньше скрипт нигде не вызывался (Cluster E). Теперь подключён к `landing-final-check.sh` как optional check (`no` = required). Это не было заявлено как fix, но фактически orphan-статус закрыт.

---

## 🟡 REMAINS (Cluster E + concerns explicitly deferred)

### R1. Cluster D — `eval` in `landing-final-check.sh`
`scripts/landing-final-check.sh:38`
```bash
OUTPUT=$(eval "$CMD" 2>&1) || EXIT=$?
```
`$CMD` собирается из строк типа `"bash '$REPO_ROOT/scripts/...' '$PROJECT/...'"` через словосплит на `|`. `eval` остался — атака возможна только если в `$PROJECT` или `$REPO_ROOT` появится одинарная кавычка (низкий риск на ваших путях). Cluster D не сделан полностью.

**Fix path:** as proposed в C8 — массив, dispatch без `eval`.

### R2. Cluster E — `verify-composed-premium.sh` parallax regex слишком широкий
`scripts/verify-composed-premium.sh:28`
```
(scrollY|[^a-zA-Z_0-9]y)[[:space:]]*\*[[:space:]]*0\.[0-9]
```
Не тронуто — Cluster E отложен. `[^a-zA-Z_0-9]y * 0.5` всё ещё match'ит случайный `y` после punctuation. False-positive риск остаётся.

### R3. Cluster E — `verify-composed-has-visuals.sh` placeholder regex узкий
`scripts/verify-composed-has-visuals.sh:19`
```bash
grep -qE '\[SLOT:|\[INFOGRAPHIC:|\[photo slot:' "$FILE"
```
`[ICON:`, `[CHART:`, `[VISUAL:`, `[PHOTO:`, `[ФОТО:`, `[ИКОНКА:` всё ещё не ловятся. 07f hard-gate может пройти при остаточных placeholders иных типов.

### R4. Cluster E — verify-* без `set -e`
Скрипты с `set -uo pipefail` (без `-e`):
- `scripts/gate-check.sh:5` — оставлено намеренно, ок (script-runner handles errors локально).
- `scripts/gate-state.sh:8`
- `scripts/render-pipeline-map.sh:15`
- `scripts/landing-final-check.sh:3`
- `scripts/verify-content-preserved.sh:2`
- `scripts/verify-identity-preserved.sh:3`
- `scripts/verify-photo-pipeline.sh:3`
- `scripts/verify-visual-qa.sh:2`
- `scripts/check-wiki-sync.sh:6`

Скрипты с правильным `set -euo pipefail`:
- `scripts/verify-composed-has-visuals.sh:10`
- `scripts/verify-gutenberg-json.sh:10`
- `scripts/verify-php-syntax.sh:10`
- `scripts/verify-site-url.sh:10`
- `scripts/check-deps.sh:3`
- `scripts/install-git-hooks.sh:5`
- `scripts/install-codex.sh:9`
- `.githooks/post-commit:5` (теперь `-Eeuo`)

Не закрыто. Cluster E.

### R5. `check-deps.sh` не валидирует `yq`/`python3`/`php`/`curl`/`pyyaml`
`scripts/check-deps.sh:19-22`
```bash
check "bats-core" bats
check "git" git
check "node" node
check "bash" bash
```
До сих пор только 4 проверки. После top-10 fix #3 `gate-check.sh` теперь *жёстко* требует `yq` (line 30-34: `exit 3` без него), но `check-deps.sh` про это молчит. `verify-site-url.sh` требует `pyyaml` (stdlib его не содержит). Misleading «All dependencies OK.» — risk остался.

### R6. C3 — суппрессия compile errors в `gate-check.sh:312-314`
```bash
cd "$REPO_ROOT" && python3 -m scripts.wiki.compile \
    --source-mode=project-graph --project="$project_slug" \
    >/dev/null 2>&1 || true
```
`2>&1` всё ещё прячет stderr. C3-fix не применён в этом блоке (хотя в post-commit аналогичный block теперь print'ит через ERR trap). Низкий риск — это не критичный путь, но симметрии с post-commit нет.

### R7. C4 — `script` runner всё ещё word-split + double-execution
`scripts/gate-check.sh:247-263`
```bash
args_raw="$(yq -r ".stages.\"$stage\".hard_checks[$i].args[] // \"\"" "$GATES_YAML" | sed "s|{project}|$project|g")"
case "$script_path" in *.sh) runner="bash" ;; *) runner="python" ;; esac
# shellcheck disable=SC2086
if $runner "$REPO_ROOT/$script_path" $args_raw >/dev/null 2>&1; then
    echo "  ✅ $check_id ($script_path)"
else
    echo "  ❌ $check_id: script $script_path failed"
    $runner "$REPO_ROOT/$script_path" $args_raw 2>&1 | sed 's/^/     /' || true
    ...
fi
```
`$args_raw` остался unquoted (word-splitting). Скрипт re-runs дважды при failure (waste + unsafe для verifier'ов с side-effects, хотя текущие verify-* идемпотентны). Путь `"Обучение вайбкодинг Кодекс"` с пробелами всё ещё может ломать args. C4 не закрыт.

### R8. M10 — soft-checks default-pass
`scripts/gate-check.sh:287-291`
```bash
case "$ans" in
    yes|y) echo "    ✅ confirmed" ;;
    no|n)  echo "    ❌ not satisfied"; fail=1 ;;
    *)     echo "    ⚠️  partial / skipped" ;;
esac
```
Не тронуто — Enter / `idk` / любая ересь = pass. Cluster A item, не сделан в этом раунде.

### R9. C10 — PIPELINE_ORDER duplication
`scripts/gate-check.sh:110-115` имеет 20 этапов, `scripts/render-pipeline-map.sh:39-44` имеет 21 (включает `08b_style`). Дрифт остался. Cluster A item.

### R10. M5 — `verify-site-url.sh` использует `pyyaml`
`scripts/verify-site-url.sh:19-26` — heredoc Python с `import yaml`. Не заменено на `yq`. Без `pyyaml` в окружении гейт fail'нет с misleading `ModuleNotFoundError`.

### R11. M6 — yq expressions в gate-state.sh не используют `env(...)` injection
`scripts/gate-state.sh:31,37` — всё ещё прямая интерполяция `"$stage"`/`"$status"` в yq фильтр. Низкий риск (имена этапов из вашего YAML), но Cluster A item.

### R12. M7 — heredoc inteprolation в `verify-identity-preserved.sh:13-26`
`$MANIFEST` shell-interpolated в Python source. Heredoc без quoting. Низкий риск, но fragile. Cluster E.

### R13. M8 — `check-wiki-sync.sh` per-file Python startup
`scripts/check-wiki-sync.sh:46-50` — на 200-block library запускает Python в цикле. `'$CACHE'` shell-interpolated в Python source. Cluster C item (token efficiency), не Cluster A/D.

### R14. M11 — `install-codex.sh` пишет в `/tmp/codex-install.err`
`scripts/install-codex.sh:50` — symlink-attack vector. Не использует `mktemp`.

### R15. M12 — `install-git-hooks.sh:19` `chmod +x .githooks/*` слишком широкий
Не тронуто.

### R16. Phase 2 review concerns
- **`--absolute-git-dir`** в post-commit не используется. `git rev-parse --git-dir` возвращает относительный путь (`.git`) если CWD = repo root, абсолютный — иначе. После `cd "$REPO_ROOT"` (`post-commit:9`) это всегда `.git` — fine для текущего использования. Не критично, но `--absolute-git-dir` был бы более defensive.
- **Trap message** — `trap 'echo "post-commit failed at line $LINENO" >&2; exit 0' ERR` — message минимальный, без `BASH_COMMAND`. Diagnostics weaker than they could be. Minor.
- **Explicit-paths fragility** — `git add wiki/index.md wiki/log.md wiki/concepts/ wiki/preview.html` — если compiler начнёт генерить новый файл (e.g. `wiki/graph.json`), он не попадёт в commit, и потом `check-wiki-sync.sh` будет ругаться. Желательно сделать список путей конфигурируемым (например, читать из `wiki/.cache.json` или хардкодить в одном месте). Совет: рассмотреть `git add wiki/index.md wiki/log.md wiki/preview.html wiki/concepts/ wiki/.cache.json` — `.cache.json` сейчас не add'ится, и check-sync будет жаловаться при каждом запуске.

---

## 🔴 NEW (regressions / issues introduced by Phase 2-4)

### N1. `gate-check.sh:152` — арифметика `seq` ломается при `checks_count=0`
```bash
for i in $(if [ "$checks_count" -gt 0 ]; then seq 0 $((checks_count - 1)); fi); do
```
В legacy-bypass path `checks_count=0` (line 148). Цикл должен пропуститься. С `set -uo pipefail` (без `-e`) это работает — `seq 0 -1` не вызывается. Но конструкция `$(if ... ; then ... ; fi)` неидиоматична. Lower risk, но при будущем добавлении `set -e` придётся помнить про этот edge case.

**Fix:** заменить на чистый `if`:
```bash
if [ "$checks_count" -gt 0 ]; then
    for i in $(seq 0 $((checks_count - 1))); do
        ...
    done
fi
```

### N2. `gate-check.sh:84-90` — TSV log race condition
```bash
LEGACY_LOG="${LANDING_SYSTEM_ROOT:-$REPO_ROOT}/audit/legacy-bypass.log"
mkdir -p "$(dirname "$LEGACY_LOG")"
...
printf '%s\t%s\t%s\t%s\n' \
    "$(date -u ...)" "$project_escaped" "$stage" "$reason_escaped" \
    >> "$LEGACY_LOG"
```
Конкурентные gate-check'и на одной машине могут перемежать строки (POSIX `>>` атомарен только для писаний ≤ PIPE_BUF, обычно 4096 байт — здесь типовая строка ~200 байт → ок). Заметка: если когда-то `legacy_reason` станет огромным (>4KB), записи могут перетираться. Низкий риск.

### N3. `gate-check.sh:147` — комментарий «(skipped — legacy bypass)» уходит на stdout сразу, до проверок
```bash
if [ "$bypass_hard_checks" = "1" ]; then
    echo "  (skipped — legacy bypass)"
    checks_count=0
```
Выводится перед заголовком hard-checks (которого нет). Визуально невнятно — пользователь видит strange line без контекста. Cosmetic.

### N4. `post-commit:11-15` — recursion guard читает только первую строку
```bash
LAST_MSG="$(git log -1 --pretty=%B 2>/dev/null | head -1)"
case "$LAST_MSG" in
    chore\(wiki\)*) exit 0 ;;
esac
```
Если кто-то закоммитит `feat: foo\n\nchore(wiki): merged auto-update` — recursion guard не сработает. Edge-case, низкий риск, но `head -1` это намерение, не баг.

### N5. `post-commit:40` — pipeline всё ещё может прятать exit code
```bash
if ! python3 -m scripts.wiki.compile --source-mode=system 2>&1 | tail -3; then
```
С `set -Eeuo pipefail` теперь exit code пайплайна = exit code последнего failing stage (`pipefail` = ON, благодаря `-Eeuo`). Это правильно. Но конструкция `if ! ... | tail -3; then` всё равно неортогональна — `tail -3` усекает диагностику до 3 строк, а компилятор может вылить 20-строчный traceback. Diagnostics страдают. Lower priority.

### N6. `gate-check.sh:202` — `find -name "$pattern"` не quoted-glob safe
```bash
count="$(find "$path" -maxdepth 1 -type f -name "$pattern" 2>/dev/null | wc -l | tr -d ' ')"
```
`$pattern` это fnmatch glob (e.g. `*.jpg`). `find` сам понимает glob, кавычки правильные. Но если pattern содержит спецсимволы шелла внутри YAML (`?`, `[`), они уйдут в `find -name` напрямую — это OK для find, но не для документации (user может подумать, что это shell glob). Не баг, доку бы добавить.

### N7. `gate-check.sh:74-79` — `legacy_allowed` пустой → user-friendly hint мог бы быть лучше
```bash
case " $legacy_allowed " in
    *" $stage "*) ;;
    *)
        echo "❌ Stage $stage marked legacy: true, but '$stage' not in legacy_allowed list"
        echo "   → fix: либо убери legacy: true, либо добавь в config/stage-gates.yaml legacy_allowed:"
        exit 1
        ;;
esac
```
Когда `legacy_allowed: []`, сообщение читается как «добавь в список», но не упоминает, что список empty by default и это intended. Minor UX.

---

## ⚪ PRE-EXISTING (from original audit, not in scope)

Все Major/Minor из первого аудита, не упомянутые в Top-10 и не в Cluster A/D:

- M1: `.env` source без логирования (gate-check.sh:39).
- M2 (частично): большая часть verify-* без `set -e` (см. R4).
- M3: parallax regex (R2).
- M4: дубли в premium checklist.
- M5: pyyaml в verify-site-url (R10).
- M6: yq env injection (R11).
- M7: heredoc inteprolation (R12).
- M8/M9: check-wiki-sync N+1 Python (R13).
- M10: soft-checks default-pass (R8).
- M11: `/tmp/codex-install.err` (R14).
- M12: chmod +x .githooks/* (R15).
- M13: `head -20` truncation в landing-final-check.sh.
- M14: нет --json mode для gate-check.
- Minor: `gate-check.sh:22` silent drop unknown flags; `08b_style` без lock; mix Russian/English; render-pipeline-map.sh без `local`; verify-* 4-line wrappers (dead-weight); php exit 2 в двух условиях; check-deps gaps; codex auth status без version pin; verify-composed-premium drift с checklist; gate-state.sh без schema validation status tokens.

---

## Verdict

**Approve with Comments.**

Three top-10 fixes (#3, #4, #7) verified — each implementation matches or *exceeds* the original audit's recipe (e.g., `dir_has_files` rejects brace patterns; `legacy_allowed` defaults to empty list = default-deny; post-commit adds explicit-path staging *plus* `-Eeuo` *plus* ERR trap). Phase 2 post-commit hook is genuinely tightened.

Cluster A (full enforcement) and Cluster E (verifier hygiene) remain open as expected — none of the seven remaining items in those clusters were claimed to be in scope.

**Recommended follow-ups (when Cluster E is opened):**
1. R3 (placeholder regex broaden) — single regex change, cheap, prevents real 07f leak.
2. R5 (check-deps for yq/python3/pyyaml) — 10 lines, prevents misleading «All deps OK» before gate-check exits 3.
3. R7 (script runner `mapfile -t args_arr` + single execution) — fixes word-split на путях с пробелами (репо path содержит «Обучение вайбкодинг Кодекс»).
4. R8 (soft-checks default-fail or re-prompt) — Cluster A high-leverage.
5. R9 (PIPELINE_ORDER единый источник) — cheap factorization.

**Critical absent issues:** none. Phase 2/4 не вводят регрессий в claimed scope. N1-N7 — cosmetic/edge-case, ни одно не блокирует.
