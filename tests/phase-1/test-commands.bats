#!/usr/bin/env bats

load '../helpers/test_helpers'

@test "landing-new command file exists" {
  assert_file_exists "$LANDING_SYSTEM_ROOT/.claude/commands/landing-new.md"
}

@test "landing-new has description frontmatter" {
  run grep -E "^description:" "$LANDING_SYSTEM_ROOT/.claude/commands/landing-new.md"
  [ "$status" -eq 0 ]
}

@test "landing-new references init.sh" {
  assert_file_contains "$LANDING_SYSTEM_ROOT/.claude/commands/landing-new.md" "init.sh"
}

@test "landing-new mentions argument-hint" {
  run grep -E "^argument-hint:" "$LANDING_SYSTEM_ROOT/.claude/commands/landing-new.md"
  [ "$status" -eq 0 ]
}

@test "landing-from-context command exists" {
  assert_file_exists "$LANDING_SYSTEM_ROOT/.claude/commands/landing-from-context.md"
}

@test "landing-from-context references from-context.sh" {
  assert_file_contains "$LANDING_SYSTEM_ROOT/.claude/commands/landing-from-context.md" "from-context.sh"
}

@test "landing-help command exists" {
  assert_file_exists "$LANDING_SYSTEM_ROOT/.claude/commands/landing-help.md"
}

@test "landing-help lists landing-new" {
  assert_file_contains "$LANDING_SYSTEM_ROOT/.claude/commands/landing-help.md" "/landing-new"
}

@test "landing-help lists landing-status" {
  assert_file_contains "$LANDING_SYSTEM_ROOT/.claude/commands/landing-help.md" "/landing-status"
}

@test "landing-status command exists" {
  assert_file_exists "$LANDING_SYSTEM_ROOT/.claude/commands/landing-status.md"
}

@test "landing-status mentions Phase 1" {
  assert_file_contains "$LANDING_SYSTEM_ROOT/.claude/commands/landing-status.md" "Phase 1"
}

@test "landing-status STAGE detection uses .gitkeep filter for all stage folders" {
  # Verify the helper function is present for stage folder checks
  run grep -E "dir_has_real_content" "$LANDING_SYSTEM_ROOT/.claude/commands/landing-status.md"
  [ "$status" -eq 0 ]
  # Verify 01_КОНТЕКСТ is checked via the helper (not raw ls -A)
  run grep -E "dir_has_real_content.*01_КОНТЕКСТ" "$LANDING_SYSTEM_ROOT/.claude/commands/landing-status.md"
  [ "$status" -eq 0 ]
  # Negative: bare ls -A on 01_КОНТЕКСТ without gitkeep filter must not exist
  run grep -E 'ls -A "\$CWD/01_КОНТЕКСТ"' "$LANDING_SYSTEM_ROOT/.claude/commands/landing-status.md"
  [ "$status" -ne 0 ]
}
