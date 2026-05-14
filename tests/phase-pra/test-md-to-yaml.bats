#!/usr/bin/env bats

setup() {
  ROOT="$(cd "$(dirname "$BATS_TEST_FILENAME")/../.." && pwd)"
  FIXTURES="$ROOT/tests/phase-pra/fixtures"
  CONVERTER="$ROOT/skills/prototype-import/scripts/md-to-yaml.py"
  VALIDATOR="$ROOT/skills/prototype-import/scripts/validate-prototype.py"
}

@test "converts sample MD to valid YAML" {
  run python3 "$CONVERTER" "$FIXTURES/prototype-sample.md" "$BATS_TMPDIR/out.yaml"
  [ "$status" -eq 0 ]
  [ -f "$BATS_TMPDIR/out.yaml" ]
  run python3 "$VALIDATOR" "$BATS_TMPDIR/out.yaml"
  [ "$status" -eq 0 ]
}

@test "yaml preserves block order and headlines" {
  python3 "$CONVERTER" "$FIXTURES/prototype-sample.md" "$BATS_TMPDIR/out.yaml"
  run python3 -c "
import yaml, sys
d = yaml.safe_load(open('$BATS_TMPDIR/out.yaml'))
assert d['blocks'][0]['type'] == 'hero', d['blocks'][0]
assert d['blocks'][0]['headline'].startswith('Ремонт'), d['blocks'][0]
assert d['blocks'][1]['type'] == 'features', d['blocks'][1]
assert len(d['blocks'][1]['items']) == 2, d['blocks'][1]
print('OK')
"
  [ "$status" -eq 0 ]
}

@test "exits non-zero on malformed MD missing Project header" {
  cat > "$BATS_TMPDIR/bad.md" <<EOF
## Block 1: hero
- headline: x
EOF
  run python3 "$CONVERTER" "$BATS_TMPDIR/bad.md" "$BATS_TMPDIR/out2.yaml"
  [ "$status" -ne 0 ]
  [[ "$output" == *"Project"* ]]
}
