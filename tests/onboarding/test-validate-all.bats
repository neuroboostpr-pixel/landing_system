#!/usr/bin/env bats

setup() {
    SCRIPT="$BATS_TEST_DIRNAME/../../scripts/validate-all.sh"
    cd "$BATS_TEST_DIRNAME/../.."
}

@test "validate-all.sh executes aggregate.py" {
    run bash "$SCRIPT"
    # Exit code 1 expected because no real keys are set
    [ "$status" -eq 1 ]
    [[ "$output" == *"firecrawl"* ]]
    [[ "$output" == *"pexels"* ]]
}

@test "validate-all.sh --service firecrawl runs only firecrawl" {
    run bash "$SCRIPT" --service firecrawl
    [[ "$output" == *"firecrawl"* ]]
    [[ "$output" != *"pexels"* ]]
}
