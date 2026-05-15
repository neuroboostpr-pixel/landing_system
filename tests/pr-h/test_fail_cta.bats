#!/usr/bin/env bats
load 'helpers.bash'

@test "fail: CTA-текст изменён в composed.html" {
    project="$(make_fake_project)"
    sed -i.bak 's/Request a test drive/Get a quote/' "$project/07b_COMPOSED/composed.html"
    run bash "$PR_H_REPO_ROOT/scripts/verify-content-preserved.sh" "$project"
    [ "$status" -eq 1 ]
    [[ "$output" == *"Request a test drive"* ]] || [[ "$output" == *"не найдено"* ]]
}
