#!/usr/bin/env bats

setup() {
  ROOT="$(cd "$(dirname "$BATS_TEST_FILENAME")/../.." && pwd)"
  SCAFFOLDER="$ROOT/skills/block-library-management/scripts/scaffold-block.py"
  VALIDATOR="$ROOT/skills/block-library-management/scripts/validate-meta.py"
  CATALOG_VAL="$ROOT/skills/block-library-management/scripts/validate-catalog.py"
}

@test "scaffolds new block with all required files" {
  TMPDIR="$BATS_TMPDIR/lib-$$"
  mkdir -p "$TMPDIR/hero"
  cat > "$TMPDIR/catalog.yaml" <<EOF
version: 1
updated: 2026-05-12
blocks: []
EOF
  run python3 "$SCAFFOLDER" \
      --id ru-hero-test-01 \
      --category hero \
      --library "$TMPDIR" \
      --template-source "$ROOT/vendor/opendesign-extracts/skill-block-template"
  [ "$status" -eq 0 ]
  [ -f "$TMPDIR/hero/ru-hero-test-01/SKILL.md" ]
  [ -f "$TMPDIR/hero/ru-hero-test-01/assets/template.html" ]
  [ -f "$TMPDIR/hero/ru-hero-test-01/assets/template-mobile.html" ]
  [ -f "$TMPDIR/hero/ru-hero-test-01/meta.yaml" ]
}

@test "scaffolded meta.yaml passes validator" {
  TMPDIR="$BATS_TMPDIR/lib-meta-$$"
  mkdir -p "$TMPDIR/hero"
  cat > "$TMPDIR/catalog.yaml" <<EOF
version: 1
updated: 2026-05-12
blocks: []
EOF
  python3 "$SCAFFOLDER" \
      --id ru-hero-test-02 \
      --category hero \
      --library "$TMPDIR" \
      --template-source "$ROOT/vendor/opendesign-extracts/skill-block-template"
  run python3 "$VALIDATOR" "$TMPDIR/hero/ru-hero-test-02/meta.yaml"
  [ "$status" -eq 0 ]
}

@test "scaffolded catalog.yaml passes validator" {
  TMPDIR="$BATS_TMPDIR/lib-cat-$$"
  mkdir -p "$TMPDIR/hero"
  cat > "$TMPDIR/catalog.yaml" <<EOF
version: 1
updated: 2026-05-12
blocks: []
EOF
  python3 "$SCAFFOLDER" \
      --id ru-hero-test-03 \
      --category hero \
      --library "$TMPDIR" \
      --template-source "$ROOT/vendor/opendesign-extracts/skill-block-template"
  run python3 "$CATALOG_VAL" "$TMPDIR/catalog.yaml"
  [ "$status" -eq 0 ]
}

@test "refuses to scaffold over existing block id" {
  TMPDIR="$BATS_TMPDIR/lib-dup-$$"
  mkdir -p "$TMPDIR/hero/ru-hero-test-04"
  cat > "$TMPDIR/catalog.yaml" <<EOF
version: 1
updated: 2026-05-12
blocks:
  - id: ru-hero-test-04
    path: hero/ru-hero-test-04/
    category: hero
    use_cases: [services]
EOF
  run python3 "$SCAFFOLDER" \
      --id ru-hero-test-04 \
      --category hero \
      --library "$TMPDIR" \
      --template-source "$ROOT/vendor/opendesign-extracts/skill-block-template"
  [ "$status" -ne 0 ]
  [[ "$output" == *"already exists"* ]]
}
