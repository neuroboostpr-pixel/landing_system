#!/usr/bin/env bats
load 'helpers.bash'

@test "fail: заголовок hero изменён в composed.html" {
    project="$(make_fake_project)"
    sed -i.bak 's/Welcome to LiXiang/Welcome to BMW/' "$project/07b_COMPOSED/composed.html"
    run bash "$PR_H_REPO_ROOT/scripts/verify-content-preserved.sh" "$project"
    [ "$status" -eq 1 ]
    [[ "$output" == *"Welcome to LiXiang"* ]] || [[ "$output" == *"не найдено"* ]]
}
