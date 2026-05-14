#!/usr/bin/env bats

setup() {
  ROOT="$(cd "$(dirname "$BATS_TEST_FILENAME")/../.." && pwd)"
  SCRIPT="$ROOT/scripts/backport-acf-to-legacy.sh"
  WORK="$(python -c "import tempfile; print(tempfile.mkdtemp().replace(chr(92),'/'))")"
  PROJECT="$WORK/legacy-project"
  mkdir -p "$PROJECT/07_КОНТЕНТ" "$PROJECT/08_КОД/wp-theme/template-parts"

  cp "$ROOT/tests/phase-stage-08/fixtures/content/minimal.md" "$PROJECT/07_КОНТЕНТ/final-copy.md"
  printf '<?php\nfunction nu_field($k,$d=""){return $d;}\nfunction nu_field_array($k,$d=array()){return $d;}\n' > "$PROJECT/08_КОД/wp-theme/functions.php"
  cat > "$PROJECT/.landing-state.yaml" <<'YAML'
project: "legacy-project"
stages:
  "07_content": {status: approved, timestamp: "2026-05-12T00:00:00Z"}
  "08_build": {status: in_progress, timestamp: ""}
legacy: true
YAML
}

teardown() { rm -rf "$WORK"; }

@test "creates artifacts when run without flags" {
  run bash "$SCRIPT" "$PROJECT"
  [ "$status" -eq 0 ]
  [ -f "$PROJECT/08_КОД/acf-fields.json" ]
  [ -f "$PROJECT/08_КОД/gutenberg-blocks/hero/block.json" ]
}

@test "creates backport-backup directory before modifying" {
  bash "$SCRIPT" "$PROJECT"
  ls -d "$PROJECT/.backport-backup-"* >/dev/null 2>&1
}

@test "--dry-run does not write files" {
  run bash "$SCRIPT" "$PROJECT" --dry-run
  [ "$status" -eq 0 ]
  [ ! -f "$PROJECT/08_КОД/acf-fields.json" ]
}

@test "without --force, refuses if acf-fields.json already exists" {
  bash "$SCRIPT" "$PROJECT"
  run bash "$SCRIPT" "$PROJECT"
  [ "$status" -ne 0 ]
  [[ "$output" == *"--force"* ]]
}

@test "with --force, regenerates over existing" {
  bash "$SCRIPT" "$PROJECT"
  run bash "$SCRIPT" "$PROJECT" --force
  [ "$status" -eq 0 ]
}

@test "removes legacy:true after successful run" {
  bash "$SCRIPT" "$PROJECT"
  ! grep -q "^legacy: true" "$PROJECT/.landing-state.yaml"
}
