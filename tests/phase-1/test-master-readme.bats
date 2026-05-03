#!/usr/bin/env bats

load '../helpers/test_helpers'

@test "master README.md exists" {
  assert_file_exists "$LANDING_SYSTEM_ROOT/README.md"
}

@test "master README.md mentions Quick Start" {
  assert_file_contains "$LANDING_SYSTEM_ROOT/README.md" "Quick Start"
}

@test "master README.md links to spec" {
  assert_file_contains "$LANDING_SYSTEM_ROOT/README.md" "2026-05-03-landing-system-design"
}

@test "master README.md mentions /landing-new" {
  assert_file_contains "$LANDING_SYSTEM_ROOT/README.md" "/landing-new"
}
