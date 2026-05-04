#!/usr/bin/env bats
# tests/phase-3/test-commands-phase3.bats

load '../helpers/test_helpers'

COMMANDS_DIR="$LANDING_SYSTEM_ROOT/.claude/commands"

@test "landing-design command file exists" {
  [ -f "$COMMANDS_DIR/landing-design.md" ]
}

@test "landing-design has description frontmatter" {
  grep -q "^description:" "$COMMANDS_DIR/landing-design.md"
}

@test "landing-design mentions design-system-generator" {
  grep -q "design-system-generator" "$COMMANDS_DIR/landing-design.md"
}

@test "landing-design mentions design-preview.html" {
  grep -q "design-preview.html" "$COMMANDS_DIR/landing-design.md"
}

@test "landing-design has Usage section" {
  grep -q "## Usage" "$COMMANDS_DIR/landing-design.md"
}

@test "landing-stack command file exists" {
  [ -f "$COMMANDS_DIR/landing-stack.md" ]
}

@test "landing-stack has description frontmatter" {
  grep -q "^description:" "$COMMANDS_DIR/landing-stack.md"
}

@test "landing-stack mentions stack-planner" {
  grep -q "stack-planner" "$COMMANDS_DIR/landing-stack.md"
}

@test "landing-stack mentions design-stack.yaml" {
  grep -q "design-stack.yaml" "$COMMANDS_DIR/landing-stack.md"
}

@test "landing-content command file exists" {
  [ -f "$COMMANDS_DIR/landing-content.md" ]
}

@test "landing-content has description frontmatter" {
  grep -q "^description:" "$COMMANDS_DIR/landing-content.md"
}

@test "landing-content mentions content-writer" {
  grep -q "content-writer" "$COMMANDS_DIR/landing-content.md"
}

@test "landing-content mentions final-copy.md" {
  grep -q "final-copy.md" "$COMMANDS_DIR/landing-content.md"
}
