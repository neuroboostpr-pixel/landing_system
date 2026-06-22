#!/usr/bin/env bash
# scripts/gate-check.sh — per-stage gate runner.
# Reads config/stage-gates.yaml, executes hard_checks, prompts soft_checks.
# Usage: gate-check.sh --stage <id> --project <dir> [--approve] [--auto]
set -uo pipefail

REPO_ROOT="$(cd "$(dirname "$0")/.." && pwd)"

# Cross-platform python detection (sets PYTHON_CMD).
__SCRIPT_DIR__="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
# shellcheck source=lib/python-cmd.sh
. "$__SCRIPT_DIR__/lib/python-cmd.sh"
GATES_YAML="${GATES_YAML:-$REPO_ROOT/config/stage-gates.yaml}"
GATE_STATE="$REPO_ROOT/scripts/gate-state.sh"

stage=""
project=""
approve=0
auto="${GATE_AUTO:-0}"

while [ $# -gt 0 ]; do
    case "$1" in
        --stage) stage="$2"; shift 2 ;;
        --project) project="$2"; shift 2 ;;
        --approve) approve=1; shift ;;
        --auto) auto=1; shift ;;
        *) shift ;;
    esac
done

[ -z "$stage" ] && { echo "ERROR: --stage required" >&2; exit 2; }
[ -z "$project" ] && { echo "ERROR: --project required" >&2; exit 2; }

# Verify yq (mikefarah/yq) is installed
if ! command -v yq >/dev/null 2>&1; then
    echo "❌ yq not installed. Install: brew install yq" >&2
    echo "   (need mikefarah/yq Go-based, not Python yq)" >&2
    exit 3
fi

[ -f "$GATES_YAML" ] || { echo "ERROR: $GATES_YAML missing" >&2; exit 2; }

# Load .env
[ -f "$REPO_ROOT/.env" ] && set -a && . "$REPO_ROOT/.env" && set +a

echo "═══ Gate check: stage=$stage project=$(basename "$project") ═══"

# Log stage_start for wiki routing observability
SESSION_ID="${CLAUDE_SESSION_ID:-unknown}"
$PYTHON_CMD -m scripts.wiki.log \
    --type stage_start \
    --stage "$stage" \
    --project "$(basename "$project")" \
    --session-id "$SESSION_ID" \
    >/dev/null 2>&1 || true

# 0. Legacy bypass — strict: stage must be in config/stage-gates.yaml legacy_allowed
# list AND state-file must provide non-empty legacy_reason. Every bypass logged.
# Evaluated BEFORE require_approved (legacy projects skip prior-stage approval too).
bypass_hard_checks=0
state_file="$project/.landing-state.yaml"
if [ -f "$state_file" ]; then
    legacy_flag="$(yq -r ".stages.\"$stage\".legacy // false" "$state_file" 2>/dev/null || echo "false")"
    # Also support top-level "legacy: true" (pre-PR-D state file format)
    if [ "$legacy_flag" != "true" ]; then
        top_level_legacy="$(yq -r '.legacy // false' "$state_file" 2>/dev/null || echo "false")"
        if [ "$top_level_legacy" = "true" ]; then
            legacy_flag="true"
        fi
    fi

    if [ "$legacy_flag" = "true" ]; then
        legacy_allowed="$(yq -r '.legacy_allowed // [] | join(" ")' "$GATES_YAML" 2>/dev/null || echo "")"
        legacy_reason="$(yq -r ".stages.\"$stage\".legacy_reason // \"\"" "$state_file" 2>/dev/null || echo "")"
        # Fallback to top-level legacy_reason
        if [ -z "$legacy_reason" ]; then
            legacy_reason="$(yq -r '.legacy_reason // ""' "$state_file" 2>/dev/null || echo "")"
        fi

        case " $legacy_allowed " in
            *" $stage "*) ;;
            *)
                echo "❌ Stage $stage marked legacy: true, but '$stage' not in legacy_allowed list"
                echo "   → fix: либо убери legacy: true, либо добавь в config/stage-gates.yaml legacy_allowed:"
                exit 1
                ;;
        esac

        if [ -z "$legacy_reason" ]; then
            echo "❌ Stage $stage marked legacy: true but missing legacy_reason field"
            echo "   → fix: добавь legacy_reason: \"<обоснование>\" в state-файл"
            exit 1
        fi

        echo "⚠️  LEGACY BYPASS: stage $stage hard-checks skipped"
        echo "    Reason: $legacy_reason"
        echo "    Allowlist: $legacy_allowed"
        LEGACY_LOG="${LANDING_SYSTEM_ROOT:-$REPO_ROOT}/audit/legacy-bypass.log"
        mkdir -p "$(dirname "$LEGACY_LOG")"
        reason_escaped="${legacy_reason//$'\t'/ }"
        project_escaped="${project//$'\t'/ }"
        printf '%s\t%s\t%s\t%s\n' \
            "$(date -u +%Y-%m-%dT%H:%M:%SZ)" "$project_escaped" "$stage" "$reason_escaped" \
            >> "$LEGACY_LOG"
        bypass_hard_checks=1
    fi
fi

# 1. Check require_approved (skipped under legacy bypass)
if [ "$bypass_hard_checks" != "1" ]; then
    required="$(yq -r ".stages.\"$stage\".require_approved // [] | join(\",\")" "$GATES_YAML")"
    if [ -n "$required" ]; then
        if ! bash "$GATE_STATE" all_approved "$project" "$required"; then
            echo "❌ Previous stages not approved. Cannot run $stage."
            exit 1
        fi
        echo "✅ Required prior stages approved: $required"
    fi
else
    required=""
fi

# 1b. Soft-lock warning: для soft-этапов — если предыдущий по pipeline не approved
# Порядок этапов — из config/stages.yaml (E1, single source of truth)
PIPELINE_ORDER=()
while IFS= read -r _sid; do
    PIPELINE_ORDER+=("$_sid")
done < <("$PYTHON_CMD" "$__SCRIPT_DIR__/stages.py" --order)

stage_lock="$(yq -r ".stages.\"$stage\".lock // \"soft\"" "$GATES_YAML")"

if [ "$stage_lock" = "soft" ] && [ -z "$required" ]; then
    # Найти предыдущий по pipeline_order
    prev=""
    for i in "${!PIPELINE_ORDER[@]}"; do
        if [ "${PIPELINE_ORDER[$i]}" = "$stage" ] && [ "$i" -gt 0 ]; then
            prev="${PIPELINE_ORDER[$((i-1))]}"
            break
        fi
    done
    if [ -n "$prev" ]; then
        prev_status="$(bash "$GATE_STATE" get "$project" "$prev" 2>/dev/null || echo "locked")"
        if [ "$prev_status" != "approved" ] && [ "$prev_status" != "n/a" ]; then
            echo "⚠️  Soft warning: предыдущий этап '$prev' имеет статус '$prev_status'."
            if [ "$auto" != "1" ] && [ -t 0 ]; then
                printf "   Точно зайти на '%s'? [y/N] " "$stage"
                read -r ans
                if [ "$ans" != "y" ] && [ "$ans" != "Y" ]; then
                    echo "Отменено."
                    exit 1
                fi
            fi
        fi
    fi
fi

# 2. Run hard_checks
fail=0
if [ "$bypass_hard_checks" = "1" ]; then
    echo "  (skipped — legacy bypass)"
    checks_count=0
else
    checks_count="$(yq -r ".stages.\"$stage\".hard_checks // [] | length" "$GATES_YAML")"
fi
for i in $(if [ "$checks_count" -gt 0 ]; then seq 0 $((checks_count - 1)); fi); do
    check_id="$(yq -r ".stages.\"$stage\".hard_checks[$i].id" "$GATES_YAML")"
    check_type="$(yq -r ".stages.\"$stage\".hard_checks[$i].type" "$GATES_YAML")"
    fix_hint="$(yq -r ".stages.\"$stage\".hard_checks[$i].fix_hint // \"\"" "$GATES_YAML")"
    # required: false → проверка информативная, её провал НЕ блокирует этап
    # (по умолчанию true). NB: НЕ использовать `// true` — оператор `//` в yq/jq
    # схлопывает и false, и null → false стал бы true. Читаем как есть; "null"
    # (ключ отсутствует) трактуем как required=true ниже.
    required="$(yq -r ".stages.\"$stage\".hard_checks[$i].required" "$GATES_YAML")"
    prev_fail="$fail"

    case "$check_type" in
        file_exists)
            path="$(yq -r ".stages.\"$stage\".hard_checks[$i].path" "$GATES_YAML" | sed "s|{project}|$project|g")"
            if [ -e "$path" ]; then
                echo "  ✅ $check_id ($path)"
            else
                echo "  ❌ $check_id: missing $path"
                [ -n "$fix_hint" ] && echo "     → $fix_hint"
                fail=1
            fi
            ;;
        file_or_dir_exists)
            path="$(yq -r ".stages.\"$stage\".hard_checks[$i].path" "$GATES_YAML" | sed "s|{project}|$project|g")"
            if [ -e "$path" ]; then
                # If directory, require non-empty (otherwise file_or_dir_exists is just file_exists with a misleading name)
                if [ -d "$path" ] && [ -z "$(ls -A "$path" 2>/dev/null)" ]; then
                    echo "  ❌ $check_id: directory $path exists but is empty"
                    [ -n "$fix_hint" ] && echo "     → $fix_hint"
                    fail=1
                else
                    echo "  ✅ $check_id ($path)"
                fi
            else
                echo "  ❌ $check_id: missing $path"
                [ -n "$fix_hint" ] && echo "     → $fix_hint"
                fail=1
            fi
            ;;
        dir_has_files)
            path="$(yq -r ".stages.\"$stage\".hard_checks[$i].path" "$GATES_YAML" | sed "s|{project}|$project|g")"
            pattern="$(yq -r ".stages.\"$stage\".hard_checks[$i].pattern // \"*\"" "$GATES_YAML")"
            min_count="$(yq -r ".stages.\"$stage\".hard_checks[$i].min_count // 1" "$GATES_YAML")"
            if [ ! -d "$path" ]; then
                echo "  ❌ $check_id: directory $path missing"
                [ -n "$fix_hint" ] && echo "     → $fix_hint"
                fail=1
            else
                case "$pattern" in
                    *\{*)
                        echo "  ❌ $check_id: brace patterns not supported ($pattern)"
                        echo "     → use a single fnmatch glob (e.g. '*.jpg') or call this check multiple times"
                        fail=1
                        continue
                        ;;
                esac
                count="$(find "$path" -maxdepth 1 -type f -name "$pattern" 2>/dev/null | wc -l | tr -d ' ')"
                if [ "$count" -ge "$min_count" ]; then
                    echo "  ✅ $check_id ($count files matching $pattern in $path)"
                else
                    echo "  ❌ $check_id: $path has $count files matching '$pattern', need ≥$min_count"
                    [ -n "$fix_hint" ] && echo "     → $fix_hint"
                    fail=1
                fi
            fi
            ;;
        http_ping)
            url="$(yq -r ".stages.\"$stage\".hard_checks[$i].url" "$GATES_YAML")"
            if curl -sfI --max-time 10 "$url" >/dev/null 2>&1; then
                echo "  ✅ $check_id ($url)"
            else
                echo "  ❌ $check_id: $url unreachable"
                fail=1
            fi
            ;;
        api_validator)
            svc="$(yq -r ".stages.\"$stage\".hard_checks[$i].validator" "$GATES_YAML")"
            if bash "$REPO_ROOT/scripts/validate-all.sh" --service "$svc" >/dev/null 2>&1; then
                echo "  ✅ $check_id ($svc)"
            else
                echo "  ❌ $check_id: $svc validator failed"
                [ -n "$fix_hint" ] && echo "     → $fix_hint"
                fail=1
            fi
            ;;
        api_validator_any_of)
            services="$(yq -r ".stages.\"$stage\".hard_checks[$i].validators | join(\" \")" "$GATES_YAML")"
            any_ok=0
            for svc in $services; do
                if bash "$REPO_ROOT/scripts/validate-all.sh" --service "$svc" >/dev/null 2>&1; then
                    any_ok=1
                    echo "  ✅ $check_id ($svc)"
                    break
                fi
            done
            if [ "$any_ok" = "0" ]; then
                echo "  ❌ $check_id: none of [$services] valid"
                [ -n "$fix_hint" ] && echo "     → $fix_hint"
                fail=1
            fi
            ;;
        script)
            script_path="$(yq -r ".stages.\"$stage\".hard_checks[$i].script" "$GATES_YAML")"
            script_args=()
            while IFS= read -r arg; do
                script_args+=("${arg//\{project\}/$project}")
            done < <(yq -r ".stages.\"$stage\".hard_checks[$i].args[]?" "$GATES_YAML" 2>/dev/null || true)
            # Determine runner by extension (python через PYTHON_CMD —
            # голого `python` на macOS/линуксах часто нет)
            case "$script_path" in
                *.sh) runner_cmd=(bash) ;;
                *)    read -r -a runner_cmd <<< "$PYTHON_CMD" ;;
            esac
            if "${runner_cmd[@]}" "$REPO_ROOT/$script_path" "${script_args[@]}" >/dev/null 2>&1; then
                echo "  ✅ $check_id ($script_path)"
            else
                echo "  ❌ $check_id: script $script_path failed"
                "${runner_cmd[@]}" "$REPO_ROOT/$script_path" "${script_args[@]}" 2>&1 | sed 's/^/     /' || true
                [ -n "$fix_hint" ] && echo "     → $fix_hint"
                fail=1
            fi
            ;;
        *)
            echo "  ❌ $check_id: unknown check type '$check_type'" >&2
            echo "     → implement this type in scripts/gate-check.sh or fix the typo in config/stage-gates.yaml" >&2
            fail=1
            ;;
    esac

    # Если упала ИМЕННО эта проверка (fail поднялся с 0) и она required:false —
    # откатываем: предупреждаем, но этап не валим.
    if [ "$fail" = "1" ] && [ "$prev_fail" = "0" ] && [ "$required" = "false" ]; then
        echo "     ⚠️  необязательная проверка ($check_id) не пройдена — не блокирует этап"
        fail=0
    fi
done

if [ "$fail" = "1" ]; then
    echo "❌ Gate failed for $stage"
    exit 1
fi

# 3. Soft checks (only when interactive and not --auto)
soft_count="$(yq -r ".stages.\"$stage\".soft_checks // [] | length" "$GATES_YAML")"
if [ "$soft_count" -gt 0 ] && [ "$auto" != "1" ]; then
    echo ""
    echo "▶ Soft checks (please answer):"
    for i in $(seq 0 $((soft_count - 1))); do
        prompt="$(yq -r ".stages.\"$stage\".soft_checks[$i].prompt" "$GATES_YAML")"
        check_id="$(yq -r ".stages.\"$stage\".soft_checks[$i].id" "$GATES_YAML")"
        read -r -p "  [$check_id] $prompt " ans
        case "$ans" in
            yes|y) echo "    ✅ confirmed" ;;
            no|n)  echo "    ❌ not satisfied"; fail=1 ;;
            *)     echo "    ⚠️  partial / skipped" ;;
        esac
    done
fi

if [ "$fail" = "1" ]; then
    echo "❌ Gate failed (soft check unsatisfied)"
    exit 1
fi

# 4. Mark in_progress or approve
if [ "$approve" = "1" ]; then
    bash "$GATE_STATE" approve "$project" "$stage"
    echo "✅ Stage $stage approved"
    # Auto-update routing-report after every approve
    cd "$REPO_ROOT" && $PYTHON_CMD -m scripts.wiki.stats --report >/dev/null 2>&1 || true
else
    bash "$GATE_STATE" set "$project" "$stage" "in_progress"
    echo "✅ Gate passed for $stage (status: in_progress)"
fi

# === PR-G: Auto-update project-graph wiki after successful gate-check ===
if [ "${fail:-1}" = "0" ] && [ -d "$project/wiki" ]; then
    project_slug="$(basename "$project")"
    cd "$REPO_ROOT" && $PYTHON_CMD -m scripts.wiki.compile \
        --source-mode=project-graph --project="$project_slug" \
        >/dev/null 2>&1 || true
fi

# === Stage Execution Protocol: refresh pipeline map after every gate-check ===
# Map stays current in <project>/wiki/pipeline-map.md without manual intervention.
if [ -f "$project/.landing-state.yaml" ]; then
    bash "$REPO_ROOT/scripts/render-pipeline-map.sh" \
        "$project/.landing-state.yaml" --write-wiki >/dev/null 2>&1 || true
fi
