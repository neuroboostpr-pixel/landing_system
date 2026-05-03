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
