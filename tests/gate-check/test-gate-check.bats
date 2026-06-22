#!/usr/bin/env bats

setup() {
    REPO_ROOT="$BATS_TEST_DIRNAME/../.."
    SCRIPT="$REPO_ROOT/scripts/gate-check.sh"
    PROJECT_DIR="$BATS_TEST_TMPDIR/test-project"
    mkdir -p "$PROJECT_DIR/00_БРИФ"
    cp "$REPO_ROOT/template/.landing-state.yaml" "$PROJECT_DIR/.landing-state.yaml"
    export GATE_AUTO=1
}

create_ds_asset_pack_plan() {
    local project="$1"
    local mood_dir="$project/05_ДИЗАЙН-СИСТЕМА/moods/grooming"
    mkdir -p "$mood_dir"
    cat > "$mood_dir/recipes.yaml" <<'YAML'
meta:
  mood: grooming
recipes: []
YAML
    cat > "$mood_dir/assets-manifest.yaml" <<'YAML'
meta:
  mood: grooming
assets:
  - id: page-bg
    нужен: true
    роль_где: фон страницы
    источник: снят-с-рефа 01/01 -> CSS
    формат: CSS
    слот: var(--lp-bg)
    статус: готов
    режим: "-"
  - id: page-sweep
    нужен: true
    роль_где: сквозная линия
    источник: снят-с-рефа 01/03
    формат: SVG
    слот: "{{decor:page-sweep}}"
    статус: заглушка
    режим: single
    промпт: Одна тонкая линия, прозрачный фон, без цвета.
to_generate:
  - id: page-sweep
    режим: single
    формат: SVG
YAML
    python3 "$REPO_ROOT/experimental/ds-engine-v2/engine/gen_assets_report.py" grooming --project "$project" >/dev/null
}

@test "fails when require_approved stages not approved" {
    # 07_content requires 07a_prototype (не approved в свежем state)
    run bash "$SCRIPT" --stage 07_content --project "$PROJECT_DIR" --auto
    [ "$status" -ne 0 ]
    [[ "$output" == *"07a_prototype"* ]]
}

@test "fails when hard_check file_exists fails" {
    bash "$REPO_ROOT/scripts/gate-state.sh" approve "$PROJECT_DIR" "00_brief"
    bash "$REPO_ROOT/scripts/gate-state.sh" approve "$PROJECT_DIR" "01_context"
    # 02_assets requires PEXELS/UNSPLASH/PIXABAY ENV — none set in tests
    run bash "$SCRIPT" --stage 02_assets --project "$PROJECT_DIR"
    [ "$status" -ne 0 ]
}

@test "passes when stage 00_brief has brief.md" {
    echo "test brief" > "$PROJECT_DIR/00_БРИФ/brief.md"
    run bash "$SCRIPT" --stage 00_brief --project "$PROJECT_DIR"
    [ "$status" -eq 0 ]
}

@test "approve flag sets status to approved" {
    echo "test brief" > "$PROJECT_DIR/00_БРИФ/brief.md"
    bash "$SCRIPT" --stage 00_brief --project "$PROJECT_DIR" --approve
    run bash "$REPO_ROOT/scripts/gate-state.sh" get "$PROJECT_DIR" "00_brief"
    [ "$output" = "approved" ]
}

@test "required:false hard_check does not block stage (07e visuals)" {
    # 07d_VISUALS/icons отсутствует → visuals_generated (dir_has_files) падает,
    # но он required:false → этап не блокируется (иконки опциональны/из Lucide).
    bash "$REPO_ROOT/scripts/gate-state.sh" approve "$PROJECT_DIR" "07c_composed"
    create_ds_asset_pack_plan "$PROJECT_DIR"
    run bash "$SCRIPT" --stage 07e_visuals --project "$PROJECT_DIR" --auto
    [ "$status" -eq 0 ]
    [[ "$output" == *"необязательная проверка"* ]]
}

@test "script hard_check preserves project paths with spaces" {
    project_with_spaces="$BATS_TEST_TMPDIR/project with spaces"
    mkdir -p "$project_with_spaces"
    cp "$REPO_ROOT/template/.landing-state.yaml" "$project_with_spaces/.landing-state.yaml"
    echo "ok" > "$project_with_spaces/file with spaces.txt"

    gates="$BATS_TEST_TMPDIR/stage-gates-space.yaml"
    cat > "$gates" <<'YAML'
stages:
  "space_script":
    name: "Space script"
    lock: hard
    require_approved: []
    hard_checks:
      - id: arg_path_exists
        type: script
        script: "tests/gate-check/fixtures/require-existing-path.py"
        args: ["{project}/file with spaces.txt"]
        required: true
YAML

    GATES_YAML="$gates" run bash "$SCRIPT" --stage space_script --project "$project_with_spaces" --auto
    [ "$status" -eq 0 ]
    [[ "$output" == *"arg_path_exists"* ]]
}
