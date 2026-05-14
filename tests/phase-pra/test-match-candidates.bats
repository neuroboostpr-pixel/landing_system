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
  - id: ru-quiz-01-step-card
    path: quiz/ru-quiz-01-step-card/
    category: quiz
    use_cases: [services]
  - id: ru-quiz-03-intermediate
    path: quiz/ru-quiz-03-intermediate/
    category: quiz
    use_cases: [services]
  - id: ru-quiz-04-lead-form
    path: quiz/ru-quiz-04-lead-form/
    category: quiz
    use_cases: [services]
  - id: ru-quiz-05-thankyou
    path: quiz/ru-quiz-05-thankyou/
    category: quiz
    use_cases: [services]
  - id: ru-quiz-06-welcome-screen
    path: quiz/ru-quiz-06-welcome-screen/
    category: quiz
    use_cases: [services]
  - id: ru-quiz-07-image-choice
    path: quiz/ru-quiz-07-image-choice/
    category: quiz
    use_cases: [services]
  - id: ru-quiz-09-multi-select
    path: quiz/ru-quiz-09-multi-select/
    category: quiz
    use_cases: [services]
  - id: ru-quiz-10-loader-analyzing
    path: quiz/ru-quiz-10-loader-analyzing/
    category: quiz
    use_cases: [services]
  - id: ru-quiz-11-discount-bonus
    path: quiz/ru-quiz-11-discount-bonus/
    category: quiz
    use_cases: [services]
  - id: ru-quiz-13-comparison-question
    path: quiz/ru-quiz-13-comparison-question/
    category: quiz
    use_cases: [services]
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

@test "quiz_role=welcome returns ru-quiz-06-welcome-screen as first match" {
  run python3 "$MATCHER" --library "$TMPLIB" --type quiz --niche services --quiz-role welcome --top 3
  [ "$status" -eq 0 ]
  first=$(echo "$output" | python3 -c "import sys, json; print(json.load(sys.stdin)[0])")
  [ "$first" = "ru-quiz-06-welcome-screen" ]
}

@test "quiz_role=question returns ru-quiz-01-step-card as first match" {
  run python3 "$MATCHER" --library "$TMPLIB" --type quiz --niche services --quiz-role question --top 5
  [ "$status" -eq 0 ]
  first=$(echo "$output" | python3 -c "import sys, json; print(json.load(sys.stdin)[0])")
  [ "$first" = "ru-quiz-01-step-card" ]
}

@test "quiz_role=question returns multiple question variants" {
  run python3 "$MATCHER" --library "$TMPLIB" --type quiz --niche services --quiz-role question --top 5
  [ "$status" -eq 0 ]
  [[ "$output" == *"ru-quiz-07-image-choice"* ]]
}

@test "quiz_role=lead-form returns ru-quiz-04-lead-form as first match" {
  run python3 "$MATCHER" --library "$TMPLIB" --type quiz --niche services --quiz-role lead-form --top 3
  [ "$status" -eq 0 ]
  first=$(echo "$output" | python3 -c "import sys, json; print(json.load(sys.stdin)[0])")
  [ "$first" = "ru-quiz-04-lead-form" ]
}

@test "quiz_role=loader returns ru-quiz-10-loader-analyzing as first match" {
  run python3 "$MATCHER" --library "$TMPLIB" --type quiz --niche services --quiz-role loader --top 3
  [ "$status" -eq 0 ]
  first=$(echo "$output" | python3 -c "import sys, json; print(json.load(sys.stdin)[0])")
  [ "$first" = "ru-quiz-10-loader-analyzing" ]
}

@test "quiz_role=thankyou returns ru-quiz-05-thankyou as first match" {
  run python3 "$MATCHER" --library "$TMPLIB" --type quiz --niche services --quiz-role thankyou --top 3
  [ "$status" -eq 0 ]
  first=$(echo "$output" | python3 -c "import sys, json; print(json.load(sys.stdin)[0])")
  [ "$first" = "ru-quiz-05-thankyou" ]
}

@test "quiz without quiz_role falls back to generic top-N scoring" {
  run python3 "$MATCHER" --library "$TMPLIB" --type quiz --niche services --top 3
  [ "$status" -eq 0 ]
  # Should return some quiz blocks via generic path
  count=$(echo "$output" | python3 -c "import sys, json; print(len(json.load(sys.stdin)))")
  [ "$count" -gt 0 ]
}
