#!/usr/bin/env bats
load 'helpers.bash'

@test "verify-identity: manifest без violations → exit 0" {
    project=$(make_project_with_manifest "")
    run bash "$PR_J_REPO_ROOT/scripts/verify-identity-preserved.sh" "$project"
    [ "$status" -eq 0 ]
    [[ "$output" == *"Identity сохранён"* ]]
}

@test "verify-identity: manifest с violation → exit 1 + details" {
    project=$(make_project_with_manifest "yes")
    run bash "$PR_J_REPO_ROOT/scripts/verify-identity-preserved.sh" "$project"
    [ "$status" -eq 1 ]
    [[ "$output" == *"hero-bg.jpg"* ]] || [[ "$output" == *"distance"* ]]
}

@test "verify-identity: manifest отсутствует → exit 0 (no-op)" {
    tmpdir=$(mktemp -d)
    run bash "$PR_J_REPO_ROOT/scripts/verify-identity-preserved.sh" "$tmpdir"
    [ "$status" -eq 0 ]
    [[ "$output" == *"нет processed manifest"* ]] || [[ "$output" == *"OK"* ]]
}
