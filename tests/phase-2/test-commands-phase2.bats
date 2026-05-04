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

@test "landing-moodboard command file exists" {
  assert_file_exists "$LANDING_SYSTEM_ROOT/.claude/commands/landing-moodboard.md"
}

@test "landing-moodboard has description frontmatter" {
  run grep -E "^description:" "$LANDING_SYSTEM_ROOT/.claude/commands/landing-moodboard.md"
  [ "$status" -eq 0 ]
}

@test "landing-moodboard mentions moodboard-composer" {
  run grep -c "moodboard-composer" "$LANDING_SYSTEM_ROOT/.claude/commands/landing-moodboard.md"
  [ "$status" -eq 0 ]
  [ "$output" -ge 1 ]
}

@test "landing-moodboard mentions moodboard.html" {
  run grep -c "moodboard.html" "$LANDING_SYSTEM_ROOT/.claude/commands/landing-moodboard.md"
  [ "$status" -eq 0 ]
  [ "$output" -ge 1 ]
}

@test "landing-brand command file exists" {
  assert_file_exists "$LANDING_SYSTEM_ROOT/.claude/commands/landing-brand.md"
}

@test "landing-brand has description frontmatter" {
  run grep -E "^description:" "$LANDING_SYSTEM_ROOT/.claude/commands/landing-brand.md"
  [ "$status" -eq 0 ]
}

@test "landing-brand mentions brand-architect" {
  run grep -c "brand-architect" "$LANDING_SYSTEM_ROOT/.claude/commands/landing-brand.md"
  [ "$status" -eq 0 ]
  [ "$output" -ge 1 ]
}

@test "landing-brand mentions brand-kit.html" {
  run grep -c "brand-kit.html" "$LANDING_SYSTEM_ROOT/.claude/commands/landing-brand.md"
  [ "$status" -eq 0 ]
  [ "$output" -ge 1 ]
}
