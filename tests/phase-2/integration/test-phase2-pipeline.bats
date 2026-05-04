#!/usr/bin/env bats

load '../../helpers/test_helpers'

# Run a quick smoke-test of the Phase 2 pipeline using fixture data.
# No real network calls — mocked via fixture files only.

setup() {
  # Create a temp project directory with the expected structure
  export TEST_PROJECT="$(mktemp -d)"

  # Create stage folders
  for stage in "00_БРИФ" "01_КОНТЕКСТ" "02_МАТЕРИАЛЫ_КЛИЕНТА" "03_РЕФЕРЕНСЫ" "04_БРЕНД" "05_ДИЗАЙН-СИСТЕМА" "06_СТЕК" "07_КОНТЕНТ" "08_КОД" "09_ДЕПЛОЙ" "10_QA" "11_АНАЛИТИКА" "12_SEO"; do
    mkdir -p "$TEST_PROJECT/$stage"
  done

  # Create extracted/ folder with fixture data
  mkdir -p "$TEST_PROJECT/04_БРЕНД/extracted"

  # Fixture palette.yaml
  cat > "$TEST_PROJECT/04_БРЕНД/extracted/palette.yaml" << 'YAML'
source_image: fixture.png
palette:
  - hex: '#ff5733'
    rgb: [255, 87, 51]
    source_pixel: [10, 20]
  - hex: '#33c1ff'
    rgb: [51, 193, 255]
    source_pixel: [50, 50]
YAML

  # Fixture fonts.yaml
  cat > "$TEST_PROJECT/04_БРЕНД/extracted/fonts.yaml" << 'YAML'
source_url: https://example.com
method: DOM CSS inspection (Playwright)
candidates:
  - family: Cabinet Grotesk
    confidence: 0.9
    source: DOM computed style
manual_review_required: false
YAML

  # Fixture icons.yaml
  cat > "$TEST_PROJECT/04_БРЕНД/extracted/icons.yaml" << 'YAML'
query_terms: [check, arrow]
recommended_library: lucide
results:
  - id: lucide:check
    name: check
    prefix: lucide
YAML

  echo "12-column, 24px gap" > "$TEST_PROJECT/04_БРЕНД/extracted/grid.md"
  echo "Subtle transitions, 200-400ms" > "$TEST_PROJECT/04_БРЕНД/extracted/motion.md"

  # Fixture refs index
  cat > "$TEST_PROJECT/03_РЕФЕРЕНСЫ/index.yaml" << 'YAML'
refs:
  - url: https://example.com
    status: approved
    tags: [hero]
YAML
}

teardown() {
  rm -rf "$TEST_PROJECT"
}

@test "phase2 integration: brand-kit build.py produces brand-kit.md" {
  run python3 "$LANDING_SYSTEM_ROOT/skills/brand-kit-build/scripts/build.py" "$TEST_PROJECT"
  [ "$status" -eq 0 ]
  assert_file_exists "$TEST_PROJECT/04_БРЕНД/brand-kit.md"
}

@test "phase2 integration: brand-kit.md contains color provenance" {
  python3 "$LANDING_SYSTEM_ROOT/skills/brand-kit-build/scripts/build.py" "$TEST_PROJECT"
  run grep "ff5733" "$TEST_PROJECT/04_БРЕНД/brand-kit.md"
  [ "$status" -eq 0 ]
}

@test "phase2 integration: brand-kit.md contains font" {
  python3 "$LANDING_SYSTEM_ROOT/skills/brand-kit-build/scripts/build.py" "$TEST_PROJECT"
  run grep "Cabinet Grotesk" "$TEST_PROJECT/04_БРЕНД/brand-kit.md"
  [ "$status" -eq 0 ]
}

@test "phase2 integration: render-html.py produces brand-kit.html" {
  python3 "$LANDING_SYSTEM_ROOT/skills/brand-kit-build/scripts/build.py" "$TEST_PROJECT"
  run python3 "$LANDING_SYSTEM_ROOT/skills/brand-kit-build/scripts/render-html.py" "$TEST_PROJECT"
  [ "$status" -eq 0 ]
  assert_file_exists "$TEST_PROJECT/04_БРЕНД/brand-kit.html"
}

@test "phase2 integration: brand-kit.html is non-empty HTML" {
  python3 "$LANDING_SYSTEM_ROOT/skills/brand-kit-build/scripts/build.py" "$TEST_PROJECT"
  python3 "$LANDING_SYSTEM_ROOT/skills/brand-kit-build/scripts/render-html.py" "$TEST_PROJECT"
  run grep "DOCTYPE html" "$TEST_PROJECT/04_БРЕНД/brand-kit.html"
  [ "$status" -eq 0 ]
}
