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
  [ -x "$LANDING_SYSTEM_ROOT/.skills/landing-from-context/scripts/from-context.sh" ]
}

@test "from-context.sh creates project and copies parent context" {
  cd "$PARENT_DIR"
  run "$LANDING_SYSTEM_ROOT/.skills/landing-from-context/scripts/from-context.sh" "$TARGET_DIR"
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
  run "$LANDING_SYSTEM_ROOT/.skills/landing-from-context/scripts/from-context.sh" "$TARGET_DIR"
  [ "$status" -eq 0 ]
  assert_file_exists "$TARGET_DIR/01_КОНТЕКСТ/исследования/audience.md"
}

@test "from-context.sh copies prototype to 07_КОНТЕНТ" {
  cd "$PARENT_DIR"
  run "$LANDING_SYSTEM_ROOT/.skills/landing-from-context/scripts/from-context.sh" "$TARGET_DIR"
  [ "$status" -eq 0 ]
  assert_file_exists "$TARGET_DIR/07_КОНТЕНТ/prototype.md"
}

@test "from-context.sh writes source-references.yaml" {
  cd "$PARENT_DIR"
  run "$LANDING_SYSTEM_ROOT/.skills/landing-from-context/scripts/from-context.sh" "$TARGET_DIR"
  [ "$status" -eq 0 ]
  assert_file_exists "$TARGET_DIR/01_КОНТЕКСТ/source-references.yaml"
  run grep "parent_path" "$TARGET_DIR/01_КОНТЕКСТ/source-references.yaml"
  [ "$status" -eq 0 ]
}
