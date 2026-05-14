#!/usr/bin/env bats

setup() {
  ROOT="$(cd "$(dirname "$BATS_TEST_FILENAME")/../.." && pwd)"
}

@test "design-tokens-generation SKILL.md mentions 9 sections" {
  run grep -c "^[0-9]\. \*\*## " "$ROOT/skills/design-tokens-generation/SKILL.md"
  [ "$status" -eq 0 ]
  [ "$output" -ge 9 ]
}

@test "SKILL.md references THIRD_PARTY_NOTICES" {
  run grep -l "THIRD_PARTY_NOTICES" "$ROOT/skills/design-tokens-generation/SKILL.md"
  [ "$status" -eq 0 ]
}
