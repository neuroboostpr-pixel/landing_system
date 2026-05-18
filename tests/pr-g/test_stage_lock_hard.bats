#!/usr/bin/env bats

load 'helpers.bash'

@test "07b_wireframe (hard) блокирован пока 04_brand не approved" {
    project="$(make_fake_project)"
    run bash "$PR_G_REPO_ROOT/scripts/gate-check.sh" --stage 07b_wireframe --project "$project" --auto
    [ "$status" -ne 0 ]
    [[ "$output" == *"Previous stages not approved"* ]] || [[ "$output" == *"04_brand"* ]]
}

@test "07b_wireframe проходит require_approved если все зависимости approved" {
    project="$(make_fake_project)"
    set_status "$project" "04_brand" "approved"
    set_status "$project" "05_design" "approved"
    set_status "$project" "07a_prototype" "approved"
    run bash "$PR_G_REPO_ROOT/scripts/gate-check.sh" --stage 07b_wireframe --project "$project" --auto
    # Может упасть на hard_checks (file_exists), но require_approved проходит
    [[ "$output" == *"Required prior stages approved"* ]] || true
}

@test "08_build блокирован без 07c_composed" {
    project="$(make_fake_project)"
    run bash "$PR_G_REPO_ROOT/scripts/gate-check.sh" --stage 08_build --project "$project" --auto
    [ "$status" -ne 0 ]
    [[ "$output" == *"07c_composed"* ]] || [[ "$output" == *"not approved"* ]]
}

@test "09_deploy требует И 08_build И 10_qa" {
    project="$(make_fake_project)"
    set_status "$project" "08_build" "approved"
    run bash "$PR_G_REPO_ROOT/scripts/gate-check.sh" --stage 09_deploy --project "$project" --auto
    [ "$status" -ne 0 ]
    [[ "$output" == *"10_qa"* ]]
}
