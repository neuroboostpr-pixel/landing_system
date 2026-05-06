#!/usr/bin/env bats

setup() {
  REPO="$(cd "$(dirname "$BATS_TEST_FILENAME")/../.." && pwd)"
  TMP="$BATS_TEST_TMPDIR"
  PROJECT="$TMP/test-niche-project"
  mkdir -p "$PROJECT"
  cp -r "$REPO/template/." "$PROJECT/"
  # Mark only 00_brief as approved
  if command -v yq >/dev/null 2>&1; then
    yq -i '.stages."00_brief".status = "approved"' "$PROJECT/.landing-state.yaml"
  else
    skip "yq not installed"
  fi
}

@test "gate-check 02_assets is blocked when 01a_niche_analysis is locked" {
  run bash "$REPO/scripts/gate-check.sh" --stage 02_assets --project "$PROJECT"
  [ "$status" -ne 0 ]
}

@test "gate-check 01a_niche_analysis fails when artifacts missing" {
  run bash "$REPO/scripts/gate-check.sh" --stage 01a_niche_analysis --project "$PROJECT"
  [ "$status" -ne 0 ]
}

@test "existing project without 01a key in state can be migrated" {
  OLD="$BATS_TEST_TMPDIR/old-project"
  mkdir -p "$OLD"
  cat > "$OLD/.landing-state.yaml" <<'EOF'
project: "old"
created: "2026-04-01T00:00:00Z"
schema_version: 1
stages:
  "00_brief":
    status: approved
    timestamp: ""
  "01_context":
    status: approved
    timestamp: ""
  "02_assets":
    status: approved
    timestamp: ""
  "03_references":
    status: locked
    timestamp: ""
EOF
  run bash "$REPO/scripts/migrate-state-add-01a.sh" "$OLD"
  [ "$status" -eq 0 ]
  grep -q "01a_niche_analysis" "$OLD/.landing-state.yaml"
}

@test "migrate-state script marks 01a as skipped when 02_assets already approved" {
  OLD="$BATS_TEST_TMPDIR/legacy-project"
  mkdir -p "$OLD"
  cat > "$OLD/.landing-state.yaml" <<'EOF'
project: "legacy"
created: "2026-04-01T00:00:00Z"
schema_version: 1
stages:
  "00_brief":
    status: approved
    timestamp: ""
  "01_context":
    status: approved
    timestamp: ""
  "02_assets":
    status: approved
    timestamp: ""
EOF
  bash "$REPO/scripts/migrate-state-add-01a.sh" "$OLD" >/dev/null
  status_value="$(yq -r '.stages."01a_niche_analysis".status' "$OLD/.landing-state.yaml")"
  [ "$status_value" = "skipped" ]
}

@test "migrate-state script marks 01a as locked when 02_assets not yet approved" {
  NEW="$BATS_TEST_TMPDIR/new-project"
  mkdir -p "$NEW"
  cat > "$NEW/.landing-state.yaml" <<'EOF'
project: "new"
created: "2026-05-01T00:00:00Z"
schema_version: 1
stages:
  "00_brief":
    status: approved
    timestamp: ""
  "01_context":
    status: in_progress
    timestamp: ""
  "02_assets":
    status: locked
    timestamp: ""
EOF
  bash "$REPO/scripts/migrate-state-add-01a.sh" "$NEW" >/dev/null
  status_value="$(yq -r '.stages."01a_niche_analysis".status' "$NEW/.landing-state.yaml")"
  [ "$status_value" = "locked" ]
}

@test "gate-check 01a fails when visual-requirements.md is missing (other 3 artifacts present)" {
  REPO="$(cd "$(dirname "$BATS_TEST_FILENAME")/../.." && pwd)"
  PROJECT="$BATS_TEST_TMPDIR/test-vr-missing"
  mkdir -p "$PROJECT"
  cp -r "$REPO/template/." "$PROJECT/"
  if command -v yq >/dev/null 2>&1; then
    yq -i '.stages."00_brief".status = "approved"' "$PROJECT/.landing-state.yaml"
  else
    skip "yq not installed"
  fi
  # Provide 3 of 4 artifacts; visual-requirements.md missing
  mkdir -p "$PROJECT/01a_АНАЛИЗ_НИШИ"
  printf "# stub\n" > "$PROJECT/01a_АНАЛИЗ_НИШИ/niche-analysis.md"
  printf "competitors: []\n" > "$PROJECT/01a_АНАЛИЗ_НИШИ/competitors.yaml"
  printf "# stub\n" > "$PROJECT/01a_АНАЛИЗ_НИШИ/positioning.md"

  run bash "$REPO/scripts/gate-check.sh" --stage 01a_niche_analysis --project "$PROJECT" --auto
  [ "$status" -ne 0 ]
  [[ "$output" == *"visual-requirements"* ]] || [[ "$output" == *"visual_requirements"* ]]
}
