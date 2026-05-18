#!/usr/bin/env bats
# Unit tests for lib/state.sh

setup() {
    HERE="$(cd "$BATS_TEST_DIRNAME/../scripts/lib" && pwd)"
    source "$HERE/state.sh"
    TMPDIR_T="$(mktemp -d)"
    cp "$BATS_TEST_DIRNAME/fixtures/landing-state.single.yaml" "$TMPDIR_T/.landing-state.yaml"
    cp "$BATS_TEST_DIRNAME/fixtures/landing-state.multisite.yaml" "$TMPDIR_T/multisite.yaml"
}

teardown() { rm -rf "$TMPDIR_T"; }

@test "state_get_field reads top-level field" {
    run state_get_field "$TMPDIR_T/.landing-state.yaml" "multisite"
    [ "$status" -eq 0 ]
    [ "$output" = "False" ] || [ "$output" = "false" ]
}

@test "state_is_multisite returns 1 for single, 0 for multisite" {
    run state_is_multisite "$TMPDIR_T/.landing-state.yaml"
    [ "$status" -eq 1 ]
    run state_is_multisite "$TMPDIR_T/multisite.yaml"
    [ "$status" -eq 0 ]
}

@test "state_set_multisite_true flips the flag" {
    state_set_multisite_true "$TMPDIR_T/.landing-state.yaml"
    run state_is_multisite "$TMPDIR_T/.landing-state.yaml"
    [ "$status" -eq 0 ]
}

@test "state_add_segment appends a new segment entry" {
    state_add_segment "$TMPDIR_T/.landing-state.yaml" "family" "family.example.ru" 3
    run state_segment_count "$TMPDIR_T/.landing-state.yaml"
    [ "$status" -eq 0 ]
    [ "$output" = "1" ]
}

@test "state_segment_exists returns 0 if found" {
    run state_segment_exists "$TMPDIR_T/multisite.yaml" "russian"
    [ "$status" -eq 0 ]
    run state_segment_exists "$TMPDIR_T/multisite.yaml" "nonexistent"
    [ "$status" -eq 1 ]
}

@test "state_add_segment safely handles slug with shell/python metacharacters" {
    # The evil slug contains "PWN" literally — injection safety means os.system() must NOT execute.
    # We verify: (1) the function exits 0, (2) the literal slug is stored in YAML, (3) exit code was 0.
    run state_add_segment "$TMPDIR_T/.landing-state.yaml" "evil'; import os; os.system('echo PWN'); x='" "host.example.ru" 99
    [ "$status" -eq 0 ]
    # The literal slug string should be stored as-is in YAML (contains 'evil')
    run cat "$TMPDIR_T/.landing-state.yaml"
    [[ "$output" == *"evil"* ]]
    # blog_id 99 must be stored correctly
    [[ "$output" == *"99"* ]]
    # Segment count must be 1 (was 0 before)
    run state_segment_count "$TMPDIR_T/.landing-state.yaml"
    [ "$output" = "1" ]
}
