#!/usr/bin/env bats

load '../helpers/test_helpers'

@test "master CLAUDE.md exists" {
  assert_file_exists "$LANDING_SYSTEM_ROOT/CLAUDE.md"
}

@test "master CLAUDE.md mentions landing-system" {
  assert_file_contains "$LANDING_SYSTEM_ROOT/CLAUDE.md" "landing-system"
}

@test "master CLAUDE.md mentions /landing-new command" {
  assert_file_contains "$LANDING_SYSTEM_ROOT/CLAUDE.md" "/landing-new"
}

@test "master CLAUDE.md mentions superpowers" {
  assert_file_contains "$LANDING_SYSTEM_ROOT/CLAUDE.md" "superpowers"
}

@test "master CLAUDE.md mentions WordPress" {
  assert_file_contains "$LANDING_SYSTEM_ROOT/CLAUDE.md" "WordPress"
}
