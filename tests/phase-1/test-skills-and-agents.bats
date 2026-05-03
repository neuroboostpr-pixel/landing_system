#!/usr/bin/env bats

load '../helpers/test_helpers'

@test "landing-project-init SKILL.md exists" {
  assert_file_exists "$LANDING_SYSTEM_ROOT/.skills/landing-project-init/SKILL.md"
}

@test "landing-project-init has frontmatter with name" {
  run grep -E "^name: landing-project-init$" "$LANDING_SYSTEM_ROOT/.skills/landing-project-init/SKILL.md"
  [ "$status" -eq 0 ]
}

@test "landing-project-init has frontmatter with description" {
  run grep -E "^description:" "$LANDING_SYSTEM_ROOT/.skills/landing-project-init/SKILL.md"
  [ "$status" -eq 0 ]
}

@test "landing-project-init mentions init.sh" {
  assert_file_contains "$LANDING_SYSTEM_ROOT/.skills/landing-project-init/SKILL.md" "init.sh"
}

@test "landing-from-context SKILL.md exists" {
  assert_file_exists "$LANDING_SYSTEM_ROOT/.skills/landing-from-context/SKILL.md"
}

@test "landing-from-context frontmatter ok" {
  run grep -E "^name: landing-from-context$" "$LANDING_SYSTEM_ROOT/.skills/landing-from-context/SKILL.md"
  [ "$status" -eq 0 ]
}
