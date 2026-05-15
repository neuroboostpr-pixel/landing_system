#!/usr/bin/env bats
load 'helpers.bash'

@test "pass: все строки прототипа есть в composed.html, порядок верный" {
    project="$(make_fake_project)"
    run bash "$PR_H_REPO_ROOT/scripts/verify-content-preserved.sh" "$project"
    [ "$status" -eq 0 ]
    [[ "$output" == *"Контент прототипа сохранён"* ]]
}
