#!/usr/bin/env bats

setup() {
  ROOT="$(cd "$(dirname "$BATS_TEST_FILENAME")/../.." && pwd)"
  MATCHER="$ROOT/skills/wireframe-rendering/scripts/match-candidates.py"

  TMPLIB="$BATS_TMPDIR/lib-$$"
  mkdir -p "$TMPLIB/hero"
  cat > "$TMPLIB/catalog.yaml" <<EOF
version: 1
updated: 2026-05-12
blocks:
  - id: ru-hero-01-services-calc
    path: hero/ru-hero-01-services-calc/
    category: hero
    use_cases: [services]
  - id: ru-hero-02-b2c-expert
    path: hero/ru-hero-02-b2c-expert/
    category: hero
    use_cases: [b2c]
  - id: ru-hero-03-local-interior
    path: hero/ru-hero-03-local-interior/
    category: hero
    use_cases: [local]
  - id: ru-features-01-3col-icons
    path: features/ru-features-01-3col-icons/
    category: features
    use_cases: [services, b2c, local]
EOF
}

@test "matches services hero" {
  run python3 "$MATCHER" --library "$TMPLIB" --type hero --niche services --top 3
  [ "$status" -eq 0 ]
  [[ "$output" == *"ru-hero-01-services-calc"* ]]
}

@test "matches features for any niche" {
  run python3 "$MATCHER" --library "$TMPLIB" --type features --niche services --top 3
  [ "$status" -eq 0 ]
  [[ "$output" == *"ru-features-01-3col-icons"* ]]
}

@test "returns nothing when no category match" {
  run python3 "$MATCHER" --library "$TMPLIB" --type pricing --niche services --top 3
  [ "$status" -eq 0 ]
  [ -z "$(echo "$output" | grep -v '^\[\]$')" ] || [ "$output" == "[]" ]
}

@test "respects --top limit" {
  run python3 "$MATCHER" --library "$TMPLIB" --type hero --niche services --top 1
  [ "$status" -eq 0 ]
  count=$(echo "$output" | python3 -c "import sys, json; print(len(json.load(sys.stdin)))")
  [ "$count" -eq 1 ]
}
