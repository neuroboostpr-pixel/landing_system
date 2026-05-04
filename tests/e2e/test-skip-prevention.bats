#!/usr/bin/env bats

setup() {
    REPO_ROOT="$BATS_TEST_DIRNAME/../.."
    PROJECT_DIR="$BATS_TEST_TMPDIR/skip-prevention"
    mkdir -p "$PROJECT_DIR/00_БРИФ" "$PROJECT_DIR/05_ДИЗАЙН-СИСТЕМА" "$PROJECT_DIR/07_КОНТЕНТ" "$PROJECT_DIR/08_КОД/wp-theme"
    cp "$REPO_ROOT/template/.landing-state.yaml" "$PROJECT_DIR/.landing-state.yaml"
    echo "brief" > "$PROJECT_DIR/00_БРИФ/brief.md"
    echo "design" > "$PROJECT_DIR/05_ДИЗАЙН-СИСТЕМА/DESIGN.md"
    echo "copy" > "$PROJECT_DIR/07_КОНТЕНТ/final-copy.md"
    echo "<?php" > "$PROJECT_DIR/08_КОД/wp-theme/functions.php"
    export GATE_AUTO=1
}

@test "08_build refuses when 02-07 not approved" {
    run bash "$REPO_ROOT/scripts/gate-check.sh" --stage 08_build --project "$PROJECT_DIR"
    [ "$status" -ne 0 ]
    [[ "$output" == *"not approved"* || "$output" == *"02_assets"* || "$output" == *"07_content"* ]]
}

@test "09_deploy refuses when 08_build not approved" {
    run bash "$REPO_ROOT/scripts/gate-check.sh" --stage 09_deploy --project "$PROJECT_DIR"
    [ "$status" -ne 0 ]
    [[ "$output" == *"08_build"* ]]
}
