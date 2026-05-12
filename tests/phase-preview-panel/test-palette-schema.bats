#!/usr/bin/env bats

setup() {
  ROOT="$(cd "$(dirname "$BATS_TEST_FILENAME")/../.." && pwd)"
  FIXTURES="$ROOT/tests/phase-preview-panel/fixtures"
  VALIDATOR="$ROOT/scripts/validate-palettes.py"
}

@test "validator accepts empty library" {
  run python "$VALIDATOR" "$FIXTURES/library-empty.yaml"
  [ "$status" -eq 0 ]
}

@test "validator accepts library with one valid palette" {
  run python "$VALIDATOR" "$FIXTURES/library-with-paper-minimal.yaml"
  [ "$status" -eq 0 ]
}

@test "validator rejects palette missing a required token" {
  run python "$VALIDATOR" "$FIXTURES/library-missing-token.yaml"
  [ "$status" -ne 0 ]
  [[ "$output" == *"missing required token"* ]]
}

@test "validator rejects duplicate ids" {
  run python "$VALIDATOR" "$FIXTURES/library-duplicate-id.yaml"
  [ "$status" -ne 0 ]
  [[ "$output" == *"duplicate id"* ]]
}

@test "validator rejects non-kebab-case id" {
  run python "$VALIDATOR" "$FIXTURES/library-bad-id.yaml"
  [ "$status" -ne 0 ]
  [[ "$output" == *"id must be kebab-case"* ]]
}

@test "global library file exists and is empty-but-valid" {
  run python "$VALIDATOR" "$ROOT/presets/palettes.yaml"
  [ "$status" -eq 0 ]
}
