#!/usr/bin/env bats
#
# Stage-08 gate-check tests for the Lazy Blocks pipeline.
# These build a minimal valid project inline (no shared fixture) so each test
# starts from a clean known-good state, then mutates one thing to assert
# a specific failure.

setup() {
  ROOT="$(cd "$(dirname "$BATS_TEST_FILENAME")/../.." && pwd)"
  WORK="$(python -c "import tempfile; print(tempfile.mkdtemp().replace(chr(92),'/'))")"
  PROJ="$WORK/project"

  # Prior-stage approved markers required by 08_build gate (07_content)
  mkdir -p "$PROJ/05_ДИЗАЙН-СИСТЕМА" "$PROJ/07_КОНТЕНТ" \
           "$PROJ/08_КОД/wp-theme/blocks/lazyblock-hero" \
           "$PROJ/08_КОД/wp-theme/assets/css"

  # Pretend prior stages exist + are approved
  printf "# DESIGN\n" > "$PROJ/05_ДИЗАЙН-СИСТЕМА/DESIGN.md"
  printf "{}\n"      > "$PROJ/05_ДИЗАЙН-СИСТЕМА/tokens.json"
  printf "## Hero\n\ntext\n" > "$PROJ/07_КОНТЕНТ/final-copy.md"

  # Stage-state with prior stages approved (gate-check reads .landing-state.yaml)
  cat > "$PROJ/.landing-state.yaml" <<'EOF'
stages:
  "00_brief": {status: approved}
  "01_context": {status: approved}
  "01a_niche_analysis": {status: approved}
  "02_assets": {status: approved}
  "03_references": {status: approved}
  "04_brand": {status: approved}
  "05_design": {status: approved}
  "06_stack": {status: approved}
  "07_content": {status: approved}
EOF

  # ── Lazy Blocks artifacts ────────────────────────────────────────────────
  # block-spec.yaml — minimal valid single block
  cat > "$PROJ/08_КОД/block-spec.yaml" <<'EOF'
version: 1
page:
  title: "Home"
  slug: "home"
blocks:
  - slug: hero
    type: single
    title: "Hero"
    icon: "star-filled"
    category: "lp-blocks"
    controls:
      - { id: c_title, name: title, type: text, label: "Title", default: "Hi" }
EOF

  # functions.php with both required markers
  cat > "$PROJ/08_КОД/wp-theme/functions.php" <<'EOF'
<?php
add_action('lzb/init', function () {
    lazyblocks()->add_block([
        'slug' => 'lazyblock/hero',
        'title' => 'Hero',
    ]);
});
EOF

  # at least one lazyblock-*/block.php
  printf "<?php // hero render\n" > "$PROJ/08_КОД/wp-theme/blocks/lazyblock-hero/block.php"

  # page-content.html
  printf "<!-- wp:lazyblock/hero /-->\n" > "$PROJ/08_КОД/page-content.html"
}

teardown() { rm -rf "$WORK"; }

@test "happy path: valid Lazy Blocks project passes 08_build gate" {
  run bash "$ROOT/scripts/gate-check.sh" --stage 08_build --project "$PROJ" --auto
  [ "$status" -eq 0 ]
}

@test "fails when block-spec.yaml is missing" {
  rm "$PROJ/08_КОД/block-spec.yaml"
  run python "$ROOT/scripts/lib/stage_08_helper.py" "$PROJ"
  [ "$status" -ne 0 ]
  [[ "$output" == *"block-spec.yaml"* ]]
}

@test "fails when block-spec.yaml is malformed" {
  printf "version: 1\nblocks: [not valid\n" > "$PROJ/08_КОД/block-spec.yaml"
  run python "$ROOT/scripts/lib/stage_08_helper.py" "$PROJ"
  [ "$status" -ne 0 ]
  [[ "$output" == *"block-spec.yaml"* ]]
}

@test "fails when functions.php lacks lzb/init" {
  printf "<?php\n// no lzb hook here\nlazyblocks()->add_block([]);\n" > "$PROJ/08_КОД/wp-theme/functions.php"
  run python "$ROOT/scripts/lib/stage_08_helper.py" "$PROJ"
  [ "$status" -ne 0 ]
  [[ "$output" == *"lzb/init"* ]]
}

@test "fails when functions.php lacks lazyblocks()->add_block(" {
  printf "<?php\nadd_action('lzb/init', function(){});\n" > "$PROJ/08_КОД/wp-theme/functions.php"
  run python "$ROOT/scripts/lib/stage_08_helper.py" "$PROJ"
  [ "$status" -ne 0 ]
  [[ "$output" == *"add_block"* ]]
}

@test "fails when no lazyblock-*/block.php under blocks/" {
  rm -rf "$PROJ/08_КОД/wp-theme/blocks"
  mkdir -p "$PROJ/08_КОД/wp-theme/blocks"
  run python "$ROOT/scripts/lib/stage_08_helper.py" "$PROJ"
  [ "$status" -ne 0 ]
  [[ "$output" == *"lazyblock-"* ]] || [[ "$output" == *"block.php"* ]]
}

@test "fails when page-content.html is missing" {
  rm "$PROJ/08_КОД/page-content.html"
  run python "$ROOT/scripts/lib/stage_08_helper.py" "$PROJ"
  [ "$status" -ne 0 ]
  [[ "$output" == *"page-content.html"* ]]
}

@test "legacy: true bypasses all hard checks" {
  rm -rf "$PROJ/08_КОД/wp-theme" "$PROJ/08_КОД/block-spec.yaml" "$PROJ/08_КОД/page-content.html"
  printf "legacy: true\n" >> "$PROJ/.landing-state.yaml"
  run python "$ROOT/scripts/lib/stage_08_helper.py" "$PROJ"
  [ "$status" -eq 0 ]
}
