#!/usr/bin/env bats

REPO="$(cd "$(dirname "${BATS_TEST_FILENAME}")/../.." && pwd)"
SCRIPT="$REPO/scripts/migrate-state-for-prd.sh"

setup() {
    TMP="$(mktemp -d)"
    cat > "$TMP/.landing-state.yaml" <<'EOF'
project: legacy
created: "2026-04-01"
schema_version: 1
stages:
  "00_brief":           {status: approved, timestamp: "2026-04-02T10:00:00"}
  "01_context":         {status: approved, timestamp: ""}
  "07_content":         {status: approved, timestamp: ""}
EOF
}
teardown() { rm -rf "$TMP"; }

@test "migration adds missing PR-D stages without overwriting existing ones" {
    run bash "$SCRIPT" "$TMP/.landing-state.yaml"
    [ "$status" -eq 0 ]

    grep -E '"00_brief":\s*\{status:\s*approved' "$TMP/.landing-state.yaml"
    grep -qE '"07a_prototype":\s*\{status:\s*locked' "$TMP/.landing-state.yaml"
    grep -qE '"07d_photos":\s*\{status:\s*locked' "$TMP/.landing-state.yaml"
    grep -qE '"07f_composed_final":\s*\{status:\s*locked' "$TMP/.landing-state.yaml"
}

@test "migration is idempotent" {
    bash "$SCRIPT" "$TMP/.landing-state.yaml"
    sum1=$(md5 -q "$TMP/.landing-state.yaml" 2>/dev/null || md5sum "$TMP/.landing-state.yaml" | awk '{print $1}')
    bash "$SCRIPT" "$TMP/.landing-state.yaml"
    sum2=$(md5 -q "$TMP/.landing-state.yaml" 2>/dev/null || md5sum "$TMP/.landing-state.yaml" | awk '{print $1}')
    [ "$sum1" = "$sum2" ]
}

@test "migration bumps schema_version to 2" {
    bash "$SCRIPT" "$TMP/.landing-state.yaml"
    grep -E '^schema_version:\s*2' "$TMP/.landing-state.yaml"
}
