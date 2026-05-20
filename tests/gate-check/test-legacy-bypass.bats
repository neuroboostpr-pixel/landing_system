#!/usr/bin/env bats

setup() {
    REPO_ROOT="$(cd "$BATS_TEST_DIRNAME/../.." && pwd)"
    export REPO_ROOT
    export TMP_PROJ="$(mktemp -d)/test-proj"
    mkdir -p "$TMP_PROJ"
    export TEST_GATES="$(mktemp).yaml"
    export LANDING_SYSTEM_ROOT="$(mktemp -d)/landing-system-root"
    mkdir -p "$LANDING_SYSTEM_ROOT/audit"
}

teardown() {
    rm -rf "$TMP_PROJ" "$LANDING_SYSTEM_ROOT"
    rm -f "$TEST_GATES"
}

@test "legacy bypass fails when stage not in legacy_allowed list" {
    cat > "$TMP_PROJ/.landing-state.yaml" <<'EOF'
project: "test"
stages:
  "08_build":
    status: locked
    legacy: true
    legacy_reason: "old project"
EOF
    run bash "$REPO_ROOT/scripts/gate-check.sh" --stage 08_build \
        --project "$TMP_PROJ" --auto
    [ "$status" -ne 0 ]
    [[ "$output" == *"not in legacy_allowed"* ]] || [[ "$output" == *"legacy_allowed"* ]]
}

@test "legacy bypass fails when legacy_reason missing" {
    cat > "$TEST_GATES" <<'EOF'
legacy_allowed: ["06_stack"]
stages:
  "06_stack":
    name: "Stack"
    lock: hard
    require_approved: []
    hard_checks: []
EOF
    cat > "$TMP_PROJ/.landing-state.yaml" <<'EOF'
project: "test"
stages:
  "06_stack":
    status: locked
    legacy: true
EOF
    run env GATES_YAML="$TEST_GATES" bash "$REPO_ROOT/scripts/gate-check.sh" \
        --stage 06_stack --project "$TMP_PROJ" --auto
    [ "$status" -ne 0 ]
    [[ "$output" == *"legacy_reason"* ]]
}

@test "legacy bypass succeeds when stage allowlisted AND reason provided" {
    cat > "$TEST_GATES" <<'EOF'
legacy_allowed: ["06_stack"]
stages:
  "06_stack":
    name: "Stack"
    lock: hard
    require_approved: []
    hard_checks: []
EOF
    cat > "$TMP_PROJ/.landing-state.yaml" <<'EOF'
project: "test"
stages:
  "06_stack":
    status: locked
    legacy: true
    legacy_reason: "migrated from v1"
EOF
    run env GATES_YAML="$TEST_GATES" bash "$REPO_ROOT/scripts/gate-check.sh" \
        --stage 06_stack --project "$TMP_PROJ" --auto
    [ "$status" -eq 0 ]
    [[ "$output" == *"LEGACY BYPASS"* ]]
}
