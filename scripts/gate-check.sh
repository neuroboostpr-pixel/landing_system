#!/usr/bin/env bash
# scripts/gate-check.sh — per-stage gate runner.
# Reads config/stage-gates.yaml, executes hard_checks, prompts soft_checks.
# Usage: gate-check.sh --stage <id> --project <dir> [--approve] [--auto]
set -uo pipefail

REPO_ROOT="$(cd "$(dirname "$0")/.." && pwd)"
GATES_YAML="$REPO_ROOT/config/stage-gates.yaml"
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

# 1. Check require_approved
required="$(yq -r ".stages.\"$stage\".require_approved // [] | join(\",\")" "$GATES_YAML")"
if [ -n "$required" ]; then
    if ! bash "$GATE_STATE" all_approved "$project" "$required"; then
        echo "❌ Previous stages not approved. Cannot run $stage."
        exit 1
    fi
    echo "✅ Required prior stages approved: $required"
fi

# 2. Run hard_checks
fail=0
# Legacy bypass: skip all hard checks if .landing-state.yaml contains "legacy: true"
if [ -f "$project/.landing-state.yaml" ] && grep -q "^[[:space:]]*legacy:[[:space:]]*true" "$project/.landing-state.yaml" 2>/dev/null; then
    echo "  ⚠ legacy:true — skipping all hard checks for $stage"
    checks_count=0
else
    checks_count="$(yq -r ".stages.\"$stage\".hard_checks // [] | length" "$GATES_YAML")"
fi
for i in $(seq 0 $((checks_count - 1))); do
    check_id="$(yq -r ".stages.\"$stage\".hard_checks[$i].id" "$GATES_YAML")"
    check_type="$(yq -r ".stages.\"$stage\".hard_checks[$i].type" "$GATES_YAML")"
    fix_hint="$(yq -r ".stages.\"$stage\".hard_checks[$i].fix_hint // \"\"" "$GATES_YAML")"

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
            args_raw="$(yq -r ".stages.\"$stage\".hard_checks[$i].args[] // \"\"" "$GATES_YAML" | sed "s|{project}|$project|g")"
            # Determine runner by extension
            case "$script_path" in
                *.sh) runner="bash" ;;
                *)    runner="python" ;;
            esac
            # shellcheck disable=SC2086
            if $runner "$REPO_ROOT/$script_path" $args_raw >/dev/null 2>&1; then
                echo "  ✅ $check_id ($script_path)"
            else
                echo "  ❌ $check_id: script $script_path failed"
                $runner "$REPO_ROOT/$script_path" $args_raw 2>&1 | sed 's/^/     /' || true
                [ -n "$fix_hint" ] && echo "     → $fix_hint"
                fail=1
            fi
            ;;
        *)
            echo "  ⚠️  $check_id: unknown type $check_type" >&2
            ;;
    esac
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
else
    bash "$GATE_STATE" set "$project" "$stage" "in_progress"
    echo "✅ Gate passed for $stage (status: in_progress)"
fi
