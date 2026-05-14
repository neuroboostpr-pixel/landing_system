#!/usr/bin/env bats

setup() {
  ROOT="$(cd "$(dirname "$BATS_TEST_FILENAME")/../.." && pwd)"
  SCRIPT="$ROOT/scripts/mark-legacy-projects.sh"
  WORK="$(python -c "import tempfile; print(tempfile.mkdtemp().replace(chr(92),'/'))")"
  mkdir -p "$WORK/Lendings/legacy-project" "$WORK/Lendings/valid-project"

  cat > "$WORK/Lendings/legacy-project/.landing-state.yaml" <<'YAML'
project: "legacy-project"
stages:
  "08_build": {status: in_progress, timestamp: ""}
YAML
  # No stage-08 artifacts → would fail gate
  mkdir -p "$WORK/Lendings/legacy-project/07_КОНТЕНТ"
  echo "## Hero\n\ntext" > "$WORK/Lendings/legacy-project/07_КОНТЕНТ/final-copy.md"

  # Copy known-good valid project
  cp -r "$ROOT/tests/phase-stage-08/fixtures/projects/valid-project/." "$WORK/Lendings/valid-project/"
}

teardown() { rm -rf "$WORK"; }

@test "marks legacy:true on project that fails gate" {
  run bash "$SCRIPT" "$WORK/Lendings"
  [ "$status" -eq 0 ]
  grep -q "^legacy: true" "$WORK/Lendings/legacy-project/.landing-state.yaml"
}

@test "does not mark project that passes gate" {
  bash "$SCRIPT" "$WORK/Lendings"
  ! grep -q "^legacy: true" "$WORK/Lendings/valid-project/.landing-state.yaml"
}

@test "idempotent: running twice does not duplicate" {
  bash "$SCRIPT" "$WORK/Lendings"
  bash "$SCRIPT" "$WORK/Lendings"
  COUNT=$(grep -c "^legacy: true" "$WORK/Lendings/legacy-project/.landing-state.yaml")
  [ "$COUNT" = "1" ]
}

@test "skips dirs without .landing-state.yaml" {
  mkdir -p "$WORK/Lendings/not-a-project"
  run bash "$SCRIPT" "$WORK/Lendings"
  [ "$status" -eq 0 ]
}
