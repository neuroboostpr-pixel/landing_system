#!/usr/bin/env bats

setup() {
  ROOT="$(cd "$(dirname "$BATS_TEST_FILENAME")/../.." && pwd)"
  FIXTURES="$ROOT/tests/phase-stage-08/fixtures/projects"
  WORK="$(python -c "import tempfile; print(tempfile.mkdtemp().replace(chr(92),'/'))")"
  cp -r "$FIXTURES/valid-project" "$WORK/project"
}

teardown() { rm -rf "$WORK"; }

@test "happy path: valid-project passes gate" {
  run bash "$ROOT/scripts/gate-check.sh" --stage 08_build --project "$WORK/project" --auto
  [ "$status" -eq 0 ]
}

@test "#1 fails when wp-theme dir missing" {
  rm -rf "$WORK/project/08_КОД/wp-theme"
  run bash "$ROOT/scripts/gate-check.sh" --stage 08_build --project "$WORK/project" --auto
  [ "$status" -ne 0 ]
  [[ "$output" == *"wp-theme"* ]]
}

@test "#2 fails when no register_block_type in functions.php" {
  printf '<?php\n' > "$WORK/project/08_КОД/wp-theme/functions.php"
  run bash "$ROOT/scripts/gate-check.sh" --stage 08_build --project "$WORK/project" --auto
  [ "$status" -ne 0 ]
  [[ "$output" == *"block registration"* ]]
}

@test "#3 fails when acf-fields.json missing" {
  rm "$WORK/project/08_КОД/acf-fields.json"
  run bash "$ROOT/scripts/gate-check.sh" --stage 08_build --project "$WORK/project" --auto
  [ "$status" -ne 0 ]
  [[ "$output" == *"acf-fields.json"* ]]
}

@test "#4 fails when acf-fields.json is invalid JSON" {
  echo "{ broken" > "$WORK/project/08_КОД/acf-fields.json"
  run bash "$ROOT/scripts/gate-check.sh" --stage 08_build --project "$WORK/project" --auto
  [ "$status" -ne 0 ]
}

@test "#5 fails when ACF group missing for H2" {
  python -c "
import json
p = '$WORK/project/08_КОД/acf-fields.json'
d = json.load(open(p))
d.pop()
json.dump(d, open(p, 'w'))
"
  run bash "$ROOT/scripts/gate-check.sh" --stage 08_build --project "$WORK/project" --auto
  [ "$status" -ne 0 ]
  [[ "$output" == *"ACF group missing"* ]]
}

@test "#7 fails when block.php template part is missing" {
  rm "$WORK/project/08_КОД/wp-theme/template-parts/block-hero.php"
  run bash "$ROOT/scripts/gate-check.sh" --stage 08_build --project "$WORK/project" --auto
  [ "$status" -ne 0 ]
  [[ "$output" == *"block-hero"* ]]
}

@test "#8 fails when block.json missing" {
  rm "$WORK/project/08_КОД/gutenberg-blocks/hero/block.json"
  run bash "$ROOT/scripts/gate-check.sh" --stage 08_build --project "$WORK/project" --auto
  [ "$status" -ne 0 ]
  [[ "$output" == *"block.json"* ]]
}

@test "legacy: true bypasses all hard checks" {
  rm -rf "$WORK/project/08_КОД/wp-theme"  # would fail #1
  echo "legacy: true" >> "$WORK/project/.landing-state.yaml"
  run bash "$ROOT/scripts/gate-check.sh" --stage 08_build --project "$WORK/project" --auto
  [ "$status" -eq 0 ]
}
