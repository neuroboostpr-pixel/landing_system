#!/usr/bin/env bats

setup() {
  ROOT="$(cd "$(dirname "$BATS_TEST_FILENAME")/../.." && pwd)"
  SCRIPT="$ROOT/skills/wp-gutenberg-block-builder/scripts/generate-block-json.py"
  FIXTURES="$ROOT/tests/phase-stage-08/fixtures"
  WORK="$(python -c "import tempfile; print(tempfile.mkdtemp().replace(chr(92),'/'))")"
  mkdir -p "$WORK/project/07_КОНТЕНТ" "$WORK/project/08_КОД"
  cp "$FIXTURES/content/minimal.md" "$WORK/project/07_КОНТЕНТ/final-copy.md"
}

teardown() { rm -rf "$WORK"; }

@test "creates block.json per block" {
  run python "$SCRIPT" --project "$WORK/project"
  [ "$status" -eq 0 ]
  [ -f "$WORK/project/08_КОД/gutenberg-blocks/hero/block.json" ]
  [ -f "$WORK/project/08_КОД/gutenberg-blocks/pricing/block.json" ]
}

@test "block.json has apiVersion 3 and acf namespace name" {
  python "$SCRIPT" --project "$WORK/project"
  HERO="$WORK/project/08_КОД/gutenberg-blocks/hero/block.json"
  python -c "
import json
d = json.load(open('$HERO'))
assert d['apiVersion'] == 3
assert d['name'] == 'acf/lp-hero'
assert d['category'] == 'lp-blocks'
assert d['acf']['renderTemplate'] == 'template-parts/block-hero.php'
"
}

@test "uses icon from block-icons.yaml" {
  python "$SCRIPT" --project "$WORK/project"
  grep -q '"icon": "cover-image"' "$WORK/project/08_КОД/gutenberg-blocks/hero/block.json"
  grep -q '"icon": "tag"' "$WORK/project/08_КОД/gutenberg-blocks/pricing/block.json"
}

@test "uses fallback icon for unmapped slugs" {
  cat > "$WORK/project/07_КОНТЕНТ/final-copy.md" <<'MD'
## Особый блок

Какой-то текст.
MD
  python "$SCRIPT" --project "$WORK/project"
  grep -q '"icon": "block-default"' "$WORK/project/08_КОД/gutenberg-blocks/osobyy-blok/block.json"
}

@test "idempotent: rerun produces same file" {
  python "$SCRIPT" --project "$WORK/project"
  cp "$WORK/project/08_КОД/gutenberg-blocks/hero/block.json" "$WORK/first.json"
  python "$SCRIPT" --project "$WORK/project"
  diff "$WORK/first.json" "$WORK/project/08_КОД/gutenberg-blocks/hero/block.json"
}
