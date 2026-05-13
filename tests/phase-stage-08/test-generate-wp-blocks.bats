#!/usr/bin/env bats
#
# Orchestrator tests for the Lazy Blocks stage-08 pipeline
# (scripts/generate-wp-blocks.py).
#
# These build a tmp project with the minimum stage-05/stage-06/stage-08 inputs
# the generators need, then assert the orchestrator produces the expected
# Lazy Blocks artifacts.

setup() {
  ROOT="$(cd "$(dirname "$BATS_TEST_FILENAME")/../.." && pwd)"
  SCRIPT="$ROOT/scripts/generate-wp-blocks.py"
  WORK="$(python -c "import tempfile; print(tempfile.mkdtemp().replace(chr(92),'/'))")"
  PROJ="$WORK/project"
  mkdir -p "$PROJ/05_ДИЗАЙН-СИСТЕМА" "$PROJ/06_СТЕК" "$PROJ/07_КОНТЕНТ" "$PROJ/08_КОД"

  # Minimal stage-05 tokens
  cat > "$PROJ/05_ДИЗАЙН-СИСТЕМА/tokens.json" <<'EOF'
{
  "colors":   {"primary": {"hex": "#111111"}, "bg": {"hex": "#ffffff"}},
  "typography": {"h1": {"family": "Inter", "size": "2rem", "weight": "700", "line_height": "1.2"}, "body": {"family": "Inter", "size": "1rem", "weight": "400", "line_height": "1.5"}},
  "spacing":  {"sm": "8px", "md": "16px"},
  "radius":   {"md": "8px"},
  "shadow":   {"md": "0 2px 4px rgba(0,0,0,.1)"}
}
EOF

  # Minimal stage-06 design-stack
  cat > "$PROJ/06_СТЕК/design-stack.yaml" <<'EOF'
icons: {provider: iconify, set: lucide}
fonts: {provider: bunny}
libraries: []
EOF

  # Stage-07 content (used by content-driven generators if invoked; harmless if not)
  printf "## Hero\n\nText\n" > "$PROJ/07_КОНТЕНТ/final-copy.md"

  # Copy the canonical example block-spec into the project
  cp "$ROOT/template/08_КОД/block-spec.example.yaml" "$PROJ/08_КОД/block-spec.yaml"
}

teardown() { rm -rf "$WORK"; }

@test "--dry-run lists all 5 steps and writes nothing" {
  run python "$SCRIPT" --project "$PROJ" --dry-run
  [ "$status" -eq 0 ]
  [[ "$output" == *"dry-run"* ]]
  [[ "$output" == *"theme scaffold"* ]]
  [[ "$output" == *"lzb templates"* ]]
  [[ "$output" == *"lzb registration"* ]]
  [[ "$output" == *"css patches"* ]]
  [[ "$output" == *"page content"* ]]
  [ ! -f "$PROJ/08_КОД/wp-theme/functions.php" ]
  [ ! -f "$PROJ/08_КОД/page-content.html" ]
}

@test "full run produces Lazy Blocks artifacts" {
  run python "$SCRIPT" --project "$PROJ"
  [ "$status" -eq 0 ]

  # functions.php with both markers
  [ -f "$PROJ/08_КОД/wp-theme/functions.php" ]
  grep -q "lzb/init" "$PROJ/08_КОД/wp-theme/functions.php"
  grep -q "lazyblocks()->add_block(" "$PROJ/08_КОД/wp-theme/functions.php"

  # at least one lazyblock-*/block.php
  ls "$PROJ/08_КОД/wp-theme/blocks/" | grep -q "^lazyblock-"
  find "$PROJ/08_КОД/wp-theme/blocks" -name "block.php" | grep -q "block.php"

  # page-content.html with wp:lazyblock markup
  [ -f "$PROJ/08_КОД/page-content.html" ]
  grep -q "<!-- wp:lazyblock/" "$PROJ/08_КОД/page-content.html"
}

@test "section-card spec → css patches contain AUTO-GENERATED marker" {
  # the example block-spec includes a section-card (tarify), so css patches must fire
  run python "$SCRIPT" --project "$PROJ"
  [ "$status" -eq 0 ]
  [ -f "$PROJ/08_КОД/wp-theme/assets/css/main.css" ]
  grep -q "AUTO-GENERATED" "$PROJ/08_КОД/wp-theme/assets/css/main.css"
}

@test "missing block-spec.yaml → orchestrator fails at lzb templates step" {
  rm "$PROJ/08_КОД/block-spec.yaml"
  run python "$SCRIPT" --project "$PROJ"
  [ "$status" -ne 0 ]
  # Step 1 (theme scaffold) doesn't need block-spec; failure must come from step 2+
  [[ "$output" == *"lzb templates"* ]] || [[ "$output" == *"block-spec"* ]]
}

@test "gate-check passes on freshly orchestrated project" {
  run python "$SCRIPT" --project "$PROJ"
  [ "$status" -eq 0 ]
  run python "$ROOT/scripts/lib/stage_08_helper.py" "$PROJ"
  [ "$status" -eq 0 ]
}
