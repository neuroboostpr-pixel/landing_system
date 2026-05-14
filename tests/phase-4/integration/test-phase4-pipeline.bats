#!/usr/bin/env bats
# tests/phase-4/integration/test-phase4-pipeline.bats
# Integration: run generate-theme.py + generate-acf.py + bundle-assets.py + render-build-preview.py on a tmp project

REPO_ROOT="$(cd "$(dirname "$BATS_TEST_FILENAME")/../../.." && pwd)"
GENERATE_THEME="$REPO_ROOT/skills/wp-gutenberg-block-builder/scripts/generate-theme.py"
BUNDLE_ASSETS="$REPO_ROOT/skills/wp-theme-assembler/scripts/bundle-assets.py"
RENDER_PREVIEW="$REPO_ROOT/skills/wp-theme-assembler/scripts/render-build-preview.py"

setup() {
  PROJECT="$(mktemp -d)"

  # 05_ДИЗАЙН-СИСТЕМА
  mkdir -p "$PROJECT/05_ДИЗАЙН-СИСТЕМА"
  cat > "$PROJECT/05_ДИЗАЙН-СИСТЕМА/tokens.json" <<'TOKENS'
{
  "colors": {"primary": {"hex": "#ff5733", "role": "primary", "source": "ref.png"}},
  "typography": {"display": {"family": "Cabinet Grotesk", "size": "3rem", "weight": "700", "line_height": "1.1", "source": "DOM"}},
  "spacing": {"md": "1rem"},
  "radius": {"md": "0.5rem"},
  "shadow": {},
  "breakpoints": {},
  "motion": {}
}
TOKENS

  # 06_СТЕК
  mkdir -p "$PROJECT/06_СТЕК"
  cat > "$PROJECT/06_СТЕК/design-stack.yaml" <<'STACK'
mode: standard
fonts:
  cdn: bunny
  families:
    - name: Cabinet Grotesk
      weights: [400, 700]
icons:
  library: lucide
js_libraries: []
STACK

  # 07_КОНТЕНТ
  mkdir -p "$PROJECT/07_КОНТЕНТ"
  cat > "$PROJECT/07_КОНТЕНТ/final-copy.md" <<'COPY'
# Landing Copy

## HERO
Заголовок

## ФОРМА
Форма заявки
COPY

  # 04_БРЕНД
  mkdir -p "$PROJECT/04_БРЕНД/extracted"
  echo "icons: []" > "$PROJECT/04_БРЕНД/extracted/icons.yaml"

  # Photos
  mkdir -p "$PROJECT/02_МАТЕРИАЛЫ_КЛИЕНТА/photos/processed"

  # 08_КОД
  mkdir -p "$PROJECT/08_КОД"
}

teardown() {
  rm -rf "$PROJECT"
}

@test "generate-theme.py exits 0 on valid project" {
  run python3 "$GENERATE_THEME" "$PROJECT"
  [ "$status" -eq 0 ]
}

@test "generate-theme.py creates style.css with CSS vars" {
  python3 "$GENERATE_THEME" "$PROJECT"
  grep -q ":root {" "$PROJECT/08_КОД/wp-theme/style.css"
  grep -qe "color-primary" "$PROJECT/08_КОД/wp-theme/style.css"
}

@test "generate-theme.py creates functions.php with enqueue" {
  python3 "$GENERATE_THEME" "$PROJECT"
  grep -q "lp_enqueue_assets" "$PROJECT/08_КОД/wp-theme/functions.php"
  grep -q "bunny.net" "$PROJECT/08_КОД/wp-theme/functions.php"
}

@test "bundle-assets.py exits 0 after generate-theme creates dirs" {
  python3 "$GENERATE_THEME" "$PROJECT"
  run python3 "$BUNDLE_ASSETS" "$PROJECT"
  [ "$status" -eq 0 ]
}

@test "bundle-assets.py stdout is valid JSON" {
  python3 "$GENERATE_THEME" "$PROJECT"
  output="$(python3 "$BUNDLE_ASSETS" "$PROJECT")"
  echo "$output" | python3 -c "import json,sys; json.load(sys.stdin)"
}

@test "render-build-preview.py exits 0 after full pipeline" {
  python3 "$GENERATE_THEME" "$PROJECT"
  run python3 "$RENDER_PREVIEW" "$PROJECT"
  [ "$status" -eq 0 ]
}

@test "render-build-preview.py creates build-preview.html" {
  python3 "$GENERATE_THEME" "$PROJECT"
  python3 "$RENDER_PREVIEW" "$PROJECT"
  [ -f "$PROJECT/08_КОД/build-preview.html" ]
}

@test "build-preview.html contains color token" {
  python3 "$GENERATE_THEME" "$PROJECT"
  python3 "$RENDER_PREVIEW" "$PROJECT"
  grep -q "#ff5733" "$PROJECT/08_КОД/build-preview.html"
}

@test "build-preview.html contains section heading" {
  python3 "$GENERATE_THEME" "$PROJECT"
  python3 "$RENDER_PREVIEW" "$PROJECT"
  grep -qi "hero\|форма" "$PROJECT/08_КОД/build-preview.html"
}
