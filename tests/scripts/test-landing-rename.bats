#!/usr/bin/env bats

setup() {
    REPO_ROOT="$BATS_TEST_DIRNAME/../.."
    SCRIPT="$REPO_ROOT/scripts/landing-rename.sh"
    export LANDINGS_ROOT="$BATS_TEST_TMPDIR/Lendings"
    mkdir -p "$LANDINGS_ROOT"
}

_make_project() {
    local slug="$1"
    local dir="$LANDINGS_ROOT/$slug"
    mkdir -p "$dir/00_БРИФ"
    cat > "$dir/.landing-state.yaml" <<EOF
project: $slug
current_stage: 03_references
stages:
  "03_references": {status: locked, timestamp: ""}
EOF
    echo "# Project $slug readme" > "$dir/README.md"
    mkdir -p "$dir/00_БРИФ"
    echo "# Brief for $slug" > "$dir/00_БРИФ/brief.md"
}

@test "no args prints usage and exits 1" {
    run bash "$SCRIPT"
    [ "$status" -eq 1 ]
    [[ "$output" == *"Usage"* ]]
}

@test "one arg prints usage and exits 1" {
    run bash "$SCRIPT" old-slug
    [ "$status" -eq 1 ]
    [[ "$output" == *"Usage"* ]]
}

@test "old slug not found exits 1" {
    run bash "$SCRIPT" no-such-project new-name
    [ "$status" -eq 1 ]
    [[ "$output" == *"не найден"* ]]
}

@test "old folder without .landing-state.yaml exits 1" {
    mkdir -p "$LANDINGS_ROOT/not-a-project"
    run bash "$SCRIPT" not-a-project new-name
    [ "$status" -eq 1 ]
    [[ "$output" == *"не лендинг-проект"* ]]
}

@test "new slug already exists exits 1" {
    _make_project old-name
    _make_project already-exists
    run bash "$SCRIPT" old-name already-exists
    [ "$status" -eq 1 ]
    [[ "$output" == *"уже существует"* ]]
}

@test "invalid new slug (uppercase) exits 1" {
    _make_project old-name
    run bash "$SCRIPT" old-name NewName
    [ "$status" -eq 1 ]
    [[ "$output" == *"kebab-case"* ]]
}

@test "invalid new slug (spaces) exits 1" {
    _make_project old-name
    run bash "$SCRIPT" old-name "new name"
    [ "$status" -eq 1 ]
    [[ "$output" == *"kebab-case"* ]]
}

@test "successful rename moves folder" {
    _make_project old-name
    run bash "$SCRIPT" old-name new-name
    [ "$status" -eq 0 ]
    [ ! -d "$LANDINGS_ROOT/old-name" ]
    [ -d "$LANDINGS_ROOT/new-name" ]
}

@test "successful rename updates project field in .landing-state.yaml" {
    _make_project old-name
    bash "$SCRIPT" old-name new-name
    VALUE=$(yq e '.project' "$LANDINGS_ROOT/new-name/.landing-state.yaml")
    [ "$VALUE" = "new-name" ]
}

@test "successful rename updates old slug in README.md" {
    _make_project old-name
    bash "$SCRIPT" old-name new-name
    run grep "old-name" "$LANDINGS_ROOT/new-name/README.md"
    [ "$status" -ne 0 ]
}

@test "successful rename updates old slug in brief.md if exists" {
    _make_project old-name
    bash "$SCRIPT" old-name new-name
    run grep "old-name" "$LANDINGS_ROOT/new-name/00_БРИФ/brief.md"
    [ "$status" -ne 0 ]
}

@test "rename prints success message" {
    _make_project old-name
    run bash "$SCRIPT" old-name new-name
    [[ "$output" == *"old-name"* ]]
    [[ "$output" == *"new-name"* ]]
    [[ "$output" == *"✅"* ]]
}
