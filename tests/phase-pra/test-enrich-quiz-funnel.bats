#!/usr/bin/env bats

setup() {
  ROOT="$(cd "$(dirname "$BATS_TEST_FILENAME")/../.." && pwd)"
  ENRICHER="$ROOT/skills/prototype-import/scripts/enrich-quiz-funnel.py"
  VALIDATOR="$ROOT/skills/prototype-import/scripts/validate-prototype.py"
  TMPDIR_TEST="$BATS_TMPDIR/enrich-$$"
  mkdir -p "$TMPDIR_TEST"
}

teardown() {
  rm -rf "$TMPDIR_TEST"
}

# -----------------------------------------------------------------------
# Fixture helpers
# -----------------------------------------------------------------------

make_proto_0_quiz() {
  cat > "$TMPDIR_TEST/proto-0quiz.yaml" <<EOF
project:
  slug: test-0quiz
  niche: services
  source_file: prototype.md
blocks:
  - position: 1
    type: hero
    headline: "Герой"
  - position: 2
    type: features
    headline: "Фичи"
EOF
}

make_proto_1_quiz() {
  cat > "$TMPDIR_TEST/proto-1quiz.yaml" <<EOF
project:
  slug: test-1quiz
  niche: services
  source_file: prototype.md
blocks:
  - position: 1
    type: hero
    headline: "Герой"
  - position: 2
    type: quiz
    headline: "Рассчитайте стоимость за 1 минуту"
  - position: 3
    type: faq
    headline: "Вопросы и ответы"
EOF
}

make_proto_2_quiz() {
  cat > "$TMPDIR_TEST/proto-2quiz.yaml" <<EOF
project:
  slug: test-2quiz
  niche: services
  source_file: prototype.md
blocks:
  - position: 1
    type: hero
    headline: "Герой"
  - position: 2
    type: quiz
    headline: "Вопрос 1"
  - position: 3
    type: quiz
    headline: "Вопрос 2"
  - position: 4
    type: faq
    headline: "FAQ"
EOF
}

make_proto_enriched() {
  # Already has quiz_role — should be idempotent
  cat > "$TMPDIR_TEST/proto-enriched.yaml" <<EOF
project:
  slug: test-enriched
  niche: services
  source_file: prototype.md
blocks:
  - position: 1
    type: quiz
    quiz_role: welcome
    headline: "Старт"
  - position: 2
    type: quiz
    quiz_role: question
    question_number: 1
    headline: "Вопрос 1"
EOF
}

# -----------------------------------------------------------------------
# Test 1: prototype with 0 quiz blocks → output identical (no changes)
# -----------------------------------------------------------------------

@test "0 quiz blocks: output identical to input" {
  make_proto_0_quiz
  run python3 "$ENRICHER" \
    --input "$TMPDIR_TEST/proto-0quiz.yaml" \
    --output "$TMPDIR_TEST/out-0quiz.yaml" \
    --log "$TMPDIR_TEST/log-0quiz.md"
  [ "$status" -eq 0 ]
  # Output should contain no quiz_role
  run grep "quiz_role" "$TMPDIR_TEST/out-0quiz.yaml"
  [ "$status" -ne 0 ]
  # Log says no quiz
  run grep -i "не найдены" "$TMPDIR_TEST/log-0quiz.md"
  [ "$status" -eq 0 ]
}

# -----------------------------------------------------------------------
# Test 2: prototype with 1 quiz → output has 9 quiz blocks with quiz_role
# -----------------------------------------------------------------------

@test "1 quiz block: expanded to 9 quiz funnel blocks" {
  make_proto_1_quiz
  run python3 "$ENRICHER" \
    --input "$TMPDIR_TEST/proto-1quiz.yaml" \
    --output "$TMPDIR_TEST/out-1quiz.yaml" \
    --log "$TMPDIR_TEST/log-1quiz.md"
  [ "$status" -eq 0 ]
  # Count quiz blocks in output
  quiz_count=$(grep -c "type: quiz" "$TMPDIR_TEST/out-1quiz.yaml")
  [ "$quiz_count" -eq 9 ]
}

@test "1 quiz block: all 9 funnel quiz_roles are present" {
  make_proto_1_quiz
  python3 "$ENRICHER" \
    --input "$TMPDIR_TEST/proto-1quiz.yaml" \
    --output "$TMPDIR_TEST/out-1quiz.yaml" \
    --log "$TMPDIR_TEST/log-1quiz.md"
  # Check all required roles are present
  grep -q "quiz_role: welcome" "$TMPDIR_TEST/out-1quiz.yaml"
  grep -q "quiz_role: question" "$TMPDIR_TEST/out-1quiz.yaml"
  grep -q "quiz_role: intermediate" "$TMPDIR_TEST/out-1quiz.yaml"
  grep -q "quiz_role: loader" "$TMPDIR_TEST/out-1quiz.yaml"
  grep -q "quiz_role: discount" "$TMPDIR_TEST/out-1quiz.yaml"
  grep -q "quiz_role: lead-form" "$TMPDIR_TEST/out-1quiz.yaml"
  grep -q "quiz_role: thankyou" "$TMPDIR_TEST/out-1quiz.yaml"
}

@test "1 quiz block: original headline preserved in welcome block" {
  make_proto_1_quiz
  python3 "$ENRICHER" \
    --input "$TMPDIR_TEST/proto-1quiz.yaml" \
    --output "$TMPDIR_TEST/out-1quiz.yaml" \
    --log "$TMPDIR_TEST/log-1quiz.md"
  grep -q "Рассчитайте стоимость за 1 минуту" "$TMPDIR_TEST/out-1quiz.yaml"
}

@test "1 quiz block: subsequent non-quiz blocks shifted correctly" {
  make_proto_1_quiz
  python3 "$ENRICHER" \
    --input "$TMPDIR_TEST/proto-1quiz.yaml" \
    --output "$TMPDIR_TEST/out-1quiz.yaml" \
    --log "$TMPDIR_TEST/log-1quiz.md"
  # faq was position 3, should now be position 3+8=11
  grep -q "position: 11" "$TMPDIR_TEST/out-1quiz.yaml"
  grep -q "type: faq" "$TMPDIR_TEST/out-1quiz.yaml"
}

@test "1 quiz block: positions are continuous (no gaps)" {
  make_proto_1_quiz
  python3 "$ENRICHER" \
    --input "$TMPDIR_TEST/proto-1quiz.yaml" \
    --output "$TMPDIR_TEST/out-1quiz.yaml" \
    --log "$TMPDIR_TEST/log-1quiz.md"
  # Extract positions and check they are 1..11 (hero + 9 quiz + faq)
  positions=$(python3 -c "
import yaml, sys
data = yaml.safe_load(open('$TMPDIR_TEST/out-1quiz.yaml'))
positions = [b['position'] for b in data['blocks']]
print(' '.join(str(p) for p in sorted(positions)))
")
  [ "$positions" = "1 2 3 4 5 6 7 8 9 10 11" ]
}

# -----------------------------------------------------------------------
# Test 3: 2 quiz questions → welcome + questions + loader + discount + lead + thankyou
# -----------------------------------------------------------------------

@test "2 quiz blocks: infrastructure blocks added (welcome+loader+discount+lead-form+thankyou)" {
  make_proto_2_quiz
  run python3 "$ENRICHER" \
    --input "$TMPDIR_TEST/proto-2quiz.yaml" \
    --output "$TMPDIR_TEST/out-2quiz.yaml" \
    --log "$TMPDIR_TEST/log-2quiz.md"
  [ "$status" -eq 0 ]
  # Should now have 2 original + 5 infra = 7 quiz blocks
  quiz_count=$(grep -c "type: quiz" "$TMPDIR_TEST/out-2quiz.yaml")
  [ "$quiz_count" -eq 7 ]
}

@test "2 quiz blocks: quiz_role=question assigned to original quiz blocks" {
  make_proto_2_quiz
  python3 "$ENRICHER" \
    --input "$TMPDIR_TEST/proto-2quiz.yaml" \
    --output "$TMPDIR_TEST/out-2quiz.yaml" \
    --log "$TMPDIR_TEST/log-2quiz.md"
  role_count=$(grep -c "quiz_role: question" "$TMPDIR_TEST/out-2quiz.yaml")
  [ "$role_count" -eq 2 ]
}

# -----------------------------------------------------------------------
# Test 4: quiz_role values are all valid (within allowed enum)
# -----------------------------------------------------------------------

@test "1 quiz expanded: all quiz_role values are valid enum values" {
  make_proto_1_quiz
  python3 "$ENRICHER" \
    --input "$TMPDIR_TEST/proto-1quiz.yaml" \
    --output "$TMPDIR_TEST/out-1quiz.yaml" \
    --log "$TMPDIR_TEST/log-1quiz.md"
  # Validate output passes validate-prototype.py (which checks quiz_role enum)
  run python3 "$VALIDATOR" "$TMPDIR_TEST/out-1quiz.yaml"
  [ "$status" -eq 0 ]
}

# -----------------------------------------------------------------------
# Test 5: Idempotency — running twice gives same result
# -----------------------------------------------------------------------

@test "idempotent: running enricher twice on already-enriched proto → no change" {
  make_proto_1_quiz
  python3 "$ENRICHER" \
    --input "$TMPDIR_TEST/proto-1quiz.yaml" \
    --output "$TMPDIR_TEST/out-1quiz.yaml" \
    --log "$TMPDIR_TEST/log-1quiz.md"
  # Run again on already-enriched output
  python3 "$ENRICHER" \
    --input "$TMPDIR_TEST/out-1quiz.yaml" \
    --output "$TMPDIR_TEST/out-1quiz-2nd.yaml" \
    --log "$TMPDIR_TEST/log-1quiz-2nd.md"
  # Count should still be 9 quiz blocks (not 81)
  quiz_count=$(grep -c "type: quiz" "$TMPDIR_TEST/out-1quiz-2nd.yaml")
  [ "$quiz_count" -eq 9 ]
  # Log should say skipped
  run grep -i "повторный\|skipped\|Пропущено" "$TMPDIR_TEST/log-1quiz-2nd.md"
  [ "$status" -eq 0 ]
}

@test "idempotent: pre-enriched proto with quiz_role → skipped without changes" {
  make_proto_enriched
  python3 "$ENRICHER" \
    --input "$TMPDIR_TEST/proto-enriched.yaml" \
    --output "$TMPDIR_TEST/out-enriched.yaml" \
    --log "$TMPDIR_TEST/log-enriched.md"
  # Block count unchanged (2)
  block_count=$(python3 -c "import yaml; d=yaml.safe_load(open('$TMPDIR_TEST/out-enriched.yaml')); print(len(d['blocks']))")
  [ "$block_count" -eq 2 ]
}

# -----------------------------------------------------------------------
# Test 6: No WhatsApp in enriched output
# -----------------------------------------------------------------------

@test "enriched output contains no WhatsApp reference" {
  make_proto_1_quiz
  python3 "$ENRICHER" \
    --input "$TMPDIR_TEST/proto-1quiz.yaml" \
    --output "$TMPDIR_TEST/out-1quiz.yaml" \
    --log "$TMPDIR_TEST/log-1quiz.md"
  run grep -i "whatsapp\|вотсап\|ватсап" "$TMPDIR_TEST/out-1quiz.yaml"
  [ "$status" -ne 0 ]
}

# -----------------------------------------------------------------------
# Test 7: Enrichment log is human-readable Russian
# -----------------------------------------------------------------------

@test "enrichment-log.md is non-empty and contains Russian text" {
  make_proto_1_quiz
  python3 "$ENRICHER" \
    --input "$TMPDIR_TEST/proto-1quiz.yaml" \
    --output "$TMPDIR_TEST/out-1quiz.yaml" \
    --log "$TMPDIR_TEST/log-1quiz.md"
  [ -s "$TMPDIR_TEST/log-1quiz.md" ]
  run grep -q "Marquiz" "$TMPDIR_TEST/log-1quiz.md"
  [ "$status" -eq 0 ]
}
