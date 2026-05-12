#!/usr/bin/env bats

setup() {
  ROOT="$(cd "$(dirname "$BATS_TEST_FILENAME")/../.." && pwd)"
  FIXTURES="$ROOT/tests/phase-pra/fixtures"
  VALIDATOR="$ROOT/skills/block-library-management/scripts/validate-catalog.py"
}

@test "accepts valid catalog" {
  run python3 "$VALIDATOR" "$FIXTURES/catalog-valid.yaml"
  [ "$status" -eq 0 ]
}

@test "rejects catalog with duplicate ids" {
  run python3 "$VALIDATOR" "$FIXTURES/catalog-duplicate-id.yaml"
  [ "$status" -ne 0 ]
  [[ "$output" == *"duplicate id"* ]]
}

@test "rejects catalog missing version" {
  run python3 "$VALIDATOR" "$FIXTURES/catalog-missing-version.yaml"
  [ "$status" -ne 0 ]
  [[ "$output" == *"version"* ]]
}

@test "accepts empty blocks list" {
  cat > "$BATS_TMPDIR/empty.yaml" <<EOF
version: 1
updated: 2026-05-12
blocks: []
EOF
  run python3 "$VALIDATOR" "$BATS_TMPDIR/empty.yaml"
  [ "$status" -eq 0 ]
}
