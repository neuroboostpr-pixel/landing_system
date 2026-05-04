#!/usr/bin/env bats

setup() {
    export HOME="$BATS_TEST_TMPDIR"
    SCRIPT="$BATS_TEST_DIRNAME/../../scripts/setup-flag.sh"
}

@test "is_complete returns 1 when flag missing" {
    run bash "$SCRIPT" is_complete
    [ "$status" -eq 1 ]
}

@test "mark_complete creates flag file" {
    run bash "$SCRIPT" mark_complete
    [ "$status" -eq 0 ]
    [ -f "$HOME/.landing-system/setup_complete" ]
}

@test "is_complete returns 0 after mark_complete" {
    bash "$SCRIPT" mark_complete
    run bash "$SCRIPT" is_complete
    [ "$status" -eq 0 ]
}

@test "reset removes flag file" {
    bash "$SCRIPT" mark_complete
    run bash "$SCRIPT" reset
    [ "$status" -eq 0 ]
    [ ! -f "$HOME/.landing-system/setup_complete" ]
}
