#!/usr/bin/env bats

setup() {
  ROOT="$(cd "$(dirname "$BATS_TEST_FILENAME")/../.." && pwd)"
  SCRIPT="$ROOT/scripts/generate-palette-css.py"
  FIXTURES="$ROOT/tests/phase-preview-panel/fixtures"
  WORK="$(mktemp -d)"
  mkdir -p "$WORK/project/04_БРЕНД" "$WORK/project/08_КОД/wp-theme/assets/css"
  cp "$FIXTURES/library-with-paper-minimal.yaml" "$WORK/project/04_БРЕНД/palettes.yaml"
}

teardown() {
  rm -rf "$WORK"
}

@test "generates a body.theme-<id> block per palette" {
  run python "$SCRIPT" --project "$WORK/project"
  [ "$status" -eq 0 ]
  CSS="$WORK/project/08_КОД/wp-theme/assets/css/palettes.css"
  [ -f "$CSS" ]
  grep -q "body.theme-paper-minimal" "$CSS"
}

@test "translates YAML keys to CSS custom properties" {
  python "$SCRIPT" --project "$WORK/project"
  CSS="$WORK/project/08_КОД/wp-theme/assets/css/palettes.css"
  grep -q -- "--bg-base: #F8F7F4" "$CSS"
  grep -q -- "--accent-rgb-coral: 4, 120, 87" "$CSS"
  grep -q -- "--accent-cta-glow-opacity: 0.15" "$CSS"
}

@test "matches expected fixture exactly for paper-minimal" {
  python "$SCRIPT" --project "$WORK/project"
  diff -u "$FIXTURES/expected-palettes.css" "$WORK/project/08_КОД/wp-theme/assets/css/palettes.css"
}
