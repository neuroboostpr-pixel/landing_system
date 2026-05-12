#!/usr/bin/env bats

setup() {
  ROOT="$(cd "$(dirname "$BATS_TEST_FILENAME")/../.." && pwd)"
  SCRIPT="$ROOT/scripts/generate-wp-blocks.py"
  FIXTURES="$ROOT/tests/phase-stage-08/fixtures"
  WORK="$(python -c "import tempfile; print(tempfile.mkdtemp().replace(chr(92),'/'))")"
  mkdir -p "$WORK/project/07_КОНТЕНТ" "$WORK/project/08_КОД/wp-theme/template-parts"
  cp "$FIXTURES/content/minimal.md" "$WORK/project/07_КОНТЕНТ/final-copy.md"
  printf '<?php\n' > "$WORK/project/08_КОД/wp-theme/functions.php"
}

teardown() { rm -rf "$WORK"; }

@test "runs B1..B4 in order" {
  run python "$SCRIPT" --project "$WORK/project"
  [ "$status" -eq 0 ]
  [ -f "$WORK/project/08_КОД/acf-fields.json" ]
  [ -f "$WORK/project/08_КОД/gutenberg-blocks/hero/block.json" ]
  grep -q "AUTO-GENERATED START" "$WORK/project/08_КОД/wp-theme/functions.php"
  [ -f "$WORK/project/08_КОД/wp-theme/template-parts/block-hero.php" ]
}

@test "--dry-run does not write files" {
  run python "$SCRIPT" --project "$WORK/project" --dry-run
  [ "$status" -eq 0 ]
  [[ "$output" == *"dry-run"* ]] || [[ "$output" == *"would"* ]]
  [ ! -f "$WORK/project/08_КОД/acf-fields.json" ]
}

@test "fails fast on content parse error" {
  echo "no h2" > "$WORK/project/07_КОНТЕНТ/final-copy.md"
  run python "$SCRIPT" --project "$WORK/project"
  [ "$status" -ne 0 ]
  [[ "$output" == *"no H2"* ]]
  [ ! -f "$WORK/project/08_КОД/acf-fields.json" ]
}
