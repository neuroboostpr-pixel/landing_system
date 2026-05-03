#!/usr/bin/env bats

load '../helpers/test_helpers'

@test "template/CLAUDE.md exists" {
  assert_file_exists "$LANDING_SYSTEM_ROOT/template/CLAUDE.md"
}

@test "template/CLAUDE.md mentions 12 этапов" {
  assert_file_contains "$LANDING_SYSTEM_ROOT/template/CLAUDE.md" "12 этап"
}

@test "template/CLAUDE.md mentions landing-orchestrator" {
  assert_file_contains "$LANDING_SYSTEM_ROOT/template/CLAUDE.md" "landing-orchestrator"
}

@test "template/CLAUDE.md mentions HARD GATE" {
  assert_file_contains "$LANDING_SYSTEM_ROOT/template/CLAUDE.md" "HARD GATE"
}

@test "template/CLAUDE.md mentions WordPress" {
  assert_file_contains "$LANDING_SYSTEM_ROOT/template/CLAUDE.md" "WordPress"
}
