#!/usr/bin/env bats

setup() {
  ROOT="$(cd "$(dirname "$BATS_TEST_FILENAME")/../.." && pwd)"
  SCRIPT="$ROOT/scripts/snapshot-palettes-to-project.py"
  FIXTURES="$ROOT/tests/phase-preview-panel/fixtures"
  WORK="$(python -c "import tempfile; print(tempfile.mkdtemp().replace(chr(92),'/'))")"
  mkdir -p "$WORK/project/04_БРЕНД"
  cp "$FIXTURES/library-three-palettes.yaml" "$WORK/library.yaml"
}

teardown() {
  rm -rf "$WORK"
}

@test "--all copies every palette from library" {
  run python "$SCRIPT" --project "$WORK/project" --library "$WORK/library.yaml" --all
  [ "$status" -eq 0 ]
  grep -q "id: paper-minimal" "$WORK/project/04_БРЕНД/palettes.yaml"
  grep -q "id: quiet-dark" "$WORK/project/04_БРЕНД/palettes.yaml"
  grep -q "id: forest-calm" "$WORK/project/04_БРЕНД/palettes.yaml"
}

@test "--id selects specific palettes by id" {
  run python "$SCRIPT" --project "$WORK/project" --library "$WORK/library.yaml" --id paper-minimal --id forest-calm
  [ "$status" -eq 0 ]
  grep -q "id: paper-minimal" "$WORK/project/04_БРЕНД/palettes.yaml"
  grep -q "id: forest-calm" "$WORK/project/04_БРЕНД/palettes.yaml"
  ! grep -q "id: quiet-dark" "$WORK/project/04_БРЕНД/palettes.yaml"
}

@test "unknown --id fails" {
  run python "$SCRIPT" --project "$WORK/project" --library "$WORK/library.yaml" --id no-such-palette
  [ "$status" -ne 0 ]
  [[ "$output" == *"no-such-palette"* ]]
}

@test "snapshot validates against schema" {
  # Corrupt the library to be missing a token in one palette
  python -c "
import yaml
with open('$WORK/library.yaml') as f: d=yaml.safe_load(f)
del d['palettes'][0]['tokens']['accent_cta_glow_opacity']
with open('$WORK/library.yaml','w') as f: yaml.safe_dump(d,f)
"
  run python "$SCRIPT" --project "$WORK/project" --library "$WORK/library.yaml" --all
  [ "$status" -ne 0 ]
}
