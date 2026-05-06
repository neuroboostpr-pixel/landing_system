#!/usr/bin/env bash
# scripts/migrate-state-add-01a.sh
# Add 01a_niche_analysis stage to an existing project's .landing-state.yaml.
# If 02_assets is already approved, mark 01a as 'skipped' (legacy projects).
# Otherwise mark as 'locked'.
set -euo pipefail

PROJECT="${1:?usage: migrate-state-add-01a.sh <project-dir>}"
STATE="$PROJECT/.landing-state.yaml"

[ -f "$STATE" ] || { echo "ERROR: $STATE not found" >&2; exit 1; }

command -v yq >/dev/null 2>&1 || { echo "ERROR: yq required" >&2; exit 2; }

# Already migrated?
if yq -e '.stages."01a_niche_analysis"' "$STATE" >/dev/null 2>&1; then
    echo "Already has 01a_niche_analysis — no-op."
    exit 0
fi

# Decide initial status
assets_status="$(yq -r '.stages."02_assets".status // "locked"' "$STATE")"
if [ "$assets_status" = "approved" ]; then
    new_status="skipped"
    echo "02_assets already approved — marking 01a as 'skipped'."
else
    new_status="locked"
    echo "02_assets not yet approved — marking 01a as 'locked'."
fi

ts="$(date -u +%Y-%m-%dT%H:%M:%SZ)"
yq -i ".stages.\"01a_niche_analysis\" = {\"status\": \"$new_status\", \"timestamp\": \"$ts\"}" "$STATE"

echo "Migration done."
