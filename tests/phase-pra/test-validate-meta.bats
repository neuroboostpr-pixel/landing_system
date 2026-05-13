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
display_name_ru: "❌ Плохой ID"
layout_summary_ru: "Тестовый блок с невалидным ID для проверки валидатора."
slots: []
source: manual
created: 2026-05-12
EOF
  run python3 "$VALIDATOR" "$BATS_TMPDIR/bad-id.yaml"
  [ "$status" -ne 0 ]
  [[ "$output" == *"kebab-case"* ]]
}

@test "rejects meta missing display_name_ru" {
  run python3 "$VALIDATOR" "$FIXTURES/meta-missing-display-name.yaml"
  [ "$status" -ne 0 ]
  [[ "$output" == *"display_name_ru"* ]]
}

@test "accepts meta with valid recommended_styles_ru" {
  cat > "$BATS_TMPDIR/meta-styles-valid.yaml" <<EOF
id: ru-hero-99-test
category: hero
ru_market: true
use_cases: [services]
description: "Test block with styles"
display_name_ru: "Test hero"
layout_summary_ru: "Тест блок с рекомендациями по стилям для проверки валидатора."
recommended_styles_ru: ["Minimalism & Swiss Style", "Glassmorphism"]
slots: []
source: manual
created: 2026-05-13
EOF
  run python3 "$VALIDATOR" "$BATS_TMPDIR/meta-styles-valid.yaml"
  [ "$status" -eq 0 ]
}

@test "rejects meta with recommended_styles_ru that is not a list" {
  cat > "$BATS_TMPDIR/meta-styles-bad.yaml" <<EOF
id: ru-hero-99-test2
category: hero
ru_market: true
use_cases: [services]
description: "Test block"
display_name_ru: "Test hero"
layout_summary_ru: "Тест блок с некорректными стилями для проверки валидатора."
recommended_styles_ru: "not-a-list"
slots: []
source: manual
created: 2026-05-13
EOF
  run python3 "$VALIDATOR" "$BATS_TMPDIR/meta-styles-bad.yaml"
  [ "$status" -ne 0 ]
  [[ "$output" == *"recommended_styles_ru"* ]]
}
