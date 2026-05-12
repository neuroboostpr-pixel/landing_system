#!/usr/bin/env bats

setup() {
  ROOT="$(cd "$(dirname "$BATS_TEST_FILENAME")/../.." && pwd)"
  SCRIPT="$ROOT/skills/wp-gutenberg-block-builder/scripts/generate-theme.py"
  FIXTURES="$ROOT/tests/phase-stage-08/fixtures"
  WORK="$(python -c "import tempfile; print(tempfile.mkdtemp().replace(chr(92),'/'))")"
  mkdir -p "$WORK/project/07_КОНТЕНТ" "$WORK/project/08_КОД/wp-theme/template-parts"
  cp "$FIXTURES/content/minimal.md" "$WORK/project/07_КОНТЕНТ/final-copy.md"
}

teardown() { rm -rf "$WORK"; }

@test "--blocks-only creates missing block-<slug>.php" {
  run python "$SCRIPT" --project "$WORK/project" --blocks-only
  [ "$status" -eq 0 ]
  [ -f "$WORK/project/08_КОД/wp-theme/template-parts/block-hero.php" ]
  [ -f "$WORK/project/08_КОД/wp-theme/template-parts/block-pricing.php" ]
}

@test "block-<slug>.php has nu_field() calls per ACF field" {
  python "$SCRIPT" --project "$WORK/project" --blocks-only
  grep -q "nu_field( 'title'" "$WORK/project/08_КОД/wp-theme/template-parts/block-hero.php"
}

@test "does NOT overwrite existing block-<slug>.php" {
  echo "<?php /* manual content, do not touch */" > "$WORK/project/08_КОД/wp-theme/template-parts/block-hero.php"
  python "$SCRIPT" --project "$WORK/project" --blocks-only
  grep -q "manual content, do not touch" "$WORK/project/08_КОД/wp-theme/template-parts/block-hero.php"
}
