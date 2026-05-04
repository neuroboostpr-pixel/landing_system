#!/usr/bin/env bats
# tests/phase-4/test-agents-phase4.bats

REPO_ROOT="$(cd "$(dirname "$BATS_TEST_FILENAME")/../.." && pwd)"
AGENTS_DIR="$REPO_ROOT/agents"

@test "wp-builder.md exists" {
  [ -f "$AGENTS_DIR/wp-builder.md" ]
}

@test "wp-builder.md has name frontmatter" {
  grep -q "^name: wp-builder" "$AGENTS_DIR/wp-builder.md"
}

@test "wp-builder.md has description frontmatter" {
  grep -q "^description:" "$AGENTS_DIR/wp-builder.md"
}

@test "wp-builder.md mentions stage 08" {
  grep -q "stage 08\|этап 08\|08" "$AGENTS_DIR/wp-builder.md"
}

@test "wp-builder.md has HARD GATE" {
  grep -qi "hard gate" "$AGENTS_DIR/wp-builder.md"
}

@test "integrations-engineer.md exists" {
  [ -f "$AGENTS_DIR/integrations-engineer.md" ]
}

@test "integrations-engineer.md has name frontmatter" {
  grep -q "^name: integrations-engineer" "$AGENTS_DIR/integrations-engineer.md"
}

@test "integrations-engineer.md mentions Telegram" {
  grep -qi "telegram" "$AGENTS_DIR/integrations-engineer.md"
}

@test "integrations-engineer.md mentions Fluent Forms" {
  grep -qi "fluent" "$AGENTS_DIR/integrations-engineer.md"
}

@test "analytics-engineer.md exists" {
  [ -f "$AGENTS_DIR/analytics-engineer.md" ]
}

@test "analytics-engineer.md has name frontmatter" {
  grep -q "^name: analytics-engineer" "$AGENTS_DIR/analytics-engineer.md"
}

@test "analytics-engineer.md mentions Yandex Metrika" {
  grep -qi "метрика\|metrika" "$AGENTS_DIR/analytics-engineer.md"
}

@test "analytics-engineer.md mentions YM_COUNTER_ID" {
  grep -q "YM_COUNTER_ID" "$AGENTS_DIR/analytics-engineer.md"
}

@test "seo-optimizer.md exists" {
  [ -f "$AGENTS_DIR/seo-optimizer.md" ]
}

@test "seo-optimizer.md has name frontmatter" {
  grep -q "^name: seo-optimizer" "$AGENTS_DIR/seo-optimizer.md"
}

@test "seo-optimizer.md mentions Schema.org" {
  grep -qi "schema.org\|schema" "$AGENTS_DIR/seo-optimizer.md"
}

@test "seo-optimizer.md mentions robots.txt" {
  grep -q "robots.txt" "$AGENTS_DIR/seo-optimizer.md"
}

@test "seo-optimizer.md has HARD GATE" {
  grep -qi "hard gate" "$AGENTS_DIR/seo-optimizer.md"
}
