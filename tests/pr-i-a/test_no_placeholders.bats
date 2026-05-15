#!/usr/bin/env bats
load 'helpers.bash'

@test "fail: composed.html содержит SVG placeholder" {
    project="$(make_project_with_placeholder)"
    run bash "$PR_I_A_REPO_ROOT/scripts/verify-photo-pipeline.sh" "$project"
    [ "$status" -eq 1 ]
    [[ "$output" == *"placeholder"* ]]
}

@test "pass: composed.html использует только processed/ файлы" {
    project="$(make_project_with_real_photos)"
    run bash "$PR_I_A_REPO_ROOT/scripts/verify-photo-pipeline.sh" "$project"
    [ "$status" -eq 0 ]
}
