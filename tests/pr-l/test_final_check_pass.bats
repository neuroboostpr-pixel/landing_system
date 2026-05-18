#!/usr/bin/env bats
load 'helpers.bash'

# Если все verify-скрипты возвращают exit 0 → landing-final-check.sh exit 0.

setup() {
    SANDBOX="$(pr_l_make_sandbox 0 0 0 0 0 0)"
    PROJECT="$(pr_l_make_project)"
}

teardown() {
    rm -rf "$SANDBOX" "$PROJECT"
}

@test "final-check: все verify exit 0 → exit 0, SUMMARY PASS" {
    run bash "$SANDBOX/scripts/landing-final-check.sh" "$PROJECT"
    [ "$status" -eq 0 ]
    [[ "$output" == *"Final check: PASS"* ]]
}
