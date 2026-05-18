#!/usr/bin/env bats
load 'helpers.bash'

setup() {
    PROJECT="$(make_project_with_composed)"
}

teardown() {
    rm -rf "$PROJECT"
}

@test "previews: все 3 файла существуют после запуска" {
    run bash "$PR_M_REPO_ROOT/scripts/generate-previews.sh" "$PROJECT"
    [ "$status" -eq 0 ]
    [ -f "$PROJECT/07b_COMPOSED/composed-desktop-preview.html" ]
    [ -f "$PROJECT/07b_COMPOSED/composed-mobile-preview.html" ]
    [ -f "$PROJECT/07b_COMPOSED/composed-previews-index.html" ]
}

@test "previews: если composed.html нет → exit 2" {
    rm -f "$PROJECT/07b_COMPOSED/composed.html"
    run bash "$PR_M_REPO_ROOT/scripts/generate-previews.sh" "$PROJECT"
    [ "$status" -eq 2 ]
}
