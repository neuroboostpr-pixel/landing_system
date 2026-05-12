#!/usr/bin/env bats

setup() {
  ROOT="$(cd "$(dirname "$BATS_TEST_FILENAME")/../.." && pwd)"
  SCRIPT="$ROOT/scripts/migrate-to-preview-panel.sh"
  FIXTURES="$ROOT/tests/phase-preview-panel/fixtures"
  WORK="$(mktemp -d)"
  cp -r "$FIXTURES/synth-project" "$WORK/project"
  # Use a temp library so test doesn't pollute the real one
  cp "$FIXTURES/library-empty.yaml" "$WORK/library.yaml"
}

teardown() {
  rm -rf "$WORK"
}

@test "removes nu-theme-bar from header.php" {
  run bash "$SCRIPT" "$WORK/project" "$WORK/library.yaml"
  [ "$status" -eq 0 ]
  ! grep -q "nu-theme-bar" "$WORK/project/08_КОД/wp-theme/header.php"
  # But other content is preserved
  grep -q "nu-header" "$WORK/project/08_КОД/wp-theme/header.php"
}

@test "removes initThemeSwitcher from main.js" {
  bash "$SCRIPT" "$WORK/project" "$WORK/library.yaml"
  ! grep -q "initThemeSwitcher" "$WORK/project/08_КОД/wp-theme/assets/js/main.js"
  grep -q "unrelated" "$WORK/project/08_КОД/wp-theme/assets/js/main.js"
}

@test "creates 04_БРЕНД/palettes.yaml with four palettes" {
  bash "$SCRIPT" "$WORK/project" "$WORK/library.yaml"
  PYAML="$WORK/project/04_БРЕНД/palettes.yaml"
  [ -f "$PYAML" ]
  grep -q "id: nu-paper" "$PYAML"
  grep -q "id: nu-quiet-dark" "$PYAML"
  grep -q "id: nu-beige" "$PYAML"
  grep -q "id: nu-iqido" "$PYAML"
}

@test "exports the four palettes to the library" {
  bash "$SCRIPT" "$WORK/project" "$WORK/library.yaml"
  grep -q "id: nu-paper" "$WORK/library.yaml"
  grep -q "id: nu-iqido" "$WORK/library.yaml"
}

@test "copies plugin from template" {
  bash "$SCRIPT" "$WORK/project" "$WORK/library.yaml"
  [ -d "$WORK/project/08_КОД/plugins/lp-preview-panel" ]
  [ -f "$WORK/project/08_КОД/plugins/lp-preview-panel/lp-preview-panel.php" ]
}

@test "generates inc/lp-preview-panel-axes.php" {
  bash "$SCRIPT" "$WORK/project" "$WORK/library.yaml"
  PHP="$WORK/project/08_КОД/wp-theme/inc/lp-preview-panel-axes.php"
  [ -f "$PHP" ]
  grep -q "'nu-iqido'" "$PHP"
  grep -q "'parallax'" "$PHP"
}

@test "adds require_once to functions.php exactly once" {
  bash "$SCRIPT" "$WORK/project" "$WORK/library.yaml"
  # Re-run; idempotent
  bash "$SCRIPT" "$WORK/project" "$WORK/library.yaml"
  COUNT=$(grep -c "lp-preview-panel-axes.php" "$WORK/project/08_КОД/wp-theme/functions.php")
  [ "$COUNT" = "1" ]
}

@test "generates palettes.css with body.theme-nu-iqido block" {
  bash "$SCRIPT" "$WORK/project" "$WORK/library.yaml"
  CSS="$WORK/project/08_КОД/wp-theme/assets/css/palettes.css"
  [ -f "$CSS" ]
  grep -q "body.theme-nu-iqido" "$CSS"
}
