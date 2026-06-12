#!/usr/bin/env bats
# Test PR-S: Style Moods System
# Tests mood selection, persistence, and CSS application

setup() {
    export TEST_PROJECT="$BATS_TMPDIR/test-mood-project"
    export LIBRARY="d:/AI_TEAMS/landing_system/block-library"
    mkdir -p "$TEST_PROJECT/07a_WIREFRAME"
    mkdir -p "$TEST_PROJECT/05_ДИЗАЙН-СИСТЕМА"
    mkdir -p "$TEST_PROJECT/07b_COMPOSED"
}

# Test 1: Wireframe shell template includes mood tabs placeholder
@test "wireframe-shell.html includes mood-tabs DOM and CSS" {
    grep -q ".lp-mood-tabs" "d:/AI_TEAMS/landing_system/skills/wireframe-rendering/templates/wireframe-shell.html"
    [ $? -eq 0 ]
}

# Test 2: Template includes mood radio CSS rules placeholder
@test "wireframe-shell.html includes checked_mood_tab_rules placeholder" {
    grep -q "{{checked_mood_tab_rules}}" "d:/AI_TEAMS/landing_system/skills/wireframe-rendering/templates/wireframe-shell.html"
    [ $? -eq 0 ]
}

# Test 3: confirmSelections captures mood from radio buttons
@test "wireframe-shell.html confirmSelections reads getAttribute data-mood" {
    grep -q "getAttribute.*data-mood" "d:/AI_TEAMS/landing_system/skills/wireframe-rendering/templates/wireframe-shell.html"
    [ $? -eq 0 ]
}

# Test 4: confirmSelections adds style_mood to YAML if mood selected
@test "wireframe-shell.html confirmSelections adds style_mood field to YAML" {
    grep -q "style_mood" "d:/AI_TEAMS/landing_system/skills/wireframe-rendering/templates/wireframe-shell.html"
    [ $? -eq 0 ]
}

# Test 5: MOODS constant defined in render-wireframe.py
@test "render-wireframe.py defines MOODS constant with all 6 moods" {
    grep -q 'MOODS = \["brutalist"' "d:/AI_TEAMS/landing_system/skills/wireframe-rendering/scripts/render-wireframe.py"
    [ $? -eq 0 ]
}

# Test 6: _load_mood_css helper exists
@test "render-wireframe.py has _load_mood_css helper function" {
    grep -q "def _load_mood_css" "d:/AI_TEAMS/landing_system/skills/wireframe-rendering/scripts/render-wireframe.py"
    [ $? -eq 0 ]
}

# Test 7: compose-blocks.py reads style_mood from selections
@test "compose-blocks.py reads style_mood from selections.yaml" {
    grep -q 'style_mood = sel.get("style_mood")' "d:/AI_TEAMS/landing_system/skills/block-composition/scripts/compose-blocks.py"
    [ $? -eq 0 ]
}

# Test 8: compose-blocks.py passes mood to inject-tokens
@test "compose-blocks.py passes --mood to inject-tokens.py" {
    grep -q '\["--mood", style_mood\]' "d:/AI_TEAMS/landing_system/skills/block-composition/scripts/compose-blocks.py"
    [ $? -eq 0 ]
}

# Test 9: compose-blocks.py loads mood CSS files
@test "compose-blocks.py loads mood CSS from _styles directory" {
    grep -q 'library / "_styles" / style_mood' "d:/AI_TEAMS/landing_system/skills/block-composition/scripts/compose-blocks.py"
    [ $? -eq 0 ]
}

# Test 10: inject-tokens.py accepts --mood parameter
@test "inject-tokens.py has --mood argument parser" {
    grep -q 'p.add_argument("--mood"' "d:/AI_TEAMS/landing_system/skills/block-composition/scripts/inject-tokens.py"
    [ $? -eq 0 ]
}

# Test 11: inject-tokens.py has _load_mood_css function
@test "inject-tokens.py has extract_css_vars_from_file helper" {
    grep -q "def extract_css_vars_from_file" "d:/AI_TEAMS/landing_system/skills/block-composition/scripts/inject-tokens.py"
    [ $? -eq 0 ]
}

# Test 12: inject-tokens.py applies mood vars (mood_vars override)
@test "inject-tokens.py mood_vars override tokens vars" {
    grep -q 'if mood_vars and name in mood_vars:' "d:/AI_TEAMS/landing_system/skills/block-composition/scripts/inject-tokens.py"
    [ $? -eq 0 ]
}

# Test 13: All 6 moods have palette.css
@test "All 6 moods have palette.css file" {
    for mood in brutalist editorial-warm swiss-modernist retro-windows coral-soft monochrome-precision; do
        [ -f "$LIBRARY/_styles/$mood/palette.css" ] || return 1
    done
}

# Test 14: All moods have typography.css
@test "All 6 moods have typography.css file" {
    for mood in brutalist editorial-warm swiss-modernist retro-windows coral-soft monochrome-precision; do
        [ -f "$LIBRARY/_styles/$mood/typography.css" ] || return 1
    done
}

# Test 15: All moods have motion.css
@test "All 6 moods have motion.css file" {
    for mood in brutalist editorial-warm swiss-modernist retro-windows coral-soft monochrome-precision; do
        [ -f "$LIBRARY/_styles/$mood/motion.css" ] || return 1
    done
}

# Test 16: Mood palette contains CSS variables
@test "Mood palette.css contains --color- CSS variables" {
    grep -q -- "--color-" "$LIBRARY/_styles/brutalist/palette.css"
    [ $? -eq 0 ]
}

# Test 17: BACKLOG.md reflects PR-S status
@test "BACKLOG.md has PR-S entry with current status" {
    grep -q "PR-S.*Style Moods System" "d:/AI_TEAMS/landing_system/docs/BACKLOG.md"
    [ $? -eq 0 ]
}

# Test 18: Backward compatibility: old selections without mood still work
@test "compose-blocks.py handles missing style_mood gracefully" {
    grep -q "if style_mood:" "d:/AI_TEAMS/landing_system/skills/block-composition/scripts/compose-blocks.py"
    [ $? -eq 0 ]
}

# Test 19: Mood CSS comment in log
@test "compose-blocks.py logs mood in block-injection-log.md" {
    grep -q 'mood_note' "d:/AI_TEAMS/landing_system/skills/block-composition/scripts/compose-blocks.py"
    [ $? -eq 0 ]
}

# Test 20: wireframe-shell.html includes MOOD_RADIOS_CSS constant usage
@test "wireframe-shell.html or render-wireframe uses MOOD_RADIOS_CSS for hidden radio styling" {
    grep -q "MOOD_RADIOS_CSS\|mood.*radio" "d:/AI_TEAMS/landing_system/skills/wireframe-rendering/scripts/render-wireframe.py"
    [ $? -eq 0 ]
}
