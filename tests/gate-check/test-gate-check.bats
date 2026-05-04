#!/usr/bin/env bats

setup() {
    REPO_ROOT="$BATS_TEST_DIRNAME/../.."
    SCRIPT="$REPO_ROOT/scripts/gate-check.sh"
    PROJECT_DIR="$BATS_TEST_TMPDIR/test-project"
    mkdir -p "$PROJECT_DIR/00_БРИФ"
    cp "$REPO_ROOT/template/.landing-state.yaml" "$PROJECT_DIR/.landing-state.yaml"
    export GATE_AUTO=1
}

@test "fails when require_approved stages not approved" {
    # 02_assets requires 00_brief + 01_context
    run bash "$SCRIPT" --stage 02_assets --project "$PROJECT_DIR"
    [ "$status" -ne 0 ]
    [[ "$output" == *"00_brief"* || "$output" == *"01_context"* ]]
}

@test "fails when hard_check file_exists fails" {
    bash "$REPO_ROOT/scripts/gate-state.sh" approve "$PROJECT_DIR" "00_brief"
    bash "$REPO_ROOT/scripts/gate-state.sh" approve "$PROJECT_DIR" "01_context"
    # 02_assets requires PEXELS/UNSPLASH/PIXABAY ENV — none set in tests
    run bash "$SCRIPT" --stage 02_assets --project "$PROJECT_DIR"
    [ "$status" -ne 0 ]
}

@test "passes when stage 00_brief has brief.md" {
    echo "test brief" > "$PROJECT_DIR/00_БРИФ/brief.md"
    run bash "$SCRIPT" --stage 00_brief --project "$PROJECT_DIR"
    [ "$status" -eq 0 ]
}

@test "approve flag sets status to approved" {
    echo "test brief" > "$PROJECT_DIR/00_БРИФ/brief.md"
    bash "$SCRIPT" --stage 00_brief --project "$PROJECT_DIR" --approve
    run bash "$REPO_ROOT/scripts/gate-state.sh" get "$PROJECT_DIR" "00_brief"
    [ "$output" = "approved" ]
}
