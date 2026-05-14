#!/usr/bin/env bats

REPO="$(cd "$(dirname "${BATS_TEST_FILENAME}")/../.." && pwd)"

setup() {
    TMP_PROJECT="$(mktemp -d)"
    mkdir -p "$TMP_PROJECT/07_ПРОТОТИП/source"
    cat > "$TMP_PROJECT/.landing-state.yaml" <<EOF
project: test
created: "2026-05-13"
schema_version: 2
stages:
  "00_brief":           {status: n/a, timestamp: ""}
  "01_context":         {status: n/a, timestamp: ""}
  "01a_niche_analysis": {status: n/a, timestamp: ""}
  "02_assets":          {status: n/a, timestamp: ""}
  "07a_prototype":      {status: in_progress, timestamp: ""}
  "07b_wireframe":      {status: locked, timestamp: ""}
EOF
    touch "$TMP_PROJECT/07_ПРОТОТИП/prototype.yaml"
}

teardown() { rm -rf "$TMP_PROJECT"; }

@test "gate-check passes for 07a_prototype with all upstream n/a" {
    run bash "$REPO/scripts/gate-check.sh" --project "$TMP_PROJECT" --stage "07a_prototype" --auto
    [ "$status" -eq 0 ]
}

@test "gate-state.sh accepts n/a status for read" {
    run bash "$REPO/scripts/gate-state.sh" get "$TMP_PROJECT" "00_brief"
    [ "$status" -eq 0 ]
    echo "$output" | grep -q "n/a"
}

@test "gate-check satisfies require_approved when upstream is n/a" {
    # Mark 07a_prototype approved (07b_wireframe requires it)
    python3 -c "
import yaml
p = '$TMP_PROJECT/.landing-state.yaml'
data = yaml.safe_load(open(p).read())
data['stages']['07a_prototype']['status'] = 'approved'
open(p, 'w').write(yaml.safe_dump(data, allow_unicode=True))
"
    mkdir -p "$TMP_PROJECT/07a_WIREFRAME"
    touch "$TMP_PROJECT/07a_WIREFRAME/wireframe.html"
    touch "$TMP_PROJECT/07a_WIREFRAME/selections.yaml"

    run bash "$REPO/scripts/gate-check.sh" --project "$TMP_PROJECT" --stage "07b_wireframe" --auto
    [ "$status" -eq 0 ]
}

@test "gate-state.sh can set status to n/a" {
    run bash "$REPO/scripts/gate-state.sh" set "$TMP_PROJECT" "06_stack" "n/a"
    [ "$status" -eq 0 ]
    run bash "$REPO/scripts/gate-state.sh" get "$TMP_PROJECT" "06_stack"
    echo "$output" | grep -q "n/a"
}

@test "gate-state.sh all_approved treats n/a as satisfied" {
    # 00_brief is n/a in setup — all_approved must consider it satisfied
    run bash "$REPO/scripts/gate-state.sh" all_approved "$TMP_PROJECT" "00_brief"
    [ "$status" -eq 0 ]
}

@test "gate-state.sh all_approved treats multiple n/a upstreams as satisfied" {
    run bash "$REPO/scripts/gate-state.sh" all_approved "$TMP_PROJECT" "00_brief,01_context,01a_niche_analysis,02_assets"
    [ "$status" -eq 0 ]
}
