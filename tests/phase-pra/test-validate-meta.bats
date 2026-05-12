#!/usr/bin/env bats

setup() {
  ROOT="$(cd "$(dirname "$BATS_TEST_FILENAME")/../.." && pwd)"
  FIXTURES="$ROOT/tests/phase-pra/fixtures"
  VALIDATOR="$ROOT/skills/block-library-management/scripts/validate-meta.py"
}

@test "accepts valid meta" {
  run python3 "$VALIDATOR" "$FIXTURES/meta-valid.yaml"
  [ "$status" -eq 0 ]
}

@test "rejects meta missing slots key" {
  run python3 "$VALIDATOR" "$FIXTURES/meta-missing-slots.yaml"
  [ "$status" -ne 0 ]
  [[ "$output" == *"slots"* ]]
}

@test "rejects meta with invalid category" {
  run python3 "$VALIDATOR" "$FIXTURES/meta-invalid-category.yaml"
  [ "$status" -ne 0 ]
  [[ "$output" == *"category"* ]]
}

@test "rejects meta with non-kebab-case id" {
  cat > "$BATS_TMPDIR/bad-id.yaml" <<EOF
id: Ru_Hero_01_BadCase
category: hero
ru_market: true
use_cases: [services]
description: "bad id"
slots: []
source: manual
created: 2026-05-12
EOF
  run python3 "$VALIDATOR" "$BATS_TMPDIR/bad-id.yaml"
  [ "$status" -ne 0 ]
  [[ "$output" == *"kebab-case"* ]]
}
