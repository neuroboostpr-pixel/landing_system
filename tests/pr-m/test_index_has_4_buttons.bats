#!/usr/bin/env bats
load 'helpers.bash'

setup() {
    PROJECT="$(make_project_with_composed)"
    bash "$PR_M_REPO_ROOT/scripts/generate-previews.sh" "$PROJECT" >/dev/null
    INDEX="$PROJECT/07b_COMPOSED/composed-previews-index.html"
}

teardown() {
    rm -rf "$PROJECT"
}

@test "index имеет кнопку 375 (mobile)" {
    grep -q 'data-w="375"' "$INDEX"
}

@test "index имеет кнопку 768 (tablet)" {
    grep -q 'data-w="768"' "$INDEX"
}

@test "index имеет кнопку 1280 (desktop)" {
    grep -q 'data-w="1280"' "$INDEX"
}

@test "index имеет кнопку 1920 (wide)" {
    grep -q 'data-w="1920"' "$INDEX"
}

@test "index содержит JS для переключения" {
    grep -q "addEventListener" "$INDEX"
}
