#!/usr/bin/env bats

setup() {
  ROOT="$(cd "$(dirname "$BATS_TEST_FILENAME")/../.." && pwd)"
}

@test "prototype-importer agent file exists" {
  [ -f "$ROOT/agents/prototype-importer.md" ]
}

@test "prototype-importer has required frontmatter" {
  run head -5 "$ROOT/agents/prototype-importer.md"
  [[ "$output" == *"name: prototype-importer"* ]]
  [[ "$output" == *"description:"* ]]
}

@test "landing-prototype command file exists" {
  [ -f "$ROOT/commands/landing-prototype.md" ]
}

@test "landing-prototype command has description frontmatter" {
  run head -3 "$ROOT/commands/landing-prototype.md"
  [[ "$output" == *"description:"* ]]
}

@test "ux-composer agent file exists" {
  [ -f "$ROOT/agents/ux-composer.md" ]
}

@test "landing-wireframe command file exists" {
  [ -f "$ROOT/commands/landing-wireframe.md" ]
}

@test "block-composer agent file exists" {
  [ -f "$ROOT/agents/block-composer.md" ]
}

@test "landing-compose command file exists" {
  [ -f "$ROOT/commands/landing-compose.md" ]
}
