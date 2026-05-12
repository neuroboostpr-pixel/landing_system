#!/usr/bin/env bash
# Mark Lendings/* projects as legacy:true if they fail stage-08 gate.
# One-shot, idempotent. Run once after merging the systemic fix.
#
# Usage: mark-legacy-projects.sh [<lendings-root>]
set -u

REPO_ROOT="$(cd "$(dirname "$0")/.." && pwd)"
LENDINGS_ROOT="${1:-$(realpath "$REPO_ROOT/../Lendings")}"

if [ ! -d "$LENDINGS_ROOT" ]; then
    echo "❌ $LENDINGS_ROOT not found" >&2
    exit 1
fi

for project in "$LENDINGS_ROOT"/*/; do
    [ -f "$project.landing-state.yaml" ] || continue
    pname="$(basename "$project")"

    if grep -q "^legacy:" "$project.landing-state.yaml"; then
        echo "  $pname — already has legacy marker"
        continue
    fi

    if bash "$REPO_ROOT/scripts/gate-check.sh" --stage 08_build --project "$project" --auto >/dev/null 2>&1; then
        echo "✓ $pname — passes stage-08, no marking needed"
    else
        echo "⚠ $pname — marking legacy:true"
        TS="$(date -u +%Y-%m-%d)"
        echo "legacy: true  # auto-marked $TS — pre-stage-08-hardening" >> "$project.landing-state.yaml"
    fi
done
