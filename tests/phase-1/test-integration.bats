#!/usr/bin/env bats

load '../helpers/test_helpers'

setup() {
  setup_temp_dir
}

teardown() {
  teardown_temp_dir
}

@test "INTEGRATION: full Phase 1 — create project from scratch" {
  TARGET="$TEST_TEMP/integration-project"

  # 1. Run init.sh
  run "$LANDING_SYSTEM_ROOT/skills/landing-project-init/scripts/init.sh" "$TARGET"
  [ "$status" -eq 0 ]

  # 2. All 13 stage folders exist
  for n in 00_БРИФ 01_КОНТЕКСТ 02_МАТЕРИАЛЫ_КЛИЕНТА 03_РЕФЕРЕНСЫ 04_БРЕНД 05_ДИЗАЙН-СИСТЕМА 06_СТЕК 07_КОНТЕНТ 08_КОД 09_ДЕПЛОЙ 10_QA 11_АНАЛИТИКА 12_SEO; do
    [ -d "$TARGET/$n" ] || { echo "missing: $n"; return 1; }
  done

  # 3. Project files exist
  [ -f "$TARGET/CLAUDE.md" ]
  [ -f "$TARGET/README.md" ]
  [ -f "$TARGET/.env.example" ]
  [ -f "$TARGET/.gitignore" ]

  # 4. Git initialized with commit
  [ -d "$TARGET/.git" ]
  run git -C "$TARGET" log --oneline
  [ "$status" -eq 0 ]
  [ -n "$output" ]
}

@test "INTEGRATION: from-context with parent" {
  PARENT="$TEST_TEMP/parent"
  mkdir -p "$PARENT/01_контекст" "$PARENT/04_документы"
  echo "niche stuff" > "$PARENT/01_контекст/niche.md"
  echo "proto" > "$PARENT/04_документы/прототип-test.md"

  TARGET="$TEST_TEMP/from-ctx-project"
  cd "$PARENT"
  run "$LANDING_SYSTEM_ROOT/skills/landing-from-context/scripts/from-context.sh" "$TARGET"
  [ "$status" -eq 0 ]

  # Project skeleton intact
  [ -d "$TARGET/00_БРИФ" ]
  # Context copied
  [ -f "$TARGET/01_КОНТЕКСТ/niche.md" ]
  [ -f "$TARGET/07_КОНТЕНТ/prototype.md" ]
  [ -f "$TARGET/01_КОНТЕКСТ/source-references.yaml" ]
}

@test "INTEGRATION: dependency check passes" {
  run "$LANDING_SYSTEM_ROOT/scripts/check-deps.sh"
  [ "$status" -eq 0 ]
}

@test "INTEGRATION: all skills have valid SKILL.md" {
  for skill_dir in "$LANDING_SYSTEM_ROOT"/skills/*/; do
    skill_md="$skill_dir/SKILL.md"
    [ -f "$skill_md" ] || { echo "missing SKILL.md in $skill_dir"; return 1; }
    grep -qE "^name:" "$skill_md" || { echo "no name in $skill_md"; return 1; }
    grep -qE "^description:" "$skill_md" || { echo "no description in $skill_md"; return 1; }
  done
}

@test "INTEGRATION: all agents have valid frontmatter" {
  for agent_md in "$LANDING_SYSTEM_ROOT"/agents/*.md; do
    grep -qE "^name:" "$agent_md" || { echo "no name in $agent_md"; return 1; }
    grep -qE "^description:" "$agent_md" || { echo "no description in $agent_md"; return 1; }
  done
}

@test "INTEGRATION: all commands have description" {
  for cmd_md in "$LANDING_SYSTEM_ROOT"/.claude/commands/*.md; do
    grep -qE "^description:" "$cmd_md" || { echo "no description in $cmd_md"; return 1; }
  done
}

@test "INTEGRATION: bats test runner is available and functional" {
  # Replacement for the recursive 'npm run test:phase-1' test (which would cause infinite recursion).
  # Instead, verify bats is installed and can run a trivial test successfully.
  run bats --version
  [ "$status" -eq 0 ]
  [[ "$output" == *"Bats"* ]]
}
