#!/usr/bin/env bats

setup() {
  ROOT="$(cd "$(dirname "$BATS_TEST_FILENAME")/../.." && pwd)"
  FIXTURES="$ROOT/tests/phase-pra/fixtures"
  VALIDATOR="$ROOT/skills/block-composition/scripts/validate-selections.py"
}

@test "accepts valid selections" {
  run python3 "$VALIDATOR" "$FIXTURES/selections-valid.yaml"
  [ "$status" -eq 0 ]
}

@test "rejects selections missing confirmed_at" {
  run python3 "$VALIDATOR" "$FIXTURES/selections-missing-confirm.yaml"
  [ "$status" -ne 0 ]
  [[ "$output" == *"confirmed_at"* ]]
}

@test "rejects selections with duplicate block_position" {
  cat > "$BATS_TMPDIR/dup.yaml" <<EOF
project_slug: example
selections:
  - block_position: 1
    chosen_variant: ru-hero-01-services-calc
  - block_position: 1
    chosen_variant: ru-hero-02-b2c-expert
confirmed_at: "2026-05-12T14:23:00Z"
EOF
  run python3 "$VALIDATOR" "$BATS_TMPDIR/dup.yaml"
  [ "$status" -ne 0 ]
  [[ "$output" == *"duplicate"* ]]
}
