#!/usr/bin/env bats

setup() {
    SCRIPT="$BATS_TEST_DIRNAME/../../scripts/wizard.sh"
    export HOME="$BATS_TEST_TMPDIR"
    export WIZARD_NONINTERACTIVE=1
}

@test "wizard prints intro section" {
    run bash "$SCRIPT"
    [[ "$output" == *"Landing System Onboarding"* ]]
}

@test "wizard checks local deps section" {
    run bash "$SCRIPT"
    [[ "$output" == *"Локальные зависимости"* ]]
}

@test "wizard checks API keys section" {
    run bash "$SCRIPT"
    [[ "$output" == *"API"* ]]
}

@test "wizard does not mark complete when validators fail" {
    run bash "$SCRIPT"
    [ ! -f "$HOME/.landing-system/setup_complete" ]
}
