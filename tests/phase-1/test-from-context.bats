#!/usr/bin/env bats

load '../helpers/test_helpers'

setup() {
  setup_temp_dir
  # Simulate parent agency project structure
  export PARENT_DIR="$TEST_TEMP/parent-agency-project"
  mkdir -p "$PARENT_DIR/01_контекст"
  mkdir -p "$PARENT_DIR/05_исследования"
  mkdir -p "$PARENT_DIR/04_документы"
  echo "Niche info" > "$PARENT_DIR/01_контекст/niche.md"
  echo "Audience research" > "$PARENT_DIR/05_исследования/audience.md"
  echo "Prototype text" > "$PARENT_DIR/04_документы/прототип-марафон.md"

  export TARGET_DIR="$TEST_TEMP/lp-test-from-context"
}

teardown() {
  teardown_temp_dir
}

@test "from-context.sh exists and executable" {
  [ -x "$LANDING_SYSTEM_ROOT/skills/landing-from-context/scripts/from-context.sh" ]
}

@test "from-context.sh creates project and copies parent context" {
  cd "$PARENT_DIR"
  run "$LANDING_SYSTEM_ROOT/skills/landing-from-context/scripts/from-context.sh" "$TARGET_DIR"
  [ "$status" -eq 0 ]

  # Project structure exists
  assert_dir_exists "$TARGET_DIR/00_БРИФ"

  # Context copied
  assert_file_exists "$TARGET_DIR/01_КОНТЕКСТ/niche.md"
  run grep "Niche info" "$TARGET_DIR/01_КОНТЕКСТ/niche.md"
  [ "$status" -eq 0 ]
}

@test "from-context.sh copies research subfolder" {
  cd "$PARENT_DIR"
  run "$LANDING_SYSTEM_ROOT/skills/landing-from-context/scripts/from-context.sh" "$TARGET_DIR"
  [ "$status" -eq 0 ]
  assert_file_exists "$TARGET_DIR/01_КОНТЕКСТ/исследования/audience.md"
}

@test "from-context.sh copies prototype to 07_КОНТЕНТ" {
  cd "$PARENT_DIR"
  run "$LANDING_SYSTEM_ROOT/skills/landing-from-context/scripts/from-context.sh" "$TARGET_DIR"
  [ "$status" -eq 0 ]
  assert_file_exists "$TARGET_DIR/07_КОНТЕНТ/prototype.md"
}

@test "from-context.sh writes source-references.yaml" {
  cd "$PARENT_DIR"
  run "$LANDING_SYSTEM_ROOT/skills/landing-from-context/scripts/from-context.sh" "$TARGET_DIR"
  [ "$status" -eq 0 ]
  assert_file_exists "$TARGET_DIR/01_КОНТЕКСТ/source-references.yaml"
  run grep "parent_path" "$TARGET_DIR/01_КОНТЕКСТ/source-references.yaml"
  [ "$status" -eq 0 ]
}

@test "from-context.sh produces valid YAML for paths with quotes" {
  PARENT_WITH_QUOTE="$TEST_TEMP/has\"quote"
  mkdir -p "$PARENT_WITH_QUOTE/01_контекст"
  echo "data" > "$PARENT_WITH_QUOTE/01_контекст/file.md"
  cd "$PARENT_WITH_QUOTE"
  run "$LANDING_SYSTEM_ROOT/skills/landing-from-context/scripts/from-context.sh" "$TARGET_DIR"
  [ "$status" -eq 0 ]
  # If python3 is available, parse and ensure valid YAML
  if command -v python3 >/dev/null; then
    run python3 -c "import yaml; yaml.safe_load(open('$TARGET_DIR/01_КОНТЕКСТ/source-references.yaml'))"
    [ "$status" -eq 0 ]
  fi
}

@test "from-context.sh produces honest manifest when nothing to copy" {
  EMPTY_PARENT="$TEST_TEMP/empty-parent"
  mkdir -p "$EMPTY_PARENT"
  cd "$EMPTY_PARENT"
  run "$LANDING_SYSTEM_ROOT/skills/landing-from-context/scripts/from-context.sh" "$TARGET_DIR"
  [ "$status" -eq 0 ]
  # Manifest should NOT claim 01_контекст was copied
  run grep "source: 01_контекст" "$TARGET_DIR/01_КОНТЕКСТ/source-references.yaml"
  [ "$status" -ne 0 ]
}

@test "from-context.sh warns about multiple prototype matches" {
  MULTI_PARENT="$TEST_TEMP/multi-proto-parent"
  mkdir -p "$MULTI_PARENT/04_документы"
  echo "v1" > "$MULTI_PARENT/04_документы/прототип-a.md"
  echo "v2" > "$MULTI_PARENT/04_документы/прототип-b.md"
  cd "$MULTI_PARENT"
  run "$LANDING_SYSTEM_ROOT/skills/landing-from-context/scripts/from-context.sh" "$TARGET_DIR"
  [ "$status" -eq 0 ]
  [[ "$output" =~ "Multiple" ]] || [[ "$output" =~ "multiple" ]] || [[ "$output" =~ "Несколько" ]]
}
