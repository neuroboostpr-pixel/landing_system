#!/usr/bin/env bats

setup() {
    REPO_ROOT="$(cd "$BATS_TEST_DIRNAME/../.." && pwd)"
    export REPO_ROOT
    export TMP_PROJ="$(mktemp -d)/test-proj"
    mkdir -p "$TMP_PROJ"
    cp "$REPO_ROOT/template/.landing-state.yaml" "$TMP_PROJ/.landing-state.yaml"

    export TEST_GATES="$(mktemp).yaml"
    cat > "$TEST_GATES" <<'EOF'
stages:
  "test_stage":
    name: "Test"
    lock: hard
    require_approved: []
    hard_checks:
      - id: unknown_check
        type: this_type_does_not_exist
        required: true
EOF
}

teardown() {
    rm -rf "$TMP_PROJ" "$TEST_GATES"
}

@test "gate-check fails (exit != 0) when hard_check uses unknown type" {
    run env GATES_YAML="$TEST_GATES" bash "$REPO_ROOT/scripts/gate-check.sh" \
        --stage test_stage --project "$TMP_PROJ" --auto
    [ "$status" -ne 0 ]
    [[ "$output" == *"unknown"* ]]
    [[ "$output" == *"this_type_does_not_exist"* ]]
}
