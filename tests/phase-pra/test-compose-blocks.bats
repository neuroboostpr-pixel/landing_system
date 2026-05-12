#!/usr/bin/env bats

setup() {
  ROOT="$(cd "$(dirname "$BATS_TEST_FILENAME")/../.." && pwd)"
  COMPOSER="$ROOT/skills/block-composition/scripts/compose-blocks.py"

  PROJECT="$BATS_TMPDIR/proj-$$"
  mkdir -p "$PROJECT/07_ПРОТОТИП" "$PROJECT/07a_WIREFRAME" "$PROJECT/05_ДИЗАЙН-СИСТЕМА"

  cat > "$PROJECT/07_ПРОТОТИП/prototype.yaml" <<EOF
project: {slug: test, niche: services, source_file: x.pdf}
blocks:
  - position: 1
    type: hero
    headline: "Hello world"
    cta: {text: "Click", action: ""}
    slots: []
EOF

  cat > "$PROJECT/07a_WIREFRAME/selections.yaml" <<EOF
project_slug: test
selections:
  - block_position: 1
    chosen_variant: ru-hero-01-services-calc
confirmed_at: "2026-05-12T14:23:00Z"
EOF

  cat > "$PROJECT/05_ДИЗАЙН-СИСТЕМА/tokens.json" <<EOF
{"color":{"bg":"#fff","fg":"#000","accent":"#0066cc"},"font":{"display":"sans","body":"sans"},"spacing":{"md":"16px","lg":"32px"}}
EOF
}

@test "produces composed.html and composed-mobile.html" {
  run python3 "$COMPOSER" --project "$PROJECT" --library "$ROOT/block-library"
  [ "$status" -eq 0 ]
  [ -f "$PROJECT/07b_COMPOSED/composed.html" ]
  [ -f "$PROJECT/07b_COMPOSED/composed-mobile.html" ]
}

@test "composed.html contains prototype headline" {
  python3 "$COMPOSER" --project "$PROJECT" --library "$ROOT/block-library"
  grep -q "Hello world" "$PROJECT/07b_COMPOSED/composed.html"
}

@test "composed.html contains accent color from tokens" {
  python3 "$COMPOSER" --project "$PROJECT" --library "$ROOT/block-library"
  grep -q "#0066cc" "$PROJECT/07b_COMPOSED/composed.html"
}

@test "block-injection-log.md is created" {
  python3 "$COMPOSER" --project "$PROJECT" --library "$ROOT/block-library"
  [ -f "$PROJECT/07b_COMPOSED/block-injection-log.md" ]
}
