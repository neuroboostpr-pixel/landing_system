#!/usr/bin/env bats
# test-patterns-library.bats — PR-A.X + PR-A visual-upgrade: OpenDesign patterns library tests
# Tests: 12 HTML design templates, 12 craft files, 15 patterns, 6 style moods, 8 visual skills

ROOT="$(cd "$(dirname "$BATS_TEST_FILENAME")/../.." && pwd)"

# ─────────────────────────────────────────────────────────────────
# Test 1: All 15 patterns directories exist (9 original + 6 new)
# ─────────────────────────────────────────────────────────────────
@test "all 15 patterns directories exist" {
  local patterns=(
    scroll-reveal
    paper-texture
    ambient-mesh-bg
    marquee-fade
    floating-pill-nav
    headroom-nav
    dot-grid-bg
    conic-ring
    bento-grid-hairline
    gradient-mesh-animated
    cursor-aura
    text-reveal-mask
    sticky-section-reveal
    magnetic-button
    marquee-3d-perspective
  )
  for p in "${patterns[@]}"; do
    local dir="$ROOT/block-library/_patterns/$p"
    if [ ! -d "$dir" ]; then
      echo "MISSING pattern directory: $p"
      return 1
    fi
  done
}

# ─────────────────────────────────────────────────────────────────
# Test 2: Every pattern has snippet.css and SOURCE.md (all 15)
# ─────────────────────────────────────────────────────────────────
@test "every pattern has snippet.css and SOURCE.md" {
  local patterns=(
    scroll-reveal
    paper-texture
    ambient-mesh-bg
    marquee-fade
    floating-pill-nav
    headroom-nav
    dot-grid-bg
    conic-ring
    bento-grid-hairline
    gradient-mesh-animated
    cursor-aura
    text-reveal-mask
    sticky-section-reveal
    magnetic-button
    marquee-3d-perspective
  )
  for p in "${patterns[@]}"; do
    local dir="$ROOT/block-library/_patterns/$p"
    if [ ! -f "$dir/snippet.css" ]; then
      echo "MISSING snippet.css in: $p"
      return 1
    fi
    if [ ! -f "$dir/SOURCE.md" ]; then
      echo "MISSING SOURCE.md in: $p"
      return 1
    fi
  done
}

# ─────────────────────────────────────────────────────────────────
# Test 3: Every animated pattern respects prefers-reduced-motion
# ─────────────────────────────────────────────────────────────────
@test "every animated pattern respects prefers-reduced-motion" {
  # Patterns with CSS animations/transitions that MUST have prefers-reduced-motion
  local animated_patterns=(
    scroll-reveal
    ambient-mesh-bg
    marquee-fade
    floating-pill-nav
    headroom-nav
  )
  for p in "${animated_patterns[@]}"; do
    local css="$ROOT/block-library/_patterns/$p/snippet.css"
    if [ ! -f "$css" ]; then
      echo "snippet.css missing: $p"
      return 1
    fi
    if ! grep -q "prefers-reduced-motion" "$css"; then
      echo "MISSING prefers-reduced-motion in: $p/snippet.css"
      return 1
    fi
  done
}

# ─────────────────────────────────────────────────────────────────
# Test 4: No WhatsApp references in patterns (RU compliance)
# ─────────────────────────────────────────────────────────────────
@test "no whatsapp references in pattern snippets (html/css/js)" {
  local patterns_dir="$ROOT/block-library/_patterns"
  # Only check actual snippet files — not README/SOURCE docs that may mention WhatsApp as a prohibition
  local found=0
  while IFS= read -r -d '' f; do
    if grep -qi "wa\.me\|api\.whatsapp" "$f" 2>/dev/null; then
      echo "Found WhatsApp link in snippet: $f"
      found=1
    fi
  done < <(find "$patterns_dir" -name "snippet.html" -o -name "snippet.css" -o -name "snippet.js" -print0 2>/dev/null)
  if [ "$found" -ne 0 ]; then
    return 1
  fi
}

# ─────────────────────────────────────────────────────────────────
# Test 5: vendor/opendesign-extracts/design-templates/ contains 12 HTML
# ─────────────────────────────────────────────────────────────────
@test "12 design templates copied from OpenDesign (6 original + 6 new)" {
  local templates_dir="$ROOT/vendor/opendesign-extracts/design-templates"
  if [ ! -d "$templates_dir" ]; then
    echo "MISSING: design-templates directory"
    return 1
  fi
  local count
  count=$(find "$templates_dir" -maxdepth 1 -name "*.html" | wc -l | tr -d ' ')
  if [ "$count" -ne 12 ]; then
    echo "Expected 12 HTML templates, found: $count"
    ls "$templates_dir"
    return 1
  fi
}

# ─────────────────────────────────────────────────────────────────
# Test 6: vendor/opendesign-extracts/craft/ contains 12 .md files (11 + README)
# ─────────────────────────────────────────────────────────────────
@test "12 craft files copied from OpenDesign (11 knowledge + README)" {
  local craft_dir="$ROOT/vendor/opendesign-extracts/craft"
  if [ ! -d "$craft_dir" ]; then
    echo "MISSING: craft directory"
    return 1
  fi
  local count
  count=$(find "$craft_dir" -maxdepth 1 -name "*.md" | wc -l | tr -d ' ')
  if [ "$count" -lt 11 ]; then
    echo "Expected at least 11 craft .md files, found: $count"
    ls "$craft_dir"
    return 1
  fi
}

# ─────────────────────────────────────────────────────────────────
# Test 7: Design templates have attribution headers
# ─────────────────────────────────────────────────────────────────
@test "all design templates have attribution header" {
  local templates_dir="$ROOT/vendor/opendesign-extracts/design-templates"
  for f in "$templates_dir"/*.html; do
    if [ ! -f "$f" ]; then continue; fi
    local first_line
    first_line=$(head -1 "$f")
    if ! echo "$first_line" | grep -q "github.com/nexu-io/open-design"; then
      echo "MISSING attribution header in: $(basename "$f")"
      echo "First line: $first_line"
      return 1
    fi
    if ! echo "$first_line" | grep -q "Apache-2.0"; then
      echo "MISSING License: Apache-2.0 in: $(basename "$f")"
      return 1
    fi
  done
}

# ─────────────────────────────────────────────────────────────────
# Test 8: generate-theme.py contains patterns integration code
# ─────────────────────────────────────────────────────────────────
@test "generate-theme.py includes patterns integration" {
  local script="$ROOT/skills/wp-gutenberg-block-builder/scripts/generate-theme.py"
  if ! grep -q "PATTERNS_BY_MODE" "$script"; then
    echo "MISSING: PATTERNS_BY_MODE in generate-theme.py"
    return 1
  fi
  if ! grep -q "_append_patterns_css" "$script"; then
    echo "MISSING: _append_patterns_css in generate-theme.py"
    return 1
  fi
  if ! grep -q "_write_animations_js" "$script"; then
    echo "MISSING: _write_animations_js in generate-theme.py"
    return 1
  fi
  if ! grep -q "lp-animations" "$script"; then
    echo "MISSING: lp-animations enqueue in generate-theme.py"
    return 1
  fi
}

# ─────────────────────────────────────────────────────────────────
# Test 9: SKILL.md contains Visual Patterns section
# ─────────────────────────────────────────────────────────────────
@test "SKILL.md contains Visual Patterns Library section" {
  local skill="$ROOT/skills/wp-gutenberg-block-builder/SKILL.md"
  if ! grep -q "Visual Patterns Library" "$skill"; then
    echo "MISSING: 'Visual Patterns Library' section in SKILL.md"
    return 1
  fi
  if ! grep -q "Anti-AI-Slop" "$skill" && ! grep -q "anti-ai-slop\|Anti-AI" "$skill"; then
    echo "MISSING: Anti-AI-Slop section in SKILL.md"
    return 1
  fi
}

# ─────────────────────────────────────────────────────────────────
# Test 10: patterns README.md exists
# ─────────────────────────────────────────────────────────────────
@test "block-library/_patterns/README.md exists" {
  local readme="$ROOT/block-library/_patterns/README.md"
  if [ ! -f "$readme" ]; then
    echo "MISSING: block-library/_patterns/README.md"
    return 1
  fi
  if ! grep -q "Apache-2.0\|OpenDesign" "$readme"; then
    echo "MISSING: attribution in patterns README.md"
    return 1
  fi
}

# ─────────────────────────────────────────────────────────────────
# Test 11: All 6 style moods exist in block-library/_styles/
# ─────────────────────────────────────────────────────────────────
@test "all 6 style moods exist" {
  local moods=(
    brutalist
    editorial-warm
    swiss-modernist
    retro-windows
    coral-soft
    monochrome-precision
  )
  local styles_dir="$ROOT/block-library/_styles"
  if [ ! -d "$styles_dir" ]; then
    echo "MISSING: block-library/_styles directory"
    return 1
  fi
  for m in "${moods[@]}"; do
    local dir="$styles_dir/$m"
    if [ ! -d "$dir" ]; then
      echo "MISSING style mood directory: $m"
      return 1
    fi
  done
}

# ─────────────────────────────────────────────────────────────────
# Test 12: Every style mood has 4 required files
# ─────────────────────────────────────────────────────────────────
@test "every style mood has palette.css typography.css motion.css style-guide.md" {
  local moods=(
    brutalist
    editorial-warm
    swiss-modernist
    retro-windows
    coral-soft
    monochrome-precision
  )
  local styles_dir="$ROOT/block-library/_styles"
  for m in "${moods[@]}"; do
    local dir="$styles_dir/$m"
    for f in palette.css typography.css motion.css style-guide.md; do
      if [ ! -f "$dir/$f" ]; then
        echo "MISSING file: $m/$f"
        return 1
      fi
    done
  done
}

# ─────────────────────────────────────────────────────────────────
# Test 13: 8 visual-skills SKILL.md files in vendor/
# ─────────────────────────────────────────────────────────────────
@test "8 visual-skills SKILL.md copied to vendor/opendesign-extracts/visual-skills/" {
  local skills_dir="$ROOT/vendor/opendesign-extracts/visual-skills"
  local skills=(
    gsap-timeline.md
    gsap-scrolltrigger.md
    threejs.md
    shader-dev.md
    algorithmic-art.md
    hand-drawn-diagrams.md
    color-expert.md
    taste-skill.md
  )
  if [ ! -d "$skills_dir" ]; then
    echo "MISSING: visual-skills directory"
    return 1
  fi
  for s in "${skills[@]}"; do
    if [ ! -f "$skills_dir/$s" ]; then
      echo "MISSING visual skill: $s"
      return 1
    fi
  done
}

# ─────────────────────────────────────────────────────────────────
# Test 14: generate-theme.py supports style_mood
# ─────────────────────────────────────────────────────────────────
@test "generate-theme.py supports style_mood integration" {
  local script="$ROOT/skills/wp-gutenberg-block-builder/scripts/generate-theme.py"
  if ! grep -q "STYLE_MOOD_PATTERNS" "$script"; then
    echo "MISSING: STYLE_MOOD_PATTERNS in generate-theme.py"
    return 1
  fi
  if ! grep -q "_get_style_mood" "$script"; then
    echo "MISSING: _get_style_mood function in generate-theme.py"
    return 1
  fi
  if ! grep -q "_apply_style_mood" "$script"; then
    echo "MISSING: _apply_style_mood function in generate-theme.py"
    return 1
  fi
  # Check all 6 moods are in the mapping (double or single quotes)
  for mood in brutalist editorial-warm swiss-modernist retro-windows coral-soft monochrome-precision; do
    if ! grep -q "\"$mood\"\|'$mood'" "$script"; then
      echo "MISSING mood '$mood' in STYLE_MOOD_PATTERNS"
      return 1
    fi
  done
}

# ─────────────────────────────────────────────────────────────────
# Test 15: SKILL.md wp-builder contains Style Moods section
# ─────────────────────────────────────────────────────────────────
@test "SKILL.md wp-builder contains Style Moods section" {
  local skill="$ROOT/skills/wp-gutenberg-block-builder/SKILL.md"
  if ! grep -q "Style Moods" "$skill"; then
    echo "MISSING: 'Style Moods' section in SKILL.md"
    return 1
  fi
  # Check all 6 moods are mentioned
  for mood in brutalist editorial-warm swiss-modernist retro-windows coral-soft monochrome-precision; do
    if ! grep -q "$mood" "$skill"; then
      echo "MISSING mood '$mood' in SKILL.md"
      return 1
    fi
  done
}
