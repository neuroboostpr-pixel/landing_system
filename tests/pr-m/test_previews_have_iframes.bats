#!/usr/bin/env bats
load 'helpers.bash'

setup() {
    PROJECT="$(make_project_with_composed)"
    bash "$PR_M_REPO_ROOT/scripts/generate-previews.sh" "$PROJECT" >/dev/null
}

teardown() {
    rm -rf "$PROJECT"
}

@test "desktop preview содержит iframe src=composed.html" {
    grep -q '<iframe src="composed.html"' "$PROJECT/07b_COMPOSED/composed-desktop-preview.html"
}

@test "mobile preview содержит iframe src=composed.html" {
    grep -q '<iframe src="composed.html"' "$PROJECT/07b_COMPOSED/composed-mobile-preview.html"
}

@test "index содержит iframe src=composed.html" {
    grep -q '<iframe src="composed.html"' "$PROJECT/07b_COMPOSED/composed-previews-index.html"
}

@test "desktop preview содержит 1280×800" {
    grep -q "1280" "$PROJECT/07b_COMPOSED/composed-desktop-preview.html"
    grep -q "800"  "$PROJECT/07b_COMPOSED/composed-desktop-preview.html"
}

@test "mobile preview содержит 375×812" {
    grep -q "375" "$PROJECT/07b_COMPOSED/composed-mobile-preview.html"
    grep -q "812" "$PROJECT/07b_COMPOSED/composed-mobile-preview.html"
}
