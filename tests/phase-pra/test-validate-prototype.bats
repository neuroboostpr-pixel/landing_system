#!/usr/bin/env bats

setup() {
  ROOT="$(cd "$(dirname "$BATS_TEST_FILENAME")/../.." && pwd)"
  FIXTURES="$ROOT/tests/phase-pra/fixtures"
  VALIDATOR="$ROOT/skills/prototype-import/scripts/validate-prototype.py"
}

@test "accepts valid prototype" {
  run python3 "$VALIDATOR" "$FIXTURES/prototype-valid.yaml"
  [ "$status" -eq 0 ]
}

@test "rejects prototype without blocks key" {
  run python3 "$VALIDATOR" "$FIXTURES/prototype-missing-blocks.yaml"
  [ "$status" -ne 0 ]
  [[ "$output" == *"blocks"* ]]
}

@test "rejects prototype with invalid niche" {
  cat > "$BATS_TMPDIR/bad-niche.yaml" <<EOF
project:
  slug: x
  niche: blogging
  source_file: x.pdf
blocks: []
EOF
  run python3 "$VALIDATOR" "$BATS_TMPDIR/bad-niche.yaml"
  [ "$status" -ne 0 ]
  [[ "$output" == *"niche"* ]]
}

@test "rejects prototype block missing position" {
  cat > "$BATS_TMPDIR/no-pos.yaml" <<EOF
project:
  slug: x
  niche: services
  source_file: x.pdf
blocks:
  - type: hero
    headline: "X"
EOF
  run python3 "$VALIDATOR" "$BATS_TMPDIR/no-pos.yaml"
  [ "$status" -ne 0 ]
  [[ "$output" == *"position"* ]]
}

@test "accepts quiz block with valid quiz_role" {
  cat > "$BATS_TMPDIR/quiz-role-valid.yaml" <<EOF
project:
  slug: x
  niche: services
  source_file: x.pdf
blocks:
  - position: 1
    type: quiz
    quiz_role: welcome
    headline: "Начать"
  - position: 2
    type: quiz
    quiz_role: lead-form
    headline: "Форма"
EOF
  run python3 "$VALIDATOR" "$BATS_TMPDIR/quiz-role-valid.yaml"
  [ "$status" -eq 0 ]
}

@test "rejects quiz block with invalid quiz_role value" {
  cat > "$BATS_TMPDIR/quiz-role-bad.yaml" <<EOF
project:
  slug: x
  niche: services
  source_file: x.pdf
blocks:
  - position: 1
    type: quiz
    quiz_role: invalid-role
    headline: "Test"
EOF
  run python3 "$VALIDATOR" "$BATS_TMPDIR/quiz-role-bad.yaml"
  [ "$status" -ne 0 ]
  [[ "$output" == *"quiz_role"* ]]
}

@test "rejects non-quiz block with quiz_role" {
  cat > "$BATS_TMPDIR/non-quiz-role.yaml" <<EOF
project:
  slug: x
  niche: services
  source_file: x.pdf
blocks:
  - position: 1
    type: hero
    quiz_role: welcome
    headline: "Hero"
EOF
  run python3 "$VALIDATOR" "$BATS_TMPDIR/non-quiz-role.yaml"
  [ "$status" -ne 0 ]
  [[ "$output" == *"quiz_role"* ]]
}

@test "accepts prototype without quiz_role (backward compatible)" {
  run python3 "$VALIDATOR" "$FIXTURES/prototype-valid.yaml"
  [ "$status" -eq 0 ]
}
