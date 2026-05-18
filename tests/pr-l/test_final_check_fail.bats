#!/usr/bin/env bats
load 'helpers.bash'

# Если хоть один обязательный verify exit 1 → landing-final-check.sh exit 1.

setup() {
    # composed-premium exit 1 (обязательная)
    SANDBOX="$(pr_l_make_sandbox 0 1 0 0 0 0)"
    PROJECT="$(pr_l_make_project)"
}

teardown() {
    rm -rf "$SANDBOX" "$PROJECT"
}

@test "final-check: composed-premium exit 1 → exit 1, SUMMARY FAIL" {
    run bash "$SANDBOX/scripts/landing-final-check.sh" "$PROJECT"
    [ "$status" -eq 1 ]
    [[ "$output" == *"Final check: FAIL"* ]]
}

@test "final-check: опциональный (visual-qa) exit 1 → всё равно exit 0" {
    local sandbox2
    sandbox2="$(pr_l_make_sandbox 0 0 0 0 0 1)"
    local project2
    project2="$(pr_l_make_project)"
    run bash "$sandbox2/scripts/landing-final-check.sh" "$project2"
    [ "$status" -eq 0 ]
    [[ "$output" == *"Final check: PASS"* ]]
    rm -rf "$sandbox2" "$project2"
}
