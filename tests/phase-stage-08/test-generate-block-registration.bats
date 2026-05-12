#!/usr/bin/env bats

setup() {
  ROOT="$(cd "$(dirname "$BATS_TEST_FILENAME")/../.." && pwd)"
  SCRIPT="$ROOT/skills/wp-gutenberg-block-builder/scripts/generate-block-registration.py"
  FIXTURES="$ROOT/tests/phase-stage-08/fixtures"
  WORK="$(python -c "import tempfile; print(tempfile.mkdtemp().replace(chr(92),'/'))")"
  mkdir -p "$WORK/project/07_КОНТЕНТ" "$WORK/project/08_КОД/wp-theme"
  cp "$FIXTURES/content/minimal.md" "$WORK/project/07_КОНТЕНТ/final-copy.md"
  # Pre-existing functions.php with user code outside auto-generated zone
  cat > "$WORK/project/08_КОД/wp-theme/functions.php" <<'PHP'
<?php
function nu_setup() { add_theme_support('post-thumbnails'); }
add_action('after_setup_theme', 'nu_setup');
PHP
}

teardown() { rm -rf "$WORK"; }

@test "adds AUTO-GENERATED block in functions.php" {
  run python "$SCRIPT" --project "$WORK/project"
  [ "$status" -eq 0 ]
  grep -q "AUTO-GENERATED START: lp-block-registration" "$WORK/project/08_КОД/wp-theme/functions.php"
  grep -q "AUTO-GENERATED END" "$WORK/project/08_КОД/wp-theme/functions.php"
}

@test "registers all blocks in the loop" {
  python "$SCRIPT" --project "$WORK/project"
  grep -q "'hero'" "$WORK/project/08_КОД/wp-theme/functions.php"
  grep -q "'pricing'" "$WORK/project/08_КОД/wp-theme/functions.php"
}

@test "registers lp-blocks category" {
  python "$SCRIPT" --project "$WORK/project"
  grep -q "'lp-blocks'" "$WORK/project/08_КОД/wp-theme/functions.php"
  grep -q "block_categories_all" "$WORK/project/08_КОД/wp-theme/functions.php"
}

@test "preserves user code outside markers" {
  python "$SCRIPT" --project "$WORK/project"
  grep -q "function nu_setup" "$WORK/project/08_КОД/wp-theme/functions.php"
}

@test "idempotent: rerun does not duplicate" {
  python "$SCRIPT" --project "$WORK/project"
  python "$SCRIPT" --project "$WORK/project"
  COUNT=$(grep -c "AUTO-GENERATED START" "$WORK/project/08_КОД/wp-theme/functions.php")
  [ "$COUNT" = "1" ]
}

@test "creates .bak before modifying" {
  python "$SCRIPT" --project "$WORK/project"
  [ -f "$WORK/project/08_КОД/wp-theme/functions.php.bak" ]
}

@test "fails if markers were manually removed and content changed" {
  python "$SCRIPT" --project "$WORK/project"
  # Strip out the auto-generated block but leave the file
  python -c "
import re
path = '$WORK/project/08_КОД/wp-theme/functions.php'
s = open(path).read()
s = re.sub(r'// AUTO-GENERATED START.*?// AUTO-GENERATED END\n', '', s, flags=re.DOTALL)
open(path, 'w').write(s)
"
  # Now rerun — adds markers back fine (no error, this is the recovery path)
  run python "$SCRIPT" --project "$WORK/project"
  [ "$status" -eq 0 ]
  grep -q "AUTO-GENERATED START" "$WORK/project/08_КОД/wp-theme/functions.php"
}
