#!/usr/bin/env bats

setup() {
  ROOT="$(cd "$(dirname "$BATS_TEST_FILENAME")/../.." && pwd)"
  RENDERER="$ROOT/skills/wireframe-rendering/scripts/render-wireframe.py"

  PROJECT="$BATS_TMPDIR/proj-$$"
  mkdir -p "$PROJECT/07_ПРОТОТИП" "$PROJECT/07a_WIREFRAME"
  cat > "$PROJECT/07_ПРОТОТИП/prototype.yaml" <<EOF
project:
  slug: example
  niche: services
  source_file: prototype.pdf
blocks:
  - position: 1
    type: hero
    headline: "Test"
    slots: []
EOF
}

@test "renders wireframe.html and candidates.yaml" {
  run python3 "$RENDERER" \
      --project "$PROJECT" \
      --library "$ROOT/block-library" \
      --template "$ROOT/skills/wireframe-rendering/templates/wireframe-shell.html"
  [ "$status" -eq 0 ]
  [ -f "$PROJECT/07a_WIREFRAME/wireframe.html" ]
  [ -f "$PROJECT/07a_WIREFRAME/candidates.yaml" ]
}

@test "wireframe.html contains radio inputs" {
  python3 "$RENDERER" \
      --project "$PROJECT" \
      --library "$ROOT/block-library" \
      --template "$ROOT/skills/wireframe-rendering/templates/wireframe-shell.html"
  run grep -c 'type="radio"' "$PROJECT/07a_WIREFRAME/wireframe.html"
  [ "$status" -eq 0 ]
  [ "$output" -ge 1 ]
}

@test "wireframe.html contains :checked CSS selector" {
  python3 "$RENDERER" \
      --project "$PROJECT" \
      --library "$ROOT/block-library" \
      --template "$ROOT/skills/wireframe-rendering/templates/wireframe-shell.html"
  run grep -c ':checked' "$PROJECT/07a_WIREFRAME/wireframe.html"
  [ "$status" -eq 0 ]
  [ "$output" -ge 1 ]
}
