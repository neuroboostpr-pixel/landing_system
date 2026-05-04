#!/usr/bin/env bats

load '../helpers/test_helpers'

@test "landing-references command file exists" {
  assert_file_exists "$LANDING_SYSTEM_ROOT/.claude/commands/landing-references.md"
}

@test "landing-references has description frontmatter" {
  run grep -E "^description:" "$LANDING_SYSTEM_ROOT/.claude/commands/landing-references.md"
  [ "$status" -eq 0 ]
}

@test "landing-references mentions references-curator" {
  run grep -c "references-curator" "$LANDING_SYSTEM_ROOT/.claude/commands/landing-references.md"
  [ "$status" -eq 0 ]
  [ "$output" -ge 1 ]
}

@test "landing-references mentions moodboard.html" {
  run grep -c "moodboard.html" "$LANDING_SYSTEM_ROOT/.claude/commands/landing-references.md"
  [ "$status" -eq 0 ]
  [ "$output" -ge 1 ]
}
