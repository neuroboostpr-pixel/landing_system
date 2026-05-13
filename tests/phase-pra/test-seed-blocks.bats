#!/usr/bin/env bats

setup() {
  ROOT="$(cd "$(dirname "$BATS_TEST_FILENAME")/../.." && pwd)"
  LIB="$ROOT/block-library"
  CATVAL="$ROOT/skills/block-library-management/scripts/validate-catalog.py"
  METAVAL="$ROOT/skills/block-library-management/scripts/validate-meta.py"
}

@test "catalog.yaml is valid" {
  run python3 "$CATVAL" "$LIB/catalog.yaml"
  [ "$status" -eq 0 ]
}

@test "all 22 seed blocks present and meta valid" {
  expected_count=22
  count=0
  for d in "$LIB"/*/*/meta.yaml; do
    run python3 "$METAVAL" "$d"
    [ "$status" -eq 0 ]
    count=$((count + 1))
  done
  [ "$count" -eq "$expected_count" ]
}

@test "every block has desktop and mobile template" {
  for d in "$LIB"/*/*/; do
    [ -f "$d/assets/template.html" ]
    [ -f "$d/assets/template-mobile.html" ]
  done
}

@test "every block template references at least one CSS var --color-accent" {
  for d in "$LIB"/*/*/; do
    grep -q -- "--color-accent" "$d/assets/template.html"
  done
}

@test "no quiz block contains WhatsApp reference" {
  ! grep -ril "whatsapp\|вотсап" "$LIB/quiz/"
}
