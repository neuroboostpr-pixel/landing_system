#!/usr/bin/env bats

setup() {
  ROOT="$(cd "$(dirname "$BATS_TEST_FILENAME")/../.." && pwd)"
  SCRIPT="$ROOT/scripts/export-palettes-to-library.py"
  FIXTURES="$ROOT/tests/phase-preview-panel/fixtures"
  WORK="$(mktemp -d)"
  # Clean copies for each test
  cp -r "$FIXTURES/project-with-new-palette" "$WORK/project"
  cp "$FIXTURES/library-empty.yaml" "$WORK/library.yaml"
}

teardown() {
  rm -rf "$WORK"
}

@test "exports a new palette into empty library" {
  run python "$SCRIPT" --project "$WORK/project" --library "$WORK/library.yaml"
  [ "$status" -eq 0 ]
  grep -q "id: forest-calm" "$WORK/library.yaml"
  grep -q 'created_in_project: "test-project"' "$WORK/library.yaml"
}

@test "skips palette whose id already exists" {
  cp "$FIXTURES/library-with-paper-minimal.yaml" "$WORK/library.yaml"
  # Add a palette to the project with id=paper-minimal
  cat > "$WORK/project/05_ДИЗАЙН-СИСТЕМА/palettes.yaml" <<'YAML'
palettes:
  - id: paper-minimal
    name: "Different name"
    description: "Different desc"
    created_at: "2026-05-12"
    created_in_project: "test-project"
    tokens:
      bg_base: "#000000"
      bg_section: "#000000"
      bg_elevated: "#000000"
      border_subtle: "#000000"
      border_strong: "#000000"
      text_primary: "#000000"
      text_soft: "#000000"
      text_dim: "#000000"
      accent_mint: "#000000"
      accent_teal: "#000000"
      accent_coral: "#000000"
      accent_coral_hover: "#000000"
      accent_coral_text: "#000000"
      accent_rgb_mint: "0, 0, 0"
      accent_rgb_coral: "0, 0, 0"
      card_bg: "#000000"
      card_border: "#000000"
      card_border_hover: "#000000"
      accent_cta_glow_opacity: "0.0"
YAML
  run python "$SCRIPT" --project "$WORK/project" --library "$WORK/library.yaml"
  [ "$status" -eq 0 ]
  [[ "$output" == *"skipped"* ]]
  # Original library entry preserved
  grep -q 'name: "Paper Minimal"' "$WORK/library.yaml"
  ! grep -q 'name: "Different name"' "$WORK/library.yaml"
}

@test "rejects invalid project YAML" {
  echo "not: [valid" > "$WORK/project/05_ДИЗАЙН-СИСТЕМА/palettes.yaml"
  run python "$SCRIPT" --project "$WORK/project" --library "$WORK/library.yaml"
  [ "$status" -ne 0 ]
}

@test "creates library file if absent" {
  rm "$WORK/library.yaml"
  run python "$SCRIPT" --project "$WORK/project" --library "$WORK/library.yaml"
  [ "$status" -eq 0 ]
  [ -f "$WORK/library.yaml" ]
  grep -q "id: forest-calm" "$WORK/library.yaml"
}
