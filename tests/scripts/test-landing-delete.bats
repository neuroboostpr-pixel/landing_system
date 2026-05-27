#!/usr/bin/env bats

setup() {
    REPO_ROOT="$BATS_TEST_DIRNAME/../.."
    SCRIPT="$REPO_ROOT/scripts/landing-delete.sh"
    # Create a fake LANDINGS_ROOT in tmpdir
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
    echo "# $slug" > "$dir/README.md"
}

@test "no args prints usage and exits 1" {
    run bash "$SCRIPT"
    [ "$status" -eq 1 ]
    [[ "$output" == *"Usage"* ]]
}

@test "non-existent slug exits 1 with error" {
    run bash "$SCRIPT" no-such-project
    [ "$status" -eq 1 ]
    [[ "$output" == *"не найден"* ]]
}

@test "folder without .landing-state.yaml exits 1" {
    mkdir -p "$LANDINGS_ROOT/not-a-project"
    run bash "$SCRIPT" not-a-project
    [ "$status" -eq 1 ]
    [[ "$output" == *"не лендинг-проект"* ]]
}

@test "wrong confirmation aborts deletion" {
    _make_project myproject
    run bash "$SCRIPT" myproject <<< "wrong-name"
    [ "$status" -eq 1 ]
    [[ "$output" == *"отменено"* ]]
    [ -d "$LANDINGS_ROOT/myproject" ]
}

@test "correct confirmation deletes folder" {
    _make_project myproject
    run bash "$SCRIPT" myproject <<< "myproject"
    [ "$status" -eq 0 ]
    [[ "$output" == *"удалён"* ]]
    [ ! -d "$LANDINGS_ROOT/myproject" ]
}

@test "summary shows project name and stage before confirmation" {
    _make_project myproject
    run bash "$SCRIPT" myproject <<< "wrong"
    [[ "$output" == *"myproject"* ]]
    [[ "$output" == *"03_references"* ]]
}
