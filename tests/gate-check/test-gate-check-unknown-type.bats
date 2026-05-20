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

@test "file_or_dir_exists passes when file exists" {
    PRO="$(mktemp -d)"
    touch "$PRO/some-file"
    cat > "$TEST_GATES" <<EOF
stages:
  "test_stage":
    name: "Test"
    lock: hard
    require_approved: []
    hard_checks:
      - id: prototype_exists
        type: file_or_dir_exists
        path: "$PRO/some-file"
        required: true
EOF
    run env GATES_YAML="$TEST_GATES" bash "$REPO_ROOT/scripts/gate-check.sh" \
        --stage test_stage --project "$PRO" --auto
    [ "$status" -eq 0 ]
    rm -rf "$PRO"
}

@test "file_or_dir_exists passes when directory exists with content" {
    PRO="$(mktemp -d)"
    mkdir -p "$PRO/some-dir"
    touch "$PRO/some-dir/inner.txt"
    cat > "$TEST_GATES" <<EOF
stages:
  "test_stage":
    name: "Test"
    lock: hard
    require_approved: []
    hard_checks:
      - id: src_dir
        type: file_or_dir_exists
        path: "$PRO/some-dir"
        required: true
EOF
    run env GATES_YAML="$TEST_GATES" bash "$REPO_ROOT/scripts/gate-check.sh" \
        --stage test_stage --project "$PRO" --auto
    [ "$status" -eq 0 ]
    rm -rf "$PRO"
}

@test "file_or_dir_exists fails when neither exists" {
    PRO="$(mktemp -d)"
    cat > "$TEST_GATES" <<EOF
stages:
  "test_stage":
    name: "Test"
    lock: hard
    require_approved: []
    hard_checks:
      - id: missing
        type: file_or_dir_exists
        path: "$PRO/nonexistent"
        required: true
EOF
    run env GATES_YAML="$TEST_GATES" bash "$REPO_ROOT/scripts/gate-check.sh" \
        --stage test_stage --project "$PRO" --auto
    [ "$status" -ne 0 ]
    rm -rf "$PRO"
}
