#!/usr/bin/env bash
# scripts/gate-state.sh — read/write .landing-state.yaml
# Usage:
#   gate-state.sh get <project-dir> <stage>
#   gate-state.sh set <project-dir> <stage> <status>
#   gate-state.sh approve <project-dir> <stage>
#   gate-state.sh all_approved <project-dir> <comma-separated-stages>
set -uo pipefail

cmd="${1:?usage: get|set|approve|all_approved}"
project="${2:?project dir required}"
state_file="$project/.landing-state.yaml"

[ -f "$state_file" ] || { echo "ERROR: $state_file not found" >&2; exit 2; }

require_yq() {
    command -v yq >/dev/null 2>&1 || { echo "ERROR: yq not installed (brew install yq)" >&2; exit 3; }
}

case "$cmd" in
    get)
        require_yq
        stage="${3:?stage required}"
        yq -r ".stages.\"$stage\".status // \"locked\"" "$state_file"
        ;;
    set)
        require_yq
        stage="${3:?stage required}"
        status="${4:?status required}"
        ts="$(date -u +%Y-%m-%dT%H:%M:%SZ)"
        yq -i ".stages.\"$stage\".status = \"$status\" | .stages.\"$stage\".timestamp = \"$ts\"" "$state_file"
        ;;
    approve)
        require_yq
        stage="${3:?stage required}"
        ts="$(date -u +%Y-%m-%dT%H:%M:%SZ)"
        yq -i ".stages.\"$stage\".status = \"approved\" | .stages.\"$stage\".timestamp = \"$ts\"" "$state_file"
        ;;
    all_approved)
        require_yq
        stages="${3:?comma-separated stages required}"
        IFS=',' read -ra arr <<< "$stages"
        missing=()
        for s in "${arr[@]}"; do
            status="$(yq -r ".stages.\"$s\".status // \"locked\"" "$state_file")"
            [ "$status" != "approved" ] && missing+=("$s")
        done
        if [ ${#missing[@]} -eq 0 ]; then
            exit 0
        else
            echo "Not approved: ${missing[*]}"
            exit 1
        fi
        ;;
    *)
        echo "Usage: $0 {get|set|approve|all_approved} <project-dir> [args]" >&2
        exit 2
        ;;
esac
