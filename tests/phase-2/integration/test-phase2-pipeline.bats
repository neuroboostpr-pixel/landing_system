#!/usr/bin/env bats

load '../../helpers/test_helpers'

setup() {
  setup_temp_dir
  export PROJECT="$TEST_TEMP/landing-test"
  # Use Phase 1 init.sh to create skeleton
  "$LANDING_SYSTEM_ROOT/.skills/landing-project-init/scripts/init.sh" "$PROJECT" >/dev/null
}

teardown() {
  teardown_temp_dir
}

@test "INTEGRATION: refs index → moodboard render pipeline" {
  cd "$LANDING_SYSTEM_ROOT"

  # Add 3 refs
  python3 .skills/references-collection/scripts/index.py add \
    "$PROJECT/03_РЕФЕРЕНСЫ" "https://example.com/a" --status approved
  python3 .skills/references-collection/scripts/index.py add \
    "$PROJECT/03_РЕФЕРЕНСЫ" "https://example.com/b" --status approved
  python3 .skills/references-collection/scripts/index.py add \
    "$PROJECT/03_РЕФЕРЕНСЫ" "https://example.com/c" --status rejected

  # Verify index.yaml
  [ -f "$PROJECT/03_РЕФЕРЕНСЫ/index.yaml" ]

  # Render moodboard
  python3 .skills/moodboard-creation/scripts/render.py \
    "$PROJECT/03_РЕФЕРЕНСЫ" --project "test"

  # Verify moodboard.html
  [ -f "$PROJECT/03_РЕФЕРЕНСЫ/moodboard.html" ]
  run grep -c "https://example.com/a" "$PROJECT/03_РЕФЕРЕНСЫ/moodboard.html"
  [ "$status" -eq 0 ]
  [ "$output" -ge 1 ]
}

@test "INTEGRATION: scaffold generates moodboard.md from approved refs" {
  cd "$LANDING_SYSTEM_ROOT"
  python3 .skills/references-collection/scripts/index.py add \
    "$PROJECT/03_РЕФЕРЕНСЫ" "https://example.com/x" --status approved

  python3 .skills/moodboard-creation/scripts/scaffold.py \
    "$PROJECT/03_РЕФЕРЕНСЫ" --project "test"

  [ -f "$PROJECT/03_РЕФЕРЕНСЫ/moodboard.md" ]
}
