#!/usr/bin/env bats
# tests/phase-4/test-commands-phase4.bats

REPO_ROOT="$(cd "$(dirname "$BATS_TEST_FILENAME")/../.." && pwd)"
COMMANDS_DIR="$REPO_ROOT/.claude/commands"
SKILLS_DIR="$REPO_ROOT/skills"

@test "landing-build.md command exists" {
  [ -f "$COMMANDS_DIR/landing-build.md" ]
}

@test "landing-build.md has description frontmatter" {
  grep -q "^description:" "$COMMANDS_DIR/landing-build.md"
}

@test "landing-build.md mentions generate-theme.py" {
  grep -q "generate-theme.py" "$COMMANDS_DIR/landing-build.md"
}

@test "landing-build.md mentions bundle-assets.py" {
  grep -q "bundle-assets.py" "$COMMANDS_DIR/landing-build.md"
}

@test "landing-build.md mentions render-build-preview.py" {
  grep -q "render-build-preview.py" "$COMMANDS_DIR/landing-build.md"
}

@test "landing-build.md mentions HARD GATE" {
  grep -qi "hard gate" "$COMMANDS_DIR/landing-build.md"
}

@test "wp-gutenberg-block-builder SKILL.md exists" {
  [ -f "$SKILLS_DIR/wp-gutenberg-block-builder/SKILL.md" ]
}

@test "wp-theme-assembler SKILL.md exists" {
  [ -f "$SKILLS_DIR/wp-theme-assembler/SKILL.md" ]
}

@test "generate-theme.py exists" {
  [ -f "$SKILLS_DIR/wp-gutenberg-block-builder/scripts/generate-theme.py" ]
}

@test "bundle-assets.py exists" {
  [ -f "$SKILLS_DIR/wp-theme-assembler/scripts/bundle-assets.py" ]
}

@test "render-build-preview.py exists" {
  [ -f "$SKILLS_DIR/wp-theme-assembler/scripts/render-build-preview.py" ]
}

@test "build-preview.html.j2 template exists" {
  [ -f "$REPO_ROOT/tools/html/templates/build-preview.html.j2" ]
}
