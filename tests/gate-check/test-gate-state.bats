#!/usr/bin/env bats

setup() {
    SCRIPT="$BATS_TEST_DIRNAME/../../scripts/gate-state.sh"
    PROJECT_DIR="$BATS_TEST_TMPDIR/test-project"
    mkdir -p "$PROJECT_DIR"
    cp "$BATS_TEST_DIRNAME/../../template/.landing-state.yaml" "$PROJECT_DIR/.landing-state.yaml"
}

@test "get returns status of stage" {
    run bash "$SCRIPT" get "$PROJECT_DIR" "00_brief"
    [ "$status" -eq 0 ]
    [ "$output" = "n/a" ]
}

@test "get returns 'locked' for unstarted stage" {
    run bash "$SCRIPT" get "$PROJECT_DIR" "08_build"
    [ "$output" = "locked" ]
}

@test "set updates stage status" {
    bash "$SCRIPT" set "$PROJECT_DIR" "02_assets" "in_progress"
    run bash "$SCRIPT" get "$PROJECT_DIR" "02_assets"
    [ "$output" = "in_progress" ]
}

@test "approve marks status approved with timestamp" {
    bash "$SCRIPT" approve "$PROJECT_DIR" "02_assets"
    run bash "$SCRIPT" get "$PROJECT_DIR" "02_assets"
    [ "$output" = "approved" ]
}

@test "all_approved returns 0 when all listed stages are approved" {
    bash "$SCRIPT" approve "$PROJECT_DIR" "00_brief"
    bash "$SCRIPT" approve "$PROJECT_DIR" "01_context"
    run bash "$SCRIPT" all_approved "$PROJECT_DIR" "00_brief,01_context"
    [ "$status" -eq 0 ]
}

@test "all_approved returns 1 when any stage not approved" {
    bash "$SCRIPT" approve "$PROJECT_DIR" "00_brief"
    # 03_references is "locked" in template (not n/a), so all_approved must return 1
    run bash "$SCRIPT" all_approved "$PROJECT_DIR" "00_brief,03_references"
    [ "$status" -eq 1 ]
    [[ "$output" == *"03_references"* ]]
}
