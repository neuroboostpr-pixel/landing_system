#!/usr/bin/env bats

load '../helpers/test_helpers'

setup() {
  setup_temp_dir
  export TARGET_DIR="$TEST_TEMP/test-project"
}

teardown() {
  teardown_temp_dir
}

@test "init.sh exists and executable" {
  [ -x "$LANDING_SYSTEM_ROOT/.skills/landing-project-init/scripts/init.sh" ]
}

@test "init.sh fails without arguments" {
  run "$LANDING_SYSTEM_ROOT/.skills/landing-project-init/scripts/init.sh"
  [ "$status" -ne 0 ]
}

@test "init.sh creates project from template" {
  run "$LANDING_SYSTEM_ROOT/.skills/landing-project-init/scripts/init.sh" "$TARGET_DIR"
  [ "$status" -eq 0 ]
  assert_dir_exists "$TARGET_DIR"
  assert_dir_exists "$TARGET_DIR/00_БРИФ"
  assert_dir_exists "$TARGET_DIR/12_SEO"
  assert_file_exists "$TARGET_DIR/CLAUDE.md"
  assert_file_exists "$TARGET_DIR/README.md"
  assert_file_exists "$TARGET_DIR/.env.example"
  assert_file_exists "$TARGET_DIR/.gitignore"
}

@test "init.sh initializes git in new project" {
  run "$LANDING_SYSTEM_ROOT/.skills/landing-project-init/scripts/init.sh" "$TARGET_DIR"
  [ "$status" -eq 0 ]
  assert_dir_exists "$TARGET_DIR/.git"
}

@test "init.sh refuses to overwrite existing project" {
  mkdir -p "$TARGET_DIR"
  touch "$TARGET_DIR/some-file"
  run "$LANDING_SYSTEM_ROOT/.skills/landing-project-init/scripts/init.sh" "$TARGET_DIR"
  [ "$status" -ne 0 ]
  [[ "$output" =~ "exists" ]] || [[ "$output" =~ "уже" ]]
}

@test "init.sh substitutes PROJECT_NAME placeholder in README" {
  run "$LANDING_SYSTEM_ROOT/.skills/landing-project-init/scripts/init.sh" "$TARGET_DIR"
  [ "$status" -eq 0 ]
  run grep "{{PROJECT_NAME}}" "$TARGET_DIR/README.md"
  [ "$status" -ne 0 ]  # placeholder gone
}

@test "init.sh does not propagate .DS_Store to new project" {
  run "$LANDING_SYSTEM_ROOT/.skills/landing-project-init/scripts/init.sh" "$TARGET_DIR"
  [ "$status" -eq 0 ]
  run find "$TARGET_DIR" -name '.DS_Store'
  [ -z "$output" ]
}
