#!/usr/bin/env bats

setup() {
  ROOT="$(cd "$(dirname "$BATS_TEST_FILENAME")/../.." && pwd)"
  SCRIPT="$ROOT/skills/wp-gutenberg-block-builder/scripts/generate-acf.py"
  FIXTURES="$ROOT/tests/phase-stage-08/fixtures"
  WORK="$(python -c "import tempfile; print(tempfile.mkdtemp().replace(chr(92),'/'))")"
  mkdir -p "$WORK/project/07_КОНТЕНТ" "$WORK/project/08_КОД"
  cp "$FIXTURES/content/minimal.md" "$WORK/project/07_КОНТЕНТ/final-copy.md"
}

teardown() { rm -rf "$WORK"; }

@test "creates acf-fields.json from minimal.md" {
  run python "$SCRIPT" --project "$WORK/project"
  [ "$status" -eq 0 ]
  [ -f "$WORK/project/08_КОД/acf-fields.json" ]
}

@test "acf-fields.json is valid JSON" {
  python "$SCRIPT" --project "$WORK/project"
  python -c "import json; json.load(open('$WORK/project/08_КОД/acf-fields.json'))"
}

@test "contains one group per H2 block" {
  python "$SCRIPT" --project "$WORK/project"
  COUNT=$(python -c "import json; print(len(json.load(open('$WORK/project/08_КОД/acf-fields.json'))))")
  [ "$COUNT" = "2" ]
}

@test "group keys are deterministic" {
  python "$SCRIPT" --project "$WORK/project"
  grep -q '"key": "group_lp_hero"' "$WORK/project/08_КОД/acf-fields.json"
  grep -q '"key": "group_lp_pricing"' "$WORK/project/08_КОД/acf-fields.json"
}

@test "location targets acf/lp-<slug> block" {
  python "$SCRIPT" --project "$WORK/project"
  grep -q '"value": "acf/lp-hero"' "$WORK/project/08_КОД/acf-fields.json"
  grep -q '"value": "acf/lp-pricing"' "$WORK/project/08_КОД/acf-fields.json"
}

@test "rerun is idempotent (same output)" {
  python "$SCRIPT" --project "$WORK/project"
  cp "$WORK/project/08_КОД/acf-fields.json" "$WORK/first.json"
  python "$SCRIPT" --project "$WORK/project"
  diff "$WORK/first.json" "$WORK/project/08_КОД/acf-fields.json"
}

@test "backs up existing acf-fields.json" {
  python "$SCRIPT" --project "$WORK/project"
  echo "garbage" > "$WORK/project/08_КОД/acf-fields.json"
  python "$SCRIPT" --project "$WORK/project"
  [ -f "$WORK/project/08_КОД/acf-fields.json.bak" ]
  grep -q "garbage" "$WORK/project/08_КОД/acf-fields.json.bak"
}

@test "exits non-zero with parse error on bad content" {
  echo "no h2 here" > "$WORK/project/07_КОНТЕНТ/final-copy.md"
  run python "$SCRIPT" --project "$WORK/project"
  [ "$status" -ne 0 ]
  [[ "$output" == *"no H2 sections"* ]]
}
