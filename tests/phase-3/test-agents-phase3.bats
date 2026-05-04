#!/usr/bin/env bats
# tests/phase-3/test-agents-phase3.bats

load '../helpers/test_helpers'

AGENTS_DIR="$LANDING_SYSTEM_ROOT/agents"

@test "design-system-generator agent file exists" {
  [ -f "$AGENTS_DIR/design-system-generator.md" ]
}

@test "design-system-generator has valid frontmatter" {
  grep -q "^name: design-system-generator" "$AGENTS_DIR/design-system-generator.md"
}

@test "design-system-generator mentions design-preview.html" {
  grep -q "design-preview.html" "$AGENTS_DIR/design-system-generator.md"
}

@test "design-system-generator mentions DESIGN.md" {
  grep -q "DESIGN.md" "$AGENTS_DIR/design-system-generator.md"
}

@test "scene-director agent file exists" {
  [ -f "$AGENTS_DIR/scene-director.md" ]
}

@test "scene-director has valid frontmatter" {
  grep -q "^name: scene-director" "$AGENTS_DIR/scene-director.md"
}

@test "scene-director mentions cinematic" {
  grep -qi "cinematic" "$AGENTS_DIR/scene-director.md"
}

@test "stack-planner agent file exists" {
  [ -f "$AGENTS_DIR/stack-planner.md" ]
}

@test "stack-planner has valid frontmatter" {
  grep -q "^name: stack-planner" "$AGENTS_DIR/stack-planner.md"
}

@test "stack-planner mentions design-stack.yaml" {
  grep -q "design-stack.yaml" "$AGENTS_DIR/stack-planner.md"
}

@test "content-writer agent file exists" {
  [ -f "$AGENTS_DIR/content-writer.md" ]
}

@test "content-writer has valid frontmatter" {
  grep -q "^name: content-writer" "$AGENTS_DIR/content-writer.md"
}

@test "content-writer mentions final-copy.md" {
  grep -q "final-copy.md" "$AGENTS_DIR/content-writer.md"
}
