#!/usr/bin/env bats

setup() {
  ROOT="$(cd "$(dirname "$BATS_TEST_FILENAME")/../.." && pwd)"
  SCRIPT="$ROOT/scripts/generate-axes-filter.py"
  FIXTURES="$ROOT/tests/phase-preview-panel/fixtures"
  WORK="$(mktemp -d)"
  mkdir -p "$WORK/project/04_БРЕНД" "$WORK/project/08_КОД/wp-theme/inc"
  cp "$FIXTURES/library-with-paper-minimal.yaml" "$WORK/project/04_БРЕНД/palettes.yaml"
}

teardown() {
  rm -rf "$WORK"
}

@test "emits a PHP file with the filter callback" {
  run python "$SCRIPT" --project "$WORK/project" --default-palette paper-minimal --hero static,parallax --default-hero static
  [ "$status" -eq 0 ]
  PHP="$WORK/project/08_КОД/wp-theme/inc/lp-preview-panel-axes.php"
  [ -f "$PHP" ]
  grep -q "add_filter( 'lp_preview_panel_axes'" "$PHP"
  grep -q "'paper-minimal' => 'Paper Minimal'" "$PHP"
  grep -q "'static'   => 'Static'" "$PHP"
  grep -q "'parallax' => 'Parallax'" "$PHP"
}

@test "matches expected fixture exactly" {
  python "$SCRIPT" --project "$WORK/project" --default-palette paper-minimal --hero static,parallax --default-hero static
  diff -u "$FIXTURES/expected-axes.php" "$WORK/project/08_КОД/wp-theme/inc/lp-preview-panel-axes.php"
}

@test "rejects --default-palette not in snapshot" {
  run python "$SCRIPT" --project "$WORK/project" --default-palette no-such --hero static --default-hero static
  [ "$status" -ne 0 ]
  [[ "$output" == *"no-such"* ]]
}

@test "rejects --default-hero not in --hero list" {
  run python "$SCRIPT" --project "$WORK/project" --default-palette paper-minimal --hero static,parallax --default-hero video
  [ "$status" -ne 0 ]
  [[ "$output" == *"video"* ]]
}
