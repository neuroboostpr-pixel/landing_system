#!/usr/bin/env bats

setup() {
  ROOT="$(cd "$(dirname "$BATS_TEST_FILENAME")/../.." && pwd)"
  SCRIPT="$ROOT/scripts/migrate-niche-to-v2.sh"
  TMP="$(mktemp -d)"
  PROJECT="$TMP/proj"
  mkdir -p "$PROJECT/01a_АНАЛИЗ_НИШИ"
}

teardown() {
  rm -rf "$TMP"
}

@test "migrate script exists and is executable" {
  [ -f "$SCRIPT" ]
  [ -x "$SCRIPT" ]
}

@test "migrate adds Mode: legacy_v1 to positioning.md without Mode header" {
  cat > "$PROJECT/01a_АНАЛИЗ_НИШИ/positioning.md" <<'EOF'
# Позиционирование: Test

## Core promise
Promise text.
EOF
  bash "$SCRIPT" "$PROJECT"
  grep -q '^\*\*Mode:\*\* legacy_v1' "$PROJECT/01a_АНАЛИЗ_НИШИ/positioning.md"
}

@test "migrate is idempotent — does not duplicate Mode header" {
  cat > "$PROJECT/01a_АНАЛИЗ_НИШИ/positioning.md" <<'EOF'
# Позиционирование: Test

**Mode:** emotional_aspiration

## Core promise
EOF
  bash "$SCRIPT" "$PROJECT"
  count=$(grep -c '^\*\*Mode:\*\*' "$PROJECT/01a_АНАЛИЗ_НИШИ/positioning.md")
  [ "$count" -eq 1 ]
}

@test "migrate creates market-profile.md stub when missing" {
  cat > "$PROJECT/01a_АНАЛИЗ_НИШИ/positioning.md" <<'EOF'
# Позиционирование: Test
EOF
  bash "$SCRIPT" "$PROJECT"
  [ -f "$PROJECT/01a_АНАЛИЗ_НИШИ/market-profile.md" ]
  grep -q "## 1. Accessibility tier" "$PROJECT/01a_АНАЛИЗ_НИШИ/market-profile.md"
  grep -q "Predicted mode:" "$PROJECT/01a_АНАЛИЗ_НИШИ/market-profile.md"
}

@test "migrate creates landing-structure.md stub when missing" {
  cat > "$PROJECT/01a_АНАЛИЗ_НИШИ/positioning.md" <<'EOF'
# Позиционирование: Test
EOF
  bash "$SCRIPT" "$PROJECT"
  [ -f "$PROJECT/01a_АНАЛИЗ_НИШИ/landing-structure.md" ]
  grep -q "Тип бренда:" "$PROJECT/01a_АНАЛИЗ_НИШИ/landing-structure.md"
  grep -q "Режим: legacy_v1" "$PROJECT/01a_АНАЛИЗ_НИШИ/landing-structure.md"
  grep -q "## Блоки лендинга" "$PROJECT/01a_АНАЛИЗ_НИШИ/landing-structure.md"
}

@test "migrate does not overwrite existing market-profile.md" {
  cat > "$PROJECT/01a_АНАЛИЗ_НИШИ/positioning.md" <<'EOF'
# Test
EOF
  echo "EXISTING CONTENT" > "$PROJECT/01a_АНАЛИЗ_НИШИ/market-profile.md"
  bash "$SCRIPT" "$PROJECT"
  grep -q "EXISTING CONTENT" "$PROJECT/01a_АНАЛИЗ_НИШИ/market-profile.md"
}

@test "migrate fails with usage when no project arg" {
  run bash "$SCRIPT"
  [ "$status" -ne 0 ]
}

@test "migrate fails when 01a folder missing" {
  rm -rf "$PROJECT/01a_АНАЛИЗ_НИШИ"
  run bash "$SCRIPT" "$PROJECT"
  [ "$status" -ne 0 ]
}

@test "generated stubs pass validators" {
  cat > "$PROJECT/01a_АНАЛИЗ_НИШИ/positioning.md" <<'EOF'
# Позиционирование: Test
## Core promise
Some promise.
EOF
  bash "$SCRIPT" "$PROJECT"
  # Convert path for python on windows
  PMP="$(cygpath -m "$PROJECT/01a_АНАЛИЗ_НИШИ/market-profile.md" 2>/dev/null || echo "$PROJECT/01a_АНАЛИЗ_НИШИ/market-profile.md")"
  PLS="$(cygpath -m "$PROJECT/01a_АНАЛИЗ_НИШИ/landing-structure.md" 2>/dev/null || echo "$PROJECT/01a_АНАЛИЗ_НИШИ/landing-structure.md")"
  PPO="$(cygpath -m "$PROJECT/01a_АНАЛИЗ_НИШИ/positioning.md" 2>/dev/null || echo "$PROJECT/01a_АНАЛИЗ_НИШИ/positioning.md")"
  python "$ROOT/skills/niche-analysis/scripts/validate-market-profile.py" "$PMP"
  python "$ROOT/skills/niche-analysis/scripts/validate-landing-structure.py" "$PLS"
  python "$ROOT/skills/niche-analysis/scripts/validate-positioning.py" "$PPO"
}
