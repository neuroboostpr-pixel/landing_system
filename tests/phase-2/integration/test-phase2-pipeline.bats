#!/usr/bin/env bats

load '../../helpers/test_helpers'

setup() {
  setup_temp_dir
  export PROJECT="$TEST_TEMP/landing-test"
  # Use Phase 1 init.sh to create skeleton
  "$LANDING_SYSTEM_ROOT/skills/landing-project-init/scripts/init.sh" "$PROJECT" >/dev/null
}

teardown() {
  teardown_temp_dir
}

@test "INTEGRATION: refs index → moodboard render pipeline" {
  cd "$LANDING_SYSTEM_ROOT"

  # Add 3 refs
  python3 skills/references-collection/scripts/index.py add \
    "$PROJECT/03_РЕФЕРЕНСЫ" "https://example.com/a" --status approved
  python3 skills/references-collection/scripts/index.py add \
    "$PROJECT/03_РЕФЕРЕНСЫ" "https://example.com/b" --status approved
  python3 skills/references-collection/scripts/index.py add \
    "$PROJECT/03_РЕФЕРЕНСЫ" "https://example.com/c" --status rejected

  # Verify index.yaml
  [ -f "$PROJECT/03_РЕФЕРЕНСЫ/index.yaml" ]

  # Render moodboard
  python3 skills/moodboard-creation/scripts/render.py \
    "$PROJECT/03_РЕФЕРЕНСЫ" --project "test"

  # Verify moodboard.html
  [ -f "$PROJECT/03_РЕФЕРЕНСЫ/moodboard.html" ]
  run grep -c "https://example.com/a" "$PROJECT/03_РЕФЕРЕНСЫ/moodboard.html"
  [ "$status" -eq 0 ]
  [ "$output" -ge 1 ]
}

@test "INTEGRATION: scaffold generates moodboard.md from approved refs" {
  cd "$LANDING_SYSTEM_ROOT"
  python3 skills/references-collection/scripts/index.py add \
    "$PROJECT/03_РЕФЕРЕНСЫ" "https://example.com/x" --status approved

  python3 skills/moodboard-creation/scripts/scaffold.py \
    "$PROJECT/03_РЕФЕРЕНСЫ" --project "test"

  [ -f "$PROJECT/03_РЕФЕРЕНСЫ/moodboard.md" ]
}

@test "INTEGRATION: style-extractor orchestrate produces 5 output files" {
  cd "$LANDING_SYSTEM_ROOT"

  # Create fixture images using Pillow
  python3 - <<'PYEOF'
from PIL import Image
import sys, os
project = os.environ["PROJECT"]
imgs_dir = project + "/03_РЕФЕРЕНСЫ/images"
os.makedirs(imgs_dir, exist_ok=True)
# Three simple colored images
Image.new("RGB", (50, 50), (200, 50, 50)).save(imgs_dir + "/ref-red.png")
Image.new("RGB", (50, 50), (50, 100, 200)).save(imgs_dir + "/ref-blue.png")
PYEOF

  # Run orchestrate without URL (no network)
  python3 skills/style-decomposition/scripts/orchestrate.py \
    "$PROJECT" \
    --images "$PROJECT/03_РЕФЕРЕНСЫ/images/ref-red.png" \
              "$PROJECT/03_РЕФЕРЕНСЫ/images/ref-blue.png"

  # Assert all 5 output files exist and are non-empty
  EXTRACTED="$PROJECT/04_БРЕНД/extracted"
  [ -f "$EXTRACTED/palette.yaml" ]
  [ -s "$EXTRACTED/palette.yaml" ]

  [ -f "$EXTRACTED/fonts.yaml" ]
  [ -s "$EXTRACTED/fonts.yaml" ]

  [ -f "$EXTRACTED/icons.yaml" ]
  [ -s "$EXTRACTED/icons.yaml" ]

  [ -f "$EXTRACTED/grid.md" ]
  [ -s "$EXTRACTED/grid.md" ]

  [ -f "$EXTRACTED/motion.md" ]
  [ -s "$EXTRACTED/motion.md" ]
}
